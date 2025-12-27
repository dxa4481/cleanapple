# Disk II Controller ROM Documentation

## Overview

The Disk II Controller uses two small PROMs:
- **P5A (256 bytes)**: Boot ROM - contains code to read sectors from disk
- **P6A (256 bytes)**: Data table - GCR (Group Coded Recording) translation table

## Memory Map

When installed in slot N (typically slot 6), the ROMs appear at:
- P5A: $CN00-$CNFF (boot code)
- P6A: Used as lookup table, not directly addressed

## P5A Boot ROM

### Purpose

The P5A ROM is executed when:
1. System powers on with disk in drive (Autostart Monitor)
2. User types `PR#6` or `C600G` from Monitor
3. DOS issues a boot command

### Entry Point

**$Cx00** (where x is slot number, typically $C600 for slot 6)

### Algorithm

1. **Initialize translation table** ($C600-$C620)
   - Builds 6-and-2 encoding table at $0356-$03FF
   
2. **Determine slot number** ($C621-$C62E)
   - JSR $FF58 (returns slot×16 in A)
   - Stores slot×16 in $2B for I/O addressing

3. **Turn on drive motor** ($C62F-$C650)
   - Access $C089,X to turn on motor
   - Wait for motor to spin up (~500ms)

4. **Seek track 0** ($C652-$C658)
   - Initialize sector pointer ($26-$27) to $0800
   - Set track/sector targets

5. **Read sector header** ($C65C-$C6A4)
   - Look for D5 AA 96 marker (address field prologue)
   - Read and decode volume, track, sector, checksum
   - Verify checksum

6. **Read sector data** ($C6A6-$C6D3)
   - Look for D5 AA AD marker (data field prologue)
   - Read 342 nibbles into $0300-$03FF and ($26),Y
   - Verify checksum

7. **Decode data** ($C6D5-$C6EF)
   - Convert 6-and-2 encoded data to bytes
   - Store at destination ($0800+)

8. **Continue or boot** ($C6F1-$C6F8)
   - If sector count not reached, read next sector
   - Otherwise, JMP $0801 to boot

### I/O Addresses

The Disk II uses soft switches at $C080-$C08F,X where X = slot×16:

| Address | Read | Write |
|---------|------|-------|
| $C080,X | Phase 0 off | Phase 0 off |
| $C081,X | Phase 0 on | Phase 0 on |
| $C082,X | Phase 1 off | Phase 1 off |
| $C083,X | Phase 1 on | Phase 1 on |
| $C084,X | Phase 2 off | Phase 2 off |
| $C085,X | Phase 2 on | Phase 2 on |
| $C086,X | Phase 3 off | Phase 3 off |
| $C087,X | Phase 3 on | Phase 3 on |
| $C088,X | Motor off | Motor off |
| $C089,X | Motor on | Motor on |
| $C08A,X | Select drive 1 | Select drive 1 |
| $C08B,X | Select drive 2 | Select drive 2 |
| $C08C,X | Read data | Read data |
| $C08D,X | Read write-protect | Check write mode |
| $C08E,X | Shift/Read | Read mode |
| $C08F,X | Load/Write | Write mode |

### Zero Page Usage

| Address | Name | Description |
|---------|------|-------------|
| $26-$27 | DEST | Destination pointer for sector data |
| $2B | SLOT16 | Slot number × 16 |
| $3C | TEMP | Temporary storage |
| $3D | SECTOR | Target sector number |
| $40 | TRACK | Target track number |
| $41 | VOLUME | Target volume number |

## P6A Translation Table ROM

### Purpose

The P6A ROM contains the GCR (Group Coded Recording) translation table.

### Format

The P6A ROM encodes 6-bit values (0-63) into valid disk bytes. Valid disk bytes must:
- Have the high bit set (bit 7 = 1)
- Not have two consecutive zero bits

This "6-and-2" encoding converts 256 bytes into 342 disk bytes.

### Translation Table

The table maps disk nibble values to their 6-bit equivalents:

| Disk Byte | 6-bit Value | Disk Byte | 6-bit Value |
|-----------|-------------|-----------|-------------|
| $96 | $00 | $E5 | $20 |
| $97 | $01 | $E6 | $21 |
| $9A | $02 | $E7 | $22 |
| $9B | $03 | $E9 | $23 |
| ... | ... | ... | ... |

## Disk Format

### Track/Sector Layout

- 35 tracks (0-34)
- 16 sectors per track (DOS 3.3) or 13 sectors (DOS 3.2)
- 256 bytes per sector

### Sector Format (DOS 3.3)

```
Gap 1: Self-sync bytes (FF FF FF...)
Address Field:
  D5 AA 96    - Prologue
  Vol Vol     - Volume (4-and-4 encoded)
  Trk Trk     - Track (4-and-4 encoded)
  Sec Sec     - Sector (4-and-4 encoded)
  Chk Chk     - Checksum (4-and-4 encoded)
  DE AA EB    - Epilogue

Gap 2: Self-sync bytes

Data Field:
  D5 AA AD    - Prologue
  342 bytes   - 6-and-2 encoded data
  Chk         - Checksum
  DE AA EB    - Epilogue
```

### 4-and-4 Encoding

Each byte is split into odd and even bits:
- First byte: bit7, bit5, bit3, bit1 (OR'd with $AA)
- Second byte: bit6, bit4, bit2, bit0 (OR'd with $AA)

### 6-and-2 Encoding

256 bytes are encoded into 342 disk bytes:
1. Bottom 2 bits of first 256 bytes → 86 bytes
2. Top 6 bits of all 256 bytes → 256 bytes
3. Each 6-bit value is translated to a valid disk byte

## Testing

Boot ROM tests should verify:
1. Correct translation table generation
2. Proper drive motor control sequences
3. Sector read operations (with simulated disk data)
4. Checksum verification

## Implementation Notes

- The boot code is relocatable (uses relative addressing)
- JSR $FF58 is a Monitor routine that returns slot×16
- JSR $FCA8 is a Monitor delay routine
- The code reads sector 0 of track 0 into $0800-$08FF
- After boot sector loads, execution continues at $0801
