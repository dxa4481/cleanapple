# Applesoft BASIC Reference

This document describes Applesoft BASIC based on published specifications
for cleanroom implementation. This is the same approach Franklin Computer Corp.
used after the 1983 Apple v. Franklin lawsuit.

## Overview

Applesoft BASIC is a floating-point BASIC interpreter for the Apple II+.
It was licensed from Microsoft and is essentially Microsoft BASIC with
Apple II-specific extensions.

- **ROM Size**: 10KB (5 × 2KB ROMs)
- **Address Range**: $D000-$F7FF
- **Type**: Floating-point BASIC interpreter

## Memory Map

| Address | ROM | Description |
|---------|-----|-------------|
| $D000-$D7FF | 341-0011 | Tokenizer, line editor |
| $D800-$DFFF | 341-0012 | Expression evaluator |
| $E000-$E7FF | 341-0013 | Statements (FOR, NEXT, etc.) |
| $E800-$EFFF | 341-0014 | Functions, I/O |
| $F000-$F7FF | 341-0015 | Math routines, strings |

## Entry Points

| Address | Name | Description |
|---------|------|-------------|
| $D000 | BASIC | Cold start |
| $D003 | WARM | Warm start (from Monitor) |
| $D43C | NEWSTT | Execute next statement |
| $D56C | CLEARM | Clear memory |
| $D66A | GOTO | Execute GOTO |
| $D7D2 | CRUNCH | Tokenize a line |
| $D995 | FINDLN | Find line number |
| $DA46 | NEW | NEW command |
| $DA5E | CLR | CLR command |
| $DA7B | RUN | RUN command |
| $DAD5 | SAVE | SAVE command (tape) |
| $DB3A | LOAD | LOAD command (tape) |
| $DD67 | FRMEVL | Evaluate expression |
| $E10C | PRINT | PRINT statement |
| $E636 | INPUT | INPUT statement |
| $E752 | READ | READ statement |
| $E7A0 | DATA | DATA statement |
| $E7B3 | IF | IF statement |
| $E846 | ON | ON statement |
| $E855 | FOR | FOR statement |
| $E8E8 | NEXT | NEXT statement |
| $E9C9 | RETURN | RETURN statement |
| $E9E5 | GOSUB | GOSUB statement |
| $EA24 | POP | POP statement |
| $EB13 | DEF | DEF FN statement |
| $EB7A | FN | FN function |
| $EBB2 | DIM | DIM statement |
| $EC4E | VARPTR | Get variable pointer |
| $EE17 | MATH+ | Floating-point addition |
| $EE8D | MATH- | Floating-point subtraction |
| $EE9E | MATH* | Floating-point multiplication |
| $EF09 | MATH/ | Floating-point division |
| $F09E | SQR | Square root |
| $F0CD | EXP | Exponential |
| $F0F2 | LOG | Natural logarithm |
| $F1E5 | SIN | Sine |
| $F1F5 | COS | Cosine |
| $F200 | TAN | Tangent |
| $F256 | ATN | Arctangent |

## Zero Page Usage

| Address | Name | Description |
|---------|------|-------------|
| $50-$51 | LINNUM | Current line number |
| $52-$53 | TEMPPT | Temporary pointer |
| $55-$56 | LASTPT | Last temporary string |
| $57-$5D | TEMPST | Temporary string stack |
| $5E-$66 | INDEX | Index registers |
| $67-$68 | TXTTAB | Start of program |
| $69-$6A | VARTAB | Start of variables |
| $6B-$6C | ARYTAB | Start of arrays |
| $6D-$6E | STREND | End of arrays |
| $6F-$70 | FRETOP | Top of string space |
| $71-$72 | FRESPC | String temp pointer |
| $73-$74 | MEMSIZ | Top of memory |
| $75-$76 | CURLIN | Current line number |
| $77-$78 | OLDLIN | Previous line |
| $79-$7A | OLDTXT | Previous text pointer |
| $7B-$7C | DATLIN | DATA line number |
| $7D-$7E | DATPTR | DATA pointer |
| $7F-$80 | INPTR | INPUT pointer |
| $81-$82 | VARNAM | Variable name |
| $83-$84 | VARPNT | Variable pointer |
| $85-$86 | FORPNT | FOR pointer |
| $9D | FAC | Floating accumulator exponent |
| $9E-$A1 | FAC+1 | FAC mantissa |
| $A2 | FACSIGN | FAC sign |
| $A5 | ARG | Argument exponent |
| $A6-$A9 | ARG+1 | ARG mantissa |
| $AA | ARGSIGN | ARG sign |
| $AB-$AC | CHRGET | Get next character routine |
| $AD-$B0 | CHRGOT | Current character |
| $B1-$B6 | TXTPTR | Text pointer |
| $B8-$BE | STACK | Evaluation stack |

## Tokens

BASIC programs are stored in tokenized form. Each keyword is replaced
by a single byte token ($80-$FF).

| Token | Keyword | Token | Keyword |
|-------|---------|-------|---------|
| $80 | END | $A0 | TAB( |
| $81 | FOR | $A1 | TO |
| $82 | NEXT | $A2 | FN |
| $83 | DATA | $A3 | SPC( |
| $84 | INPUT | $A4 | THEN |
| $85 | DEL | $A5 | AT |
| $86 | DIM | $A6 | NOT |
| $87 | READ | $A7 | STEP |
| $88 | GR | $A8 | + |
| $89 | TEXT | $A9 | - |
| $8A | PR# | $AA | * |
| $8B | IN# | $AB | / |
| $8C | CALL | $AC | ^ |
| $8D | PLOT | $AD | AND |
| $8E | HLIN | $AE | OR |
| $8F | VLIN | $AF | > |
| $90 | HGR2 | $B0 | = |
| $91 | HGR | $B1 | < |
| $92 | HCOLOR= | $B2 | SGN |
| $93 | HPLOT | $B3 | INT |
| $94 | DRAW | $B4 | ABS |
| $95 | XDRAW | $B5 | USR |
| $96 | HTAB | $B6 | FRE |
| $97 | HOME | $B7 | SCRN( |
| $98 | ROT= | $B8 | PDL |
| $99 | SCALE= | $B9 | POS |
| $9A | SHLOAD | $BA | SQR |
| $9B | TRACE | $BB | RND |
| $9C | NOTRACE | $BC | LOG |
| $9D | NORMAL | $BD | EXP |
| $9E | INVERSE | $BE | COS |
| $9F | FLASH | $BF | SIN |

| Token | Keyword | Token | Keyword |
|-------|---------|-------|---------|
| $C0 | TAN | $D0 | STORE |
| $C1 | ATN | $D1 | RECALL |
| $C2 | PEEK | $D2 | (unused) |
| $C3 | LEN | $D3 | (unused) |
| $C4 | STR$ | $D4 | (unused) |
| $C5 | VAL | ... | ... |
| $C6 | ASC |
| $C7 | CHR$ |
| $C8 | LEFT$ |
| $C9 | RIGHT$ |
| $CA | MID$ |
| $CB | GO | (for GOTO/GOSUB) |

## Floating Point Format

Applesoft uses 5-byte floating-point numbers:

```
Byte 0: Exponent (excess-128 notation)
        $00 = number is zero
        $01-$FF = exponent + 128

Bytes 1-4: Mantissa (normalized, implied leading 1)
        Byte 1: MSB of mantissa (bit 7 = sign: 0=positive, 1=negative)
        Bytes 2-4: Rest of mantissa
```

### Example Values

| Value | Exponent | Mantissa (hex) |
|-------|----------|----------------|
| 0 | $00 | $00 00 00 00 |
| 1 | $81 | $00 00 00 00 |
| 2 | $82 | $00 00 00 00 |
| -1 | $81 | $80 00 00 00 |
| 0.5 | $80 | $00 00 00 00 |
| 10 | $84 | $20 00 00 00 |
| 3.14159 | $82 | $49 0F DA A2 |

### Floating Point Operations

The FAC (Floating Point Accumulator) at $9D-$A2 is used for calculations.
ARG at $A5-$AA holds the second operand.

Operations:
- FADD: FAC = FAC + ARG
- FSUB: FAC = FAC - ARG  
- FMULT: FAC = FAC × ARG
- FDIV: FAC = FAC ÷ ARG

## Program Storage Format

BASIC programs are stored as linked list of lines:

```
For each line:
  Bytes 0-1: Pointer to next line (0 if last line)
  Bytes 2-3: Line number (16-bit)
  Bytes 4+:  Tokenized BASIC text
  Last byte: $00 (end of line marker)
```

## CHRGET Routine

The CHRGET routine at $00B1 is copied from ROM to zero page.
It's the core routine for parsing:

```assembly
CHRGET: INC TXTPTR      ; Increment text pointer
        BNE CHRGOT
        INC TXTPTR+1
CHRGOT: LDA $0000       ; Self-modifying: address = TXTPTR
        CMP #$3A        ; Compare with ':'
        BCS DONE        ; If >= ':', not a digit
        CMP #$20        ; Compare with space
        BEQ CHRGET      ; Skip spaces
        SEC
        SBC #$30        ; Convert digit
        SEC
        SBC #$D0        ; Set carry if digit 0-9
DONE:   RTS
```

## Interpreter Main Loop

```
1. Get next character (CHRGET)
2. If end of line ($00), go to next line
3. If colon ($3A), go to next statement
4. If digit, syntax error (line numbers start statements)
5. Otherwise, look up token in command table
6. Execute command
7. Go to step 1
```

## Error Messages

| Code | Message |
|------|---------|
| 0 | NEXT WITHOUT FOR |
| 16 | SYNTAX ERROR |
| 22 | RETURN WITHOUT GOSUB |
| 42 | OUT OF DATA |
| 53 | ILLEGAL QUANTITY |
| 69 | OVERFLOW |
| 77 | OUT OF MEMORY |
| 90 | UNDEF'D STATEMENT |
| 107 | BAD SUBSCRIPT |
| 120 | REDIM'D ARRAY |
| 133 | DIVISION BY ZERO |
| 163 | TYPE MISMATCH |
| 176 | STRING TOO LONG |
| 191 | FORMULA TOO COMPLEX |
| 224 | UNDEF'D FUNCTION |
| 254 | RE-ENTER |
| 255 | (BREAK) |

## Graphics Extensions

Applesoft includes these Apple II-specific graphics commands:

### Lo-Res Graphics
- `GR` - Switch to lo-res graphics mode
- `COLOR=n` - Set drawing color (0-15)
- `PLOT X,Y` - Plot point
- `HLIN X1,X2 AT Y` - Horizontal line
- `VLIN Y1,Y2 AT X` - Vertical line
- `SCRN(X,Y)` - Read screen color

### Hi-Res Graphics
- `HGR` - Switch to hi-res page 1
- `HGR2` - Switch to hi-res page 2
- `HCOLOR=n` - Set hi-res color (0-7)
- `HPLOT X,Y` - Plot point (0-279, 0-191)
- `HPLOT TO X,Y` - Draw line to point
- `DRAW n AT X,Y` - Draw shape
- `XDRAW n AT X,Y` - XOR draw shape
- `ROT=n` - Set rotation (0-63)
- `SCALE=n` - Set scale factor

## Implementation Notes for Cleanroom

1. **Use Microsoft BASIC documentation** - Applesoft is MS BASIC
2. **Floating point from published algorithms** - IEEE-style methods
3. **Entry points must match** - Software depends on exact addresses
4. **Zero page must match** - Programs directly access these locations
5. **Token values must match** - Saved programs use these tokens
6. **Error codes must match** - Programs may check for specific errors

## Sources

- Applesoft BASIC Programming Reference Manual
- Microsoft BASIC-80 Reference Manual (Applesoft derives from this)
- Apple II Reference Manual
- Inside Applesoft (published documentation)
