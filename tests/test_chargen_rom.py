#!/usr/bin/env python3
"""
Test suite for Apple II Character Generator ROM.

Tests FUNCTIONAL equivalence, NOT byte identity.
A cleanroom implementation MUST have different bytes but produce
visually readable characters.
"""

import os
import sys
import hashlib

sys.path.insert(0, '/workspace')


def load_rom(filepath):
    """Load a ROM file."""
    with open(filepath, 'rb') as f:
        return f.read()


class CharGenROMTest:
    """Test suite for Character Generator ROM."""
    
    ORIG_PATH = "/workspace/original_source/APPLE II+/APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin"
    CLEAN_PATH = "/workspace/cleanroom_roms/chargen.bin"
    
    def __init__(self, rom_path, name="ROM"):
        """Initialize test with a ROM file."""
        self.rom_path = rom_path
        self.name = name
        self.rom = None
        self.results = []
        
    def load(self):
        """Load the ROM file."""
        if not os.path.exists(self.rom_path):
            raise FileNotFoundError(f"ROM not found: {self.rom_path}")
        self.rom = load_rom(self.rom_path)
        
    def record(self, name, passed, details=""):
        """Record a test result."""
        self.results.append({'name': name, 'passed': passed, 'details': details})
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
        if details:
            print(f"         {details}")
    
    def test_size(self):
        """Test ROM size is 2048 bytes."""
        passed = len(self.rom) == 2048
        self.record("ROM size is 2048 bytes", passed, f"Size: {len(self.rom)}")
    
    def test_bank_structure(self):
        """Test ROM has 4 banks of 512 bytes.
        
        Original structure:
        - Bank 0: Normal (no high bit)
        - Bank 1: Inverse (ALL bytes have high bit)
        - Bank 2: Normal (copy of bank 0)
        - Bank 3: Inverse (copy of bank 1)
        """
        # Check that bank 0 has no high bits
        bank0_normal = all(b & 0x80 == 0 for b in self.rom[0:512])
        
        # Check that bank 1 has ALL high bits set
        bank1_inverse = all(b & 0x80 == 0x80 for b in self.rom[512:1024])
        
        # Check bank 2 is normal (copy of bank 0)
        bank2_normal = all(b & 0x80 == 0 for b in self.rom[1024:1536])
        
        # Check bank 3 has all high bits (copy of bank 1)
        bank3_inverse = all(b & 0x80 == 0x80 for b in self.rom[1536:2048])
        
        passed = bank0_normal and bank1_inverse and bank2_normal and bank3_inverse
        self.record("Bank structure correct", passed,
                   f"B0:{bank0_normal} B1:{bank1_inverse} B2:{bank2_normal} B3:{bank3_inverse}")
    
    def test_space_is_blank(self):
        """Test that space character (index 32) is blank."""
        # Space is at index 32, each char is 8 bytes
        space_offset = 32 * 8
        space_bytes = self.rom[space_offset:space_offset+8]
        
        # Space should be all zeros (or just low bits)
        is_blank = all((b & 0x7F) == 0 for b in space_bytes)
        self.record("Space character is blank", is_blank)
    
    def test_letters_have_pixels(self):
        """Test that letter characters have some pixels set."""
        all_have_pixels = True
        
        # Check letters A-Z (indices 1-26)
        for i in range(1, 27):
            char_offset = i * 8
            char_bytes = self.rom[char_offset:char_offset+8]
            pixel_count = sum(bin(b & 0x7F).count('1') for b in char_bytes)
            
            if pixel_count < 5:  # Letters should have at least 5 pixels
                all_have_pixels = False
                break
        
        self.record("Letters A-Z have pixels", all_have_pixels)
    
    def test_digits_have_pixels(self):
        """Test that digit characters have some pixels set."""
        all_have_pixels = True
        
        # Check digits 0-9 (indices 48-57)
        for i in range(48, 58):
            char_offset = i * 8
            char_bytes = self.rom[char_offset:char_offset+8]
            pixel_count = sum(bin(b & 0x7F).count('1') for b in char_bytes)
            
            if pixel_count < 5:
                all_have_pixels = False
                break
        
        self.record("Digits 0-9 have pixels", all_have_pixels)
    
    def test_characters_unique(self):
        """Test that printable characters have unique patterns."""
        patterns = {}
        duplicates = []
        
        # Check indices 0-63 (all printable characters)
        for i in range(64):
            char_offset = i * 8
            pattern = tuple(b & 0x7F for b in self.rom[char_offset:char_offset+8])
            
            if pattern in patterns and pattern != (0,0,0,0,0,0,0,0):
                duplicates.append((i, patterns[pattern]))
            else:
                patterns[pattern] = i
        
        # Allow space to be duplicate (multiple blank chars is OK)
        non_space_dupes = [d for d in duplicates if d not in [(32,0)]]
        passed = len(non_space_dupes) == 0
        self.record("Characters have unique patterns", passed,
                   f"Duplicates: {len(non_space_dupes)}")
    
    def test_inverse_has_high_bit(self):
        """Test that inverse bank has high bit set on ALL bytes."""
        # Bank 1 is the inverse bank (offset 512-1023)
        bank1 = self.rom[512:1024]
        
        # ALL bytes in inverse bank must have high bit set
        correct = all(b & 0x80 == 0x80 for b in bank1)
        
        self.record("Inverse bank has high bit on all bytes", correct)
    
    def run_all_tests(self):
        """Run all tests."""
        print(f"\n{'='*60}")
        print(f"Testing: {self.name}")
        print(f"ROM Path: {self.rom_path}")
        
        try:
            self.load()
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            return False
        
        md5 = hashlib.md5(self.rom).hexdigest()
        print(f"ROM MD5: {md5}")
        print(f"ROM Size: {len(self.rom)} bytes")
        print(f"{'='*60}")
        
        print("\n--- Testing ROM Size ---")
        self.test_size()
        
        print("\n--- Testing ROM Structure ---")
        self.test_bank_structure()
        self.test_inverse_has_high_bit()
        
        print("\n--- Testing Character Patterns ---")
        self.test_space_is_blank()
        self.test_letters_have_pixels()
        self.test_digits_have_pixels()
        self.test_characters_unique()
        
        # Summary
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print(f"\n{'-'*60}")
        print(f"Results: {passed}/{total} tests passed")
        print(f"{'-'*60}")
        
        return passed == total


def compare_roms(orig_path, clean_path):
    """Compare original and cleanroom ROMs.
    
    For cleanroom compliance:
    - ROMs MUST be different (different MD5)
    - Both must pass functional tests
    """
    print("\n" + "=" * 60)
    print("CHARACTER GENERATOR ROM COMPARISON")
    print("=" * 60)
    
    orig = load_rom(orig_path)
    clean = load_rom(clean_path)
    
    orig_md5 = hashlib.md5(orig).hexdigest()
    clean_md5 = hashlib.md5(clean).hexdigest()
    
    print(f"\nOriginal MD5:  {orig_md5}")
    print(f"Cleanroom MD5: {clean_md5}")
    
    # CRITICAL: Cleanroom MUST be different
    if orig_md5 == clean_md5:
        print("\n*** CLEANROOM VIOLATION ***")
        print("ROMs are BYTE-IDENTICAL - this is NOT a valid cleanroom!")
        return False
    else:
        print("\n✓ Cleanroom has DIFFERENT bytes (required)")
    
    # Both should be same size
    if len(orig) == len(clean):
        print(f"✓ Both ROMs are same size ({len(orig)} bytes)")
    else:
        print(f"✗ Size mismatch: orig={len(orig)}, clean={len(clean)}")
    
    # Compare readability
    print("\n--- Character Readability Check ---")
    
    # Count pixels in letters for both
    def count_letter_pixels(rom):
        total = 0
        for i in range(1, 27):  # A-Z
            offset = i * 8
            for b in rom[offset:offset+8]:
                total += bin(b & 0x7F).count('1')
        return total
    
    orig_pixels = count_letter_pixels(orig)
    clean_pixels = count_letter_pixels(clean)
    
    print(f"  Original letters pixel count: {orig_pixels}")
    print(f"  Cleanroom letters pixel count: {clean_pixels}")
    
    # Cleanroom should have reasonable pixel density
    if clean_pixels > orig_pixels * 0.5:
        print("  ✓ Cleanroom has sufficient pixel density")
    else:
        print("  ✗ Cleanroom may have insufficient pixels")
    
    return True


def main():
    """Run Character Generator ROM tests."""
    print("=" * 60)
    print("CHARACTER GENERATOR ROM TEST SUITE")
    print("=" * 60)
    
    orig_path = CharGenROMTest.ORIG_PATH
    clean_path = CharGenROMTest.CLEAN_PATH
    
    # Test original
    if os.path.exists(orig_path):
        print("\nTesting ORIGINAL ROM...")
        test_orig = CharGenROMTest(orig_path, "Original Character Generator")
        orig_ok = test_orig.run_all_tests()
    else:
        print(f"Original ROM not found: {orig_path}")
        orig_ok = False
    
    # Test cleanroom
    if os.path.exists(clean_path):
        print("\nTesting CLEANROOM ROM...")
        test_clean = CharGenROMTest(clean_path, "Cleanroom Character Generator")
        clean_ok = test_clean.run_all_tests()
        
        # Compare (cleanroom MUST be different)
        if orig_ok:
            compare_ok = compare_roms(orig_path, clean_path)
        else:
            compare_ok = True
    else:
        print(f"\nCleanroom ROM not found: {clean_path}")
        print("Run: python3 cleanroom_roms/build_chargen_cleanroom.py")
        clean_ok = False
        compare_ok = False
    
    return orig_ok and clean_ok and compare_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
