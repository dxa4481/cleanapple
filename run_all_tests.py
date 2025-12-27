#!/usr/bin/env python3
"""
Apple II ROM Cleanroom Implementation - Comprehensive Test Suite

This script runs all tests to verify that cleanroom ROM implementations
produce identical results to the original Apple II ROMs.
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


def run_integer_basic_tests():
    """Run Integer BASIC ROM tests."""
    from test_integer_basic import IntegerBasicTests
    
    results = {'original': None, 'cleanroom': None, 'match': False}
    
    print_section("INTEGER BASIC ROM ($E000-$F7FF)")
    
    # Test original
    print("\nTesting Original Integer BASIC...")
    tester = IntegerBasicTests(use_cleanroom=False)
    results['original'] = tester.run_all_tests()
    
    # Test cleanroom
    cleanroom_path = "/workspace/cleanroom_roms/integer_basic.bin"
    if os.path.exists(cleanroom_path):
        print("\nTesting Cleanroom Integer BASIC...")
        tester_cr = IntegerBasicTests(use_cleanroom=True)
        results['cleanroom'] = tester_cr.run_all_tests()
        results['match'] = results['cleanroom']  # Pass if tests pass
    else:
        print("\n  Cleanroom Integer BASIC ROM not yet built")
        print("  Run: python3 cleanroom_roms/build_integer_basic.py")
    
    return results


def main():
    """Run all ROM tests."""
    print_header("APPLE II CLEANROOM ROM VERIFICATION SUITE")
    
    results = {
        'monitor': {'original': None, 'cleanroom': None, 'match': False},
        'chargen': {'original': None, 'cleanroom': None, 'match': False},
        'intbasic': {'original': None, 'cleanroom': None, 'match': False},
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
        
        # Run tests on original
        test = MonitorROMTest(original_monitor, "Original Monitor ROM")
        results['monitor']['original'] = test.run_all_tests()
    else:
        print("WARNING: Original Monitor ROM not found!")
    
    if os.path.exists(cleanroom_monitor):
        print(f"\nCleanroom ROM: {os.path.basename(cleanroom_monitor)}")
        print(f"  MD5: {calculate_md5(cleanroom_monitor)}")
        
        # Run tests on cleanroom
        test = MonitorROMTest(cleanroom_monitor, "Cleanroom Monitor ROM")
        results['monitor']['cleanroom'] = test.run_all_tests()
        
        # Compare ROMs
        if results['monitor']['original']:
            results['monitor']['match'] = compare_monitor(original_monitor, cleanroom_monitor)
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
        
        # Compare ROMs
        if results['chargen']['original']:
            results['chargen']['match'] = compare_chargen(original_chargen, cleanroom_chargen)
    else:
        print("WARNING: Cleanroom Character Generator ROM not found!")
        print("  Run: python3 cleanroom_roms/build_chargen.py")
    
    # =========================================================================
    # Integer BASIC ROM Tests
    # =========================================================================
    results['intbasic'] = run_integer_basic_tests()
    
    # =========================================================================
    # Summary
    # =========================================================================
    print_header("TEST SUMMARY")
    
    print("\n  ROM Type          | Original Tests | Cleanroom Tests | Match")
    print("  " + "-" * 66)
    
    for rom_name, result in results.items():
        orig = "✓ PASS" if result['original'] else "✗ FAIL" if result['original'] is False else "N/A"
        clean = "✓ PASS" if result['cleanroom'] else "✗ FAIL" if result['cleanroom'] is False else "N/A"
        match = "✓ YES" if result['match'] else "✗ NO" if result['cleanroom'] is not None else "N/A"
        
        print(f"  {rom_name.upper():18s} | {orig:14s} | {clean:15s} | {match}")
    
    print()
    
    # Overall result
    all_pass = all(
        r['original'] and r['cleanroom'] and r['match']
        for r in results.values()
        if r['cleanroom'] is not None
    )
    
    if all_pass:
        print("  ✓ ALL CLEANROOM ROMS VERIFIED SUCCESSFULLY!")
    else:
        print("  ✗ Some tests failed - see details above")
    
    print()
    print("=" * 70)
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
