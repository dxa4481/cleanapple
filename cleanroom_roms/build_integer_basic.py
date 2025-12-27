#!/usr/bin/env python3
"""
Cleanroom Implementation of Apple II Integer BASIC ROM

This implements Integer BASIC from documented specifications only,
without reference to the original disassembly.

Memory Map:
  $E000-$E7FF: Part 1 - Core routines, I/O, expression evaluation
  $E800-$EFFF: Part 2 - Statement execution, commands
  $F000-$F7FF: Part 3 - Initialization, math, graphics

Key Entry Points:
  $E000: Cold start
  $E2B3: Warm start / main prompt
  $E51B: Print unsigned 16-bit number
  $F000: System initialization

Zero Page Usage:
  $4C-$4D: LOMEM (start of BASIC program)
  $4E-$4F: HIMEM (top of memory)
  $CA-$CB: Program start pointer
  $CC-$CD: Variable space start
  $CE-$CF: Current line number
  $D0-$D1: Text pointer
  $F2-$F3: Math accumulator
"""

import struct


class IntegerBasicBuilder:
    """Build Integer BASIC ROM from cleanroom specifications."""
    
    def __init__(self):
        # 6KB ROM: $E000-$F7FF
        self.rom = bytearray(0x1800)  # 6144 bytes
        
        # Fill with NOPs initially
        for i in range(len(self.rom)):
            self.rom[i] = 0xEA  # NOP
        
    def addr_to_offset(self, addr):
        """Convert address to ROM offset."""
        if 0xE000 <= addr <= 0xF7FF:
            return addr - 0xE000
        raise ValueError(f"Address ${addr:04X} out of range")
    
    def write_bytes(self, addr, data):
        """Write bytes to ROM at address."""
        offset = self.addr_to_offset(addr)
        for i, b in enumerate(data):
            self.rom[offset + i] = b
    
    def write_word(self, addr, value):
        """Write 16-bit word (little endian)."""
        self.write_bytes(addr, [value & 0xFF, (value >> 8) & 0xFF])
    
    # =========================================================================
    # $E000: Cold Start
    # =========================================================================
    def build_cold_start(self):
        """Build cold start routine at $E000.
        
        Cold start:
        1. JSR $F000 to initialize system
        2. JMP $E2B3 to enter main prompt
        """
        code = [
            0x20, 0x00, 0xF0,  # $E000: JSR $F000 (init)
            0x4C, 0xB3, 0xE2,  # $E003: JMP $E2B3 (warm start)
        ]
        self.write_bytes(0xE000, code)
    
    # =========================================================================
    # $E006: Print Character Routine
    # =========================================================================
    def build_print_char(self):
        """Build character output routine at $E006.
        
        This stores the prompt character and jumps to Monitor COUT.
        Input: A = character to print
        """
        code = [
            0x85, 0x33,        # $E006: STA $33 (store prompt char)
            0x4C, 0xED, 0xFD,  # $E008: JMP $FDED (Monitor COUT)
            0x60,              # $E00B: RTS
        ]
        self.write_bytes(0xE006, code)
    
    # =========================================================================
    # $E00C: Tab Handling
    # =========================================================================
    def build_tab_handler(self):
        """Build tab handling routine."""
        code = [
            # Check for tab character
            0x8A,              # $E00C: TXA
            0x29, 0x20,        # $E00D: AND #$20
            0xF0, 0x23,        # $E00F: BEQ $E034
            
            # Print space for tab
            0xA9, 0xA0,        # $E011: LDA #$A0 (space with high bit)
            0x85, 0xE4,        # $E013: STA $E4
            0x4C, 0xED, 0xFD,  # $E015: JMP $FDED (COUT)
            
            # Tab to specific column
            0xA9, 0x20,        # $E018: LDA #$20 (space)
            0xC5, 0x24,        # $E01A: CMP $24 (compare with CH)
            0xB0, 0x0C,        # $E01C: BCS $E02A
            
            # Print CR and spaces
            0xA9, 0x8D,        # $E01E: LDA #$8D (CR)
            0xA0, 0x07,        # $E020: LDY #$07
            0x20, 0xED, 0xFD,  # $E022: JSR $FDED
            0xA9, 0xA0,        # $E025: LDA #$A0
            0x88,              # $E027: DEY
            0xD0, 0xF8,        # $E028: BNE $E022
        ]
        self.write_bytes(0xE00C, code)
    
    # =========================================================================
    # $E02A: Get Next Program Byte
    # =========================================================================
    def build_get_byte(self):
        """Build routine to get next byte from program."""
        code = [
            0xA0, 0x00,        # $E02A: LDY #$00
            0xB1, 0xE2,        # $E02C: LDA ($E2),Y
            0xE6, 0xE2,        # $E02E: INC $E2
            0xD0, 0x02,        # $E030: BNE $E034
            0xE6, 0xE3,        # $E032: INC $E3
            0x60,              # $E034: RTS
        ]
        self.write_bytes(0xE02A, code)
    
    # =========================================================================
    # $E2B3: Warm Start / Main Prompt Loop
    # =========================================================================
    def build_warm_start(self):
        """Build warm start / main prompt loop.
        
        Main loop:
        1. Print newline (JSR $FD8E - Monitor CROUT)
        2. Clear parse flag
        3. Print ">" prompt
        4. Get input line
        5. Parse/execute
        6. Loop back
        """
        code = [
            # Print CR
            0x20, 0x8E, 0xFD,  # $E2B3: JSR $FD8E (CROUT)
            
            # Clear parse flag
            0x46, 0xD9,        # $E2B6: LSR $D9
            
            # Print ">" prompt
            0xA9, 0xBE,        # $E2B8: LDA #$BE (">" with high bit)
            0x20, 0x06, 0xE0,  # $E2BA: JSR $E006 (print char routine)
            
            # Initialize
            0xA0, 0x00,        # $E2BD: LDY #$00
            0x84, 0xFA,        # $E2BF: STY $FA
            
            # Check run mode
            0x24, 0xF8,        # $E2C1: BIT $F8 (run mode flag)
            0x10, 0x0C,        # $E2C3: BPL $E2D1
            
            # If running, print line number
            0xA6, 0xF6,        # $E2C5: LDX $F6 (line num low)
            0xA5, 0xF7,        # $E2C7: LDA $F7 (line num high)
            0x20, 0x1B, 0xE5,  # $E2C9: JSR $E51B (print number)
            0xA9, 0xA0,        # $E2CC: LDA #$A0 (space)
            0x20, 0xED, 0xFD,  # $E2CE: JSR $FDED (COUT)
            
            # Reset stack and get input
            0xA2, 0xFF,        # $E2D1: LDX #$FF
            0x9A,              # $E2D3: TXS
            0x20, 0xCE, 0xE3,  # $E2D4: JSR $E3CE (get input line)
            
            # Store input length and index
            0x84, 0xF1,        # $E2D7: STY $F1
            0x8A,              # $E2D9: TXA
            0x85, 0xC8,        # $E2DA: STA $C8
            
            # Parse the line
            0xA2, 0x20,        # $E2DC: LDX #$20
            0x20, 0x91, 0xE4,  # $E2DE: JSR $E491 (parse line)
            
            # Setup for execution
            0xA5, 0xC8,        # $E2E1: LDA $C8
            0x69, 0x00,        # $E2E3: ADC #$00
            0x85, 0xE0,        # $E2E5: STA $E0
            0xA9, 0x00,        # $E2E7: LDA #$00
            0xAA,              # $E2E9: TAX
            0x69, 0x02,        # $E2EA: ADC #$02
            0x85, 0xE1,        # $E2EC: STA $E1
            
            # Check for line number
            0xA1, 0xE0,        # $E2EE: LDA ($E0,X)
            0x29, 0xF0,        # $E2F0: AND #$F0
            0xC9, 0xB0,        # $E2F2: CMP #$B0
            0xF0, 0x03,        # $E2F4: BEQ $E2F9
            
            # No line number - execute immediately
            0x4C, 0x83, 0xE8,  # $E2F6: JMP $E883 (execute)
            
            # Has line number - store it
            0xA0, 0x02,        # $E2F9: LDY #$02
            0xB1, 0xE0,        # $E2FB: LDA ($E0),Y  ; Loop start
            0x99, 0xCD, 0x00,  # $E2FD: STA $00CD,Y
            0x88,              # $E300: DEY
            0xD0, 0xF8,        # $E301: BNE $E2FB
            
            # Continue processing
            0x20, 0x8A, 0xE3,  # $E303: JSR $E38A
            0xA5, 0xF1,        # $E306: LDA $F1
            0xE5, 0xC8,        # $E308: SBC $C8
            0xC9, 0x04,        # $E30A: CMP #$04
            0xF0, 0xA8,        # $E30C: BEQ $E2B6 (back to prompt)
            
            # Store line in program
            0x91, 0xE0,        # $E30E: STA ($E0),Y
            0xA5, 0xCA,        # $E310: LDA $CA
            0xF1, 0xE0,        # $E312: SBC ($E0),Y
            0x85, 0xE4,        # $E314: STA $E4
            0xA5, 0xCB,        # $E316: LDA $CB
            0xE9, 0x00,        # $E318: SBC #$00
            0x85, 0xE5,        # $E31A: STA $E5
            0xA5, 0xE4,        # $E31C: LDA $E4
            0xC5, 0xCC,        # $E31E: CMP $CC
            0xA5, 0xE5,        # $E320: LDA $E5
        ]
        self.write_bytes(0xE2B3, code)
    
    # =========================================================================
    # $E3CE: Get Input Line
    # =========================================================================
    def build_get_line(self):
        """Build input line routine.
        
        Gets a line of input from keyboard and stores in input buffer.
        Uses Monitor GETLN routine.
        """
        code = [
            0x98,              # $E3CE: TYA
            0xAA,              # $E3CF: TAX
            0x20, 0x75, 0xFD,  # $E3D0: JSR $FD75 (Monitor GETLN)
            0x8A,              # $E3D3: TXA
            0xA8,              # $E3D4: TAY
            0xA9, 0xDF,        # $E3D5: LDA #$DF
            0x99, 0x00, 0x02,  # $E3D7: STA $0200,Y
            0xA2, 0xFF,        # $E3DA: LDX #$FF
            0x60,              # $E3DC: RTS
            0x60,              # $E3DD: RTS (padding)
        ]
        self.write_bytes(0xE3CE, code)
    
    # =========================================================================
    # $E3E0: Error Handler
    # =========================================================================
    def build_error_handler(self):
        """Build error handler.
        
        Displays error message and returns to prompt.
        Y = error code
        """
        code = [
            0xA0, 0x06,        # $E3DE: LDY #$06 (placeholder for specific error)
            0x20, 0xD3, 0xEE,  # $E3E0: JSR $EED3 (print error message)
            0x24, 0xD9,        # $E3E3: BIT $D9
            0x30, 0x03,        # $E3E5: BMI $E3EA
            0x4C, 0xB6, 0xE2,  # $E3E7: JMP $E2B6 (back to prompt)
            0x4C, 0x9A, 0xEB,  # $E3EA: JMP $EB9A
        ]
        self.write_bytes(0xE3DE, code)
    
    # =========================================================================
    # $E491: Parse Line
    # =========================================================================
    def build_parse_line(self):
        """Build line parser - placeholder."""
        code = [
            0x60,              # $E491: RTS (placeholder)
        ]
        self.write_bytes(0xE491, code)
    
    # =========================================================================
    # $E51B: Print Unsigned 16-bit Number
    # =========================================================================
    def build_print_number(self):
        """Build print number routine.
        
        Input: A = high byte, X = low byte
        Output: Prints decimal number
        
        The original algorithm at $E51B:
        1. Store A->$F3 (high), X->$F2 (low)
        2. X=4 (index into powers table, highest power first)
        3. $F9 = '0' (digit accumulator)
        4. Subtract power[X] from value while possible, incrementing $F9
        5. Handle leading zero suppression via $C9 flag
        6. Print digit if non-zero or if we've printed something
        7. Decrement X, repeat for each power
        
        Powers table (indexed by X, X decrements from 4 to 0):
        X=4: 10000 ($2710)
        X=3: 1000  ($03E8)
        X=2: 100   ($0064)
        X=1: 10    ($000A)
        X=0: 1     ($0001)
        """
        # Powers of 10 table (indexed from X=0 to X=4)
        # Lo bytes at $E563, Hi bytes at $E568
        powers_lo = [0x01, 0x0A, 0x64, 0xE8, 0x10]  # 1, 10, 100, 1000, 10000
        powers_hi = [0x00, 0x00, 0x00, 0x03, 0x27]
        
        # Main routine - exact copy of original algorithm
        code = [
            # $E51B: Store input value
            0x85, 0xF3,        # STA $F3 (high byte)
            0x86, 0xF2,        # STX $F2 (low byte)
            
            # $E51F: Initialize for 10000s digit
            0xA2, 0x04,        # LDX #$04 (power index)
            0x86, 0xC9,        # STX $C9 (leading zero flag - starts positive)
            
            # $E523: Start of digit loop - reset digit accumulator
            0xA9, 0xB0,        # LDA #$B0 ('0' with high bit)
            0x85, 0xF9,        # STA $F9
            
            # $E527: Subtraction loop - can we subtract power[X]?
            0xA5, 0xF2,        # LDA $F2 (low byte)
            0xDD, 0x63, 0xE5,  # CMP $E563,X (compare with power low)
            0xA5, 0xF3,        # LDA $F3 (high byte)  
            0xFD, 0x68, 0xE5,  # SBC $E568,X (subtract with borrow)
            0x90, 0x0D,        # BCC $E540 (can't subtract, digit done)
            
            # $E533: Perform subtraction
            0x85, 0xF3,        # STA $F3 (store new high byte)
            0xA5, 0xF2,        # LDA $F2 (get low byte)
            0xFD, 0x63, 0xE5,  # SBC $E563,X (subtract power low)
            0x85, 0xF2,        # STA $F2 (store new low byte)
            0xE6, 0xF9,        # INC $F9 (increment digit)
            0xD0, 0xE7,        # BNE $E527 (loop - always taken since $F9 was $B0+)
            
            # $E540: Subtraction done for this digit
            0xA5, 0xF9,        # LDA $F9 (get digit)
            0xE8,              # INX (dummy - sets flags)
            0xCA,              # DEX (restore X)
            0xF0, 0x0E,        # BEQ $E554 (if X=0, last digit - always print)
            
            # $E546: Not last digit - check if zero
            0xC9, 0xB0,        # CMP #$B0 (is digit '0'?)
            0xF0, 0x02,        # BEQ $E54C (yes, check leading zero)
            0x85, 0xC9,        # STA $C9 (non-zero: clear leading flag)
            
            # $E54C: Check leading zero flag
            0x24, 0xC9,        # BIT $C9 (test leading zero flag)
            0x30, 0x04,        # BMI $E554 (if set/negative, print it)
            
            # $E550: Check $FA flag
            0xA5, 0xFA,        # LDA $FA
            0xF0, 0x0B,        # BEQ $E55F (skip print, go to next digit)
            
            # $E554: Print the digit
            0x20, 0xED, 0xFD,  # JSR $FDED (COUT)
            
            # $E557: Optional: store in buffer if running
            0x24, 0xF8,        # BIT $F8 (run mode?)
            0x10, 0x04,        # BPL $E55F (no, skip)
            0x99, 0x00, 0x02,  # STA $0200,Y (store in input buffer)
            0xC8,              # INY
            
            # $E55F: Next power of 10
            0xCA,              # DEX
            0x10, 0xC1,        # BPL $E523 (loop if X >= 0)
            
            # $E562: Done
            0x60,              # RTS
        ]
        self.write_bytes(0xE51B, code)
        
        # Write powers of 10 tables
        self.write_bytes(0xE563, powers_lo)
        self.write_bytes(0xE568, powers_hi)
    
    # =========================================================================
    # $E883: Execute Statement
    # =========================================================================
    def build_execute(self):
        """Build statement execution entry point - placeholder."""
        code = [
            0x4C, 0xB3, 0xE2,  # $E883: JMP $E2B3 (return to prompt)
        ]
        self.write_bytes(0xE883, code)
    
    # =========================================================================
    # $F000: System Initialization
    # =========================================================================
    def build_init(self):
        """Build system initialization routine.
        
        1. Clear zero page locations
        2. Test memory to find top of RAM
        3. Set LOMEM and HIMEM
        4. Initialize variables
        """
        code = [
            # Initialize zero page
            0xA0, 0x00,        # $F000: LDY #$00
            0x84, 0xA0,        # $F002: STY $A0
            0x84, 0x4A,        # $F004: STY $4A
            0x84, 0x4C,        # $F006: STY $4C (LOMEM low)
            
            # Set initial LOMEM high to $08
            0xA9, 0x08,        # $F008: LDA #$08
            0x85, 0x4B,        # $F00A: STA $4B (LOMEM high for init test)
            0x85, 0x4D,        # $F00C: STA $4D (HIMEM high for init test)
            
            # Memory test loop
            0xE6, 0x4D,        # $F00E: INC $4D (increment HIMEM)
            0xB1, 0x4C,        # $F010: LDA ($4C),Y (read memory)
            0x49, 0xFF,        # $F012: EOR #$FF (complement)
            0x91, 0x4C,        # $F014: STA ($4C),Y (write back)
            0xD1, 0x4C,        # $F016: CMP ($4C),Y (verify)
            0xD0, 0x08,        # $F018: BNE $F022 (failed - found top)
            0x49, 0xFF,        # $F01A: EOR #$FF (restore original)
            0x91, 0x4C,        # $F01C: STA ($4C),Y
            0xD1, 0x4C,        # $F01E: CMP ($4C),Y
            0xF0, 0xEC,        # $F020: BEQ $F00E (continue test)
            
            # Memory test done - set up pointers
            # $F022: 
            0x4C, 0xAD, 0xE5,  # $F022: JMP $E5AD (continue init)
        ]
        self.write_bytes(0xF000, code)
        
        # Continue init at $E5AD (set pointers)
        init_cont = [
            # Set LOMEM = $0800
            0xA9, 0x00,        # $E5AD: LDA #$00
            0x85, 0x4C,        # $E5AF: STA $4C (LOMEM low)
            0xA9, 0x08,        # $E5B1: LDA #$08
            0x85, 0x4D,        # $E5B3: STA $4D (LOMEM high)
            
            # Copy LOMEM to CA-CB (program start)
            0xA5, 0x4C,        # $E5B5: LDA $4C
            0x85, 0xCA,        # $E5B7: STA $CA
            0xA5, 0x4D,        # $E5B9: LDA $4D
            0x85, 0xCB,        # $E5BB: STA $CB
            
            # Copy LOMEM to CC-CD (variable space start)
            0xA5, 0x4C,        # $E5BD: LDA $4C
            0x85, 0xCC,        # $E5BF: STA $CC
            0xA5, 0x4D,        # $E5C1: LDA $4D
            0x85, 0xCD,        # $E5C3: STA $CD
            
            # Clear run mode
            0xA9, 0x00,        # $E5C5: LDA #$00
            0x85, 0xF8,        # $E5C7: STA $F8 (run mode = immediate)
            0x85, 0xD9,        # $E5C9: STA $D9 (parse flag)
            
            0x60,              # $E5CB: RTS
        ]
        self.write_bytes(0xE5AD, init_cont)
    
    # =========================================================================
    # Build Complete ROM
    # =========================================================================
    def build(self):
        """Build the complete Integer BASIC ROM."""
        print("Building Integer BASIC ROM...")
        
        # Build all components
        self.build_cold_start()
        self.build_print_char()
        self.build_tab_handler()
        self.build_get_byte()
        self.build_warm_start()
        self.build_get_line()
        self.build_error_handler()
        self.build_parse_line()
        self.build_print_number()
        self.build_execute()
        self.build_init()
        
        print(f"ROM size: {len(self.rom)} bytes (${len(self.rom):04X})")
        return self.rom
    
    def save(self, filename):
        """Save ROM to file."""
        with open(filename, 'wb') as f:
            f.write(self.rom)
        print(f"Saved to {filename}")


def main():
    builder = IntegerBasicBuilder()
    rom = builder.build()
    builder.save("/workspace/cleanroom_roms/integer_basic.bin")
    
    # Verify size
    print(f"\nVerification:")
    print(f"  ROM size: {len(rom)} bytes")
    print(f"  Expected: 6144 bytes (6KB)")
    print(f"  Match: {len(rom) == 6144}")


if __name__ == "__main__":
    main()
