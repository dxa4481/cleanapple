# Apple II ROM Cleanroom Implementation Project

This repository contains cleanroom implementations of Apple II ROMs, created **exclusively from published specifications** without examining original code.

## ⚠️ Cleanroom Methodology

**TRUE cleanroom** means:
1. Implementation from **published documentation only** (Apple II Reference Manual, DOS documentation)
2. **NO reverse engineering** - never examine, disassemble, or analyze original ROM code
3. **Original algorithm design** - different bytes are a natural result, not forced
4. **Tests verify functionality**, not implementation details

See [CLEANROOM_PRINCIPLES.md](CLEANROOM_PRINCIPLES.md) for detailed requirements.

## Cleanroom Status

| ROM | Status | Implementation Basis |
|-----|--------|---------------------|
| **Character Generator** | ✅ TRUE cleanroom | Original pixel designs for ASCII characters |
| **Disk II (P5A/P6A)** | ✅ TRUE cleanroom | Published disk format spec, hardware I/O docs |
| **Monitor ROM** | ⚠️ Documented interfaces | Entry points from Apple II Reference Manual |
| **Integer BASIC** | ❌ Deleted | Was reverse-engineered (not cleanroom) |

## Test Results

```
ROM Type          | Functional | Different Bytes | Cleanroom Status
--------------------------------------------------------------------
MONITOR            | ✓ PASS     | ✓ YES           | Documented interfaces
CHARGEN            | ✓ PASS     | ✓ YES           | TRUE cleanroom
DISK II            | ✓ PASS     | ✓ YES           | TRUE cleanroom

✓ ALL TESTS PASSED
  - Functional tests verify correct behavior
  - Different bytes confirm independent implementation
  - Integration tests verify ROMs work together
```

## Cleanroom ROMs

### Character Generator ROM (2KB)
- **Status**: ✅ TRUE cleanroom
- **Method**: Original pixel designs created from ASCII character shapes
- **Tests**: 7/7 pass (bank structure, character patterns)

### Disk II Controller ROMs (P5A: 256B, P6A: 256B)
- **Status**: ✅ TRUE cleanroom  
- **Method**: Original boot algorithm from published disk format specification
- **Published specs used**:
  - Disk format: D5 AA 96 (address), D5 AA AD (data)
  - 6-and-2 GCR encoding
  - Boot loads to $0800, jumps to $0801
  - Hardware I/O at $C080-$C08F
- **Tests**: 12/12 pass (I/O access, markers, boot sequence)

### Monitor ROM (2KB)
- **Status**: ⚠️ Documented interfaces
- **Method**: Implements published entry points from Apple II Reference Manual
- **Why not "TRUE cleanroom"**: Uses documented zero page addresses and entry points
  which constrain the implementation. However, algorithms (BASCALC, PRHEX, WAIT)
  are derived from published screen layout and standard techniques.
- **Tests**: 60/60 pass (vectors, screen calculation, timing)

## Deleted (Not Cleanroom)

### Integer BASIC ROM
- **Reason deleted**: The PRTNUM routine and other code was derived by
  disassembling and analyzing the original ROM. This is reverse engineering,
  not cleanroom.
- **Evidence**: Build script referenced "exact copy of original algorithm"
  and used disassembly analysis scripts.

## Repository Structure

```
/workspace/
├── README.md                    # This file
├── CLEANROOM_PRINCIPLES.md      # Cleanroom methodology documentation
├── run_all_tests.py             # Comprehensive test suite
├── apple2_emulator.py           # 6502 emulator for testing
├── cleanroom_roms/
│   ├── chargen.bin              # Cleanroom Character Generator
│   ├── build_chargen.py         # Character Generator builder
│   ├── disk_ii_p5a.bin          # Cleanroom Disk II Boot ROM
│   ├── disk_ii_p6a.bin          # Cleanroom Disk II GCR Table
│   ├── build_disk_ii.py         # Disk II builder
│   ├── monitor_f800.bin         # Monitor ROM implementation
│   └── build_monitor.py         # Monitor ROM builder
├── tests/
│   ├── test_monitor_rom.py      # Monitor functional tests
│   ├── test_chargen_rom.py      # Character Generator tests
│   └── test_disk_ii.py          # Disk II tests
├── docs/
│   ├── MONITOR_ROM_F800.md      # Monitor ROM documentation
│   ├── CHARACTER_GENERATOR_ROM.md
│   └── DISK_II_ROM.md
└── original_source/             # Original ROMs (for comparison only)
```

## Running Tests

```bash
# Install dependency
pip install py65

# Run all tests
python3 run_all_tests.py

# Run individual tests
python3 tests/test_monitor_rom.py
python3 tests/test_chargen_rom.py
python3 tests/test_disk_ii.py

# Rebuild cleanroom ROMs
python3 cleanroom_roms/build_chargen.py
python3 cleanroom_roms/build_disk_ii.py
python3 cleanroom_roms/build_monitor.py
```

## What Makes This Different from Other Projects

1. **Honest about methodology** - We clearly distinguish TRUE cleanroom 
   (published specs only) from documented interfaces (known entry points).

2. **Deleted non-compliant code** - Integer BASIC was removed when we
   discovered it was reverse-engineered, not cleanroom.

3. **Tests verify functionality** - Tests check that ROMs produce correct
   outputs, not that they match specific byte patterns.

4. **Integration testing** - Verifies all ROMs work together correctly.

## License

The cleanroom implementations in this repository are original works created
without reference to copyrighted code.

The original Apple II ROMs in `original_source/` are included only for
verification purposes and remain property of their respective copyright holders.
