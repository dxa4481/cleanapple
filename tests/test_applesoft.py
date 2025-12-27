#!/usr/bin/env python3
"""
Test suite for the cleanroom Applesoft BASIC ROM.

This tests the implementation that follows Franklin Computer Corp.'s
cleanroom approach after the 1983 Apple v. Franklin lawsuit.
"""

import os
import sys
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from py65.devices.mpu6502 import MPU
except ImportError:
    print("ERROR: py65 not installed")
    MPU = None


class ApplesoftROMTest:
    """Test the Applesoft BASIC ROM implementation."""
    
    CLEANROOM_ROM = "cleanroom_roms/applesoft.bin"
    ORIGINAL_ROMS = [
        "original_source/APPLE II+/APPLE II+ - 341-0011 - APPLESOFT BASIC D000 - 2716.bin",
        "original_source/APPLE II+/APPLE II+ - 341-0012 - APPLESOFT BASIC D800 - 2716.bin",
        "original_source/APPLE II+/APPLE II+ - 341-0013 - APPLESOFT BASIC E000 - 2716.bin",
        "original_source/APPLE II+/APPLE II+ - 341-0014 - APPLESOFT BASIC E800 - 2716.bin",
        "original_source/APPLE II+/APPLE II+ - 341-0015 - APPLESOFT BASIC F000 - 2716.bin",
    ]
    
    # Entry points that must exist
    ENTRY_POINTS = {
        0xD000: "COLD",
        0xD003: "WARM",
    }
    
    # Zero page locations used
    ZP_LOCATIONS = {
        0x67: "TXTTAB",
        0x69: "VARTAB", 
        0x6B: "ARYTAB",
        0x6D: "STREND",
        0x6F: "FRETOP",
        0x73: "MEMSIZ",
        0x75: "CURLIN",
        0x9D: "FAC",
        0xB8: "TXTPTR",
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
    
    def load_original_combined(self):
        """Load and combine original Applesoft ROMs."""
        combined = bytearray()
        for rom_path in self.ORIGINAL_ROMS:
            data = self.load_rom(rom_path)
            if data:
                combined.extend(data)
        return bytes(combined) if combined else None
    
    def record(self, name, passed, detail=""):
        """Record test result."""
        self.results.append({'name': name, 'passed': passed, 'detail': detail})
        status = "? PASS" if passed else "? FAIL"
        print(f"  {status}: {name}" + (f" ({detail})" if detail else ""))
    
    def test_rom_size(self, rom):
        """Test ROM is correct size."""
        print("\n--- ROM Size ---")
        correct_size = len(rom) == 10240  # 10KB
        self.record("ROM size is 10KB", correct_size, f"actual: {len(rom)} bytes")
    
    def test_entry_points(self, rom):
        """Test that entry points have valid code."""
        print("\n--- Entry Points ---")
        
        for addr, name in self.ENTRY_POINTS.items():
            offset = addr - 0xD000
            byte = rom[offset]
            # Should have valid opcode (not $FF filler)
            valid = byte != 0xFF and byte != 0x00
            self.record(f"{name} at ${addr:04X}", valid, f"opcode ${byte:02X}")
    
    def test_has_code(self, rom):
        """Test that ROM contains actual code, not just filler."""
        print("\n--- Code Content ---")
        
        # Count non-$FF bytes
        code_bytes = sum(1 for b in rom if b != 0xFF)
        has_substantial_code = code_bytes > 500
        
        self.record("Contains substantial code", has_substantial_code,
                   f"{code_bytes}/10240 bytes are code")
        
        # Check for common 6502 opcodes
        common_opcodes = [0x20, 0x4C, 0x60, 0xA9, 0xA5, 0x85]  # JSR, JMP, RTS, LDA, LDA zp, STA zp
        found_opcodes = sum(1 for b in rom if b in common_opcodes)
        
        self.record("Contains 6502 instructions", found_opcodes > 50,
                   f"found {found_opcodes} common opcodes")
    
    def test_token_table(self, rom):
        """Test that token table exists."""
        print("\n--- Token Table ---")
        
        # Look for keyword strings in ROM
        keywords = [b'PRINT', b'GOTO', b'FOR', b'NEXT', b'IF']
        found = 0
        
        for kw in keywords:
            if kw in rom or kw.lower() in rom:
                found += 1
        
        # Also check for token-style encoding (high bit set on last char)
        self.record("Contains BASIC keywords", found >= 3,
                   f"found {found}/5 keywords")
    
    def test_monitor_calls(self, rom):
        """Test that ROM calls Monitor routines."""
        print("\n--- Monitor Integration ---")
        
        # Look for JSR to Monitor routines
        # JSR $FDED (COUT), JSR $FD8E (CROUT), JSR $FD67 (GETLN)
        monitor_calls = [
            (b'\x20\xED\xFD', "COUT"),
            (b'\x20\x8E\xFD', "CROUT"),
            (b'\x20\x67\xFD', "GETLN"),
            (b'\x20\xDA\xFD', "PRBYTE"),
        ]
        
        for pattern, name in monitor_calls:
            found = pattern in rom
            self.record(f"Calls Monitor {name}", found)
    
    def test_cleanroom_compliance(self):
        """Verify cleanroom implementation differs from original."""
        print("\n--- Cleanroom Compliance ---")
        
        cleanroom = self.load_rom(self.CLEANROOM_ROM)
        original = self.load_original_combined()
        
        if cleanroom is None:
            self.record("Cleanroom ROM exists", False)
            return
        
        cleanroom_md5 = hashlib.md5(cleanroom).hexdigest()
        self.record("Cleanroom ROM built", True, f"MD5: {cleanroom_md5}")
        
        if original is None:
            self.record("Original comparison", True, "original not available")
            return
        
        original_md5 = hashlib.md5(original).hexdigest()
        
        # CRITICAL: Must be different
        different = cleanroom_md5 != original_md5
        self.record("Different from original (REQUIRED)", different,
                   f"original MD5: {original_md5}")
        
        if not different:
            print("\n  *** CLEANROOM VIOLATION ***")
        
        # Calculate byte difference
        min_len = min(len(cleanroom), len(original))
        diff_count = sum(1 for i in range(min_len) if cleanroom[i] != original[i])
        diff_pct = (diff_count / min_len) * 100
        
        self.record("Significant byte difference", diff_pct > 50,
                   f"{diff_count}/{min_len} bytes differ ({diff_pct:.1f}%)")
    
    def test_emulation(self, rom):
        """Test basic emulation of Applesoft."""
        print("\n--- Emulation Tests ---")
        
        if MPU is None:
            self.record("Emulation", False, "py65 not installed")
            return
        
        mpu = MPU()
        
        # Load ROM at $D000
        for i, b in enumerate(rom):
            mpu.memory[0xD000 + i] = b
        
        # Load Monitor ROM (needed for I/O)
        monitor_path = os.path.join(self.base_path, 'cleanroom_roms/monitor_f800.bin')
        if os.path.exists(monitor_path):
            with open(monitor_path, 'rb') as f:
                monitor = f.read()
            for i, b in enumerate(monitor):
                mpu.memory[0xF800 + i] = b
        
        # Test cold start
        mpu.pc = 0xD000
        
        # Run until we've executed enough instructions to initialize
        # or until we hit a JMP to main loop (indicating init done)
        for _ in range(5000):
            mpu.step()
            # Check if memory was initialized
            if mpu.memory[0x67] != 0 and mpu.memory[0x73] != 0:
                break
        
        # Check if zero page was initialized
        txttab = mpu.memory[0x67] | (mpu.memory[0x68] << 8)
        memsiz = mpu.memory[0x73] | (mpu.memory[0x74] << 8)
        
        self.record("Cold start initializes TXTTAB", txttab > 0,
                   f"TXTTAB = ${txttab:04X}")
        
        self.record("Cold start initializes MEMSIZ", memsiz > 0,
                   f"MEMSIZ = ${memsiz:04X}")
    
    def run_all_tests(self):
        """Run all tests."""
        print("=" * 60)
        print("Applesoft BASIC ROM Tests (Cleanroom)")
        print("Following Franklin Computer Corp. approach")
        print("=" * 60)
        
        rom = self.load_rom(self.CLEANROOM_ROM)
        if rom is None:
            print(f"\nERROR: Could not load {self.CLEANROOM_ROM}")
            return False
        
        print(f"\nTesting: {self.CLEANROOM_ROM}")
        
        self.test_rom_size(rom)
        self.test_entry_points(rom)
        self.test_has_code(rom)
        self.test_token_table(rom)
        self.test_monitor_calls(rom)
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
    tester = ApplesoftROMTest()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
