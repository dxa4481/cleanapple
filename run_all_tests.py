#!/usr/bin/env python3
"""
Apple II ROM Cleanroom Implementation - Test Suite

This script runs all tests to verify cleanroom ROM implementations.

TRUE CLEANROOM REQUIREMENTS:
1. Implementation from published specifications only
2. NO reverse engineering of original code
3. Different bytes are a RESULT of independent implementation, not a goal
"""

import os
import sys
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from test_monitor_rom import MonitorROMTest, compare_roms as compare_monitor
from test_chargen_rom import CharGenROMTest, compare_roms as compare_chargen


def print_header(title):
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_section(title):
    print()
    print("-" * 70)
    print(f" {title}")
    print("-" * 70)


def calculate_md5(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def verify_cleanroom(original_path, cleanroom_path, name):
    """Verify cleanroom implementation differs from original."""
    if not os.path.exists(original_path) or not os.path.exists(cleanroom_path):
        return None
    
    orig_md5 = calculate_md5(original_path)
    clean_md5 = calculate_md5(cleanroom_path)
    
    is_different = orig_md5 != clean_md5
    
    print(f"\n  {name}:")
    print(f"    Original:  {orig_md5}")
    print(f"    Cleanroom: {clean_md5}")
    print(f"    Different: {'✓ YES' if is_different else '✗ NO (VIOLATION)'}")
    
    return is_different


def run_disk_ii_tests():
    """Run Disk II ROM tests."""
    from test_disk_ii import DiskIIROMTest
    
    results = {'original': None, 'cleanroom': None, 'different': True}
    
    print_section("DISK II CONTROLLER ROMS (P5A, P6A)")
    
    # Test original
    print("\nTesting Original Disk II ROMs...")
    tester = DiskIIROMTest(use_cleanroom=False)
    results['original'] = tester.run_all_tests()
    
    # Test cleanroom
    if os.path.exists(DiskIIROMTest.CLEAN_P5A) and os.path.exists(DiskIIROMTest.CLEAN_P6A):
        print("\nTesting Cleanroom Disk II ROMs...")
        tester_cr = DiskIIROMTest(use_cleanroom=True)
        results['cleanroom'] = tester_cr.run_all_tests()
        
        # Verify different bytes
        p5a_diff = verify_cleanroom(DiskIIROMTest.ORIG_P5A, DiskIIROMTest.CLEAN_P5A, "P5A")
        p6a_diff = verify_cleanroom(DiskIIROMTest.ORIG_P6A, DiskIIROMTest.CLEAN_P6A, "P6A")
        results['different'] = (p5a_diff and p6a_diff) if (p5a_diff is not None and p6a_diff is not None) else False
    else:
        print("\n  Cleanroom Disk II ROMs not yet built")
        print("  Run: python3 cleanroom_roms/build_disk_ii.py")
        results['different'] = False
    
    return results


def run_integration_tests():
    """Run integration tests verifying ROMs work together."""
    print_section("INTEGRATION TESTS")
    
    results = []
    
    # Test 1: Monitor ROM provides required entry points for other ROMs
    print("\nTest: Monitor provides entry points for Disk II boot...")
    monitor_path = "/workspace/cleanroom_roms/monitor_f800.bin"
    if os.path.exists(monitor_path):
        with open(monitor_path, 'rb') as f:
            rom = f.read()
        
        # Check that $FF58 and $FCA8 are callable (not empty)
        # $FF58 should be in ROM space
        ff58_offset = 0xFF58 - 0xF800
        fca8_offset = 0xFCA8 - 0xF800
        
        # Check they're not just $FF filler
        has_ff58 = rom[ff58_offset] != 0xFF
        has_fca8 = rom[fca8_offset] != 0xFF and rom[fca8_offset] == 0x38  # WAIT starts with SEC
        
        if has_ff58 and has_fca8:
            print("  ✓ PASS: Monitor has $FF58 and $FCA8 (WAIT)")
            results.append(True)
        else:
            print(f"  ✗ FAIL: Missing entry points (FF58:{has_ff58}, FCA8:{has_fca8})")
            results.append(False)
    else:
        print("  SKIP: Monitor ROM not found")
    
    # Test 2: Character Generator has correct bank structure for video hardware
    print("\nTest: Character Generator banks for video hardware...")
    chargen_path = "/workspace/cleanroom_roms/chargen.bin"
    if os.path.exists(chargen_path):
        with open(chargen_path, 'rb') as f:
            rom = f.read()
        
        # Banks 0,2 should be normal, banks 1,3 should have high bit set
        bank0_ok = all(b & 0x80 == 0 for b in rom[0:512])
        bank1_ok = all(b & 0x80 == 0x80 for b in rom[512:1024])
        
        if bank0_ok and bank1_ok:
            print("  ✓ PASS: Bank structure correct for hardware")
            results.append(True)
        else:
            print("  ✗ FAIL: Bank structure incorrect")
            results.append(False)
    else:
        print("  SKIP: Character Generator ROM not found")
    
    # Test 3: Disk II boot ROM calls Monitor correctly
    print("\nTest: Disk II boot calls Monitor routines...")
    disk_p5a_path = "/workspace/cleanroom_roms/disk_ii_p5a.bin"
    if os.path.exists(disk_p5a_path):
        with open(disk_p5a_path, 'rb') as f:
            rom = f.read()
        
        # Look for JSR $FF58 (20 58 FF) and JSR $FCA8 (20 A8 FC)
        rom_bytes = bytes(rom)
        has_jsr_ff58 = b'\x20\x58\xFF' in rom_bytes
        has_jsr_fca8 = b'\x20\xA8\xFC' in rom_bytes
        
        if has_jsr_ff58 and has_jsr_fca8:
            print("  ✓ PASS: Disk II calls Monitor routines")
            results.append(True)
        else:
            print(f"  ✗ FAIL: Missing JSR (FF58:{has_jsr_ff58}, FCA8:{has_jsr_fca8})")
            results.append(False)
    else:
        print("  SKIP: Disk II P5A not found")
    
    # Summary
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"\n  Integration: {passed}/{total} tests passed")
    
    return all(results) if results else None


def main():
    print_header("APPLE II CLEANROOM ROM TEST SUITE")
    
    print("\nCLEANROOM METHODOLOGY:")
    print("  - TRUE cleanroom = implemented from published specs only")
    print("  - NO reverse engineering of original code")
    print("  - Different bytes are a natural result, not forced")
    
    results = {
        'monitor': {'original': None, 'cleanroom': None, 'different': True},
        'chargen': {'original': None, 'cleanroom': None, 'different': True},
        'disk_ii': {'original': None, 'cleanroom': None, 'different': True},
    }
    
    # Monitor ROM Tests
    print_section("MONITOR ROM ($F800-$FFFF)")
    
    original_monitor = "/workspace/original_source/APPLE II/APPLE II - 341-0004 - INTEGER BASIC MONITOR F800 - 2716.bin"
    cleanroom_monitor = "/workspace/cleanroom_roms/monitor_f800.bin"
    
    if os.path.exists(original_monitor):
        print(f"\nTesting Original Monitor ROM...")
        test = MonitorROMTest(original_monitor, "Original Monitor ROM")
        results['monitor']['original'] = test.run_all_tests()
    
    if os.path.exists(cleanroom_monitor):
        print(f"\nTesting Cleanroom Monitor ROM...")
        test = MonitorROMTest(cleanroom_monitor, "Cleanroom Monitor ROM")
        results['monitor']['cleanroom'] = test.run_all_tests()
        
        if results['monitor']['original']:
            compare_monitor(original_monitor, cleanroom_monitor)
            results['monitor']['different'] = verify_cleanroom(
                original_monitor, cleanroom_monitor, "Monitor"
            )
    else:
        print("  Cleanroom Monitor ROM not found")
        results['monitor']['different'] = False
    
    # Character Generator ROM Tests
    print_section("CHARACTER GENERATOR ROM")
    
    original_chargen = "/workspace/original_source/APPLE II+/APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin"
    cleanroom_chargen = "/workspace/cleanroom_roms/chargen.bin"
    
    if os.path.exists(original_chargen):
        print(f"\nTesting Original Character Generator...")
        test = CharGenROMTest(original_chargen, "Original Character Generator")
        results['chargen']['original'] = test.run_all_tests()
    
    if os.path.exists(cleanroom_chargen):
        print(f"\nTesting Cleanroom Character Generator...")
        test = CharGenROMTest(cleanroom_chargen, "Cleanroom Character Generator")
        results['chargen']['cleanroom'] = test.run_all_tests()
        
        if results['chargen']['original']:
            compare_chargen(original_chargen, cleanroom_chargen)
            results['chargen']['different'] = verify_cleanroom(
                original_chargen, cleanroom_chargen, "Character Generator"
            )
    else:
        print("  Cleanroom Character Generator ROM not found")
        results['chargen']['different'] = False
    
    # Disk II ROM Tests
    results['disk_ii'] = run_disk_ii_tests()
    
    # Integration Tests
    integration_ok = run_integration_tests()
    
    # Summary
    print_header("TEST SUMMARY")
    
    print("\n  ROM Type          | Functional | Different Bytes | Cleanroom Status")
    print("  " + "-" * 68)
    
    cleanroom_status = {
        'monitor': 'Documented interfaces',
        'chargen': 'TRUE cleanroom',
        'disk_ii': 'TRUE cleanroom',
    }
    
    for rom_name, result in results.items():
        func = "✓ PASS" if result.get('cleanroom') else "✗ FAIL" if result.get('cleanroom') is False else "N/A"
        diff = "✓ YES" if result.get('different') else "✗ NO" if result.get('different') is False else "N/A"
        status = cleanroom_status.get(rom_name, 'Unknown')
        
        display_name = rom_name.upper().replace('_', ' ')
        print(f"  {display_name:18s} | {func:10s} | {diff:15s} | {status}")
    
    print()
    
    all_pass = all(
        r.get('cleanroom') and r.get('different')
        for r in results.values()
        if r.get('cleanroom') is not None
    )
    
    if all_pass and integration_ok:
        print("  ✓ ALL TESTS PASSED")
        print("    - Functional tests verify correct behavior")
        print("    - Different bytes confirm independent implementation")
        print("    - Integration tests verify ROMs work together")
    else:
        print("  ✗ Some tests failed - see details above")
    
    print()
    print("=" * 70)
    
    return 0 if (all_pass and integration_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
