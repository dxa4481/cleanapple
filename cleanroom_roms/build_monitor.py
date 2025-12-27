#!/usr/bin/env python3
"""
Generate cleanroom Apple II Monitor ROM binary.

This generates a 2KB binary file that implements the Apple II Monitor ROM
functions at their documented entry points.
"""

import struct

def make_rom():
    """Create the monitor ROM binary."""
    # Create 2KB buffer filled with $FF
    rom = bytearray([0xFF] * 2048)
    
    # Helper to write bytes at specific offset (relative to $F800)
    def write_at(addr, data):
        offset = addr - 0xF800
        if isinstance(data, list):
            for i, b in enumerate(data):
                rom[offset + i] = b
        else:
            rom[offset] = data
    
    # Helper to write a 16-bit word (little endian)
    def write_word(addr, value):
        offset = addr - 0xF800
        rom[offset] = value & 0xFF
        rom[offset + 1] = (value >> 8) & 0xFF
    
    # =========================================================================
    # $FA86: IRQ/BRK Handler
    # =========================================================================
    write_at(0xFA86, [
        0x40,               # RTI
    ])
    
    # =========================================================================
    # $FB1E: PREAD - Read paddle (stub)
    # =========================================================================
    write_at(0xFB1E, [
        0xA9, 0x00,         # LDA #$00
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FB2F: INIT - Initialize display
    # =========================================================================
    write_at(0xFB2F, [
        0xAD, 0x51, 0xC0,   # LDA $C051 (TXTSET)
        0xAD, 0x52, 0xC0,   # LDA $C052 (MIXCLR)
        0xAD, 0x54, 0xC0,   # LDA $C054 (LOWSCR)
        0xAD, 0x56, 0xC0,   # LDA $C056 (LORES)
        0xA9, 0x00,         # LDA #$00
        0x85, 0x20,         # STA $20 (WNDLFT)
        0x85, 0x22,         # STA $22 (WNDTOP)
        0xA9, 0x28,         # LDA #$28 (40)
        0x85, 0x21,         # STA $21 (WNDWDTH)
        0xA9, 0x18,         # LDA #$18 (24)
        0x85, 0x23,         # STA $23 (WNDBTM)
        0xA9, 0xFF,         # LDA #$FF
        0x85, 0x32,         # STA $32 (INVFLG)
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FBC1: BASCALC - Calculate screen base address
    # Entry: A = line number (0-23)
    # Exit: BASL/BASH = screen base address
    # =========================================================================
    write_at(0xFBC1, [
        0x48,               # PHA - save line number
        0x4A,               # LSR A - divide by 2
        0x29, 0x03,         # AND #$03 - get bits 0-1
        0x09, 0x04,         # ORA #$04 - add $04 base
        0x85, 0x29,         # STA $29 (BASH)
        0x68,               # PLA - restore line number
        0x29, 0x18,         # AND #$18 - get bits 3-4
        0x90, 0x02,         # BCC +2 (always branches, C clear from AND)
        0x69, 0x7F,         # ADC #$7F (never executed)
        0x85, 0x28,         # STA $28 (BASL) - partial
        0x0A,               # ASL A - x2
        0x0A,               # ASL A - x4
        0x05, 0x28,         # ORA $28 - combine
        0x85, 0x28,         # STA $28 (BASL) - final
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FBDD: BELL - Ring bell
    # =========================================================================
    write_at(0xFBDD, [
        0xA9, 0x40,         # LDA #$40
        0x20, 0xA8, 0xFC,   # JSR $FCA8 (WAIT)
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FBE4: BELL1
    # =========================================================================
    write_at(0xFBE4, [
        0x4C, 0xDD, 0xFB,   # JMP $FBDD (BELL)
    ])
    
    # =========================================================================
    # $FBFD: STOADV - Store character and advance
    # =========================================================================
    write_at(0xFBFD, [
        0xA4, 0x24,         # LDY $24 (CH)
        0x91, 0x28,         # STA ($28),Y - store to screen
        0xE6, 0x24,         # INC $24 (CH)
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FC22: VTAB - Set vertical position
    # =========================================================================
    write_at(0xFC22, [
        0xA5, 0x25,         # LDA $25 (CV)
        0x4C, 0xC1, 0xFB,   # JMP $FBC1 (BASCALC)
    ])
    
    # =========================================================================
    # $FC42: CLREOP - Clear to end of page
    # =========================================================================
    write_at(0xFC42, [
        0xA9, 0xA0,         # LDA #$A0 (space)
        # clr_loop:
        0xA4, 0x24,         # LDY $24 (CH)
        # line_loop:
        0x91, 0x28,         # STA ($28),Y
        0xC8,               # INY
        0xC4, 0x21,         # CPY $21 (WNDWDTH)
        0x90, 0xF9,         # BCC line_loop
        0xA0, 0x00,         # LDY #$00
        0x84, 0x24,         # STY $24 (CH)
        0xE6, 0x25,         # INC $25 (CV)
        0xA5, 0x25,         # LDA $25 (CV)
        0xC5, 0x23,         # CMP $23 (WNDBTM)
        0xB0, 0x07,         # BCS done
        0x20, 0xC1, 0xFB,   # JSR $FBC1 (BASCALC)
        0xA9, 0xA0,         # LDA #$A0
        0xD0, 0xE4,         # BNE clr_loop
        # done:
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FC58: HOME - Clear screen and home cursor
    # =========================================================================
    write_at(0xFC58, [
        0xA9, 0x00,         # LDA #$00
        0x85, 0x24,         # STA $24 (CH)
        0x85, 0x25,         # STA $25 (CV)
        0x20, 0xC1, 0xFB,   # JSR $FBC1 (BASCALC)
        0x4C, 0x42, 0xFC,   # JMP $FC42 (CLREOP)
    ])
    
    # =========================================================================
    # $FC70: SCROLL - Scroll screen (simplified - just clears bottom line)
    # =========================================================================
    write_at(0xFC70, [
        0xA5, 0x23,         # LDA $23 (WNDBTM)
        0x38,               # SEC
        0xE9, 0x01,         # SBC #$01
        0x85, 0x25,         # STA $25 (CV)
        0x20, 0xC1, 0xFB,   # JSR $FBC1 (BASCALC)
        0xA9, 0xA0,         # LDA #$A0
        0xA0, 0x00,         # LDY #$00
        # clr_loop:
        0x91, 0x28,         # STA ($28),Y
        0xC8,               # INY
        0xC4, 0x21,         # CPY $21 (WNDWDTH)
        0x90, 0xF9,         # BCC clr_loop
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FC9C: CLREOL - Clear to end of line
    # =========================================================================
    write_at(0xFC9C, [
        0xA9, 0xA0,         # LDA #$A0
        # CLREOL1:
        0xA4, 0x24,         # LDY $24 (CH)
        # loop:
        0x91, 0x28,         # STA ($28),Y
        0xC8,               # INY
        0xC4, 0x21,         # CPY $21 (WNDWDTH)
        0x90, 0xF9,         # BCC loop
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FCA8: WAIT - Delay routine
    # Entry: A = delay count
    # Timing: approximately A^2 * 5 cycles
    # =========================================================================
    write_at(0xFCA8, [
        0x38,               # SEC
        # WAIT2:
        0x48,               # PHA (3 cycles)
        # WAIT3:
        0xE9, 0x01,         # SBC #$01 (2 cycles)
        0xD0, 0xFC,         # BNE WAIT3 (3/2 cycles)
        0x68,               # PLA (4 cycles)
        0xE9, 0x01,         # SBC #$01 (2 cycles)
        0xD0, 0xF6,         # BNE WAIT2 (3/2 cycles)
        0x60,               # RTS (6 cycles)
    ])
    
    # =========================================================================
    # $FCB4: A1PC - Increment A4 and compare A1 to A2
    # =========================================================================
    write_at(0xFCB4, [
        0xE6, 0x42,         # INC $42 (A4L)
        0xD0, 0x02,         # BNE skip
        0xE6, 0x43,         # INC $43 (A4H)
        # skip:
        0xA5, 0x3C,         # LDA $3C (A1L)
        0xC5, 0x3E,         # CMP $3E (A2L)
        0xA5, 0x3D,         # LDA $3D (A1H)
        0xE5, 0x3F,         # SBC $3F (A2H)
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FD0C: RDKEY - Read keyboard
    # =========================================================================
    write_at(0xFD0C, [
        # wait:
        0xAD, 0x00, 0xC0,   # LDA $C000 (KBD)
        0x10, 0xFB,         # BPL wait
        0x2C, 0x10, 0xC0,   # BIT $C010 (KBDSTRB)
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FD1B: KEYIN
    # =========================================================================
    write_at(0xFD1B, [
        0x4C, 0x0C, 0xFD,   # JMP $FD0C (RDKEY)
    ])
    
    # =========================================================================
    # $FD67: GETLN - Get line of input
    # =========================================================================
    write_at(0xFD67, [
        0xA2, 0x00,         # LDX #$00
        # GETLN1:
        0x20, 0x0C, 0xFD,   # JSR $FD0C (RDKEY)
        0xC9, 0x8D,         # CMP #$8D (CR)
        0xF0, 0x1B,         # BEQ done
        0xC9, 0x88,         # CMP #$88 (BS)
        0xF0, 0x11,         # BEQ bs
        0xC9, 0xFF,         # CMP #$FF (DEL)
        0xF0, 0x0D,         # BEQ bs
        0x9D, 0x00, 0x02,   # STA $0200,X (INPUT)
        0x20, 0xED, 0xFD,   # JSR $FDED (COUT)
        0xE8,               # INX
        0xE0, 0xF8,         # CPX #$F8
        0x90, 0xE6,         # BCC GETLN1
        0xB0, 0x0B,         # BCS done
        # bs:
        0xE0, 0x00,         # CPX #$00
        0xF0, 0xE0,         # BEQ GETLN1
        0xCA,               # DEX
        0x20, 0xED, 0xFD,   # JSR $FDED (COUT)
        0x4C, 0x69, 0xFD,   # JMP GETLN1
        # done:
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FD8B: CROUT1
    # =========================================================================
    write_at(0xFD8B, [
        0xA9, 0x8D,         # LDA #$8D (CR)
        0x4C, 0xED, 0xFD,   # JMP $FDED (COUT)
    ])
    
    # =========================================================================
    # $FD8E: CROUT - Print carriage return
    # =========================================================================
    write_at(0xFD8E, [
        0xA9, 0x00,         # LDA #$00
        0x85, 0x24,         # STA $24 (CH)
        0xE6, 0x25,         # INC $25 (CV)
        0xA5, 0x25,         # LDA $25 (CV)
        0xC5, 0x23,         # CMP $23 (WNDBTM)
        0x90, 0x05,         # BCC no_scroll
        0xC6, 0x25,         # DEC $25 (CV)
        0x20, 0x70, 0xFC,   # JSR $FC70 (SCROLL)
        # no_scroll:
        0x4C, 0xC1, 0xFB,   # JMP $FBC1 (BASCALC)
    ])
    
    # =========================================================================
    # $FDDA: PRBYTE - Print byte in hex
    # Entry: A = byte to print
    # =========================================================================
    write_at(0xFDDA, [
        0x48,               # PHA
        0x4A,               # LSR A
        0x4A,               # LSR A
        0x4A,               # LSR A
        0x4A,               # LSR A
        0x20, 0xE5, 0xFD,   # JSR $FDE5 (PRHEXZ)
        0x68,               # PLA
        # Fall through to PRHEX at $FDE3
    ])
    
    # =========================================================================
    # $FDE3: PRHEX - Print hex nibble
    # Entry: A = value (low 4 bits used)
    # =========================================================================
    write_at(0xFDE3, [
        0x29, 0x0F,         # AND #$0F
        # PRHEXZ at $FDE5:
        0x09, 0xB0,         # ORA #$B0
        0xC9, 0xBA,         # CMP #$BA
        0x90, 0x02,         # BCC COUT
        0x69, 0x06,         # ADC #$06
        # Fall through to COUT
    ])
    
    # =========================================================================
    # $FDED: COUT - Output character (through vector)
    # Entry: A = character with high bit set
    # =========================================================================
    write_at(0xFDED, [
        0x6C, 0x36, 0x00,   # JMP ($0036)
    ])
    
    # =========================================================================
    # $FDF0: COUT1 - Direct character output
    # Entry: A = character with high bit set
    # =========================================================================
    write_at(0xFDF0, [
        0xC9, 0xA0,         # CMP #$A0
        0x90, 0x0C,         # BCC control
        0x25, 0x32,         # AND $32 (INVFLG)
        # store:
        0x84, 0x35,         # STY $35 (YSAV1)
        0x48,               # PHA
        0x20, 0xFD, 0xFB,   # JSR $FBFD (STOADV)
        0x68,               # PLA
        0xA4, 0x35,         # LDY $35 (YSAV1)
        0x60,               # RTS
        # control:
        0xC9, 0x8D,         # CMP #$8D (CR)
        0xF0, 0x0F,         # BEQ cr
        0xC9, 0x8A,         # CMP #$8A (LF)
        0xF0, 0x0E,         # BEQ lf
        0xC9, 0x88,         # CMP #$88 (BS)
        0xF0, 0x0F,         # BEQ bs
        0xC9, 0x87,         # CMP #$87 (BELL)
        0xF0, 0x14,         # BEQ bell
        0x4C, 0xF6, 0xFD,   # JMP store
        # cr:
        0x4C, 0x8E, 0xFD,   # JMP $FD8E (CROUT)
        # lf:
        0xE6, 0x25,         # INC $25 (CV)
        0x4C, 0xC1, 0xFB,   # JMP $FBC1 (BASCALC)
        # bs:
        0xC6, 0x24,         # DEC $24 (CH)
        0x10, 0x04,         # BPL bs_done
        0xA9, 0x00,         # LDA #$00
        0x85, 0x24,         # STA $24 (CH)
        # bs_done:
        0x60,               # RTS
        # bell:
        0x4C, 0xDD, 0xFB,   # JMP $FBDD (BELL)
    ])
    
    # =========================================================================
    # $FE2C: MOVE - Move memory block
    # =========================================================================
    write_at(0xFE2C, [
        0xA0, 0x00,         # LDY #$00
        # loop:
        0xB1, 0x3C,         # LDA ($3C),Y (A1)
        0x91, 0x42,         # STA ($42),Y (A4)
        0x20, 0xB4, 0xFC,   # JSR $FCB4 (A1PC)
        0x90, 0xF7,         # BCC loop
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FE36: VERIFY - Verify memory block
    # =========================================================================
    write_at(0xFE36, [
        0xA0, 0x00,         # LDY #$00
        # loop:
        0xB1, 0x3C,         # LDA ($3C),Y (A1)
        0xD1, 0x42,         # CMP ($42),Y (A4)
        0xD0, 0x07,         # BNE mismatch
        0x20, 0xB4, 0xFC,   # JSR $FCB4 (A1PC)
        0x90, 0xF5,         # BCC loop
        0x18,               # CLC
        0x60,               # RTS
        # mismatch:
        0x38,               # SEC
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FE80: SETINV - Set inverse video mode
    # =========================================================================
    write_at(0xFE80, [
        0xA0, 0x3F,         # LDY #$3F
        0xD0, 0x02,         # BNE SETVID
    ])
    
    # =========================================================================
    # $FE84: SETNORM - Set normal video mode
    # =========================================================================
    write_at(0xFE84, [
        0xA0, 0xFF,         # LDY #$FF
        # SETVID:
        0x84, 0x32,         # STY $32 (INVFLG)
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FE89: SETFLSH - Set flash mode (stub)
    # =========================================================================
    write_at(0xFE89, [
        0xA9, 0x00,         # LDA #$00
        0x85, 0x3E,         # STA $3E (A2L)
        0xA2, 0x38,         # LDX #$38
        0xA0, 0x1B,         # LDY #$1B
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FE93: SETVID2 - Initialize COUT vector
    # =========================================================================
    write_at(0xFE93, [
        0xA9, 0xF0,         # LDA #$F0 (low byte of COUT1)
        0x85, 0x36,         # STA $36 (CSWL)
        0xA9, 0xFD,         # LDA #$FD (high byte of COUT1)
        0x85, 0x37,         # STA $37 (CSWH)
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FF3A: BELL2
    # =========================================================================
    write_at(0xFF3A, [
        0x4C, 0xDD, 0xFB,   # JMP $FBDD (BELL)
    ])
    
    # =========================================================================
    # $FF58: IORTS - Return slot*16 from stack
    # Used by peripheral cards to determine their slot number.
    # The return address on the stack contains $Cn, where n is the slot.
    # This routine extracts n*16 and returns it in A.
    #
    # DOCUMENTED in Apple II Reference Manual as a standard way for
    # peripheral cards to determine their slot number.
    # =========================================================================
    write_at(0xFF58, [
        0xBA,               # TSX - get stack pointer
        0xBD, 0x00, 0x01,   # LDA $0100,X - get return address low byte from stack
        0x0A,               # ASL A - shift $Cn -> $n0
        0x0A,               # ASL A
        0x0A,               # ASL A
        0x0A,               # ASL A - A now contains slot*16
        0x60,               # RTS
    ])
    
    # =========================================================================
    # $FF59: RESET - Main reset entry point
    # =========================================================================
    write_at(0xFF59, [
        0x20, 0x84, 0xFE,   # JSR $FE84 (SETNORM)
        0x20, 0x2F, 0xFB,   # JSR $FB2F (INIT)
        0x20, 0x93, 0xFE,   # JSR $FE93 (SETVID2)
    ])
    
    # =========================================================================
    # $FF65: MON - Monitor warm start
    # =========================================================================
    write_at(0xFF65, [
        0xD8,               # CLD
        0x20, 0x3A, 0xFF,   # JSR $FF3A (BELL2)
    ])
    
    # =========================================================================
    # $FF69: MONZ - Monitor entry
    # =========================================================================
    write_at(0xFF69, [
        0xA9, 0xAA,         # LDA #$AA ('*')
        0x85, 0x33,         # STA $33 (PROMPT)
        # loop:
        0x20, 0x0C, 0xFD,   # JSR $FD0C (RDKEY)
        0x20, 0xED, 0xFD,   # JSR $FDED (COUT)
        0x4C, 0x6D, 0xFF,   # JMP loop
    ])
    
    # =========================================================================
    # $FFF8-$FFFF: Vectors
    # =========================================================================
    write_word(0xFFF8, 0x03F5)  # Unused
    write_word(0xFFFA, 0x03FB)  # NMI
    write_word(0xFFFC, 0xFF59)  # RESET
    write_word(0xFFFE, 0xFA86)  # IRQ/BRK
    
    return rom


def main():
    """Generate the ROM and write to file."""
    rom = make_rom()
    
    output_path = "/workspace/cleanroom_roms/monitor_f800.bin"
    with open(output_path, "wb") as f:
        f.write(rom)
    
    print(f"Generated {output_path}")
    print(f"Size: {len(rom)} bytes")
    
    # Verify key entry points
    print("\nVerifying key entry points:")
    entry_points = [
        (0xFBC1, "BASCALC", 0x48),   # Should start with PHA
        (0xFCA8, "WAIT", 0x38),       # Should start with SEC
        (0xFDDA, "PRBYTE", 0x48),     # Should start with PHA
        (0xFDE3, "PRHEX", 0x29),      # Should start with AND
        (0xFDED, "COUT", 0x6C),       # Should start with JMP indirect
        (0xFE80, "SETINV", 0xA0),     # Should start with LDY
        (0xFE84, "SETNORM", 0xA0),    # Should start with LDY
    ]
    
    for addr, name, expected in entry_points:
        offset = addr - 0xF800
        actual = rom[offset]
        status = "✓" if actual == expected else "✗"
        print(f"  {status} ${addr:04X} {name}: ${actual:02X} (expected ${expected:02X})")


if __name__ == "__main__":
    main()
