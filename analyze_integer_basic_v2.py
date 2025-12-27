#!/usr/bin/env python3
"""
Detailed analysis of Apple II Integer BASIC ROM.

This tool maps out the complete structure of Integer BASIC.
"""

import os
from py65.devices.mpu6502 import MPU as MPU6502
from py65.disassembler import Disassembler


def load_roms():
    """Load all Integer BASIC ROMs."""
    memory = bytearray(65536)
    
    roms = [
        ("/workspace/original_source/APPLE II/APPLE II - 341-0001 - INTEGER BASIC E000 - 2716.bin", 0xE000),
        ("/workspace/original_source/APPLE II/APPLE II - 341-0002 - INTEGER BASIC E800 - 2716.bin", 0xE800),
        ("/workspace/original_source/APPLE II/APPLE II - 341-0003 - INTEGER BASIC F000 - 2716.bin", 0xF000),
        ("/workspace/original_source/APPLE II/APPLE II - 341-0004 - INTEGER BASIC MONITOR F800 - 2716.bin", 0xF800),
    ]
    
    for path, addr in roms:
        with open(path, 'rb') as f:
            data = f.read()
        for i, b in enumerate(data):
            memory[addr + i] = b
    
    return memory


def disasm_at(memory, addr, count=20):
    """Disassemble at address."""
    mpu = MPU6502()
    dis = Disassembler(mpu)
    
    for i in range(65536):
        mpu.memory[i] = memory[i]
    
    lines = []
    for _ in range(count):
        try:
            length, instr = dis.instruction_at(addr)
            hex_bytes = ' '.join(f'{memory[addr+i]:02X}' for i in range(length))
            lines.append(f"${addr:04X}: {hex_bytes:12s} {instr}")
            addr += length
        except:
            lines.append(f"${addr:04X}: {memory[addr]:02X}           .byte ${memory[addr]:02X}")
            addr += 1
    
    return '\n'.join(lines)


# Known Integer BASIC Zero Page locations
ZERO_PAGE = {
    0x4C: "LOMEM - Start of BASIC program",
    0x4D: "LOMEM+1",
    0x4E: "HIMEM - End of available memory",
    0x4F: "HIMEM+1",
    0x50: "Variable pointer low",
    0x51: "Variable pointer high",
    0x52: "Array pointer low",
    0x53: "Array pointer high",
    0xCA: "Program start pointer low",
    0xCB: "Program start pointer high",
    0xCC: "Variable space start low",
    0xCD: "Variable space start high",
    0xCE: "Current line low",
    0xCF: "Current line high",
    0xD0: "TXTPTR - Text pointer low",
    0xD1: "TXTPTR+1",
    0xD5: "Run flag",
    0xD6: "Token being processed",
    0xD7: "FOR/NEXT flag",
    0xD8: "Temp storage",
    0xD9: "Parse flag",
    0xDA: "Temp pointer low",
    0xDB: "Temp pointer high",
    0xDC: "Current line number low",
    0xDD: "Current line number high",
    0xE0: "Work pointer low",
    0xE1: "Work pointer high",
    0xE2: "Pointer 2 low",
    0xE3: "Pointer 2 high",
    0xE4: "Pointer 3 low",
    0xE5: "Pointer 3 high",
    0xE6: "Pointer 4 low",
    0xE7: "Pointer 4 high",
    0xF1: "Input line index",
    0xF6: "Saved line number low",
    0xF7: "Saved line number high",
    0xF8: "RUN/immediate flag",
    0xFA: "Temp",
    0xFB: "Subroutine nesting level",
    0xFC: "FOR nesting level",
}


# Known Integer BASIC tokens (values 0x00-0x7F are tokens)
TOKENS = {
    # The actual token values need to be determined from the ROM
    # These are approximate based on Apple II documentation
}


def find_error_messages(memory):
    """Find error messages in the ROM."""
    # Error messages typically have format: text ending with high-bit-set character
    errors = []
    
    # Known error message locations (typical)
    # Integer BASIC error messages are usually in a table
    
    # Search for ">nnnn" patterns which could be error numbers
    for addr in range(0xE000, 0xF800):
        # Look for sequences that look like error text
        if memory[addr] == ord('>') | 0x80:  # '>' with high bit
            # Might be start of error prompt
            errors.append((addr, "Possible error message"))
    
    return errors


def analyze_token_dispatch(memory):
    """Find the token dispatch table."""
    # Integer BASIC typically has a jump table for token execution
    # Look for sequences of JMP or JSR instructions
    
    tables = []
    for addr in range(0xE000, 0xF000):
        # Look for pairs of bytes that look like addresses in ROM range
        low = memory[addr]
        high = memory[addr + 1]
        target = (high << 8) | low
        
        if 0xE000 <= target <= 0xF800:
            # Count how many consecutive address-like pairs
            count = 0
            a = addr
            while a < addr + 100:
                l = memory[a]
                h = memory[a + 1]
                t = (h << 8) | l
                if 0xE000 <= t <= 0xF800:
                    count += 1
                    a += 2
                else:
                    break
            
            if count >= 10:  # Found at least 10 consecutive addresses
                tables.append((addr, count))
    
    return tables


def main():
    memory = load_roms()
    
    print("=" * 70)
    print("INTEGER BASIC DETAILED ANALYSIS")
    print("=" * 70)
    
    # =======================================================================
    # ENTRY POINT $E000
    # =======================================================================
    print("\n" + "=" * 70)
    print("COLD START ($E000)")
    print("=" * 70)
    print("""
The entry point at $E000 is the cold start for Integer BASIC.
It initializes memory and enters the BASIC prompt.
""")
    print(disasm_at(memory, 0xE000, 15))
    
    # =======================================================================
    # INIT ROUTINE AT $F000
    # =======================================================================
    print("\n" + "=" * 70)
    print("INIT ROUTINE ($F000)")
    print("=" * 70)
    print("""
The cold start calls $F000 to initialize the system.
""")
    print(disasm_at(memory, 0xF000, 30))
    
    # =======================================================================
    # MAIN PROMPT LOOP $E2B3
    # =======================================================================
    print("\n" + "=" * 70)
    print("MAIN PROMPT LOOP ($E2B3)")
    print("=" * 70)
    print("""
After initialization, control goes to $E2B3 which is the main
BASIC prompt loop. It:
1. Prints the ">" prompt
2. Gets user input
3. Parses and executes the line
""")
    print(disasm_at(memory, 0xE2B3, 40))
    
    # =======================================================================
    # INPUT ROUTINE
    # =======================================================================
    print("\n" + "=" * 70)
    print("INPUT/TOKENIZE ROUTINE")
    print("=" * 70)
    print(disasm_at(memory, 0xE3CE, 30))
    
    # =======================================================================
    # PARSE EXPRESSION
    # =======================================================================
    print("\n" + "=" * 70)
    print("EXPRESSION EVALUATOR AREA ($E500)")
    print("=" * 70)
    print(disasm_at(memory, 0xE500, 30))
    
    # =======================================================================
    # PRINT ROUTINE
    # =======================================================================
    print("\n" + "=" * 70)
    print("PRINT NUMBER ($E51B)")
    print("=" * 70)
    print("""
$E51B appears to be the print number routine.
""")
    print(disasm_at(memory, 0xE51B, 25))
    
    # =======================================================================
    # TOKEN TABLE AREA
    # =======================================================================
    print("\n" + "=" * 70)
    print("COMMAND EXECUTION AREA ($E800)")
    print("=" * 70)
    print(disasm_at(memory, 0xE800, 30))
    
    # =======================================================================
    # GOSUB/RETURN
    # =======================================================================
    print("\n" + "=" * 70)
    print("GOSUB/RETURN AREA ($E880)")
    print("=" * 70)
    print(disasm_at(memory, 0xE880, 30))
    
    # =======================================================================
    # MULTIPLICATION
    # =======================================================================
    print("\n" + "=" * 70)
    print("MULTIPLY/DIVIDE AREA ($F100)")
    print("=" * 70)
    print(disasm_at(memory, 0xF100, 30))
    
    # =======================================================================
    # KEY DATA TABLES
    # =======================================================================
    print("\n" + "=" * 70)
    print("DATA TABLES SEARCH")
    print("=" * 70)
    
    # Look for potential address tables
    tables = analyze_token_dispatch(memory)
    print(f"\nFound {len(tables)} potential address tables:")
    for addr, count in tables[:10]:
        print(f"  ${addr:04X}: {count} consecutive addresses")
        # Show first few addresses
        for i in range(min(5, count)):
            low = memory[addr + i*2]
            high = memory[addr + i*2 + 1]
            target = (high << 8) | low
            print(f"    [{i}] ${target:04X}")
    
    # =======================================================================
    # ZERO PAGE DOCUMENTATION
    # =======================================================================
    print("\n" + "=" * 70)
    print("ZERO PAGE LOCATIONS")
    print("=" * 70)
    for addr, desc in sorted(ZERO_PAGE.items()):
        print(f"  ${addr:02X}: {desc}")
    
    # =======================================================================
    # KEY ROUTINES SUMMARY
    # =======================================================================
    print("\n" + "=" * 70)
    print("KEY ROUTINES SUMMARY")
    print("=" * 70)
    
    routines = [
        (0xE000, "Cold start entry"),
        (0xE003, "Jump to prompt (after init)"),
        (0xE006, "Set prompt character and print"),
        (0xE00C, "TAB handling"),
        (0xE018, "Tab/space output"),
        (0xE02A, "Get next character from program"),
        (0xE035, "LIST routine"),
        (0xE04B, "LIST all"),
        (0xE05D, "LIST partial"),
        (0xE06D, "Process line"),
        (0xE2B3, "Main prompt / warm start"),
        (0xE2D4, "Get input line"),
        (0xE3CE, "Parse input / tokenize"),
        (0xE38A, "Evaluate token"),
        (0xE491, "Execute statement"),
        (0xE51B, "Print 16-bit number"),
        (0xE56D, "Find variable"),
        (0xE576, "Find end of variable"),
        (0xE5A0, "Expression parser"),
        (0xE6A4, "Evaluate factor"),
        (0xE715, "Get token"),
        (0xE800, "Statement dispatch"),
        (0xE883, "RUN"),
        (0xE8C0, "GOSUB"),
        (0xE8DB, "RETURN"),
        (0xE912, "Variable lookup"),
        (0xEF00, "RUN entry"),
        (0xEFD3, "Clear variables"),
        (0xF000, "Initialize BASIC"),
        (0xF044, "Memory test"),
        (0xF100, "Multiply"),
        (0xF12E, "Divide"),
        (0xF1E0, "LET statement"),
        (0xF200, "IF statement"),
    ]
    
    for addr, desc in routines:
        print(f"  ${addr:04X}: {desc}")


if __name__ == "__main__":
    main()
