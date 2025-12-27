# Programmer's Aid #1 Reference

This document describes the Programmer's Aid #1 ROM (341-0016) based on
published specifications from Apple's documentation.

## Overview

Programmer's Aid #1 is a utility ROM that provides:
- Hi-res graphics routines (HPLOT, HCOLOR, HGR, etc.)
- Memory relocation utilities
- Screen dump to printer
- Extended monitor commands
- Tape storage utilities

ROM Size: 2048 bytes (2716 EPROM)
Address: $D000-$D7FF (or used as utility, called from BASIC)

## Entry Points

### Hi-Res Graphics Routines

| Address | Name | Description |
|---------|------|-------------|
| $D000 | HIRES | Switch to hi-res mode, clear screen |
| $D003 | HGR | Same as HIRES |
| $D006 | HGR2 | Hi-res page 2 |
| $D009 | SETHCOL | Set hi-res color |
| $D00C | HCLR | Clear hi-res screen |
| $D00F | BKGND | Set background color |
| $D012 | HPLOT | Plot point at (X,Y) |
| $D015 | HLIN | Draw line to (X,Y) |
| $D018 | DRAW | Draw shape at (X,Y) |
| $D01B | XDRAW | XOR draw shape |
| $D01E | SHLOAD | Load shape table from tape |
| $D021 | ROT | Set rotation |
| $D024 | SCALE | Set scale factor |
| $D027 | HFIND | Find cursor position |
| $D02A | DRAW1 | Draw with shape pointer |
| $D02D | SETHPAG | Set hi-res page |

### Memory Utilities

| Address | Name | Description |
|---------|------|-------------|
| $D030 | MOVE | Move memory block |
| $D033 | VERIFY | Verify memory against tape |
| $D036 | LIST | List memory as hex dump |
| $D039 | MEMSIZ | Report memory size |

### Printer/Tape Utilities

| Address | Name | Description |
|---------|------|-------------|
| $D03C | TAPEIN | Read from tape |
| $D03F | TAPEOUT | Write to tape |
| $D042 | PRNTAX | Print A and X as hex |
| $D045 | SCROLL | Scroll hi-res screen |
| $D048 | GBYTE | Get byte from tape |

## Detailed Entry Point Specifications

### HIRES / HGR ($D000 / $D003)

Switch to hi-res graphics mode, page 1, mixed mode.

**Entry:**
- None

**Exit:**
- Graphics mode enabled
- Page 1 displayed ($2000-$3FFF)
- Mixed mode (4 lines text at bottom)
- Screen cleared to background color

**Soft Switches Set:**
- $C050 (TXTCLR) - Graphics mode
- $C053 (MIXSET) - Mixed mode
- $C054 (LOWSCR) - Page 1
- $C057 (HIRES) - Hi-res mode

---

### HGR2 ($D006)

Switch to hi-res graphics mode, page 2, full screen.

**Entry:**
- None

**Exit:**
- Graphics mode enabled
- Page 2 displayed ($4000-$5FFF)
- Full screen mode (no text)
- Screen cleared

**Soft Switches Set:**
- $C050, $C052, $C055, $C057

---

### SETHCOL / HCOLOR ($D009)

Set the hi-res plotting color.

**Entry:**
- A = color (0-7)

**Exit:**
- Color stored for subsequent plot operations

**Colors:**
| Value | Color |
|-------|-------|
| 0 | Black |
| 1 | Green |
| 2 | Violet |
| 3 | White |
| 4 | Black |
| 5 | Orange |
| 6 | Blue |
| 7 | White |

---

### HCLR ($D00C)

Clear the hi-res screen to the current background color.

**Entry:**
- None

**Exit:**
- Current hi-res page cleared

---

### HPLOT ($D012)

Plot a point in hi-res graphics.

**Entry:**
- X register = X coordinate low byte (0-255)
- Y register = Y coordinate (0-191)
- A register = X coordinate high byte (0-1)

Full X range is 0-279 (9 bits).

**Exit:**
- Point plotted at (X,Y)
- Cursor position updated

---

### HLIN / HPLOT TO ($D015)

Draw a line from current cursor position to (X,Y).

**Entry:**
- Same as HPLOT: X,Y,A contain destination coordinates

**Exit:**
- Line drawn from current position to (X,Y)
- Cursor updated to new position

**Algorithm:**
Uses Bresenham's line algorithm or equivalent to draw pixels between points.

---

### ROT ($D021)

Set rotation for shape drawing.

**Entry:**
- A = rotation value (0-63)

**Exit:**
- Rotation stored for DRAW/XDRAW

**Rotation Values:**
- 0 = 0°
- 16 = 90°
- 32 = 180°
- 48 = 270°

---

### SCALE ($D024)

Set scale factor for shape drawing.

**Entry:**
- A = scale factor (1-255)

**Exit:**
- Scale stored for DRAW/XDRAW

**Scale Values:**
- 1 = smallest
- Higher = larger shapes

---

### DRAW ($D018)

Draw a shape from the shape table.

**Entry:**
- A = shape number
- Shape table pointer must be set

**Exit:**
- Shape drawn at current cursor position
- Using current rotation and scale

---

### XDRAW ($D01B)

XOR draw a shape (toggles pixels).

**Entry:**
- Same as DRAW

**Exit:**
- Shape XOR'd at cursor position
- Can be used to erase by drawing same shape twice

---

## Hi-Res Screen Memory Layout

### Memory Map

| Page | Address Range | Description |
|------|---------------|-------------|
| 1 | $2000-$3FFF | 8192 bytes, 280×192 pixels |
| 2 | $4000-$5FFF | 8192 bytes, 280×192 pixels |

### Line Addressing

Lines are interleaved in groups of 8. For line Y (0-191):

```
group = Y / 64        (0, 1, or 2)
row = (Y % 64) / 8    (0-7)
offset = Y % 8        (0-7)

base = $2000 + (group * 40) + (row * 128) + (offset * 1024)
```

### Byte Layout

Each byte contains 7 horizontal pixels:
- Bits 0-6: Pixel data (1=on, 0=off)
- Bit 7: Color shift flag (0=violet/green, 1=blue/orange)

40 bytes per line × 7 pixels = 280 horizontal pixels

### Pixel Addressing

To plot point (X, Y):
1. Calculate line base address
2. Byte offset = X / 7
3. Bit position = X % 7
4. Address = base + byte_offset

## Zero Page Usage

Programmer's Aid uses these zero page locations:

| Address | Name | Description |
|---------|------|-------------|
| $E0 | HPAG | Hi-res page ($20 or $40) |
| $E2 | HBASL | Hi-res base address low |
| $E3 | HBASH | Hi-res base address high |
| $E4 | HNDX | Horizontal byte index |
| $E5 | HMASK | Horizontal bit mask |
| $E6 | HCOLOR | Current hi-res color |
| $E7 | HCOUNT | Count for operations |
| $E8-$E9 | SHAPEL/H | Shape table pointer |
| $EA | COLMASK | Color mask |
| $EB | SCALE | Scale factor |
| $EC | ROT | Rotation value |
| $ED | HPOSN | Horizontal position |
| $EE-$EF | DXL/DXH | Delta X for lines |
| $F0-$F1 | DYL/DYH | Delta Y for lines |
| $F2-$F3 | CURLNL/H | Current line address |
| $F4-$F5 | DESTLNL/H | Destination line |

## Implementation Notes for Cleanroom

1. **Entry point addresses are fixed** - Software depends on these exact addresses

2. **Soft switch access is required** - Must toggle $C050-$C057 correctly

3. **Screen memory layout is hardware-defined** - Must use correct interleaving

4. **Color handling is hardware-specific** - Bit 7 determines color palette

5. **Line algorithm can vary** - Bresenham's or any equivalent algorithm

6. **Zero page locations are conventional** - Many programs assume these addresses

## Sources

- Apple II Reference Manual
- Applesoft BASIC Programming Reference Manual
- Apple II Programmer's Aid #1 Installation and Operating Manual
