#!/usr/bin/env python3
"""
Test suite for Apple II Disk II Controller ROMs.

Tests the original and cleanroom implementations of the P5A (boot) and
P6A (GCR translation) ROMs.
"""

import os
import sys
import hashlib

sys.path.insert(0, '/workspace')

from py65.devices.mpu6502 import MPU as MPU6502
from py65.disassembler import Disassembler


class DiskIITests:
    """Test suite for Disk II Controller ROMs."""
    
    # ROM paths
    ORIG_P5A = "/workspace/original_source/DISK II P5A.bin"
    ORIG_P6A = "/workspace/original_source/DISK II P6A.bin"
    CLEAN_P5A = "/workspace/cleanroom_roms/disk_ii_p5a.bin"
    CLEAN_P6A = "/workspace/cleanroom_roms/disk_ii_p6a.bin"
    
    # Boot ROM is loaded at $C600 for slot 6
    BASE_ADDR = 0xC600
    
    def __init__(self, use_cleanroom=False):
        """Initialize test suite."""
        self.use_cleanroom = use_cleanroom
        self.results = []
        self.p5a = None
        self.p6a = None
        
    def load_roms(self):
        """Load P5A and P6A ROMs."""
        if self.use_cleanroom:
            p5a_path = self.CLEAN_P5A
            p6a_path = self.CLEAN_P6A
        else:
            p5a_path = self.ORIG_P5A
            p6a_path = self.ORIG_P6A
        
        if not os.path.exists(p5a_path):
            raise FileNotFoundError(f"P5A ROM not found: {p5a_path}")
        if not os.path.exists(p6a_path):
            raise FileNotFoundError(f"P6A ROM not found: {p6a_path}")
        
        with open(p5a_path, 'rb') as f:
            self.p5a = f.read()
        with open(p6a_path, 'rb') as f:
            self.p6a = f.read()
    
    def record_result(self, name, passed, details=""):
        """Record a test result."""
        self.results.append({
            'name': name,
            'passed': passed,
            'details': details
        })
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
        if details and not passed:
            print(f"         {details}")
    
    # =========================================================================
    # P5A Boot ROM Tests
    # =========================================================================
    
    def test_p5a_size(self):
        """Test P5A ROM size."""
        passed = len(self.p5a) == 256
        self.record_result(
            "P5A size is 256 bytes",
            passed,
            f"Size: {len(self.p5a)}"
        )
    
    def test_p5a_entry_point(self):
        """Test that P5A starts with expected instructions."""
        # First instruction should be LDX #$20
        passed = self.p5a[0] == 0xA2 and self.p5a[1] == 0x20
        self.record_result(
            "P5A starts with LDX #$20",
            passed,
            f"Bytes: ${self.p5a[0]:02X} ${self.p5a[1]:02X}"
        )
    
    def test_p5a_jsr_ff58(self):
        """Test that P5A calls Monitor $FF58 to get slot number."""
        # Look for JSR $FF58 (20 58 FF)
        found = False
        for i in range(len(self.p5a) - 2):
            if self.p5a[i:i+3] == bytes([0x20, 0x58, 0xFF]):
                found = True
                break
        
        self.record_result(
            "P5A calls JSR $FF58",
            found,
            "Monitor routine to get slot number"
        )
    
    def test_p5a_jsr_fca8(self):
        """Test that P5A calls Monitor $FCA8 for delay."""
        # Look for JSR $FCA8 (20 A8 FC)
        found = False
        for i in range(len(self.p5a) - 2):
            if self.p5a[i:i+3] == bytes([0x20, 0xA8, 0xFC]):
                found = True
                break
        
        self.record_result(
            "P5A calls JSR $FCA8",
            found,
            "Monitor delay routine for motor spinup"
        )
    
    def test_p5a_boot_jump(self):
        """Test that P5A ends with JMP $0801."""
        # Look for JMP $0801 (4C 01 08)
        found = False
        for i in range(len(self.p5a) - 2):
            if self.p5a[i:i+3] == bytes([0x4C, 0x01, 0x08]):
                found = True
                break
        
        self.record_result(
            "P5A ends with JMP $0801",
            found,
            "Jumps to loaded boot sector"
        )
    
    def test_p5a_address_markers(self):
        """Test for D5 AA 96 address field marker detection."""
        # Look for EOR #$D5 (49 D5) and CMP #$AA (C9 AA) and CMP #$96 (C9 96)
        has_d5 = bytes([0x49, 0xD5]) in self.p5a
        has_aa = bytes([0xC9, 0xAA]) in self.p5a
        has_96 = bytes([0xC9, 0x96]) in self.p5a
        
        passed = has_d5 and has_aa and has_96
        self.record_result(
            "P5A detects D5 AA 96 address marker",
            passed,
            f"D5:{has_d5} AA:{has_aa} 96:{has_96}"
        )
    
    def test_p5a_data_marker(self):
        """Test for D5 AA AD data field marker detection."""
        # Look for EOR #$AD (49 AD)
        has_ad = bytes([0x49, 0xAD]) in self.p5a
        
        self.record_result(
            "P5A detects D5 AA AD data marker",
            has_ad,
            "Data field prologue"
        )
    
    def test_p5a_translation_table(self):
        """Test that P5A builds translation table at $0356."""
        # Look for STA $0356,X (9D 56 03)
        found = bytes([0x9D, 0x56, 0x03]) in self.p5a
        
        self.record_result(
            "P5A builds table at $0356",
            found,
            "6-and-2 translation table"
        )
    
    def test_p5a_decode_via_table(self):
        """Test that P5A uses translation table for decoding."""
        # Look for EOR $02D6,Y (59 D6 02)
        found = bytes([0x59, 0xD6, 0x02]) in self.p5a
        
        self.record_result(
            "P5A decodes via $02D6 table",
            found,
            "GCR decode lookup"
        )
    
    # =========================================================================
    # P6A Translation Table Tests
    # =========================================================================
    
    def test_p6a_size(self):
        """Test P6A ROM size."""
        passed = len(self.p6a) == 256
        self.record_result(
            "P6A size is 256 bytes",
            passed,
            f"Size: {len(self.p6a)}"
        )
    
    def test_p6a_has_patterns(self):
        """Test P6A contains GCR patterns."""
        # P6A should have repeating patterns
        has_0a = self.p6a.count(0x0A) > 20  # 0x0A appears frequently
        
        self.record_result(
            "P6A contains GCR patterns",
            has_0a,
            f"0x0A count: {self.p6a.count(0x0A)}"
        )
    
    def test_p6a_structure(self):
        """Test P6A has expected structure."""
        # Check first few bytes
        expected_start = bytes([0x88, 0xB8, 0x88, 0x08])
        passed = self.p6a[:4] == expected_start
        
        self.record_result(
            "P6A starts with expected bytes",
            passed,
            f"Expected: {expected_start.hex()}, Got: {self.p6a[:4].hex()}"
        )
    
    # =========================================================================
    # MD5 Comparison Tests
    # =========================================================================
    
    def test_p5a_md5(self):
        """Compare P5A MD5 with original."""
        with open(self.ORIG_P5A, 'rb') as f:
            orig_md5 = hashlib.md5(f.read()).hexdigest()
        
        clean_md5 = hashlib.md5(self.p5a).hexdigest()
        
        passed = orig_md5 == clean_md5
        self.record_result(
            "P5A MD5 matches original",
            passed,
            f"Original: {orig_md5}, Cleanroom: {clean_md5}"
        )
    
    def test_p6a_md5(self):
        """Compare P6A MD5 with original."""
        with open(self.ORIG_P6A, 'rb') as f:
            orig_md5 = hashlib.md5(f.read()).hexdigest()
        
        clean_md5 = hashlib.md5(self.p6a).hexdigest()
        
        passed = orig_md5 == clean_md5
        self.record_result(
            "P6A MD5 matches original",
            passed,
            f"Original: {orig_md5}, Cleanroom: {clean_md5}"
        )
    
    # =========================================================================
    # Run All Tests
    # =========================================================================
    
    def run_all_tests(self):
        """Run all tests."""
        mode = "CLEANROOM" if self.use_cleanroom else "ORIGINAL"
        print(f"\n{'='*60}")
        print(f"DISK II ROM TESTS ({mode})")
        print(f"{'='*60}")
        
        try:
            self.load_roms()
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            return False
        
        # P5A tests
        print("\n--- P5A Boot ROM Tests ---")
        self.test_p5a_size()
        self.test_p5a_entry_point()
        self.test_p5a_jsr_ff58()
        self.test_p5a_jsr_fca8()
        self.test_p5a_boot_jump()
        self.test_p5a_address_markers()
        self.test_p5a_data_marker()
        self.test_p5a_translation_table()
        self.test_p5a_decode_via_table()
        
        # P6A tests
        print("\n--- P6A Translation Table Tests ---")
        self.test_p6a_size()
        self.test_p6a_has_patterns()
        self.test_p6a_structure()
        
        # MD5 tests (only for cleanroom)
        if self.use_cleanroom:
            print("\n--- MD5 Comparison Tests ---")
            self.test_p5a_md5()
            self.test_p6a_md5()
        
        # Summary
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print(f"\n{'='*60}")
        print(f"RESULTS: {passed}/{total} tests passed")
        print(f"{'='*60}")
        
        return passed == total


def compare_roms():
    """Compare original and cleanroom ROMs."""
    print("\n" + "=" * 60)
    print("DISK II ROM BYTE-BY-BYTE COMPARISON")
    print("=" * 60)
    
    p5a_orig = open("/workspace/original_source/DISK II P5A.bin", 'rb').read()
    p5a_clean = open("/workspace/cleanroom_roms/disk_ii_p5a.bin", 'rb').read()
    p6a_orig = open("/workspace/original_source/DISK II P6A.bin", 'rb').read()
    p6a_clean = open("/workspace/cleanroom_roms/disk_ii_p6a.bin", 'rb').read()
    
    print(f"\nP5A: {'✓ IDENTICAL' if p5a_orig == p5a_clean else '✗ DIFFERENT'}")
    print(f"P6A: {'✓ IDENTICAL' if p6a_orig == p6a_clean else '✗ DIFFERENT'}")
    
    return p5a_orig == p5a_clean and p6a_orig == p6a_clean


def main():
    """Run Disk II ROM tests."""
    # Test original ROMs
    print("Testing ORIGINAL Disk II ROMs...")
    tester = DiskIITests(use_cleanroom=False)
    original_ok = tester.run_all_tests()
    
    # Test cleanroom ROMs
    if os.path.exists("/workspace/cleanroom_roms/disk_ii_p5a.bin"):
        print("\nTesting CLEANROOM Disk II ROMs...")
        tester_cr = DiskIITests(use_cleanroom=True)
        cleanroom_ok = tester_cr.run_all_tests()
        
        # Compare
        compare_ok = compare_roms()
    else:
        print("\nCleanroom Disk II ROMs not found - run build_disk_ii.py first")
        cleanroom_ok = False
        compare_ok = False
    
    return original_ok and cleanroom_ok and compare_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
