#!/usr/bin/env python3
"""
Apple II ROM Cleanroom Implementation - Comprehensive Test Suite

This script runs all tests to verify that cleanroom ROM implementations:
1. Pass all functional tests (same behavior as original)
2. Are NOT byte-identical to originals (cleanroom requirement)

CRITICAL: Byte-identical ROMs are NOT valid cleanroom implementations!
"""

import os
import sys
import hashlib

# Add tests directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from test_monitor_rom import MonitorROMTest, compare_roms as compare_monitor
from test_chargen_rom import CharGenROMTest, compare_roms as compare_chargen, load_rom


def print_header(title):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_section(title):
    """Print a section header."""
    print()
    print("-" * 70)
    print(f" {title}")
    print("-" * 70)


def calculate_md5(filepath):
    """Calculate MD5 hash of a file."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def check_cleanroom_compliance(original_path, cleanroom_path, rom_name):
    """Verify cleanroom implementation is NOT byte-identical.
    
    Returns True if valid cleanroom (different bytes), False if violation.
    """
    orig_md5 = calculate_md5(original_path)
    clean_md5 = calculate_md5(cleanroom_path)
    
    if orig_md5 == clean_md5:
        print(f"\n  *** CLEANROOM VIOLATION: {rom_name} ***")
        print(f"  Original MD5:  {orig_md5}")
        print(f"  Cleanroom MD5: {clean_md5}")
        print("  ROMs are BYTE-IDENTICAL - this is NOT a valid cleanroom!")
        print("  The cleanroom ROM must be reimplemented with different code.")
        return False
    else:
        print(f"\n  ✓ {rom_name}: Different bytes (valid cleanroom)")
        print(f"    Original:  {orig_md5}")
        print(f"    Cleanroom: {clean_md5}")
        return True


def run_integer_basic_tests():
    """Run Integer BASIC ROM tests."""
    from test_integer_basic import IntegerBasicTests
    
    results = {'original': None, 'cleanroom': None, 'match': False, 'compliant': True}
    
    print_section("INTEGER BASIC ROM ($E000-$F7FF)")
    
    original_path = "/workspace/original_source/APPLE II/APPLE II - 341-0005 - INTEGER BASIC E000 - 2316.bin"
    cleanroom_path = "/workspace/cleanroom_roms/integer_basic.bin"
    
    # Test original
    print("\nTesting Original Integer BASIC...")
    tester = IntegerBasicTests(use_cleanroom=False)
    results['original'] = tester.run_all_tests()
    
    # Test cleanroom
    if os.path.exists(cleanroom_path):
        print("\nTesting Cleanroom Integer BASIC...")
        tester_cr = IntegerBasicTests(use_cleanroom=True)
        results['cleanroom'] = tester_cr.run_all_tests()
        results['match'] = results['cleanroom']
        
        # Verify cleanroom compliance
        if os.path.exists(original_path):
            results['compliant'] = check_cleanroom_compliance(
                original_path, cleanroom_path, "Integer BASIC"
            )
    else:
        print("\n  Cleanroom Integer BASIC ROM not yet built")
        print("  Run: python3 cleanroom_roms/build_integer_basic.py")
    
    return results


def run_disk_ii_tests():
    """Run Disk II ROM tests."""
    from test_disk_ii import DiskIIROMTest
    
    results = {'original': None, 'cleanroom': None, 'match': False, 'compliant': True}
    
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
        results['match'] = results['cleanroom']
        
        # Verify cleanroom compliance
        p5a_compliant = check_cleanroom_compliance(
            DiskIIROMTest.ORIG_P5A, DiskIIROMTest.CLEAN_P5A, "P5A"
        )
        p6a_compliant = check_cleanroom_compliance(
            DiskIIROMTest.ORIG_P6A, DiskIIROMTest.CLEAN_P6A, "P6A"
        )
        results['compliant'] = p5a_compliant and p6a_compliant
    else:
        print("\n  Cleanroom Disk II ROMs not yet built")
        print("  Run: python3 cleanroom_roms/build_disk_ii.py")
    
    return results


def main():
    """Run all ROM tests."""
    print_header("APPLE II CLEANROOM ROM VERIFICATION SUITE")
    
    print("\nCLEANROOM REQUIREMENT:")
    print("  - ROMs must pass all functional tests")
    print("  - ROMs must NOT be byte-identical to originals")
    print("  - Byte-identical ROMs indicate copying, not cleanroom implementation")
    
    results = {
        'monitor': {'original': None, 'cleanroom': None, 'match': False, 'compliant': True},
        'chargen': {'original': None, 'cleanroom': None, 'match': False, 'compliant': True},
        'intbasic': {'original': None, 'cleanroom': None, 'match': False, 'compliant': True},
        'disk_ii': {'original': None, 'cleanroom': None, 'match': False, 'compliant': True},
    }
    
    # =========================================================================
    # Monitor ROM Tests
    # =========================================================================
    print_section("MONITOR ROM ($F800-$FFFF)")
    
    original_monitor = "/workspace/original_source/APPLE II/APPLE II - 341-0004 - INTEGER BASIC MONITOR F800 - 2716.bin"
    cleanroom_monitor = "/workspace/cleanroom_roms/monitor_f800.bin"
    
    if os.path.exists(original_monitor):
        print(f"\nOriginal ROM: {os.path.basename(original_monitor)}")
        print(f"  MD5: {calculate_md5(original_monitor)}")
        
        test = MonitorROMTest(original_monitor, "Original Monitor ROM")
        results['monitor']['original'] = test.run_all_tests()
    else:
        print("WARNING: Original Monitor ROM not found!")
    
    if os.path.exists(cleanroom_monitor):
        print(f"\nCleanroom ROM: {os.path.basename(cleanroom_monitor)}")
        print(f"  MD5: {calculate_md5(cleanroom_monitor)}")
        
        test = MonitorROMTest(cleanroom_monitor, "Cleanroom Monitor ROM")
        results['monitor']['cleanroom'] = test.run_all_tests()
        
        if results['monitor']['original']:
            results['monitor']['match'] = compare_monitor(original_monitor, cleanroom_monitor)
            # Verify cleanroom compliance
            results['monitor']['compliant'] = check_cleanroom_compliance(
                original_monitor, cleanroom_monitor, "Monitor"
            )
    else:
        print("WARNING: Cleanroom Monitor ROM not found!")
        print("  Run: python3 cleanroom_roms/build_monitor.py")
    
    # =========================================================================
    # Character Generator ROM Tests
    # =========================================================================
    print_section("CHARACTER GENERATOR ROM")
    
    original_chargen = "/workspace/original_source/APPLE II+/APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin"
    cleanroom_chargen = "/workspace/cleanroom_roms/chargen.bin"
    
    if os.path.exists(original_chargen):
        print(f"\nOriginal ROM: {os.path.basename(original_chargen)}")
        print(f"  MD5: {calculate_md5(original_chargen)}")
        
        test = CharGenROMTest(original_chargen, "Original Character Generator ROM")
        results['chargen']['original'] = test.run_all_tests()
    else:
        print("WARNING: Original Character Generator ROM not found!")
    
    if os.path.exists(cleanroom_chargen):
        print(f"\nCleanroom ROM: {os.path.basename(cleanroom_chargen)}")
        print(f"  MD5: {calculate_md5(cleanroom_chargen)}")
        
        test = CharGenROMTest(cleanroom_chargen, "Cleanroom Character Generator ROM")
        results['chargen']['cleanroom'] = test.run_all_tests()
        
        if results['chargen']['original']:
            results['chargen']['match'] = compare_chargen(original_chargen, cleanroom_chargen)
            # Verify cleanroom compliance
            results['chargen']['compliant'] = check_cleanroom_compliance(
                original_chargen, cleanroom_chargen, "Character Generator"
            )
    else:
        print("WARNING: Cleanroom Character Generator ROM not found!")
        print("  Run: python3 cleanroom_roms/build_chargen.py")
    
    # =========================================================================
    # Integer BASIC ROM Tests
    # =========================================================================
    results['intbasic'] = run_integer_basic_tests()
    
    # =========================================================================
    # Disk II ROM Tests
    # =========================================================================
    results['disk_ii'] = run_disk_ii_tests()
    
    # =========================================================================
    # Summary
    # =========================================================================
    print_header("TEST SUMMARY")
    
    print("\n  ROM Type          | Functional | Cleanroom | Different Bytes")
    print("  " + "-" * 62)
    
    for rom_name, result in results.items():
        orig = "✓ PASS" if result['original'] else "✗ FAIL" if result['original'] is False else "N/A"
        clean = "✓ PASS" if result['cleanroom'] else "✗ FAIL" if result['cleanroom'] is False else "N/A"
        compliant = "✓ YES" if result['compliant'] else "✗ VIOLATION"
        
        if result['cleanroom'] is None:
            compliant = "N/A"
        
        display_name = rom_name.upper().replace('_', ' ')
        print(f"  {display_name:18s} | {orig:10s} | {clean:9s} | {compliant}")
    
    print()
    
    # Overall result - must pass tests AND be cleanroom compliant
    all_pass = all(
        r['original'] and r['cleanroom'] and r['match'] and r['compliant']
        for r in results.values()
        if r['cleanroom'] is not None
    )
    
    if all_pass:
        print("  ✓ ALL CLEANROOM ROMS VERIFIED SUCCESSFULLY!")
        print("    - All functional tests pass")
        print("    - All ROMs have different bytes (valid cleanroom)")
    else:
        failed = []
        for name, r in results.items():
            if r['cleanroom'] is not None:
                if not r['match']:
                    failed.append(f"{name}: functional tests failed")
                elif not r['compliant']:
                    failed.append(f"{name}: byte-identical (NOT cleanroom)")
        
        if failed:
            print("  ✗ FAILURES:")
            for f in failed:
                print(f"    - {f}")
    
    print()
    print("=" * 70)
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
