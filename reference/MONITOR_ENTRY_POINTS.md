# Apple II Monitor ROM Entry Points

This document lists the documented entry points for the Apple II Monitor ROM.
These are published interfaces that cleanroom implementations must match.

## Character Output

### COUT ($FDED)
Output character to screen through vector.

**Entry:**
- A = character to output (high bit set: $80-$FF)

**Exit:**
- Character displayed at cursor position
- Cursor advanced

**Action:**
- Jumps through vector at CSWL/CSWH ($36-$37)
- Default vector points to COUT1

---

### COUT1 ($FDF0)
Direct character output (bypasses vector).

**Entry:**
- A = character to output (high bit set)

**Exit:**
- Character displayed
- Cursor position updated
- BASL/BASH updated

**Handles:**
- Printable characters ($A0-$FF)
- Carriage return ($8D)
- Line feed ($8A)
- Backspace ($88)
- Bell ($87)

---

### PRBYTE ($FDDA)
Print byte as two hexadecimal digits.

**Entry:**
- A = byte to print

**Exit:**
- Two hex characters output
- A destroyed

**Algorithm:**
1. Save A (PHA)
2. Shift right 4 times to get high nibble
3. Call PRHEX to print high nibble
4. Restore A (PLA)
5. Fall through to PRHEX for low nibble

---

### PRHEX ($FDE3)
Print low nibble of A as hexadecimal digit.

**Entry:**
- A = value (low 4 bits used)

**Exit:**
- One hex character output ('0'-'9' or 'A'-'F')
- A destroyed

**Algorithm:**
1. AND #$0F to isolate low nibble
2. ORA #$B0 to convert to '0'-'9' range
3. If result >= $BA (would be ':'), add 6 to get 'A'-'F'
4. Output character

---

### CROUT ($FD8E)
Output carriage return.

**Exit:**
- Cursor moved to column 0
- Cursor moved down one line (scrolls if at bottom)

---

## Screen Management

### HOME ($FC58)
Clear screen and home cursor.

**Exit:**
- Cursor at position (0,0)
- Screen filled with spaces

---

### CLREOP ($FC42)
Clear from cursor to end of page.

**Exit:**
- All characters from cursor to bottom-right cleared

---

### CLREOL ($FC9C)
Clear from cursor to end of line.

**Exit:**
- Characters from cursor to right edge cleared

---

### VTAB ($FC22)
Set vertical position.

**Entry:**
- CV ($25) = line number (0-23)

**Exit:**
- Cursor moved to specified line
- BASL/BASH updated

---

### BASCALC ($FBC1)
Calculate text screen base address for a line.

**Entry:**
- A = line number (0-23)

**Exit:**
- BASL ($28) = low byte of screen address
- BASH ($29) = high byte of screen address

**Algorithm:**
Based on the non-contiguous text screen layout:
- Lines 0,8,16 start at $0400,$0428,$0450
- Lines 1,9,17 start at $0480,$04A8,$04D0
- etc.

---

### SCROLL ($FC70)
Scroll text window up one line.

**Exit:**
- All lines moved up
- Bottom line cleared

---

## Video Mode

### SETINV ($FE80)
Set inverse video mode.

**Exit:**
- INVFLG ($32) = $3F

---

### SETNORM ($FE84)
Set normal video mode.

**Exit:**
- INVFLG ($32) = $FF

---

## Keyboard Input

### RDKEY ($FD0C)
Read keyboard (waits for keypress).

**Exit:**
- A = key code with high bit set

**Action:**
1. Wait until $C000 bit 7 is set
2. Read key code
3. Clear keyboard strobe ($C010)
4. Return key in A

---

### GETLN ($FD67)
Get line of input.

**Entry:**
- None (uses prompt from $33)

**Exit:**
- Input in buffer at $0200
- X = length of input

**Handles:**
- Character echo
- Backspace editing
- Carriage return to end input

---

## Timing

### WAIT ($FCA8)
Delay routine.

**Entry:**
- A = delay count

**Timing:**
- Approximately (A × A × 2.5 + A × 13.5) cycles
- At 1 MHz: roughly A × A × 2.5 microseconds

**Algorithm:**
```
    SEC
WAIT2:
    PHA
WAIT3:
    SBC #$01
    BNE WAIT3
    PLA
    SBC #$01
    BNE WAIT2
    RTS
```

---

## Sound

### BELL ($FBDD)
Ring the bell (beep speaker).

**Action:**
- Generates audible beep by toggling speaker
- Uses WAIT for timing

---

## Miscellaneous

### INIT ($FB2F)
Initialize display.

**Exit:**
- Text mode set
- Window set to full screen (40×24)
- INVFLG set to normal

**Sets:**
- $C051 (text mode)
- $C052 (full screen)
- $C054 (page 1)
- WNDLFT = 0, WNDWDTH = 40
- WNDTOP = 0, WNDBTM = 24
- INVFLG = $FF

---

### IORTS ($FF58)
Return slot number from stack.

**Entry:**
- Called via JSR from peripheral card ROM at $Cnxx

**Exit:**
- A = slot number × 16 (e.g., $60 for slot 6)

**Algorithm:**
1. Get return address from stack (points to $Cnxx)
2. Extract slot number from high nibble of low byte
3. Return slot × 16 in A

---

### RESET ($FF59)
System reset entry point.

**Action:**
1. Initialize display (JSR INIT)
2. Set normal video mode
3. Set up I/O vectors
4. Enter monitor

---

## Memory Operations

### MOVE ($FE2C)
Move memory block.

**Entry:**
- A1L/H ($3C-$3D) = source start
- A2L/H ($3E-$3F) = source end
- A4L/H ($42-$43) = destination

**Exit:**
- Memory block copied

---

### VERIFY ($FE36)
Compare memory blocks.

**Entry:**
- A1L/H ($3C-$3D) = block 1 start
- A2L/H ($3E-$3F) = block 1 end
- A4L/H ($42-$43) = block 2 start

**Exit:**
- C = 0 if blocks match
- C = 1 if mismatch found

---

## System Vectors ($FFF8-$FFFF)

| Address | Vector | Description |
|---------|--------|-------------|
| $FFFA | NMI | Non-maskable interrupt |
| $FFFC | RESET | Power-on/reset |
| $FFFE | IRQ/BRK | Interrupt request / break |

These vectors point to addresses within the Monitor ROM.

---

## Zero Page Usage

The Monitor uses these zero page locations:

| Address | Name | Description |
|---------|------|-------------|
| $20 | WNDLFT | Window left edge |
| $21 | WNDWDTH | Window width |
| $22 | WNDTOP | Window top edge |
| $23 | WNDBTM | Window bottom |
| $24 | CH | Cursor horizontal |
| $25 | CV | Cursor vertical |
| $28 | BASL | Screen base low |
| $29 | BASH | Screen base high |
| $32 | INVFLG | Inverse flag |
| $33 | PROMPT | Prompt character |
| $36-$37 | CSWL/H | Character out vector |
| $38-$39 | KSWL/H | Keyboard in vector |

---

## Notes for Cleanroom Implementation

1. **Entry point addresses must match** - Software depends on JSR $FDDA etc.
2. **Zero page usage must match** - Other code reads/writes these locations
3. **Vector behavior must match** - COUT via $0036 vector is required
4. **Timing is approximate** - WAIT doesn't need exact cycle count
5. **Algorithms can differ** - Only inputs and outputs matter

## Sources

- Apple II Reference Manual (Red Book)
- Apple II Technical Reference Manual
