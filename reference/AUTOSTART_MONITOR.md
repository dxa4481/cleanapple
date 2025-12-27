# Apple II+ Autostart Monitor Reference

This document describes the Autostart Monitor ROM (341-0020) used in the Apple II+.
This is for cleanroom implementation based on published specifications.

## Overview

The Autostart Monitor is an enhanced version of the Integer BASIC Monitor that:
1. Automatically boots from disk if a bootable disk is present
2. Provides additional functionality for Applesoft BASIC
3. Maintains backward compatibility with Integer BASIC Monitor entry points

## Autostart Sequence

On power-up or reset:

1. Initialize hardware (same as Integer BASIC Monitor)
2. Check for disk controller in slots (typically slot 6)
3. If disk controller found:
   - Execute boot ROM at $Cn00 (where n = slot number)
   - Boot ROM loads boot sector to $0800 and jumps to $0801
4. If no disk or boot fails:
   - Display "APPLE ][" or similar message
   - Enter monitor prompt

## Slot Detection

The Autostart Monitor scans slots 7 down to 1 looking for:
- Peripheral cards with boot capability
- Disk II controller (identifiable by specific bytes in ROM)

To detect a Disk II:
- Read $CnFC - should contain $20 (JSR opcode) or $00
- Read $CnFE - should contain $00
- Read $CnFF - should contain $00 or specific signature

## Memory Map

Same as Integer BASIC Monitor:

| Address | Description |
|---------|-------------|
| $F800-$FAFF | Utility routines |
| $FB00-$FBFF | Screen routines |
| $FC00-$FCFF | Additional routines, WAIT |
| $FD00-$FDFF | Character I/O |
| $FE00-$FEFF | Mode setting |
| $FF00-$FFFF | Monitor commands, vectors |

## Entry Points

All Integer BASIC Monitor entry points must be maintained:

| Address | Name | Description |
|---------|------|-------------|
| $FB2F | INIT | Initialize display |
| $FBC1 | BASCALC | Calculate screen address |
| $FBDD | BELL | Ring bell |
| $FC58 | HOME | Clear screen |
| $FC70 | SCROLL | Scroll screen |
| $FCA8 | WAIT | Delay routine |
| $FD0C | RDKEY | Read keyboard |
| $FD67 | GETLN | Get line input |
| $FD8E | CROUT | Carriage return |
| $FDDA | PRBYTE | Print hex byte |
| $FDE3 | PRHEX | Print hex nibble |
| $FDED | COUT | Character output |
| $FDF0 | COUT1 | Direct char output |
| $FE80 | SETINV | Set inverse |
| $FE84 | SETNORM | Set normal |
| $FF58 | IORTS | Get slot number |
| $FF59 | - | Reset entry point |

## Additional Entry Points (Autostart specific)

| Address | Name | Description |
|---------|------|-------------|
| $FA62 | - | Applesoft cold start |
| $FA81 | - | Applesoft relocate |
| $FAA6 | - | Scan for peripheral |
| $FAD7 | REGDSP | Display registers |
| $FB1E | PREAD | Read paddle |
| $FB39 | SETTXT | Set text mode |
| $FB40 | SETGR | Set graphics mode |
| $FB4B | - | Print "APPLE ][" |

## Power-Up Byte ($03F4)

The power-up byte at $03F4 is used to detect warm vs cold start:
- If $03F4 contains $A5 (EOR of $5A), it's a warm start
- Otherwise, it's a cold start

On cold start:
1. Clear memory check
2. Initialize system
3. Scan for boot device
4. Attempt boot or enter monitor

On warm start:
1. Check if $03F2-$03F3 contains valid address
2. If valid, jump there
3. Otherwise, treat as cold start

## Reset Handling

Reset vector ($FFFC-$FFFD) points to reset handler:

1. Check power-up byte
2. If warm start and valid soft entry, use it
3. Otherwise, perform cold start sequence

## Applesoft Support

The Autostart Monitor includes hooks for Applesoft BASIC:

- Vector at $03F5-$03F7 for ampersand (&) command
- Vector at $03F8-$03FA for Ctrl-Y
- Support for floating point routines

## Differences from Integer BASIC Monitor

1. **Autostart**: Automatically boots from disk
2. **Power-up detection**: Uses $03F4 to detect warm/cold start
3. **Additional routines**: SETTXT, SETGR, PREAD
4. **Applesoft hooks**: Vectors for BASIC extensions
5. **Boot scan**: Checks slots for bootable devices

## Cleanroom Implementation Notes

For cleanroom implementation:

1. **Maintain entry points** - All documented addresses must work
2. **Autostart is optional** - Can implement without auto-boot
3. **Zero page must match** - Same locations as Integer BASIC Monitor
4. **Vectors must work** - CSWL/KSWL vectors required
5. **Screen memory same** - Same text screen layout

## Boot Sequence Pseudocode

```
RESET:
    Initialize stack pointer
    Initialize display (JSR INIT)
    
    ; Check for warm start
    LDA $03F4
    EOR #$A5
    BNE cold_start
    
    ; Warm start - check soft entry
    LDA $03F2
    ORA $03F3
    BEQ cold_start
    JMP ($03F2)
    
cold_start:
    ; Clear zero page, set up vectors
    ...
    
    ; Scan for boot device
    LDX #$70        ; Start at slot 7
scan_loop:
    ; Check if valid boot ROM
    LDA $CnFF       ; Read signature
    ...
    ; If found, boot from it
    JMP $Cn00
    
    DEX             ; Next slot
    DEX
    DEX
    DEX
    DEX
    DEX
    DEX
    DEX
    DEX
    DEX
    DEX
    DEX
    DEX
    DEX
    DEX
    DEX             ; X = X - 16
    BPL scan_loop
    
    ; No boot device - enter monitor
    JMP MON
```

## Sources

- Apple II+ Reference Manual
- Apple II Technical Reference Manual
- Applesoft BASIC Programming Reference Manual
