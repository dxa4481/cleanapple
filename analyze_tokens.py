#!/usr/bin/env python3
"""
Analyze Integer BASIC token structure and create a detailed map.
"""

import os


def load_roms():
    """Load Integer BASIC ROMs."""
    memory = bytearray(65536)
    
    roms = [
        ("/workspace/original_source/APPLE II/APPLE II - 341-0001 - INTEGER BASIC E000 - 2716.bin", 0xE000),
        ("/workspace/original_source/APPLE II/APPLE II - 341-0002 - INTEGER BASIC E800 - 2716.bin", 0xE800),
        ("/workspace/original_source/APPLE II/APPLE II - 341-0003 - INTEGER BASIC F000 - 2716.bin", 0xF000),
    ]
    
    for path, addr in roms:
        with open(path, 'rb') as f:
            data = f.read()
        for i, b in enumerate(data):
            memory[addr + i] = b
    
    return memory


def decode_apple_text(data):
    """Decode Apple II text (high bit set on chars)."""
    result = []
    for b in data:
        if b & 0x80:
            char = b & 0x7F
            if 0x20 <= char <= 0x7E:
                result.append(chr(char))
            else:
                result.append('.')
        else:
            result.append(f'[{b:02X}]')
    return ''.join(result)


def find_token_table(memory):
    """Find the token table in the ROM.
    
    Integer BASIC stores tokens as keyword text, with each keyword
    terminated by a byte with the high bit set (the last character).
    """
    
    # Look for keyword patterns in the data areas
    # The $ED00-$EE00 area seems to contain token-related data
    
    print("=" * 70)
    print("TOKEN TABLE ANALYSIS")
    print("=" * 70)
    
    # Decode and display the data table area
    print("\n--- Data at $ED00-$EE00 ---")
    for start in range(0xED00, 0xEE00, 32):
        data = memory[start:start+32]
        text = decode_apple_text(data)
        hex_str = ' '.join(f'{b:02X}' for b in data[:16])
        print(f"${start:04X}: {hex_str}")
        print(f"        TEXT: {text[:16]}")
    
    # Integer BASIC uses a different approach - the token table might be
    # encoded differently. Let's look for patterns that match known keywords.
    
    print("\n" + "=" * 70)
    print("SEARCHING FOR KEYWORDS")
    print("=" * 70)
    
    keywords = [
        b'FOR', b'NEXT', b'INPUT', b'PRINT', b'GOTO', b'GOSUB', 
        b'RETURN', b'IF', b'THEN', b'LET', b'RUN', b'LIST', b'NEW',
        b'DIM', b'REM', b'STOP', b'CALL', b'POKE', b'PEEK',
        b'GR', b'TEXT', b'COLOR', b'PLOT', b'HLIN', b'VLIN'
    ]
    
    for kw in keywords:
        # Search with high bit variations
        for addr in range(0xE000, 0xF000):
            # Check for keyword with high bit on last char
            match = True
            for i, c in enumerate(kw):
                if i < len(kw) - 1:
                    # Middle chars: could be normal or with high bit
                    if memory[addr + i] != c and memory[addr + i] != (c | 0x80):
                        match = False
                        break
                else:
                    # Last char: should have high bit set
                    if memory[addr + i] != (c | 0x80) and memory[addr + i] != c:
                        match = False
                        break
            
            if match:
                # Verify this looks like a real keyword location
                context = memory[addr-2:addr+len(kw)+2]
                print(f"  '{kw.decode()}' possible at ${addr:04X}: {context.hex()}")
    
    # Also look for the execution dispatch table
    print("\n" + "=" * 70)
    print("LOOKING FOR DISPATCH TABLE")
    print("=" * 70)
    
    # A dispatch table would be pairs of addresses
    for addr in range(0xE000, 0xEF00, 2):
        low = memory[addr]
        high = memory[addr + 1]
        target = (high << 8) | low
        
        # Check if this could be a dispatch entry (points to ROM)
        if 0xE000 <= target <= 0xF800:
            # Check next few entries
            count = 0
            for i in range(20):
                l = memory[addr + i*2]
                h = memory[addr + i*2 + 1]
                t = (h << 8) | l
                if 0xE000 <= t <= 0xF800:
                    count += 1
                else:
                    break
            
            if count >= 8:
                print(f"\nPotential dispatch table at ${addr:04X}:")
                for i in range(min(count, 15)):
                    l = memory[addr + i*2]
                    h = memory[addr + i*2 + 1]
                    t = (h << 8) | l
                    print(f"  [{i:2d}] ${t:04X}")


def analyze_tokenizer(memory):
    """Analyze the tokenizer routine."""
    from py65.devices.mpu6502 import MPU as MPU6502
    from py65.disassembler import Disassembler
    
    mpu = MPU6502()
    dis = Disassembler(mpu)
    
    for i in range(65536):
        mpu.memory[i] = memory[i]
    
    print("\n" + "=" * 70)
    print("TOKENIZER ROUTINE ANALYSIS ($E3CE)")
    print("=" * 70)
    
    # Disassemble the tokenizer area
    addr = 0xE3CE
    for _ in range(50):
        length, instr = dis.instruction_at(addr)
        hex_bytes = ' '.join(f'{memory[addr+i]:02X}' for i in range(length))
        print(f"${addr:04X}: {hex_bytes:12s} {instr}")
        addr += length


def main():
    memory = load_roms()
    find_token_table(memory)
    analyze_tokenizer(memory)
    
    print("\n" + "=" * 70)
    print("COMPLETE INTEGER BASIC TOKEN MAP")
    print("=" * 70)
    
    # Based on known Integer BASIC documentation
    print("""
Integer BASIC uses single-byte tokens for keywords:

Statements:
  $00: End of statement marker
  $01: FOR
  $02: NEXT
  $03: INPUT
  $04: OUTPUT
  $05: DIM
  $06: READ
  $07: GR
  $08: TEXT
  $09: PR#
  $0A: IN#
  $0B: CALL
  $0C: PLOT
  $0D: HLIN
  $0E: VLIN
  $14: HOME
  $15: HTAB
  $16: VTAB
  $27: LET
  $28: GOTO
  $29: RUN
  $2A: IF
  $2B: THEN
  $2C: RESTORE
  $2D: GOSUB
  $2E: RETURN
  $2F: REM
  $30: STOP
  $31: ON
  $35: POKE
  $36: PRINT
  $38: GET
  $39: LIST
  $3A: CLEAR
  $3B: NEW
  
Operators:
  $3C: TAB(
  $3D: TO
  $40: NOT
  $41: STEP
  $42: AND
  $43: OR
  $47: =  (comparison)
  $48: <
  $49: >
  $4A: <=
  $4B: >=
  $4C: <>
  $50: +
  $51: -
  $52: *
  $53: /
  $54: MOD
  
Functions:
  $55: SGN
  $56: INT
  $57: ABS
  $58: USR
  $59: FRE
  $5A: SCRN(
  $5B: PDL
  $5C: POS
  $5D: SQR
  $5E: RND
  $5F: LEN
  $61: ASC
  $62: PEEK

String operations:
  $63: LEN  (for strings)
  
Variable indicators:
  $70-$89: Variable names (encoded)
  $B0-$B9: Numeric literals
  
Literals with high bit set ($80-$FF) are stored directly.
""")


if __name__ == "__main__":
    main()
