# Cleanroom Implementation Principles

## CRITICAL LEGAL REQUIREMENT

**A cleanroom implementation MUST NOT produce byte-for-byte identical code to the original.**

If a cleanroom ROM has the same MD5 hash as the original, it is **NOT** a cleanroom implementation - it is a copy, which violates copyright law.

## What Cleanroom Means

A cleanroom implementation is code that:

1. **Implements the same FUNCTIONALITY** as the original
2. **Produces the same OUTPUTS** for the same inputs
3. **Uses DIFFERENT CODE** to achieve those results
4. **Is written independently** based only on:
   - Published documentation
   - Observed external behavior
   - Interface specifications

## What Cleanroom Does NOT Mean

- Copying original bytes
- Disassembling and transcribing original code
- Producing byte-identical binaries
- Using the same internal algorithms (unless independently derived)

## Verification Requirements

For each cleanroom ROM:

| Check | Pass Criteria |
|-------|--------------|
| MD5 Hash | MUST be DIFFERENT from original |
| Functional Tests | MUST produce same outputs |
| Size | Should match (for compatibility) |
| Interface | MUST match documented entry points |

## Implementation Process

### Step 1: Document the Interface
- Entry points and their expected behavior
- Input/output specifications  
- Side effects (memory, registers)
- Timing requirements (if critical)

### Step 2: Implement Independently
- Write new code based ONLY on documentation
- Do NOT look at disassembly while coding
- Use your own algorithms to achieve the same results
- Make different implementation choices where possible

### Step 3: Verify Functionality
- Test that outputs match for all documented inputs
- Verify register states after calls
- Check memory modifications
- Confirm timing (if critical)

### Step 4: Confirm Non-Identity
- Calculate MD5 of cleanroom ROM
- Compare to original ROM MD5
- **If identical, the implementation has FAILED**
- Re-implement with different approach

## Examples

### CORRECT: Monitor ROM
```
Original MD5:  bc0163ca04c463e06f99fb029ad21b1f
Cleanroom MD5: d4c6dad016151c21fb03679205bbc649
Status: ✓ VALID - Different bytes, same functionality
```

### INCORRECT: Character Generator (DELETED)
```
Original MD5:  9ac0dc8c4d0002eb45b0b84be0bde5ec
Cleanroom MD5: 9ac0dc8c4d0002eb45b0b84be0bde5ec
Status: ✗ INVALID - Identical bytes = copied, not cleanroom
```

## Character Generator Special Case

For the Character Generator ROM, the cleanroom implementation must:
- Create character glyphs that are **visually recognizable** as the intended characters
- Use **DIFFERENT pixel patterns** than the original
- The characters should be readable and functional
- They do NOT need to look identical to the original font

Example: The letter 'A' must be recognizable as 'A', but can use a different font design.

## Disk II ROM Special Case

For the Disk II Controller ROMs:
- P5A must implement disk boot functionality
- The code structure should be DIFFERENT
- It can use different instruction sequences
- It must perform the same I/O operations
- The GCR tables can use different internal organization

## Consequences of Violation

If a cleanroom ROM is byte-identical to the original:
1. **DELETE IT IMMEDIATELY**
2. Document the violation
3. Re-implement from scratch
4. Verify non-identity before committing
