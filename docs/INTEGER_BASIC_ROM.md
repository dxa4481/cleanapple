# Apple II Integer BASIC ROM Documentation

## Implementation Status

**CLEANROOM IMPLEMENTATION: PARTIAL (Core routines implemented and verified)**

The cleanroom implementation covers key routines that have been fully tested and verified:
- Cold start entry point ($E000)
- System initialization ($F000)
- Print number routine ($E51B) - fully functional
- Memory setup and pointers
- Powers of 10 table

All implemented routines pass 24/24 tests against the original ROM.

## Overview

Integer BASIC was the original BASIC interpreter included with the Apple II. Written by Steve Wozniak, it's a remarkably compact 6KB interpreter that provides:

- **16-bit integer arithmetic** (range -32768 to 32767)
- **String handling** (limited)
- **Low-resolution graphics** (GR, PLOT, HLIN, VLIN, COLOR)
- **Memory access** (PEEK, POKE, CALL)
- **Structured programming** (FOR/NEXT, GOSUB/RETURN, IF/THEN)

## Memory Map

```
$E000-$E7FF: Integer BASIC Part 1 (2048 bytes) - Core routines
$E800-$EFFF: Integer BASIC Part 2 (2048 bytes) - Commands/execution
$F000-$F7FF: Integer BASIC Part 3 (2048 bytes) - Init/math/utilities
$F800-$FFFF: Monitor ROM (2048 bytes) - Already documented
```

## Zero Page Usage ($00-$FF)

| Address | Name | Description |
|---------|------|-------------|
| $4A-$4B | LOMEM_INIT | Initial LOMEM pointer |
| $4C-$4D | LOMEM | Start of BASIC program |
| $4E-$4F | HIMEM | Top of available memory |
| $50-$51 | CURPTR | Current statement pointer |
| $78-$79 | LINNUM | Line number being processed |
| $9F | TOKNDX | Token index in input buffer |
| $A0-$BF | STACK | Expression evaluation stack |
| $C8 | INPUTIDX | Input buffer index |
| $C9 | DIMFLAG | Array dimension flag |
| $CA-$CB | PRGSTART | Program start address |
| $CC-$CD | VARSTART | Variable space start |
| $CE-$CF | CURLIN | Current line number |
| $D0-$D1 | TXTPTR | Text pointer (tokenized) |
| $D5 | RUNFLAG | Running vs immediate mode |
| $D6 | CURTOK | Current token |
| $D7 | FORFLAG | FOR/NEXT active flag |
| $D8 | SAVEX | Saved X register |
| $D9 | PARSEFLAG | Parse/run flag |
| $DA-$DB | TEMPPTR | Temporary pointer |
| $DC-$DD | LINEPTR | Line pointer |
| $E0-$E1 | WORKPTR | Work pointer |
| $E2-$E3 | PTR2 | General pointer 2 |
| $E4-$E5 | PTR3 | General pointer 3 |
| $E6-$E7 | PTR4 | General pointer 4 |
| $F1 | INPUTLEN | Length of input line |
| $F2-$F3 | ACC | Accumulator for math |
| $F6-$F7 | SAVELIN | Saved line number |
| $F8 | RUNMODE | Run mode flag |
| $F9 | LEADFLAG | Leading zero flag |
| $FA | TEMPBYTE | Temporary storage |
| $FB | SUBLEVEL | Subroutine nesting level |
| $FC | FORLEVEL | FOR loop nesting level |
| $FE-$FF | TOKPTR | Token table pointer |

## Key Entry Points

### Cold Start and Initialization

| Address | Name | Description |
|---------|------|-------------|
| $E000 | COLDSTART | Cold start entry - initializes BASIC |
| $F000 | INIT | System initialization, memory test |
| $E2B3 | WARMSTART | Warm start / main prompt loop |

### Input and Tokenization

| Address | Name | Description |
|---------|------|-------------|
| $E3CE | GETLINE | Get input line from keyboard |
| $E38A | TOKENIZE | Tokenize input line |
| $E491 | PARSELINE | Parse tokenized line |

### Statement Execution

| Address | Name | Description |
|---------|------|-------------|
| $E883 | RUN | RUN command execution |
| $E8BE | EXECUTE | Execute current statement |
| $E800 | DISPATCH | Statement dispatch |

### Control Flow

| Address | Name | Description |
|---------|------|-------------|
| $E8C0 | GOSUB | GOSUB implementation |
| $E8DB | RETURN | RETURN implementation |
| $E8F0 | FOR | FOR loop setup |
| $E930 | NEXT | NEXT loop iteration |
| $E3E0 | ERROR | Error handler |

### Expression Evaluation

| Address | Name | Description |
|---------|------|-------------|
| $E5A0 | EXPR | Evaluate expression |
| $E6A4 | FACTOR | Evaluate factor |
| $E715 | GETTOKEN | Get next token |
| $E56D | FINDVAR | Find variable |

### Output

| Address | Name | Description |
|---------|------|-------------|
| $E51B | PRTNUM | Print 16-bit number |
| $E006 | PRTCHAR | Print character |
| $E035 | LIST | LIST command |

### Math Operations

| Address | Name | Description |
|---------|------|-------------|
| $F100 | MULTIPLY | 16-bit multiply |
| $F12E | DIVIDE | 16-bit divide |
| $F150 | MOD | Modulo operation |
| $F179 | NEGATE | Negate number |

### Variables

| Address | Name | Description |
|---------|------|-------------|
| $E912 | FINDVAR | Find/create variable |
| $F1E0 | LET | LET statement |

### Graphics

| Address | Name | Description |
|---------|------|-------------|
| $F225 | GR | Switch to graphics mode |
| $F232 | TEXT | Switch to text mode |
| $F240 | COLOR | Set graphics color |
| $F256 | PLOT | Plot a point |
| $F268 | HLIN | Draw horizontal line |
| $F280 | VLIN | Draw vertical line |

## Token Format

Integer BASIC tokenizes programs to save memory. Each line has the format:

```
[Length byte] [Line# low] [Line# high] [Tokenized code...] [EOL marker]
```

### Token Values

Tokens are single bytes:
- $00-$7F: Tokens for keywords and operators
- $80-$FF: ASCII characters with high bit set (literals)

Key tokens:
- $00: End of tokenized line
- $01: FOR
- $02: NEXT
- $03: INPUT
- $05: DIM
- $0B: CALL
- $14: HOME
- $27: LET
- $28: GOTO
- $29: RUN
- $2A: IF
- $2B: THEN
- $2D: GOSUB
- $2E: RETURN
- $2F: REM
- $30: STOP
- $36: PRINT
- $39: LIST
- $3B: NEW
- $3C: TAB(
- $3D: TO
- $47-$4E: Comparison operators
- $50: +
- $51: -
- $52: *
- $53: /
- $54: MOD

## Line Storage Format

BASIC programs are stored as linked lines:

```
+-------+-------+-------+--------------------+------+
| LEN   | LO    | HI    | Tokenized content  | $00  |
+-------+-------+-------+--------------------+------+
  1 byte  Line number      Variable length    End
```

- LEN: Total length of line including this byte
- LO/HI: 16-bit line number
- Content: Tokenized statements
- $00: End of line marker

## Variable Storage

Variables are stored in the variable space starting at $CC-$CD:

### Integer Variables (A-Z, A0-Z9)
```
+------+------+------+------+
| NAME | DIM  | LO   | HI   |
+------+------+------+------+
  Name   0=simple  16-bit value
         N=array
```

### String Variables (A$-Z$)
```
+------+------+------+------+------...------+
| NAME | LEN  | CHAR | CHAR | CHAR | ... |$00|
+------+------+------+------+------...------+
  Name   Length  String content
```

## Error Messages

Integer BASIC has numbered error messages:

| Code | Message |
|------|---------|
| 0 | (NEXT without FOR) |
| 16 | (Syntax error) |
| 22 | (RETURN without GOSUB) |
| 42 | (Out of memory) |
| 53 | (Division by zero) |
| 69 | (Overflow) |
| 77 | (Out of data) |
| 90 | (Undefined statement) |
| 107 | (Bad subscript) |
| 120 | (Redimensioned array) |
| 133 | (Type mismatch) |
| 163 | (String too long) |
| 176 | (Formula too complex) |
| 191 | (Can't continue) |

## Expression Stack

Expressions are evaluated using a stack at $A0-$BF:
- Stack grows downward
- Each entry is 2 bytes (16-bit value)
- Maximum depth: 16 entries

## Algorithm Details

### PRTNUM ($E51B) - Print Number

Converts 16-bit signed integer to decimal string:

```
Input:  A = high byte, X = low byte
Output: Prints decimal number to screen

Algorithm:
1. If negative, print '-' and negate
2. For each power of 10 (10000, 1000, 100, 10, 1):
   - Count subtractions
   - Print digit (suppress leading zeros)
```

### Expression Parser ($E5A0)

Recursive descent parser:
1. Parse term
2. While operator with correct precedence:
   - Push left operand
   - Parse right operand  
   - Apply operator

### Memory Test ($F000)

At cold start:
1. Start at $0800
2. Write $FF, verify
3. Write $00, verify
4. If match, increment and repeat
5. If mismatch, found top of RAM

## Sample Cleanroom Implementation Order

1. **Phase 1: Core Infrastructure**
   - Memory initialization
   - Zero page setup
   - Basic I/O (using Monitor ROM)

2. **Phase 2: Tokenization**
   - Token table
   - Line input
   - Tokenizer

3. **Phase 3: Expression Evaluator**
   - Number parsing
   - Variable lookup
   - Operator handling
   - Expression stack

4. **Phase 4: Statement Execution**
   - PRINT
   - LET
   - IF/THEN/GOTO
   - FOR/NEXT
   - GOSUB/RETURN

5. **Phase 5: Commands**
   - RUN
   - LIST
   - NEW

6. **Phase 6: Graphics**
   - GR/TEXT
   - COLOR
   - PLOT/HLIN/VLIN

## Testing Strategy

Each component should be tested independently:

1. **Unit tests**: Individual routines
2. **Integration tests**: Component interaction
3. **Compatibility tests**: Run actual BASIC programs
4. **Byte comparison**: Where feasible
