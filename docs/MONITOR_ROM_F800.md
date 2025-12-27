# Apple II Monitor ROM ($F800-$FFFF) Documentation

## Overview

The Apple II Monitor ROM is a 2KB EPROM (2716) that resides at memory addresses $F800-$FFFF. It provides essential system services including:

- Character output routines
- Hexadecimal printing
- Screen management
- Keyboard input
- Memory examination and manipulation
- System initialization

## Memory Map

```
$F800-$FAFF: Monitor utilities, tables, initialization
$FB00-$FBFF: Screen and video routines  
$FC00-$FCFF: Additional screen routines, WAIT
$FD00-$FDFF: Character I/O, hex printing
$FE00-$FEFF: Mode setting, memory operations
$FF00-$FFF7: Monitor command processing
$FFF8-$FFFF: System vectors
```

## System Vectors

| Address | Name    | Description |
|---------|---------|-------------|
| $FFFC   | RESET   | Reset vector - entry point at $FF59 |
| $FFFE   | IRQ/BRK | Interrupt vector - entry point at $FA86 |

## Zero Page Usage

The Monitor uses the following zero page locations:

| Address | Name    | Description |
|---------|---------|-------------|
| $20     | WNDLFT  | Window left edge (0-39) |
| $21     | WNDWDTH | Window width (1-40) |
| $22     | WNDTOP  | Window top edge (0-23) |
| $23     | WNDBTM  | Window bottom (1-24) |
| $24     | CH      | Cursor horizontal position |
| $25     | CV      | Cursor vertical position |
| $28     | BASL    | Base address low (screen line) |
| $29     | BASH    | Base address high |
| $32     | INVFLG  | Inverse flag: $FF=normal, $3F=inverse |
| $33     | PROMPT  | Prompt character (usually $AA '*') |
| $34     | YSAV    | Y register save |
| $35     | YSAV1   | Y register save 2 |
| $36-$37 | CSWL/H  | Character output vector |
| $38-$39 | KSWL/H  | Keyboard input vector |
| $3C-$3D | A1L/H   | Address 1 |
| $3E-$3F | A2L/H   | Address 2 |
| $40-$41 | A3L/H   | Address 3 |
| $42-$43 | A4L/H   | Address 4 |

## Key Entry Points

### Character Output

#### COUT ($FDED)
Output character in A register.

**Entry:**
- A = character to output (high bit should be set: $80-$FF)

**Exit:**
- Character displayed at current cursor position
- Cursor advanced

**Notes:**
- Actually JMP ($0036) - jumps through CSWL/CSWH vector
- Default CSWL points to COUT1 ($FDF0)

#### COUT1 ($FDF0)  
Actual character output routine.

**Entry:**
- A = character (high bit set)

**Exit:**
- Character displayed
- Cursor position updated
- BASL/BASH updated

### Hex Printing

#### PRBYTE ($FDDA)
Print A register as two hexadecimal digits.

**Entry:**
- A = byte to print

**Exit:**
- Two hex characters printed to screen
- Cursor advanced by 2

**Algorithm:**
```
    PHA             ; Save A
    LSR A           ; Shift high nibble to low
    LSR A
    LSR A
    LSR A
    JSR PRHEX       ; Print high nibble
    PLA             ; Restore A
    ; Fall through to PRHEX for low nibble
```

#### PRHEX ($FDE3) / PRHEXZ ($FDE5)
Print low nibble of A as hexadecimal digit.

**Entry:**
- A = byte (only low 4 bits used)

**Exit:**  
- One hex character ('0'-'9' or 'A'-'F') printed

**Algorithm:**
```
PRHEX:
    AND #$0F        ; Mask to low nibble
PRHEXZ:
    ORA #$B0        ; Convert to '0'-'9' + $80
    CMP #$BA        ; Is it > '9'?
    BCC COUT        ; No, print it
    ADC #$06        ; Yes, adjust to 'A'-'F'
    JMP COUT        ; Print character
```

### Screen Management

#### BASCALC ($FBC1)
Calculate screen base address for line number in A.

**Entry:**
- A = line number (0-23)

**Exit:**
- BASL ($28) = low byte of screen address
- BASH ($29) = high byte of screen address

**Screen Address Table:**
The Apple II has a non-linear screen memory layout:
```
Line 0:  $0400    Line 8:  $0428    Line 16: $0450
Line 1:  $0480    Line 9:  $04A8    Line 17: $04D0
Line 2:  $0500    Line 10: $0528    Line 18: $0550
Line 3:  $0580    Line 11: $05A8    Line 19: $05D0
Line 4:  $0600    Line 12: $0628    Line 20: $0650
Line 5:  $0680    Line 13: $06A8    Line 21: $06D0
Line 6:  $0700    Line 14: $0728    Line 22: $0750
Line 7:  $0780    Line 15: $07A8    Line 23: $07D0
```

**Algorithm:**
```
BASCALC:
    PHA
    LSR A           ; Divide by 2
    AND #$03        ; Get bits for $04xx-$07xx
    ORA #$04        ; High byte is $04, $05, $06, or $07
    STA BASH
    PLA
    AND #$18        ; Get bits 3-4
    BCC *+4         ; (carry clear from AND)
    ADC #$7F        ; Add $80 if carry set
    STA BASL
    ASL A           ; x2
    ASL A           ; x4
    ORA BASL        ; Combine
    STA BASL
    RTS
```

#### VTAB ($FC22)  
Set vertical position based on CV.

**Entry:**
- CV ($25) = desired line (0-23)

**Exit:**
- BASL/BASH set to screen address for line

#### HOME ($FC58)
Clear screen and home cursor.

**Entry:**
- None

**Exit:**
- Screen filled with spaces ($A0)
- CH = 0, CV = 0
- Cursor at top-left

### Display Mode

#### SETNORM ($FE84)
Set normal display mode.

**Entry:**
- None

**Exit:**
- INVFLG ($32) = $FF

#### SETINV ($FE80)
Set inverse display mode.

**Entry:**
- None

**Exit:**
- INVFLG ($32) = $3F

### Timing

#### WAIT ($FCA8)
Delay routine.

**Entry:**
- A = delay value (larger = longer delay)

**Exit:**
- Returns after delay
- A, X, Y may be modified

**Timing:**
- Approximately (A * 2.5 + 13.5) * A + 13 cycles
- At 1 MHz, A=$FF gives about 0.1 second delay

**Algorithm:**
```
WAIT:
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

### Initialization

#### INIT ($FB2F)
Initialize video subsystem.

**Entry:**
- None

**Exit:**
- Video mode set to text
- Window variables initialized
- INVFLG set to normal

### Keyboard Input

#### RDKEY ($FD0C)
Read key from keyboard.

**Entry:**
- None

**Exit:**
- A = key value with high bit set

**Notes:**
- Waits for key if none available
- Clears keyboard strobe

#### GETLN ($FD6A)
Get line of input.

**Entry:**
- None

**Exit:**
- Line stored in input buffer at $0200
- X = length of input

## Test Verification Criteria

For a cleanroom implementation to be considered equivalent, it must:

1. **Vector Compatibility:**
   - Reset vector at $FFFC-$FFFD must point to valid initialization code
   - IRQ/BRK vector at $FFFE-$FFFF must point to valid handler

2. **PRHEX Compatibility:**
   - Input $00-$09 → Output '0'-'9' (ASCII $B0-$B9)
   - Input $0A-$0F → Output 'A'-'F' (ASCII $C1-$C6)

3. **PRBYTE Compatibility:**
   - Print two hex digits for any byte value
   - Cursor advances by 2 positions

4. **BASCALC Compatibility:**
   - All 24 lines must produce correct base addresses
   - Must match the Apple II screen memory layout

5. **SETINV/SETNORM Compatibility:**
   - SETINV must set INVFLG to $3F
   - SETNORM must set INVFLG to $FF

6. **WAIT Compatibility:**
   - Must produce consistent timing delays
   - May vary in exact cycle count but proportions must match

## Checksum

Original ROM Checksum (MD5): Calculated at test time

## References

- Apple II Reference Manual (1979)
- Apple II Programmer's Reference Manual
- "Assembly Language Programming for the Apple II" by Randy Hyde
- "What's Where in the Apple" by William Luebbert
