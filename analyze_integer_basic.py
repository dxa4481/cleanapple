#!/usr/bin/env python3
"""
Analyze and disassemble Apple II Integer BASIC ROM.

Integer BASIC spans $E000-$F7FF (6KB) plus Monitor at $F800-$FFFF.
This tool analyzes the structure and documents entry points.
"""

import os
from py65.devices.mpu6502 import MPU as MPU6502
from py65.disassembler import Disassembler


def load_integer_basic():
    """Load all Integer BASIC ROMs into a single memory image."""
    memory = bytearray(65536)
    
    roms = [
        ("/workspace/original_source/APPLE II/APPLE II - 341-0001 - INTEGER BASIC E000 - 2716.bin", 0xE000),
        ("/workspace/original_source/APPLE II/APPLE II - 341-0002 - INTEGER BASIC E800 - 2716.bin", 0xE800),
        ("/workspace/original_source/APPLE II/APPLE II - 341-0003 - INTEGER BASIC F000 - 2716.bin", 0xF000),
        ("/workspace/original_source/APPLE II/APPLE II - 341-0004 - INTEGER BASIC MONITOR F800 - 2716.bin", 0xF800),
    ]
    
    for path, addr in roms:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = f.read()
            for i, b in enumerate(data):
                memory[addr + i] = b
            print(f"Loaded {os.path.basename(path)} at ${addr:04X}")
    
    return memory


def disassemble_range(memory, start, end):
    """Disassemble a range of memory."""
    mpu = MPU6502()
    dis = Disassembler(mpu)
    
    for i in range(65536):
        mpu.memory[i] = memory[i]
    
    output = []
    addr = start
    while addr <= end:
        try:
            length, disasm = dis.instruction_at(addr)
            output.append((addr, disasm, memory[addr:addr+length]))
            addr += length
        except:
            output.append((addr, f".byte ${memory[addr]:02X}", [memory[addr]]))
            addr += 1
    
    return output


def find_jsr_targets(memory, start, end):
    """Find all JSR targets in a range."""
    targets = set()
    addr = start
    while addr < end - 2:
        if memory[addr] == 0x20:  # JSR
            target = memory[addr + 1] | (memory[addr + 2] << 8)
            targets.add(target)
        addr += 1
    return sorted(targets)


def find_jmp_targets(memory, start, end):
    """Find all JMP targets in a range."""
    targets = set()
    addr = start
    while addr < end - 2:
        if memory[addr] == 0x4C:  # JMP absolute
            target = memory[addr + 1] | (memory[addr + 2] << 8)
            targets.add(target)
        addr += 1
    return sorted(targets)


def find_strings(memory, start, end):
    """Find potential string data (sequences of printable chars with high bit)."""
    strings = []
    i = start
    while i < end:
        # Look for sequences of bytes with high bit set (Apple II text)
        if memory[i] >= 0x80:
            s = ""
            j = i
            while j < end and memory[j] >= 0x80 and memory[j] < 0xFF:
                char = memory[j] & 0x7F
                if 0x20 <= char <= 0x7E:
                    s += chr(char)
                    j += 1
                else:
                    break
            if len(s) >= 3:
                strings.append((i, s))
                i = j
                continue
        i += 1
    return strings


def analyze_known_entry_points(memory):
    """Document known Integer BASIC entry points."""
    
    # Known entry points from Apple II documentation
    entry_points = {
        # Cold start and warm start
        0xE000: "Cold start - initialize and enter BASIC",
        
        # Error handling
        0xE2B3: "Print error message",
        0xE3E0: "Error handler",
        
        # Tokenizer  
        0xE5A0: "Tokenize line",
        
        # Parser/Evaluator
        0xE6A4: "Evaluate expression",
        0xE700: "Get next token",
        
        # Statement execution
        0xE800: "Execute statement",
        
        # Commands
        0xEF00: "RUN command",
        0xEF29: "LIST command",
        0xEF7D: "NEW command",
        
        # Variables
        0xE912: "Find/create variable",
        
        # I/O
        0xED00: "PRINT statement",
        0xED70: "INPUT statement",
        
        # Math
        0xF100: "Multiply",
        0xF12E: "Divide",
        
        # Utilities
        0xF4A5: "Print number",
    }
    
    return entry_points


def analyze_token_table(memory):
    """Look for the token table in Integer BASIC."""
    # Integer BASIC tokens are stored as text with high bit set on last char
    # The token table should be a sequence of keywords
    
    keywords = [
        "FOR", "NEXT", "INPUT", "OUTPUT", "DIM", "READ", "GR", "TEXT",
        "PR#", "IN#", "CALL", "PLOT", "HLIN", "VLIN", "HGR", "HGR2",
        "HPLOT", "DRAW", "XDRAW", "HTAB", "HOME", "ROT=", "SCALE=",
        "SHLOAD", "TRACE", "NOTRACE", "NORMAL", "INVERSE", "FLASH",
        "COLOR=", "POP", "VTAB", "HIMEM:", "LOMEM:", "ONERR", "RESUME",
        "RECALL", "STORE", "SPEED=", "LET", "GOTO", "RUN", "IF", "THEN",
        "RESTORE", "GOSUB", "RETURN", "REM", "STOP", "ON", "WAIT",
        "LOAD", "SAVE", "DEF", "POKE", "PRINT", "CONT", "LIST", "CLEAR",
        "GET", "NEW", "TAB(", "TO", "FN", "SPC(", "THEN", "AT", "NOT",
        "STEP", "AND", "OR", "SGN", "INT", "ABS", "USR", "FRE", "SCRN(",
        "PDL", "POS", "SQR", "RND", "LOG", "EXP", "COS", "SIN", "TAN",
        "ATN", "PEEK", "LEN", "STR$", "VAL", "ASC", "CHR$", "LEFT$",
        "RIGHT$", "MID$"
    ]
    
    # Search for keyword patterns in ROM
    found_tokens = []
    for addr in range(0xE000, 0xF800):
        # Look for "FOR" pattern (C6 CF D2 with last char having high bit)
        if memory[addr:addr+3] == bytes([ord('F')|0x80, ord('O'), ord('R')|0x80]):
            found_tokens.append((addr, "Possible token table"))
            break
    
    return found_tokens


def main():
    """Main analysis routine."""
    print("=" * 70)
    print("INTEGER BASIC ROM ANALYSIS")
    print("=" * 70)
    
    memory = load_integer_basic()
    
    # Analyze structure
    print("\n" + "-" * 70)
    print("ROM STRUCTURE")
    print("-" * 70)
    print(f"$E000-$E7FF: Integer BASIC Part 1 (2048 bytes)")
    print(f"$E800-$EFFF: Integer BASIC Part 2 (2048 bytes)")
    print(f"$F000-$F7FF: Integer BASIC Part 3 (2048 bytes)")
    print(f"$F800-$FFFF: Monitor ROM (2048 bytes)")
    print(f"Total Integer BASIC: 6144 bytes (6KB)")
    
    # Entry point from cold start
    print("\n" + "-" * 70)
    print("COLD START ANALYSIS ($E000)")
    print("-" * 70)
    
    disasm = disassemble_range(memory, 0xE000, 0xE030)
    for addr, instr, data in disasm:
        hex_bytes = ' '.join(f'{b:02X}' for b in data)
        print(f"${addr:04X}: {hex_bytes:12s} {instr}")
    
    # Find JSR targets
    print("\n" + "-" * 70)
    print("SUBROUTINE TARGETS (JSR destinations)")
    print("-" * 70)
    
    jsr_targets = find_jsr_targets(memory, 0xE000, 0xF800)
    print(f"Found {len(jsr_targets)} unique JSR targets:")
    for target in jsr_targets[:40]:  # First 40
        print(f"  ${target:04X}")
    if len(jsr_targets) > 40:
        print(f"  ... and {len(jsr_targets) - 40} more")
    
    # Find strings
    print("\n" + "-" * 70)
    print("STRING DATA (Keywords, Error Messages)")
    print("-" * 70)
    
    strings = find_strings(memory, 0xE000, 0xF800)
    for addr, s in strings[:30]:
        print(f"  ${addr:04X}: \"{s}\"")
    
    # Disassemble key sections
    print("\n" + "-" * 70)
    print("KEY ROUTINE: $E000 (Cold Start)")
    print("-" * 70)
    
    disasm = disassemble_range(memory, 0xE000, 0xE080)
    for addr, instr, data in disasm:
        hex_bytes = ' '.join(f'{b:02X}' for b in data)
        print(f"${addr:04X}: {hex_bytes:12s} {instr}")
    
    # More key areas
    print("\n" + "-" * 70)
    print("KEY ROUTINE: $E2B0 (Error Handler Area)")
    print("-" * 70)
    
    disasm = disassemble_range(memory, 0xE2B0, 0xE320)
    for addr, instr, data in disasm:
        hex_bytes = ' '.join(f'{b:02X}' for b in data)
        print(f"${addr:04X}: {hex_bytes:12s} {instr}")
    
    # Print section
    print("\n" + "-" * 70)
    print("KEY ROUTINE: $ED00 Area (Likely PRINT/OUTPUT)")
    print("-" * 70)
    
    disasm = disassemble_range(memory, 0xED00, 0xED80)
    for addr, instr, data in disasm:
        hex_bytes = ' '.join(f'{b:02X}' for b in data)
        print(f"${addr:04X}: {hex_bytes:12s} {instr}")


if __name__ == "__main__":
    main()
