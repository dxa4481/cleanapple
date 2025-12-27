# Cleanroom Implementation Principles

## What TRUE Cleanroom Means

A cleanroom implementation is code written **ONLY** from published specifications, without ever examining the original code.

### Requirements for TRUE Cleanroom

1. **Published Specifications Only**
   - Apple II Reference Manual
   - DOS 3.3 disk format documentation
   - Hardware interface specifications
   - Published API documentation

2. **No Reverse Engineering**
   - Never disassemble original ROM
   - Never analyze original code behavior to understand algorithms
   - Never copy instruction sequences

3. **Original Algorithm Design**
   - Implement your own algorithm to achieve documented behavior
   - Your code structure will naturally differ from original
   - Different byte sequences are the RESULT, not the GOAL

### What Cleanroom Does NOT Mean

- Making bytes "different" by adding NOPs
- Copying code and rearranging it
- Reverse-engineering then reimplementing

## This Project's Cleanroom Status

### ✅ TRUE Cleanroom

| ROM | Evidence |
|-----|----------|
| **Character Generator** | Original pixel designs created from ASCII character shapes |
| **Disk II P5A/P6A** | Original boot algorithm from published disk format spec |

### ⚠️ Partial Cleanroom (Documented Interfaces)

| ROM | Notes |
|-----|-------|
| **Monitor ROM** | Entry points from Apple II Reference Manual, standard algorithms |

The Monitor ROM implements documented entry points ($FDDA PRBYTE, $FBC1 BASCALC, etc.) using standard algorithms. The screen memory layout is documented in the Reference Manual, so BASCALC can be independently derived.

### ❌ NOT Cleanroom (Deleted)

| ROM | Why Deleted |
|-----|-------------|
| **Integer BASIC** | Algorithm was reverse-engineered from disassembly |

Integer BASIC was deleted because the PRTNUM routine and other code was derived by disassembling and analyzing the original ROM, then reimplementing. This is reverse engineering, not cleanroom.

## Verification

For each cleanroom ROM:

| Check | Purpose |
|-------|---------|
| Different MD5 | Natural result of independent implementation |
| Functional tests | Verify documented behavior is achieved |
| Source documentation | Must cite published spec, not "original algorithm" |

## How to Implement True Cleanroom

### Step 1: Gather Published Specs
- Find official documentation
- Note interfaces, inputs, outputs
- Do NOT look at original code

### Step 2: Design Your Algorithm
- Figure out how YOU would solve the problem
- Use your own code structure
- Make your own design decisions

### Step 3: Implement and Test
- Write code based on YOUR design
- Test against documented behavior
- If tests fail, fix YOUR code (don't peek at original)

### Example: Disk II Boot ROM

**Published spec says:**
- Load sector 0, track 0 into $0800
- Jump to $0801
- Disk format uses D5 AA 96 / D5 AA AD markers
- 6-and-2 GCR encoding

**My cleanroom implementation:**
- Designed my own state machine approach
- Used my own register allocation
- Created my own loop structures
- Result: functionally correct, completely different code

## Red Flags (NOT Cleanroom)

- Comments like "exact copy of original algorithm"
- References to specific original ROM addresses
- Code structure that mirrors original
- Disassembly scripts in the repo
