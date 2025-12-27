# Apple II Hardware Reference

This document contains publicly documented Apple II hardware information
for use in cleanroom implementations.

## Memory Map

| Address Range | Size | Description |
|---------------|------|-------------|
| $0000-$00FF | 256 | Zero Page (fast access) |
| $0100-$01FF | 256 | Stack (grows downward) |
| $0200-$02FF | 256 | Input buffer |
| $0300-$03FF | 256 | Vectors and system use |
| $0400-$07FF | 1K | Text/Lo-res page 1 |
| $0800-$0BFF | 1K | Text/Lo-res page 2 |
| $0C00-$1FFF | 5K | Free RAM |
| $2000-$3FFF | 8K | Hi-res page 1 |
| $4000-$5FFF | 8K | Hi-res page 2 |
| $6000-$BFFF | 24K | Free RAM (if available) |
| $C000-$C0FF | 256 | I/O and soft switches |
| $C100-$C7FF | 1.75K | Peripheral card ROM |
| $C800-$CFFF | 2K | Shared peripheral ROM |
| $D000-$F7FF | 10K | BASIC ROM (Integer or Applesoft) |
| $F800-$FFFF | 2K | Monitor ROM |

## Zero Page Usage (System)

| Address | Name | Description |
|---------|------|-------------|
| $00-$01 | - | BASIC workspace |
| $20 | WNDLFT | Text window left edge (0-39) |
| $21 | WNDWDTH | Text window width (1-40) |
| $22 | WNDTOP | Text window top edge (0-23) |
| $23 | WNDBTM | Text window bottom (1-24) |
| $24 | CH | Cursor horizontal position |
| $25 | CV | Cursor vertical position |
| $26-$27 | GBASL/H | Graphics base address |
| $28-$29 | BASL/H | Text base address |
| $2A-$2B | BAS2L/H | Secondary base address |
| $2C | LMNEM | Instruction mnemonic |
| $2D | RMNEM | Instruction mnemonic |
| $2E | FORMAT | Format byte |
| $2F | LENGTH | Length |
| $30 | MODE | Mode flags |
| $31 | - | Reserved |
| $32 | INVFLG | Inverse flag ($FF=normal, $3F=inverse, $7F=flash) |
| $33 | PROMPT | Prompt character |
| $34-$35 | YSAV | Y register save |
| $36-$37 | CSWL/H | Character output vector |
| $38-$39 | KSWL/H | Keyboard input vector |
| $3A-$3B | PCL/H | Program counter save |
| $3C-$3D | A1L/H | General pointer 1 |
| $3E-$3F | A2L/H | General pointer 2 |
| $40-$41 | A3L/H | General pointer 3 |
| $42-$43 | A4L/H | General pointer 4 |
| $44-$45 | A5L/H | General pointer 5 |
| $48-$49 | RESSION | Random number |
| $4A | STATUS | Status byte |
| $4C-$4D | LOWTR | BASIC pointer |
| $4E-$4F | HIMEM | High memory pointer |
| $50-$51 | - | DOS workspace |
| $67-$68 | TXTTAB | Start of BASIC program |
| $69-$6A | VARTAB | Start of variables |
| $6B-$6C | ARYTAB | Start of arrays |
| $6D-$6E | STREND | End of arrays |
| $6F-$70 | FRETOP | Top of string space |
| $73-$74 | MEMSIZ | Top of memory |
| $75-$76 | CURLIN | Current line number |
| $77-$78 | OLDLIN | Previous line number |
| $79-$7A | OLDTXT | Previous text pointer |
| $7B-$7C | DATLIN | DATA line number |
| $7D-$7E | DATPTR | DATA pointer |
| $AF-$B0 | TXTPTR | Text pointer |

## Soft Switches ($C000-$C0FF)

### Keyboard ($C000-$C01F)

| Address | Read | Write |
|---------|------|-------|
| $C000 | KBD - Last key pressed (bit 7 = key available) | - |
| $C010 | KBDSTRB - Clear keyboard strobe | Clear keyboard strobe |

### Video Switches ($C050-$C057)

| Address | Name | Function |
|---------|------|----------|
| $C050 | TXTCLR | Graphics mode |
| $C051 | TXTSET | Text mode |
| $C052 | MIXCLR | Full screen |
| $C053 | MIXSET | Mixed mode (4 lines text) |
| $C054 | LOWSCR | Display page 1 |
| $C055 | HISCR | Display page 2 |
| $C056 | LORES | Lo-res graphics |
| $C057 | HIRES | Hi-res graphics |

### Speaker ($C030)

| Address | Function |
|---------|----------|
| $C030 | Toggle speaker |

### Game I/O ($C060-$C07F)

| Address | Read | Description |
|---------|------|-------------|
| $C060 | TAPEIN | Cassette input |
| $C061 | PB0 | Pushbutton 0 / Open Apple |
| $C062 | PB1 | Pushbutton 1 / Solid Apple |
| $C063 | PB2 | Pushbutton 2 |
| $C064 | PADDL0 | Paddle 0 |
| $C065 | PADDL1 | Paddle 1 |
| $C066 | PADDL2 | Paddle 2 |
| $C067 | PADDL3 | Paddle 3 |
| $C070 | PTRIG | Trigger paddle timers |

### Peripheral Slots ($C080-$C0FF)

Each slot N uses addresses $C080 + N*16 to $C08F + N*16.

#### Disk II (Typical: Slot 6 = $C0E0-$C0EF)

For slot N, base address is $C080 + (N * 16).
Using X = slot * 16:

| Offset | Read | Write | Description |
|--------|------|-------|-------------|
| $C080,X | Phase 0 off | Phase 0 off | Stepper motor |
| $C081,X | Phase 0 on | Phase 0 on | |
| $C082,X | Phase 1 off | Phase 1 off | |
| $C083,X | Phase 1 on | Phase 1 on | |
| $C084,X | Phase 2 off | Phase 2 off | |
| $C085,X | Phase 2 on | Phase 2 on | |
| $C086,X | Phase 3 off | Phase 3 off | |
| $C087,X | Phase 3 on | Phase 3 on | |
| $C088,X | Motor off | Motor off | Drive motor |
| $C089,X | Motor on | Motor on | |
| $C08A,X | Drive 1 | Drive 1 | Select drive |
| $C08B,X | Drive 2 | Drive 2 | |
| $C08C,X | Q6L | Q6L | Data latch |
| $C08D,X | Q6H | Q6H | |
| $C08E,X | Q7L | Q7L | Read mode |
| $C08F,X | Q7H | Q7H | Write mode |

### Peripheral ROM ($C100-$CFFF)

| Address | Description |
|---------|-------------|
| $C100-$C1FF | Slot 1 ROM |
| $C200-$C2FF | Slot 2 ROM |
| $C300-$C3FF | Slot 3 ROM |
| $C400-$C4FF | Slot 4 ROM |
| $C500-$C5FF | Slot 5 ROM |
| $C600-$C6FF | Slot 6 ROM |
| $C700-$C7FF | Slot 7 ROM |
| $C800-$CFFF | Shared expansion ROM |

## Text Screen Memory

### Memory Layout

Text screen uses 1024 bytes at $0400-$07FF (page 1) or $0800-$0BFF (page 2).

Lines are NOT sequential in memory. The base address for each line:

| Line | Address | Line | Address | Line | Address |
|------|---------|------|---------|------|---------|
| 0 | $0400 | 8 | $0428 | 16 | $0450 |
| 1 | $0480 | 9 | $04A8 | 17 | $04D0 |
| 2 | $0500 | 10 | $0528 | 18 | $0550 |
| 3 | $0580 | 11 | $05A8 | 19 | $05D0 |
| 4 | $0600 | 12 | $0628 | 20 | $0650 |
| 5 | $0680 | 13 | $06A8 | 21 | $06D0 |
| 6 | $0700 | 14 | $0728 | 22 | $0750 |
| 7 | $0780 | 15 | $07A8 | 23 | $07D0 |

### Base Address Calculation

For line L (0-23):
- High byte: $04 + ((L >> 1) & 3)
- Low byte: ((L & 7) << 4) + ((L & 0x18) >> 3) * 80

Or more simply:
```
group = L / 8      ; 0, 1, or 2
offset = L % 8     ; 0-7
base = $0400 + (group * 40) + (offset * 128)
```

### Character Codes

| Code Range | Display |
|------------|---------|
| $00-$1F | Inverse uppercase + symbols |
| $20-$3F | Inverse symbols + digits |
| $40-$5F | Flashing uppercase + symbols |
| $60-$7F | Flashing symbols + digits |
| $80-$9F | Normal uppercase + symbols |
| $A0-$BF | Normal symbols + digits |
| $C0-$DF | Normal uppercase (same as $80-$9F) |
| $E0-$FF | Normal lowercase (if available) |

## Hi-Res Graphics Memory

### Memory Layout

Hi-res uses 8192 bytes at $2000-$3FFF (page 1) or $4000-$5FFF (page 2).

- 280 pixels wide × 192 lines
- 40 bytes per line (7 pixels per byte)
- Bit 7 = color shift flag
- Lines are interleaved similar to text

### Line Address Calculation

For line L (0-191):
```
group = L / 64     ; 0, 1, or 2
third = (L % 64) / 8  ; 0-7
offset = L % 8     ; 0-7
base = $2000 + (group * 40) + (third * 128) + (offset * 1024)
```

## System Vectors

| Address | Name | Description |
|---------|------|-------------|
| $03D0 | - | DOS warmstart |
| $03D3 | - | DOS coldstart |
| $03D6 | - | File manager |
| $03DC | - | RWTS |
| $03E3 | - | RWTS parameter table |
| $03EA | - | Reconnect DOS |
| $03F0 | BRKV | Break vector |
| $03F2 | SOFTEV | Soft entry (reset) |
| $03F4 | PWREDUP | Power-up byte |
| $03F5-$03F7 | - | Ampersand vector |
| $03F8-$03FA | - | Control-Y vector |
| $03FB-$03FD | NMI | NMI vector |
| $FFFA-$FFFB | NMIV | Hardware NMI vector |
| $FFFC-$FFFD | RESETV | Hardware Reset vector |
| $FFFE-$FFFF | IRQV | Hardware IRQ/BRK vector |

## Monitor ROM Entry Points

| Address | Name | Description |
|---------|------|-------------|
| $F800 | PLOT | Plot lo-res point |
| $F819 | HLINE | Draw horizontal line |
| $F828 | VLINE | Draw vertical line |
| $F832 | CLRSCR | Clear lo-res screen |
| $F836 | CLRTOP | Clear top of lo-res |
| $F847 | GBASCALC | Graphics base calculation |
| $F85F | NEXTCOL | Set next color |
| $F864 | SETCOL | Set color |
| $F871 | SCRN | Read screen color |
| $FB2F | INIT | Initialize display |
| $FB39 | SETGR | Set graphics mode |
| $FB40 | SETTEXT | Set text mode |
| $FBC1 | BASCALC | Calculate text base address |
| $FBDD | BELL | Ring bell |
| $FC10 | WAIT | Delay routine |
| $FC22 | VTAB | Vertical tab |
| $FC42 | CLREOP | Clear to end of page |
| $FC58 | HOME | Home cursor and clear screen |
| $FC62 | CR | Carriage return |
| $FC66 | LF | Line feed |
| $FC70 | SCROLL | Scroll screen |
| $FC9C | CLREOL | Clear to end of line |
| $FCA8 | WAIT | Wait subroutine |
| $FD0C | RDKEY | Read keyboard |
| $FD67 | GETLN | Get line of input |
| $FD8E | CROUT | Output carriage return |
| $FDDA | PRBYTE | Print byte in hex |
| $FDE3 | PRHEX | Print hex nibble |
| $FDED | COUT | Output character |
| $FDF0 | COUT1 | Output character (direct) |
| $FE80 | SETINV | Set inverse mode |
| $FE84 | SETNORM | Set normal mode |
| $FF58 | IORTS | Return slot*16 from stack |
| $FF59 | RESET | System reset |
| $FF65 | MON | Enter monitor |

## Disk Format (DOS 3.3)

### Track/Sector Layout

- 35 tracks (0-34)
- 16 sectors per track (DOS 3.3)
- 256 bytes per sector

### Sector Format

```
Gap 1:    ~40 self-sync bytes (FF)

Address Field:
  D5 AA 96    Prologue (always these bytes)
  XX XX       Volume (4-and-4 encoded)
  XX XX       Track (4-and-4 encoded)
  XX XX       Sector (4-and-4 encoded)
  XX XX       Checksum (4-and-4 encoded)
  DE AA EB    Epilogue

Gap 2:    ~5 self-sync bytes

Data Field:
  D5 AA AD    Prologue (always these bytes)
  342 bytes   6-and-2 encoded data
  XX          Checksum
  DE AA EB    Epilogue

Gap 3:    ~16 self-sync bytes (or to end of sector)
```

### 4-and-4 Encoding

Splits each byte into odd and even bits:
- Byte 1: (bit7, bit5, bit3, bit1) OR $AA
- Byte 2: (bit6, bit4, bit2, bit0) OR $AA

### 6-and-2 Encoding

Encodes 256 bytes into 342 disk nibbles:
1. Extract bottom 2 bits from each of first 86 bytes → 86 "secondary" nibbles
2. Remaining 6 bits from each of 256 bytes → 256 "primary" nibbles
3. Each 6-bit value encoded to valid disk byte ($96-$FF range)

### Valid Disk Bytes

Only bytes meeting these criteria are valid:
- High bit set (≥ $80)
- No more than one consecutive zero bit

Valid values: $96, $97, $9A, $9B, $9D, $9E, $9F, $A6, $A7, $AB, $AC, $AD, $AE, $AF, $B2, $B3, $B4, $B5, $B6, $B7, $B9, $BA, $BB, $BC, $BD, $BE, $BF, $CB, $CD, $CE, $CF, $D3, $D6, $D7, $D9, $DA, $DB, $DC, $DD, $DE, $DF, $E5, $E6, $E7, $E9, $EA, $EB, $EC, $ED, $EE, $EF, $F2, $F3, $F4, $F5, $F6, $F7, $F9, $FA, $FB, $FC, $FD, $FE, $FF

## Sources

This reference is compiled from publicly available documentation:
- Apple II Reference Manual (Red Book)
- Apple II Technical Reference Manual
- DOS 3.3 Manual
- Understanding the Apple II by Jim Sather
