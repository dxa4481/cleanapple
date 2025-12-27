# Apple Mouse Interface Card Reference

This document describes the Apple Mouse Interface Card firmware based on
published specifications from Apple's Technical Reference manuals.

## Overview

The Apple Mouse Interface Card is a peripheral card that provides:
- Mouse position tracking (X, Y coordinates)
- Button state detection
- Interrupt-driven or polled operation
- ProDOS and Pascal compatible firmware

## Memory Map

The Mouse Card uses standard Apple II peripheral card addressing:

| Address | Description |
|---------|-------------|
| $Cn00-$CnFF | 256-byte slot ROM |
| $C800-$CFFF | Shared 2KB expansion ROM |

Where n = slot number (1-7).

## Firmware Entry Points

The Mouse Card firmware follows the Apple II firmware protocol:

### Standard Slot ROM Locations

| Offset | Name | Description |
|--------|------|-------------|
| $Cn00 | - | Start of code (not an entry point) |
| $Cn05 | - | Pascal 1.1 firmware signature ($38) |
| $Cn07 | - | Pascal 1.1 firmware signature ($18) |
| $Cn0B | - | Pascal 1.1 firmware signature ($01) |
| $Cn0C | - | Entry point offset (for Pascal) |
| $CnFB | - | Firmware ID byte |
| $CnFC | - | Firmware ID byte |
| $CnFD | - | Firmware ID byte |
| $CnFE | - | Firmware status byte |
| $CnFF | - | Firmware ID byte ($20 for mouse) |

### Mouse Firmware Entry Points

Accessed via indirect jump table at $Cn12:

| Entry | Address | Name | Description |
|-------|---------|------|-------------|
| 0 | $Cn12 | SETMOUSE | Initialize/configure mouse |
| 1 | $Cn14 | SERVEMOUSE | Handle mouse interrupt |
| 2 | $Cn16 | READMOUSE | Read mouse position/status |
| 3 | $Cn18 | CLEARMOUSE | Clear mouse data |
| 4 | $Cn1A | POSMOUSE | Position mouse cursor |
| 5 | $Cn1C | CLAMPMOUSE | Set mouse movement bounds |
| 6 | $Cn1E | HOMEMOUSE | Home mouse to clamp origin |
| 7 | $Cn20 | INITMOUSE | Initialize mouse hardware |

### Entry Point Details

#### SETMOUSE ($Cn12)
Configure mouse operating mode.

**Entry:**
- A = mode byte:
  - Bit 0: Enable mouse (1=on, 0=off)
  - Bit 1: Enable VBL interrupt
  - Bit 2: Enable button interrupt
  - Bit 3: Enable movement interrupt
  - Bits 4-7: Reserved (must be 0)

**Exit:**
- Carry clear = success
- Carry set = failure

#### SERVEMOUSE ($Cn14)
Service mouse interrupt (call from interrupt handler).

**Entry:**
- None

**Exit:**
- A = interrupt status
- Carry clear = this card caused interrupt
- Carry set = not this card

#### READMOUSE ($Cn16)
Read current mouse position and button state.

**Entry:**
- None

**Exit:**
- Mouse data in screen holes:
  - $0478+n = X low byte
  - $04F8+n = X high byte
  - $0578+n = Y low byte
  - $05F8+n = Y high byte
  - $0678+n = Reserved
  - $06F8+n = Reserved
  - $0778+n = Button/interrupt status
  - $07F8+n = Mode byte

Where n = slot number.

**Button/Status byte ($0778+n):**
- Bit 7: Button currently down
- Bit 6: Button was down (latched)
- Bit 5: X moved since last read
- Bit 4: Y moved since last read
- Bit 3: Reserved
- Bit 2-0: Reserved

#### CLEARMOUSE ($Cn18)
Clear all mouse data.

**Entry:**
- None

**Exit:**
- All position data zeroed
- Carry clear

#### POSMOUSE ($Cn1A)
Set mouse position to specified coordinates.

**Entry:**
- Mouse position in screen holes (same format as READMOUSE)

**Exit:**
- Position updated
- Carry clear

#### CLAMPMOUSE ($Cn1C)
Set bounds for mouse movement.

**Entry:**
- A = axis (0=X, 1=Y)
- Clamp values in screen holes:
  - $0478+n = Low clamp low byte
  - $04F8+n = Low clamp high byte  
  - $0578+n = High clamp low byte
  - $05F8+n = High clamp high byte

**Exit:**
- Bounds updated
- Carry clear

#### HOMEMOUSE ($Cn1E)
Move mouse to clamp origin.

**Entry:**
- None

**Exit:**
- Position set to low clamp values
- Carry clear

#### INITMOUSE ($Cn20)
Initialize mouse hardware.

**Entry:**
- None

**Exit:**
- Mouse hardware reset
- Mode cleared
- Carry clear

## Screen Holes

The Mouse firmware uses "screen holes" - unused bytes in the text screen
memory that exist due to the interleaved screen layout.

| Address | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 | Slot 6 | Slot 7 |
|---------|--------|--------|--------|--------|--------|--------|--------|
| $0478-$047F | $0479 | $047A | $047B | $047C | $047D | $047E | $047F |
| $04F8-$04FF | $04F9 | $04FA | $04FB | $04FC | $04FD | $04FE | $04FF |
| $0578-$057F | $0579 | $057A | $057B | $057C | $057D | $057E | $057F |
| $05F8-$05FF | $05F9 | $05FA | $05FB | $05FC | $05FD | $05FE | $05FF |
| $0678-$067F | $0679 | $067A | $067B | $067C | $067D | $067E | $067F |
| $06F8-$06FF | $06F9 | $06FA | $06FB | $06FC | $06FD | $06FE | $06FF |
| $0778-$077F | $0779 | $077A | $077B | $077C | $077D | $077E | $077F |
| $07F8-$07FF | $07F9 | $07FA | $07FB | $07FC | $07FD | $07FE | $07FF |

## Hardware Interface

The mouse hardware is accessed through the card's I/O space:

| Address | Read | Write |
|---------|------|-------|
| $C080+n*16 | Read X delta | - |
| $C081+n*16 | Read Y delta | - |
| $C082+n*16 | Read status | - |
| $C083+n*16 | Read interrupt | Clear interrupt |
| $C084+n*16 | - | Set mode |

The hardware provides:
- Quadrature encoder inputs for X and Y movement
- Button input
- Interrupt generation

## Firmware ID Bytes

The Mouse Card is identified by these signature bytes:

| Address | Value | Description |
|---------|-------|-------------|
| $CnFB | $D6 | Mouse firmware ID |
| $CnFC | $00 | Reserved |
| $CnFD | $00 | Reserved |
| $CnFF | $20 | Generic ID (SmartPort compatible) |

## Pascal Protocol

For Pascal 1.1 compatibility:

| Offset | Value | Description |
|--------|-------|-------------|
| $Cn05 | $38 | SEC instruction |
| $Cn07 | $18 | CLC instruction |
| $Cn0B | $01 | Device type (1 = special) |
| $Cn0C | $20 | Entry offset (points to INITMOUSE) |

## ProDOS Protocol

The mouse firmware is SmartPort-compatible and can be accessed
via ProDOS MLI calls, but direct firmware calls are more common
for mouse operations.

## Interrupt Handling

When interrupts are enabled:

1. Mouse generates IRQ on configured events
2. Interrupt handler checks all cards
3. SERVEMOUSE returns carry clear if this card caused interrupt
4. Handler reads mouse data and clears interrupt

## Sample Usage

```assembly
; Initialize mouse in slot 4
    LDX #$40        ; Slot 4 * 16
    JSR $C412       ; SETMOUSE
    LDA #$01        ; Enable mouse, no interrupts
    JSR $C420       ; INITMOUSE

; Read mouse position
    JSR $C416       ; READMOUSE
    LDA $047C       ; X low byte (slot 4)
    LDA $04FC       ; X high byte
    LDA $057C       ; Y low byte
    LDA $05FC       ; Y high byte
    LDA $077C       ; Button/status
```

## Sources

- Apple Mouse Interface Card Technical Reference
- Apple IIe Technical Reference Manual
- ProDOS Technical Reference Manual
