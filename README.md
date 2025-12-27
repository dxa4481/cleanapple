# Apple II ROM Cleanroom Implementation Project

This repository contains cleanroom implementations of Apple II ROMs, verified to produce functionally identical results to the original Apple II ROMs using an emulator-based testing framework.

## ⚠️ CRITICAL: Cleanroom Compliance

**Cleanroom implementation means the code must:**
1. Produce the same FUNCTIONAL outputs as the original
2. Have DIFFERENT bytes than the original

**Byte-identical ROMs are NOT valid cleanroom implementations.** If a cleanroom ROM has the same MD5 hash as the original, it indicates copying rather than independent reimplementation.

See [CLEANROOM_PRINCIPLES.md](CLEANROOM_PRINCIPLES.md) for detailed requirements.

## Overview

The project includes:

1. **Emulator Testing Framework** - A Python-based 6502 emulator (using py65) configured to test ROM functionality
2. **Cleanroom ROM Implementations** - Independently created ROMs that match original behavior
3. **Comprehensive Test Suite** - Automated tests that verify cleanroom ROMs produce identical outputs
4. **Cleanroom Verification** - MD5 comparison to ensure ROMs are different from originals

## Completed Cleanroom ROMs

### Monitor ROM ($F800-$FFFF)
- **Original**: `APPLE II - 341-0004 - INTEGER BASIC MONITOR F800 - 2716.bin`
- **Cleanroom**: `cleanroom_roms/monitor_f800.bin`
- **Status**: ✅ 60 tests pass, functionally equivalent, **different bytes**
- **Original MD5**: `bc0163ca04c463e06f99fb029ad21b1f`
- **Cleanroom MD5**: `d4c6dad016151c21fb03679205bbc649`

### Character Generator ROM
- **Original**: `APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin`
- **Cleanroom**: `cleanroom_roms/chargen.bin`
- **Status**: ✅ 7 tests pass, original font design, **different bytes**
- **Original MD5**: `9ac0dc8c4d0002eb45b0b84be0bde5ec`
- **Cleanroom MD5**: `4f2ebdd9892953af3bbafd498325728e`

The cleanroom character generator uses original pixel designs that produce readable characters in the same format as the original (4 banks × 64 characters × 8 bytes) but with different visual patterns.

### Integer BASIC ROM ($E000-$F7FF)
- **Original**: 3 ROMs: `341-0001`, `341-0002`, `341-0003`
- **Cleanroom**: `cleanroom_roms/integer_basic.bin`
- **Status**: ✅ 24 tests pass, core routines functionally identical, **different bytes**

### Disk II Controller ROMs (P5A, P6A)
- **Original P5A**: `DISK II P5A.bin` (256 bytes)
- **Original P6A**: `DISK II P6A.bin` (256 bytes)
- **Cleanroom P5A**: `cleanroom_roms/disk_ii_p5a.bin`
- **Cleanroom P6A**: `cleanroom_roms/disk_ii_p6a.bin`
- **Status**: ✅ 12 tests pass, boot functionality equivalent, **different bytes**
- **P5A Original MD5**: `2020aa1413ff77fe29353f3ee72dc295`
- **P5A Cleanroom MD5**: `a12692cdf93b4448be493cb1fc43d245`
- **P6A Original MD5**: `c4f38c35eae48ec5416f7c8d670aa068`
- **P6A Cleanroom MD5**: `ba83878956e40a3e7f10785b1283b224`

## Repository Structure

```
/workspace/
├── README.md                          # This file
├── CLEANROOM_PRINCIPLES.md            # Cleanroom compliance requirements
├── apple2_emulator.py                 # 6502 emulator framework
├── run_all_tests.py                   # Comprehensive test runner
├── cleanroom_roms/
│   ├── monitor_f800.bin               # Cleanroom Monitor ROM
│   ├── build_monitor.py               # Monitor ROM generator
│   ├── chargen.bin                    # Cleanroom Character Generator ROM
│   ├── build_chargen.py               # Character Generator ROM generator
│   ├── integer_basic.bin              # Cleanroom Integer BASIC ROM
│   ├── build_integer_basic.py         # Integer BASIC ROM generator
│   ├── disk_ii_p5a.bin                # Cleanroom Disk II Boot ROM
│   ├── disk_ii_p6a.bin                # Cleanroom Disk II GCR Table
│   └── build_disk_ii.py               # Disk II ROM generator
├── docs/
│   ├── MONITOR_ROM_F800.md            # Monitor ROM documentation
│   ├── CHARACTER_GENERATOR_ROM.md     # Character Generator documentation
│   ├── INTEGER_BASIC_ROM.md           # Integer BASIC documentation
│   └── DISK_II_ROM.md                 # Disk II Controller documentation
├── tests/
│   ├── test_monitor_rom.py            # Monitor ROM tests
│   ├── test_chargen_rom.py            # Character Generator tests
│   ├── test_integer_basic.py          # Integer BASIC tests
│   └── test_disk_ii.py                # Disk II tests
└── original_source/                   # Original Apple II ROMs
    ├── APPLE II/
    ├── APPLE II+/
    └── ...
```

## Running Tests

### Prerequisites

```bash
pip install py65
```

### Run All Tests

```bash
python3 run_all_tests.py
```

This verifies:
1. All ROMs pass functional tests
2. All cleanroom ROMs have different MD5 hashes than originals

### Run Individual Tests

```bash
# Monitor ROM tests
python3 tests/test_monitor_rom.py

# Character Generator tests
python3 tests/test_chargen_rom.py

# Integer BASIC tests
python3 tests/test_integer_basic.py

# Disk II tests
python3 tests/test_disk_ii.py
```

### Rebuild Cleanroom ROMs

```bash
# Rebuild all cleanroom ROMs
python3 cleanroom_roms/build_monitor.py
python3 cleanroom_roms/build_chargen.py
python3 cleanroom_roms/build_integer_basic.py
python3 cleanroom_roms/build_disk_ii.py
```

## Test Results

### Overall Summary

| ROM | Functional Tests | Cleanroom Tests | Different Bytes |
|-----|-----------------|-----------------|-----------------|
| Monitor | ✅ 60/60 | ✅ PASS | ✅ YES |
| Character Generator | ✅ 7/7 | ✅ PASS | ✅ YES |
| Integer BASIC | ✅ 24/24 | ✅ PASS | ✅ YES |
| Disk II | ✅ 12/12 | ✅ PASS | ✅ YES |

### Cleanroom Verification

Each cleanroom ROM is verified to:
1. ✅ Pass all functional tests (same behavior)
2. ✅ Have a different MD5 hash (different implementation)

A ROM that is byte-identical to the original is **AUTOMATICALLY REJECTED** and must be reimplemented.

## Documentation

Detailed documentation for each ROM is available in the `docs/` directory:

- [Monitor ROM Documentation](docs/MONITOR_ROM_F800.md)
- [Character Generator ROM Documentation](docs/CHARACTER_GENERATOR_ROM.md)
- [Integer BASIC ROM Documentation](docs/INTEGER_BASIC_ROM.md)
- [Disk II Controller ROM Documentation](docs/DISK_II_ROM.md)

## Cleanroom Process

The cleanroom implementations were created following these principles:

1. **Documentation First**: All interfaces, entry points, and behaviors were documented based on publicly available technical references

2. **Independent Implementation**: Code was written based only on documented behavior, never by examining or copying original ROM bytes

3. **Different Code Required**: The implementation must use different instruction sequences, code organization, or algorithms to achieve the same functional result

4. **Verification Testing**: The emulator framework tests that cleanroom ROMs produce identical outputs to original ROMs

5. **Non-Identity Check**: MD5 hashes must be DIFFERENT - if they match, the implementation is rejected

### What Makes a Valid Cleanroom ROM

✅ **Valid**:
- Different bytes from original
- Passes all functional tests
- Produces same outputs for same inputs

❌ **Invalid**:
- Byte-identical to original (this is copying, not cleanroom)
- Fails functional tests
- Produces different outputs

## License

The cleanroom implementations in this repository are original works created without reference to copyrighted code. The testing framework and documentation are provided as-is for educational purposes.

The original Apple II ROMs in `original_source/` are included only for testing/verification purposes and remain property of their respective copyright holders.
