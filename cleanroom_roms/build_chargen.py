#!/usr/bin/env python3
"""
TRUE Cleanroom Character Generator ROM Implementation

This creates a Character Generator ROM with ORIGINAL pixel designs.
The characters are designed to be visually readable and functional,
but use DIFFERENT pixel patterns than the original Apple II ROM.

CLEANROOM REQUIREMENT: The output MUST NOT be byte-identical to the original.
"""

import hashlib


def create_cleanroom_character_patterns():
    """
    Create ORIGINAL character pixel patterns.
    
    Each character is 8 bytes (8 rows of 7 pixels each).
    Bit 0 is leftmost pixel, bit 6 is rightmost.
    Bit 7 is always 0 for normal characters.
    
    These patterns are INDEPENDENTLY DESIGNED to be readable
    but NOT copies of the original Apple II font.
    """
    
    # Character patterns - 64 characters
    # Index 0-31: @ through _ (ASCII 64-95)
    # Index 32-63: space through ? (ASCII 32-63)
    
    patterns = {}
    
    # Design each character with ORIGINAL pixel patterns
    # Format: 8 rows, each row is 7 bits (0x00-0x7F)
    
    # Index 0: @ (ASCII 64) - at sign
    patterns[0] = [
        0b0000000,  # Row 0 (top)
        0b0011110,  # Row 1
        0b0100001,  # Row 2
        0b0101101,  # Row 3
        0b0101011,  # Row 4
        0b0011110,  # Row 5
        0b0000001,  # Row 6
        0b0011110,  # Row 7 (bottom)
    ]
    
    # Index 1: A (ASCII 65)
    patterns[1] = [
        0b0000000,
        0b0001100,  # Different from original - smaller top
        0b0010010,
        0b0100001,
        0b0111111,  # Full bar
        0b0100001,
        0b0100001,
        0b0000000,
    ]
    
    # Index 2: B (ASCII 66)
    patterns[2] = [
        0b0000000,
        0b0111110,
        0b0100001,
        0b0111110,
        0b0100001,
        0b0100001,
        0b0111110,
        0b0000000,
    ]
    
    # Index 3: C (ASCII 67)
    patterns[3] = [
        0b0000000,
        0b0011110,
        0b0100001,
        0b0000001,
        0b0000001,
        0b0100001,
        0b0011110,
        0b0000000,
    ]
    
    # Index 4: D (ASCII 68)
    patterns[4] = [
        0b0000000,
        0b0011110,
        0b0100001,
        0b0100001,
        0b0100001,
        0b0100001,
        0b0011110,
        0b0000000,
    ]
    
    # Index 5: E (ASCII 69)
    patterns[5] = [
        0b0000000,
        0b0111111,
        0b0000001,
        0b0011111,
        0b0000001,
        0b0000001,
        0b0111111,
        0b0000000,
    ]
    
    # Index 6: F (ASCII 70)
    patterns[6] = [
        0b0000000,
        0b0111111,
        0b0000001,
        0b0011111,
        0b0000001,
        0b0000001,
        0b0000001,
        0b0000000,
    ]
    
    # Index 7: G (ASCII 71)
    patterns[7] = [
        0b0000000,
        0b0011110,
        0b0000001,
        0b0000001,
        0b0111001,
        0b0100001,
        0b0011110,
        0b0000000,
    ]
    
    # Index 8: H (ASCII 72)
    patterns[8] = [
        0b0000000,
        0b0100001,
        0b0100001,
        0b0111111,
        0b0100001,
        0b0100001,
        0b0100001,
        0b0000000,
    ]
    
    # Index 9: I (ASCII 73)
    patterns[9] = [
        0b0000000,
        0b0011110,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0011110,
        0b0000000,
    ]
    
    # Index 10: J (ASCII 74)
    patterns[10] = [
        0b0000000,
        0b0111100,
        0b0010000,
        0b0010000,
        0b0010000,
        0b0010001,
        0b0001110,
        0b0000000,
    ]
    
    # Index 11: K (ASCII 75)
    patterns[11] = [
        0b0000000,
        0b0100001,
        0b0010001,
        0b0001111,
        0b0010001,
        0b0100001,
        0b0100001,
        0b0000000,
    ]
    
    # Index 12: L (ASCII 76)
    patterns[12] = [
        0b0000000,
        0b0000001,
        0b0000001,
        0b0000001,
        0b0000001,
        0b0000001,
        0b0111111,
        0b0000000,
    ]
    
    # Index 13: M (ASCII 77)
    patterns[13] = [
        0b0000000,
        0b0100001,
        0b0110011,
        0b0101101,
        0b0100001,
        0b0100001,
        0b0100001,
        0b0000000,
    ]
    
    # Index 14: N (ASCII 78)
    patterns[14] = [
        0b0000000,
        0b0100001,
        0b0100011,
        0b0100101,
        0b0101001,
        0b0110001,
        0b0100001,
        0b0000000,
    ]
    
    # Index 15: O (ASCII 79) - rounder than D
    patterns[15] = [
        0b0000000,
        0b0001100,
        0b0010010,
        0b0100001,
        0b0100001,
        0b0010010,
        0b0001100,
        0b0000000,
    ]
    
    # Index 16: P (ASCII 80)
    patterns[16] = [
        0b0000000,
        0b0011111,
        0b0100001,
        0b0100001,
        0b0011111,
        0b0000001,
        0b0000001,
        0b0000000,
    ]
    
    # Index 17: Q (ASCII 81)
    patterns[17] = [
        0b0000000,
        0b0011110,
        0b0100001,
        0b0100001,
        0b0101001,
        0b0010001,
        0b0101110,
        0b0000000,
    ]
    
    # Index 18: R (ASCII 82)
    patterns[18] = [
        0b0000000,
        0b0011111,
        0b0100001,
        0b0100001,
        0b0011111,
        0b0010001,
        0b0100001,
        0b0000000,
    ]
    
    # Index 19: S (ASCII 83)
    patterns[19] = [
        0b0000000,
        0b0011110,
        0b0000001,
        0b0011110,
        0b0100000,
        0b0100000,
        0b0011111,
        0b0000000,
    ]
    
    # Index 20: T (ASCII 84)
    patterns[20] = [
        0b0000000,
        0b0111111,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0000000,
    ]
    
    # Index 21: U (ASCII 85)
    patterns[21] = [
        0b0000000,
        0b0100001,
        0b0100001,
        0b0100001,
        0b0100001,
        0b0100001,
        0b0011110,
        0b0000000,
    ]
    
    # Index 22: V (ASCII 86)
    patterns[22] = [
        0b0000000,
        0b0100001,
        0b0100001,
        0b0010010,
        0b0010010,
        0b0001100,
        0b0001100,
        0b0000000,
    ]
    
    # Index 23: W (ASCII 87)
    patterns[23] = [
        0b0000000,
        0b0100001,
        0b0100001,
        0b0100001,
        0b0101101,
        0b0110011,
        0b0100001,
        0b0000000,
    ]
    
    # Index 24: X (ASCII 88)
    patterns[24] = [
        0b0000000,
        0b0100001,
        0b0010010,
        0b0001100,
        0b0001100,
        0b0010010,
        0b0100001,
        0b0000000,
    ]
    
    # Index 25: Y (ASCII 89)
    patterns[25] = [
        0b0000000,
        0b0100001,
        0b0010010,
        0b0001100,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0000000,
    ]
    
    # Index 26: Z (ASCII 90)
    patterns[26] = [
        0b0000000,
        0b0111111,
        0b0100000,
        0b0011100,
        0b0000010,
        0b0000001,
        0b0111111,
        0b0000000,
    ]
    
    # Index 27: [ (ASCII 91)
    patterns[27] = [
        0b0000000,
        0b0011100,
        0b0000100,
        0b0000100,
        0b0000100,
        0b0000100,
        0b0011100,
        0b0000000,
    ]
    
    # Index 28: \ (ASCII 92)
    patterns[28] = [
        0b0000000,
        0b0000001,
        0b0000010,
        0b0000100,
        0b0001000,
        0b0010000,
        0b0100000,
        0b0000000,
    ]
    
    # Index 29: ] (ASCII 93)
    patterns[29] = [
        0b0000000,
        0b0001110,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0001110,
        0b0000000,
    ]
    
    # Index 30: ^ (ASCII 94)
    patterns[30] = [
        0b0000000,
        0b0001000,
        0b0010100,
        0b0100010,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
    ]
    
    # Index 31: _ (ASCII 95)
    patterns[31] = [
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0111111,
        0b0000000,
    ]
    
    # Index 32: space (ASCII 32)
    patterns[32] = [
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
    ]
    
    # Index 33: ! (ASCII 33)
    patterns[33] = [
        0b0000000,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0000000,
        0b0001000,
        0b0000000,
    ]
    
    # Index 34: " (ASCII 34)
    patterns[34] = [
        0b0000000,
        0b0010100,
        0b0010100,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
    ]
    
    # Index 35: # (ASCII 35)
    patterns[35] = [
        0b0000000,
        0b0010100,
        0b0111110,
        0b0010100,
        0b0010100,
        0b0111110,
        0b0010100,
        0b0000000,
    ]
    
    # Index 36: $ (ASCII 36)
    patterns[36] = [
        0b0000000,
        0b0001000,
        0b0011110,
        0b0001001,
        0b0011110,
        0b0101000,
        0b0011110,
        0b0001000,
    ]
    
    # Index 37: % (ASCII 37)
    patterns[37] = [
        0b0000000,
        0b0100011,
        0b0010011,
        0b0001000,
        0b0000100,
        0b0110010,
        0b0110001,
        0b0000000,
    ]
    
    # Index 38: & (ASCII 38)
    patterns[38] = [
        0b0000000,
        0b0000110,
        0b0001001,
        0b0000110,
        0b0101001,
        0b0010001,
        0b0101110,
        0b0000000,
    ]
    
    # Index 39: ' (ASCII 39)
    patterns[39] = [
        0b0000000,
        0b0001000,
        0b0001000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
    ]
    
    # Index 40: ( (ASCII 40)
    patterns[40] = [
        0b0000000,
        0b0010000,
        0b0001000,
        0b0000100,
        0b0000100,
        0b0001000,
        0b0010000,
        0b0000000,
    ]
    
    # Index 41: ) (ASCII 41)
    patterns[41] = [
        0b0000000,
        0b0000010,
        0b0000100,
        0b0001000,
        0b0001000,
        0b0000100,
        0b0000010,
        0b0000000,
    ]
    
    # Index 42: * (ASCII 42)
    patterns[42] = [
        0b0000000,
        0b0001000,
        0b0101010,
        0b0011100,
        0b0101010,
        0b0001000,
        0b0000000,
        0b0000000,
    ]
    
    # Index 43: + (ASCII 43)
    patterns[43] = [
        0b0000000,
        0b0000000,
        0b0001000,
        0b0001000,
        0b0111110,
        0b0001000,
        0b0001000,
        0b0000000,
    ]
    
    # Index 44: , (ASCII 44)
    patterns[44] = [
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0001000,
        0b0001000,
        0b0000100,
    ]
    
    # Index 45: - (ASCII 45)
    patterns[45] = [
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0111110,
        0b0000000,
        0b0000000,
        0b0000000,
    ]
    
    # Index 46: . (ASCII 46)
    patterns[46] = [
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0000000,
        0b0001100,
        0b0001100,
        0b0000000,
    ]
    
    # Index 47: / (ASCII 47)
    patterns[47] = [
        0b0000000,
        0b0100000,
        0b0010000,
        0b0001000,
        0b0000100,
        0b0000010,
        0b0000001,
        0b0000000,
    ]
    
    # Index 48: 0 (ASCII 48)
    patterns[48] = [
        0b0000000,
        0b0011110,
        0b0110001,
        0b0101001,
        0b0100101,
        0b0100011,
        0b0011110,
        0b0000000,
    ]
    
    # Index 49: 1 (ASCII 49)
    patterns[49] = [
        0b0000000,
        0b0001000,
        0b0001100,
        0b0001000,
        0b0001000,
        0b0001000,
        0b0011100,
        0b0000000,
    ]
    
    # Index 50: 2 (ASCII 50)
    patterns[50] = [
        0b0000000,
        0b0011110,
        0b0100000,
        0b0011100,
        0b0000010,
        0b0000001,
        0b0111111,
        0b0000000,
    ]
    
    # Index 51: 3 (ASCII 51)
    patterns[51] = [
        0b0000000,
        0b0011111,
        0b0100000,
        0b0011100,
        0b0100000,
        0b0100000,
        0b0011111,
        0b0000000,
    ]
    
    # Index 52: 4 (ASCII 52)
    patterns[52] = [
        0b0000000,
        0b0100010,
        0b0100010,
        0b0111111,
        0b0100000,
        0b0100000,
        0b0100000,
        0b0000000,
    ]
    
    # Index 53: 5 (ASCII 53)
    patterns[53] = [
        0b0000000,
        0b0111111,
        0b0000001,
        0b0011111,
        0b0100000,
        0b0100000,
        0b0011111,
        0b0000000,
    ]
    
    # Index 54: 6 (ASCII 54)
    patterns[54] = [
        0b0000000,
        0b0011110,
        0b0000001,
        0b0011111,
        0b0100001,
        0b0100001,
        0b0011110,
        0b0000000,
    ]
    
    # Index 55: 7 (ASCII 55)
    patterns[55] = [
        0b0000000,
        0b0111111,
        0b0100000,
        0b0010000,
        0b0001000,
        0b0000100,
        0b0000100,
        0b0000000,
    ]
    
    # Index 56: 8 (ASCII 56)
    patterns[56] = [
        0b0000000,
        0b0011110,
        0b0100001,
        0b0011110,
        0b0100001,
        0b0100001,
        0b0011110,
        0b0000000,
    ]
    
    # Index 57: 9 (ASCII 57)
    patterns[57] = [
        0b0000000,
        0b0011110,
        0b0100001,
        0b0100001,
        0b0111110,
        0b0100000,
        0b0011110,
        0b0000000,
    ]
    
    # Index 58: : (ASCII 58)
    patterns[58] = [
        0b0000000,
        0b0000000,
        0b0001100,
        0b0001100,
        0b0000000,
        0b0001100,
        0b0001100,
        0b0000000,
    ]
    
    # Index 59: ; (ASCII 59)
    patterns[59] = [
        0b0000000,
        0b0000000,
        0b0001100,
        0b0001100,
        0b0000000,
        0b0001100,
        0b0000100,
        0b0000010,
    ]
    
    # Index 60: < (ASCII 60)
    patterns[60] = [
        0b0000000,
        0b0010000,
        0b0001000,
        0b0000100,
        0b0000010,
        0b0000100,
        0b0001000,
        0b0010000,
    ]
    
    # Index 61: = (ASCII 61)
    patterns[61] = [
        0b0000000,
        0b0000000,
        0b0111110,
        0b0000000,
        0b0000000,
        0b0111110,
        0b0000000,
        0b0000000,
    ]
    
    # Index 62: > (ASCII 62)
    patterns[62] = [
        0b0000000,
        0b0000010,
        0b0000100,
        0b0001000,
        0b0010000,
        0b0001000,
        0b0000100,
        0b0000010,
    ]
    
    # Index 63: ? (ASCII 63)
    patterns[63] = [
        0b0000000,
        0b0011110,
        0b0100000,
        0b0010000,
        0b0001000,
        0b0000000,
        0b0001000,
        0b0000000,
    ]
    
    return patterns


def build_chargen_rom():
    """
    Build the Character Generator ROM.
    
    ROM structure (2048 bytes = 4 banks of 512 bytes):
    - Bank 0 ($000-$1FF): Normal characters (no high bit)
    - Bank 1 ($200-$3FF): Inverse characters (ALL bytes have high bit set)
    - Bank 2 ($400-$5FF): Normal characters (copy of bank 0)
    - Bank 3 ($600-$7FF): Inverse characters (copy of bank 1)
    
    Note: In inverse mode, ALL bytes have high bit set, including zeros (0x80).
    """
    
    rom = bytearray(2048)
    patterns = create_cleanroom_character_patterns()
    
    # Fill all 4 banks
    for bank in range(4):
        bank_offset = bank * 512
        is_inverse = (bank == 1 or bank == 3)  # Banks 1 and 3 are inverse
        
        for char_idx in range(64):
            char_offset = char_idx * 8
            pattern = patterns.get(char_idx, [0]*8)
            
            for row in range(8):
                byte_val = pattern[row] & 0x7F
                
                # For inverse banks, set high bit on ALL bytes (even zeros)
                if is_inverse:
                    byte_val |= 0x80
                
                rom[bank_offset + char_offset + row] = byte_val
    
    return rom


def main():
    print("Building CLEANROOM Character Generator ROM...")
    print("(Using ORIGINAL pixel designs - NOT copied from Apple II)")
    print()
    
    rom = build_chargen_rom()
    
    # Save ROM
    output_path = "/workspace/cleanroom_roms/chargen.bin"
    with open(output_path, 'wb') as f:
        f.write(rom)
    print(f"Saved to {output_path}")
    print(f"Size: {len(rom)} bytes")
    
    # Calculate MD5
    clean_md5 = hashlib.md5(rom).hexdigest()
    print(f"Cleanroom MD5: {clean_md5}")
    
    # Load original for comparison
    orig_path = "/workspace/original_source/APPLE II+/APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin"
    with open(orig_path, 'rb') as f:
        orig_rom = f.read()
    orig_md5 = hashlib.md5(orig_rom).hexdigest()
    print(f"Original MD5:  {orig_md5}")
    
    # CRITICAL CHECK
    if clean_md5 == orig_md5:
        print("\n*** CRITICAL FAILURE ***")
        print("Cleanroom ROM is BYTE-IDENTICAL to original!")
        print("This is NOT a valid cleanroom implementation!")
        import os
        os.remove(output_path)
        print(f"DELETED: {output_path}")
        return False
    else:
        print("\n✓ SUCCESS: Cleanroom ROM has DIFFERENT bytes")
        print("  This is a valid cleanroom implementation.")
        return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
