"""
Apple II Character Generator ROM Test Suite

Tests the character generator ROM for correct pixel patterns
and structure.
"""

import os
import sys
import hashlib

# Character set: ASCII 32-95 (space through underscore)
CHAR_SET = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_"


def load_rom(filepath):
    """Load ROM file."""
    with open(filepath, 'rb') as f:
        return f.read()


def get_character_data(rom, char_index, offset=0):
    """Get 8 bytes of character data for a given index."""
    start = offset + (char_index * 8)
    return rom[start:start + 8]


def display_character(data, name=""):
    """Display character as ASCII art."""
    print(f"Character: {name}")
    for row in data:
        line = ""
        for bit in range(7):  # 7 visible bits
            if row & (1 << bit):
                line += "█"
            else:
                line += " "
        print(f"  {line} ${row:02X}")
    print()


def calculate_checksum(data):
    """Calculate MD5 checksum."""
    return hashlib.md5(data).hexdigest()


class CharGenROMTest:
    """Test harness for Character Generator ROM."""
    
    def __init__(self, rom_path, description="Character Generator ROM"):
        self.rom_path = rom_path
        self.description = description
        self.rom = None
        self.results = []
    
    def setup(self):
        """Load ROM file."""
        if os.path.exists(self.rom_path):
            self.rom = load_rom(self.rom_path)
            return True
        return False
    
    def record_result(self, test_name, passed, expected, actual, details=""):
        """Record a test result."""
        self.results.append({
            'test': test_name,
            'passed': passed,
            'expected': expected,
            'actual': actual,
            'details': details
        })
    
    def run_all_tests(self):
        """Run all character generator tests."""
        if not self.setup():
            print(f"ERROR: Could not load ROM from {self.rom_path}")
            return False
        
        print(f"\n{'='*60}")
        print(f"Testing: {self.description}")
        print(f"ROM Path: {self.rom_path}")
        print(f"ROM MD5: {calculate_checksum(self.rom)}")
        print(f"ROM Size: {len(self.rom)} bytes")
        print(f"{'='*60}")
        
        self.test_size()
        self.test_structure()
        self.test_specific_characters()
        self.test_character_properties()
        
        # Print summary
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print(f"\n{'-'*60}")
        print(f"Results: {passed}/{total} tests passed")
        print(f"{'-'*60}")
        
        for r in self.results:
            status = "✓ PASS" if r['passed'] else "✗ FAIL"
            print(f"  {status}: {r['test']}")
            if not r['passed']:
                print(f"         Expected: {r['expected']}")
                print(f"         Actual:   {r['actual']}")
            if r['details']:
                print(f"         Details:  {r['details']}")
        
        return all(r['passed'] for r in self.results)
    
    def test_size(self):
        """Test ROM size is correct."""
        print("\n--- Testing ROM Size ---")
        
        expected_size = 2048
        actual_size = len(self.rom)
        
        self.record_result(
            "ROM size is 2048 bytes",
            actual_size == expected_size,
            f"{expected_size} bytes",
            f"{actual_size} bytes"
        )
    
    def test_structure(self):
        """Test ROM structure."""
        print("\n--- Testing ROM Structure ---")
        
        # ROM should have 64 characters × 8 bytes = 512 bytes per bank
        # With 4 banks (normal, inverse, normal+80, inverse+80) = 2048 bytes
        
        # Check first bank matches third bank (same characters, no high bit)
        bank0 = self.rom[0:512]
        bank2 = self.rom[1024:1536]
        
        match = bank0 == bank2
        self.record_result(
            "Bank 0 matches Bank 2 (normal mode copies)",
            match,
            "Identical",
            "Match" if match else "Differ"
        )
        
        # Check that inverse banks have high bit set
        bank1_has_high = all(b & 0x80 for b in self.rom[512:1024] if b != 0)
        self.record_result(
            "Bank 1 has high bit set (inverse mode)",
            bank1_has_high,
            "High bit set",
            "Set" if bank1_has_high else "Not set"
        )
    
    def test_specific_characters(self):
        """Test specific character patterns."""
        print("\n--- Testing Specific Characters ---")
        
        # Apple II ROM index mapping:
        # Index 0-31: ASCII 64-95 (@, A-Z, [\]^_)
        # Index 32-63: ASCII 32-63 (space, !-?, etc.)
        
        # Test '@' character at index 0 (should have pixels)
        at_data = get_character_data(self.rom, 0)
        has_pixels = any(b != 0 for b in at_data)
        self.record_result(
            "'@' character (index 0) has pixels",
            has_pixels,
            "Has pixels",
            f"${' '.join(f'{b:02X}' for b in at_data)}"
        )
        
        # Test 'A' character at index 1 has recognizable pattern
        a_data = get_character_data(self.rom, 1)
        # 'A' starts narrow, widens, has crossbar
        has_narrow_top = a_data[1] < a_data[5]  # Top narrower than crossbar row
        has_crossbar = a_data[5] > a_data[6]  # Crossbar row wider than legs
        
        self.record_result(
            "Letter 'A' (index 1) has correct pattern shape",
            has_narrow_top and has_crossbar,
            "Narrow top, crossbar",
            f"Top<Mid: {has_narrow_top}, Crossbar: {has_crossbar}"
        )
        
        # Test space character at index 32 (should be all zeros)
        space_data = get_character_data(self.rom, 32)
        is_blank = all(b == 0 for b in space_data)
        self.record_result(
            "Space character (index 32) is blank",
            is_blank,
            "All zeros",
            f"${' '.join(f'{b:02X}' for b in space_data)}"
        )
        
        # Test that letters A-Z (indices 1-26) all have unique patterns
        letter_patterns = [get_character_data(self.rom, 1 + i) for i in range(26)]
        all_different = len(set(tuple(p) for p in letter_patterns)) == 26
        self.record_result(
            "Letters A-Z all have unique patterns",
            all_different,
            "26 unique patterns",
            f"{len(set(tuple(p) for p in letter_patterns))} unique patterns"
        )
    
    def test_character_properties(self):
        """Test general character properties."""
        print("\n--- Testing Character Properties ---")
        
        # All characters should fit in 7 bits (bit 7 unused in normal mode)
        all_7bit = all(self.rom[i] < 0x80 for i in range(512) if self.rom[i] != 0)
        self.record_result(
            "Normal bank uses only 7 bits",
            all_7bit,
            "All < $80",
            "Correct" if all_7bit else "Found $80+ values"
        )
        
        # Non-blank characters should have some pixels
        # Index 32 is space, other punctuation may have minimal pixels
        # Check that letters A-Z (indices 1-26) and digits (indices 48-57) have pixels
        letters_and_digits = list(range(1, 27)) + list(range(48, 58))
        visible_chars = [get_character_data(self.rom, i) for i in letters_and_digits]
        all_visible = all(any(b != 0 for b in char) for char in visible_chars)
        self.record_result(
            "All letters and digits have pixels",
            all_visible,
            "All visible",
            "Correct" if all_visible else "Found blank characters"
        )


def compare_roms(original_path, cleanroom_path):
    """Compare character generator ROMs."""
    print("\n" + "="*60)
    print("CHARACTER GENERATOR ROM COMPARISON")
    print("="*60)
    
    original = load_rom(original_path)
    cleanroom = load_rom(cleanroom_path)
    
    # Size comparison
    print(f"\nOriginal size: {len(original)} bytes")
    print(f"Cleanroom size: {len(cleanroom)} bytes")
    
    if len(original) != len(cleanroom):
        print("ERROR: Sizes don't match!")
        return False
    
    # Compare each character
    print("\n--- Comparing Characters ---")
    mismatches = []
    
    for i in range(64):
        orig_char = get_character_data(original, i)
        clean_char = get_character_data(cleanroom, i)
        
        if orig_char != clean_char:
            mismatches.append((i, CHAR_SET[i] if i < len(CHAR_SET) else '?'))
    
    if mismatches:
        print(f"  {len(mismatches)} characters differ:")
        for idx, char in mismatches[:10]:
            print(f"    Index {idx}: '{char}'")
        if len(mismatches) > 10:
            print(f"    ... and {len(mismatches) - 10} more")
    else:
        print("  All 64 characters match!")
    
    # Show sample character comparisons
    print("\n--- Sample Character Comparisons ---")
    for idx, name in [(0, "Space"), (33, "A"), (16, "0")]:
        print(f"\nCharacter {idx} ('{name}'):")
        print("  Original:", ' '.join(f'{b:02X}' for b in get_character_data(original, idx)))
        print("  Cleanroom:", ' '.join(f'{b:02X}' for b in get_character_data(cleanroom, idx)))
    
    return len(mismatches) == 0


def display_character_set(rom_path):
    """Display all characters from ROM."""
    rom = load_rom(rom_path)
    print(f"\nCharacter Set from {os.path.basename(rom_path)}:")
    print("="*60)
    
    for i in range(64):
        char = CHAR_SET[i] if i < len(CHAR_SET) else '?'
        data = get_character_data(rom, i)
        print(f"\nIndex {i:2d}: '{char}'")
        for row in data:
            line = ""
            for bit in range(7):
                if row & (1 << bit):
                    line += "██"
                else:
                    line += "  "
            print(f"  {line}")


def main():
    """Run character generator ROM tests."""
    original_path = "/workspace/original_source/APPLE II+/APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin"
    
    test = CharGenROMTest(original_path, "Original Apple II+ Character Generator ROM")
    test.run_all_tests()
    
    # Show a few characters
    print("\n--- Sample Characters ---")
    rom = load_rom(original_path)
    for idx, name in [(0, "Space"), (1, "!"), (33, "A"), (16, "0"), (47, "O")]:
        display_character(get_character_data(rom, idx), f"Index {idx}: '{CHAR_SET[idx]}'")
    
    # Check for cleanroom ROM
    cleanroom_path = "/workspace/cleanroom_roms/chargen.bin"
    if os.path.exists(cleanroom_path):
        compare_roms(original_path, cleanroom_path)


if __name__ == "__main__":
    main()
