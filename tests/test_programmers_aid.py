#!/usr/bin/env python3
"""
Test suite for the Programmer's Aid #1 ROM.

Tests verify:
1. Entry point structure
2. Hi-res graphics routine functionality
3. Soft switch access
4. Zero page usage
5. Cleanroom compliance (different bytes from original)
"""

import os
import sys
import hashlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from py65.devices.mpu6502 import MPU
except ImportError:
    print("Warning: py65 not installed. Some tests will be skipped.")
    MPU = None


class ProgrammersAidROMTest:
    """Test the Programmer's Aid #1 ROM implementation."""
    
    CLEANROOM_ROM = "cleanroom_roms/programmers_aid.bin"
    ORIGINAL_ROM = "original_source/APPLE II/APPLE II - 341-0016 - PROGRAMMER'S  AID #1 - 2716.bin"
    
    # Entry point offsets from $D000
    ENTRY_POINTS = {
        0x000: "HIRES",
        0x003: "HGR",
        0x006: "HGR2",
        0x009: "SETHCOL",
        0x00C: "HCLR",
        0x00F: "BKGND",
        0x012: "HPLOT",
        0x015: "HLIN",
        0x018: "DRAW",
        0x01B: "XDRAW",
        0x01E: "SHLOAD",
        0x021: "ROT",
        0x024: "SCALE",
        0x027: "HFIND",
        0x02A: "DRAW1",
        0x02D: "SETHPAG",
    }
    
    # Zero page locations used
    ZERO_PAGE = {
        0xE0: "HPAG",
        0xE2: "HBASL",
        0xE3: "HBASH",
        0xE4: "HNDX",
        0xE5: "HMASK",
        0xE6: "HCOLOR",
        0xEB: "SCALE",
        0xEC: "ROT",
    }
    
    # Soft switches
    SOFT_SWITCHES = {
        0xC050: "TXTCLR",
        0xC051: "TXTSET",
        0xC052: "MIXCLR",
        0xC053: "MIXSET",
        0xC054: "LOWSCR",
        0xC055: "HISCR",
        0xC056: "LORES",
        0xC057: "HIRES",
    }
    
    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.results = []
        
    def load_rom(self, path):
        """Load a ROM file."""
        full_path = os.path.join(self.base_path, path)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                return f.read()
        return None
    
    def record(self, name, passed, detail=""):
        """Record a test result."""
        self.results.append({
            'name': name,
            'passed': passed,
            'detail': detail
        })
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}" + (f" ({detail})" if detail else ""))
        return passed
    
    def test_entry_points(self, rom):
        """Test that all entry points have valid code."""
        print("\n--- Entry Points ---")
        
        for offset, name in self.ENTRY_POINTS.items():
            byte = rom[offset]
            # Should be JMP ($4C) or valid instruction
            valid = byte in [0x4C, 0x20, 0xEA, 0x60, 0x18, 0x38, 0x48, 0x68, 0xA9]
            self.record(f"{name} at $D{offset:03X}", valid, f"opcode ${byte:02X}")
    
    def test_soft_switch_access(self, rom):
        """Test that ROM accesses appropriate soft switches."""
        print("\n--- Soft Switch Access ---")
        
        rom_bytes = bytes(rom)
        
        # HIRES/HGR routines should access graphics soft switches
        # Look for LDA $C0xx patterns (opcode $AD)
        graphics_switches = [0xC050, 0xC053, 0xC054, 0xC057]  # TXTCLR, MIXSET, LOWSCR, HIRES
        
        found_switches = []
        for switch in graphics_switches:
            low = switch & 0xFF
            high = (switch >> 8) & 0xFF
            # Look for LDA $xxxx pattern
            for i in range(len(rom_bytes) - 2):
                if rom_bytes[i] == 0xAD and rom_bytes[i+1] == low and rom_bytes[i+2] == high:
                    found_switches.append(switch)
                    break
        
        self.record("Accesses graphics soft switches", len(found_switches) >= 3,
                   f"found {len(found_switches)}/4")
    
    def test_zero_page_usage(self, rom):
        """Test that ROM uses documented zero page locations."""
        print("\n--- Zero Page Usage ---")
        
        rom_bytes = bytes(rom)
        
        # Look for STA $Ex or LDA $Ex patterns
        found_zp = []
        for zp_addr in self.ZERO_PAGE.keys():
            # STA zp = $85 xx, LDA zp = $A5 xx
            for i in range(len(rom_bytes) - 1):
                if rom_bytes[i] in [0x85, 0xA5] and rom_bytes[i+1] == zp_addr:
                    found_zp.append(zp_addr)
                    break
        
        self.record("Uses documented zero page", len(found_zp) >= 3,
                   f"found {len(found_zp)}/{len(self.ZERO_PAGE)} locations")
    
    def test_hires_implementation(self, rom):
        """Test HIRES/HGR implementation details."""
        print("\n--- HIRES Implementation ---")
        
        rom_bytes = bytes(rom)
        
        # HIRES should set page to $20 (LDA #$20 = $A9 $20)
        has_page1 = b'\xA9\x20' in rom_bytes
        self.record("Sets page 1 base ($20)", has_page1)
        
        # HGR2 should set page to $40 (LDA #$40 = $A9 $40)
        has_page2 = b'\xA9\x40' in rom_bytes
        self.record("Sets page 2 base ($40)", has_page2)
        
        # Should have RTS instructions (routines return)
        rts_count = rom_bytes.count(0x60)
        self.record("Contains RTS instructions", rts_count >= 5,
                   f"found {rts_count}")
    
    def test_color_routine(self, rom):
        """Test SETHCOL implementation."""
        print("\n--- Color Routine ---")
        
        rom_bytes = bytes(rom)
        
        # SETHCOL should AND with 7 to mask color (AND #$07 = $29 $07)
        has_color_mask = b'\x29\x07' in rom_bytes
        self.record("Has color mask (AND #$07)", has_color_mask)
        
        # Should store to HCOLOR ($E6)
        has_color_store = b'\x85\xE6' in rom_bytes
        self.record("Stores to HCOLOR ($E6)", has_color_store)
    
    def test_cleanroom_compliance(self):
        """Verify cleanroom implementation differs from original."""
        print("\n--- Cleanroom Compliance ---")
        
        cleanroom = self.load_rom(self.CLEANROOM_ROM)
        original = self.load_rom(self.ORIGINAL_ROM)
        
        if cleanroom is None:
            self.record("Cleanroom ROM exists", False, "file not found")
            return
        
        cleanroom_md5 = hashlib.md5(cleanroom).hexdigest()
        self.record("Cleanroom ROM built", True, f"MD5: {cleanroom_md5}")
        
        if original is None:
            self.record("Original ROM comparison", True, 
                       "original not available (OK for cleanroom)")
            return
        
        original_md5 = hashlib.md5(original).hexdigest()
        
        # CRITICAL: Cleanroom MUST differ from original
        different = cleanroom_md5 != original_md5
        self.record("Different from original (REQUIRED)", different,
                   f"original MD5: {original_md5}")
        
        if not different:
            print("\n  *** CLEANROOM VIOLATION: ROM is byte-identical to original! ***")
        
        # Count differing bytes
        min_len = min(len(cleanroom), len(original))
        diff_count = sum(1 for i in range(min_len) if cleanroom[i] != original[i])
        diff_percent = (diff_count / min_len) * 100
        
        self.record("Byte difference analysis", diff_percent > 10,
                   f"{diff_count}/{min_len} bytes differ ({diff_percent:.1f}%)")
    
    def test_emulation(self, rom):
        """Test ROM behavior in emulator."""
        print("\n--- Emulation Tests ---")
        
        if MPU is None:
            self.record("Emulation tests", False, "py65 not installed")
            return
        
        # Create CPU and memory
        mpu = MPU()
        
        # Load ROM at $D000
        rom_base = 0xD000
        for i, byte in enumerate(rom):
            mpu.memory[rom_base + i] = byte
        
        # Test SETHCOL ($D009)
        # Set A = 5 (orange color)
        mpu.a = 5
        mpu.pc = 0xD009
        
        # Run until RTS
        max_cycles = 100
        cycles = 0
        while mpu.memory[mpu.pc] != 0x60 and cycles < max_cycles:
            mpu.step()
            cycles += 1
        
        # Check that color was stored
        color_stored = mpu.memory[0xE6] == 5
        self.record("SETHCOL stores color", color_stored,
                   f"$E6 = ${mpu.memory[0xE6]:02X}")
        
        # Test ROT ($D021)
        mpu.a = 16  # 90 degrees
        mpu.pc = 0xD021
        
        cycles = 0
        while mpu.memory[mpu.pc] != 0x60 and cycles < max_cycles:
            mpu.step()
            cycles += 1
        
        # Check rotation stored
        rot_stored = mpu.memory[0xEC] == 16
        self.record("ROT stores rotation", rot_stored,
                   f"$EC = ${mpu.memory[0xEC]:02X}")
    
    def run_all_tests(self):
        """Run all tests."""
        print("=" * 60)
        print("Programmer's Aid #1 ROM Tests")
        print("=" * 60)
        
        rom = self.load_rom(self.CLEANROOM_ROM)
        if rom is None:
            print(f"\nERROR: Could not load {self.CLEANROOM_ROM}")
            return False
        
        print(f"\nTesting: {self.CLEANROOM_ROM}")
        print(f"ROM Size: {len(rom)} bytes")
        
        self.test_entry_points(rom)
        self.test_soft_switch_access(rom)
        self.test_zero_page_usage(rom)
        self.test_hires_implementation(rom)
        self.test_color_routine(rom)
        self.test_emulation(rom)
        self.test_cleanroom_compliance()
        
        # Summary
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print("\n" + "=" * 60)
        print(f"Results: {passed}/{total} tests passed")
        print("=" * 60)
        
        return passed == total


def main():
    tester = ProgrammersAidROMTest()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
