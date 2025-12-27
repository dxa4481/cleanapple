# MOS 6502 Instruction Set Reference

This is a reference for the MOS Technology 6502 microprocessor used in the Apple II.
This information is from published 6502 documentation, not from analyzing any ROM.

## Registers

| Register | Size | Description |
|----------|------|-------------|
| A | 8-bit | Accumulator - main arithmetic register |
| X | 8-bit | Index register X |
| Y | 8-bit | Index register Y |
| SP | 8-bit | Stack pointer (stack at $0100-$01FF) |
| PC | 16-bit | Program counter |
| P | 8-bit | Processor status (flags) |

## Status Flags (P Register)

```
Bit 7 6 5 4 3 2 1 0
    N V - B D I Z C
```

| Flag | Bit | Name | Description |
|------|-----|------|-------------|
| N | 7 | Negative | Set if result bit 7 is set |
| V | 6 | Overflow | Set on signed arithmetic overflow |
| - | 5 | Unused | Always 1 |
| B | 4 | Break | Set by BRK instruction |
| D | 3 | Decimal | BCD mode for ADC/SBC |
| I | 2 | Interrupt | IRQ disable when set |
| Z | 1 | Zero | Set if result is zero |
| C | 0 | Carry | Carry/borrow flag |

## Addressing Modes

| Mode | Syntax | Example | Description |
|------|--------|---------|-------------|
| Implied | - | `CLC` | No operand |
| Accumulator | A | `ASL A` | Operates on A register |
| Immediate | #$nn | `LDA #$42` | 8-bit constant |
| Zero Page | $nn | `LDA $42` | Address $00nn |
| Zero Page,X | $nn,X | `LDA $42,X` | Address $00nn + X |
| Zero Page,Y | $nn,Y | `LDX $42,Y` | Address $00nn + Y |
| Absolute | $nnnn | `LDA $1234` | 16-bit address |
| Absolute,X | $nnnn,X | `LDA $1234,X` | Address + X |
| Absolute,Y | $nnnn,Y | `LDA $1234,Y` | Address + Y |
| Indirect | ($nnnn) | `JMP ($1234)` | Pointer (JMP only) |
| (Indirect,X) | ($nn,X) | `LDA ($42,X)` | ZP pointer + X |
| (Indirect),Y | ($nn),Y | `LDA ($42),Y` | ZP pointer, then + Y |
| Relative | $nn | `BEQ $nn` | PC + signed offset |

## Instruction Set by Category

### Load/Store Operations

| Opcode | Instruction | Addressing Modes | Flags | Cycles |
|--------|-------------|------------------|-------|--------|
| LDA | Load Accumulator | imm,zp,zpx,abs,abx,aby,idx,idy | N,Z | 2-6 |
| LDX | Load X Register | imm,zp,zpy,abs,aby | N,Z | 2-4 |
| LDY | Load Y Register | imm,zp,zpx,abs,abx | N,Z | 2-4 |
| STA | Store Accumulator | zp,zpx,abs,abx,aby,idx,idy | - | 3-6 |
| STX | Store X Register | zp,zpy,abs | - | 3-4 |
| STY | Store Y Register | zp,zpx,abs | - | 3-4 |

### Register Transfers

| Opcode | Instruction | Description | Flags | Cycles |
|--------|-------------|-------------|-------|--------|
| TAX | Transfer A to X | X = A | N,Z | 2 |
| TAY | Transfer A to Y | Y = A | N,Z | 2 |
| TXA | Transfer X to A | A = X | N,Z | 2 |
| TYA | Transfer Y to A | A = Y | N,Z | 2 |
| TSX | Transfer SP to X | X = SP | N,Z | 2 |
| TXS | Transfer X to SP | SP = X | - | 2 |

### Stack Operations

| Opcode | Instruction | Description | Flags | Cycles |
|--------|-------------|-------------|-------|--------|
| PHA | Push Accumulator | Push A to stack | - | 3 |
| PHP | Push Processor Status | Push P to stack | - | 3 |
| PLA | Pull Accumulator | Pull A from stack | N,Z | 4 |
| PLP | Pull Processor Status | Pull P from stack | All | 4 |

### Arithmetic Operations

| Opcode | Instruction | Description | Flags | Cycles |
|--------|-------------|-------------|-------|--------|
| ADC | Add with Carry | A = A + M + C | N,V,Z,C | 2-6 |
| SBC | Subtract with Carry | A = A - M - (1-C) | N,V,Z,C | 2-6 |
| CMP | Compare Accumulator | A - M (flags only) | N,Z,C | 2-6 |
| CPX | Compare X Register | X - M (flags only) | N,Z,C | 2-4 |
| CPY | Compare Y Register | Y - M (flags only) | N,Z,C | 2-4 |

### Increment/Decrement

| Opcode | Instruction | Description | Flags | Cycles |
|--------|-------------|-------------|-------|--------|
| INC | Increment Memory | M = M + 1 | N,Z | 5-7 |
| INX | Increment X | X = X + 1 | N,Z | 2 |
| INY | Increment Y | Y = Y + 1 | N,Z | 2 |
| DEC | Decrement Memory | M = M - 1 | N,Z | 5-7 |
| DEX | Decrement X | X = X - 1 | N,Z | 2 |
| DEY | Decrement Y | Y = Y - 1 | N,Z | 2 |

### Logical Operations

| Opcode | Instruction | Description | Flags | Cycles |
|--------|-------------|-------------|-------|--------|
| AND | Logical AND | A = A & M | N,Z | 2-6 |
| ORA | Logical OR | A = A \| M | N,Z | 2-6 |
| EOR | Exclusive OR | A = A ^ M | N,Z | 2-6 |
| BIT | Bit Test | N=M7, V=M6, Z=A&M | N,V,Z | 3-4 |

### Shift/Rotate Operations

| Opcode | Instruction | Description | Flags | Cycles |
|--------|-------------|-------------|-------|--------|
| ASL | Arithmetic Shift Left | C <- [76543210] <- 0 | N,Z,C | 2-7 |
| LSR | Logical Shift Right | 0 -> [76543210] -> C | N,Z,C | 2-7 |
| ROL | Rotate Left | C <- [76543210] <- C | N,Z,C | 2-7 |
| ROR | Rotate Right | C -> [76543210] -> C | N,Z,C | 2-7 |

### Branch Instructions

All branches are relative addressing, 2 bytes, 2 cycles (+1 if taken, +1 if page crossed)

| Opcode | Instruction | Condition |
|--------|-------------|-----------|
| BCC | Branch if Carry Clear | C = 0 |
| BCS | Branch if Carry Set | C = 1 |
| BEQ | Branch if Equal (Zero) | Z = 1 |
| BNE | Branch if Not Equal | Z = 0 |
| BMI | Branch if Minus | N = 1 |
| BPL | Branch if Plus | N = 0 |
| BVC | Branch if Overflow Clear | V = 0 |
| BVS | Branch if Overflow Set | V = 1 |

### Jump/Call Instructions

| Opcode | Instruction | Description | Cycles |
|--------|-------------|-------------|--------|
| JMP | Jump | PC = address | 3 (abs), 5 (ind) |
| JSR | Jump to Subroutine | Push PC+2, PC = address | 6 |
| RTS | Return from Subroutine | Pull PC, PC = PC + 1 | 6 |
| RTI | Return from Interrupt | Pull P, Pull PC | 6 |
| BRK | Software Interrupt | Push PC+2, Push P, PC = ($FFFE) | 7 |

### Flag Instructions

| Opcode | Instruction | Description | Cycles |
|--------|-------------|-------------|--------|
| CLC | Clear Carry | C = 0 | 2 |
| SEC | Set Carry | C = 1 | 2 |
| CLD | Clear Decimal | D = 0 | 2 |
| SED | Set Decimal | D = 1 | 2 |
| CLI | Clear Interrupt Disable | I = 0 | 2 |
| SEI | Set Interrupt Disable | I = 1 | 2 |
| CLV | Clear Overflow | V = 0 | 2 |

### Miscellaneous

| Opcode | Instruction | Description | Cycles |
|--------|-------------|-------------|--------|
| NOP | No Operation | Do nothing | 2 |

## Opcode Matrix (Hex)

```
    | x0  x1  x2  x3  x4  x5  x6  x7  x8  x9  xA  xB  xC  xD  xE  xF
----+----------------------------------------------------------------
0x  | BRK ORA --- --- --- ORA ASL --- PHP ORA ASL --- --- ORA ASL ---
1x  | BPL ORA --- --- --- ORA ASL --- CLC ORA --- --- --- ORA ASL ---
2x  | JSR AND --- --- BIT AND ROL --- PLP AND ROL --- BIT AND ROL ---
3x  | BMI AND --- --- --- AND ROL --- SEC AND --- --- --- AND ROL ---
4x  | RTI EOR --- --- --- EOR LSR --- PHA EOR LSR --- JMP EOR LSR ---
5x  | BVC EOR --- --- --- EOR LSR --- CLI EOR --- --- --- EOR LSR ---
6x  | RTS ADC --- --- --- ADC ROR --- PLA ADC ROR --- JMP ADC ROR ---
7x  | BVS ADC --- --- --- ADC ROR --- SEI ADC --- --- --- ADC ROR ---
8x  | --- STA --- --- STY STA STX --- DEY --- TXA --- STY STA STX ---
9x  | BCC STA --- --- STY STA STX --- TYA STA TXS --- --- STA --- ---
Ax  | LDY LDA LDX --- LDY LDA LDX --- TAY LDA TAX --- LDY LDA LDX ---
Bx  | BCS LDA --- --- LDY LDA LDX --- CLV LDA TSX --- LDY LDA LDX ---
Cx  | CPY CMP --- --- CPY CMP DEC --- INY CMP DEX --- CPY CMP DEC ---
Dx  | BNE CMP --- --- --- CMP DEC --- CLD CMP --- --- --- CMP DEC ---
Ex  | CPX SBC --- --- CPX SBC INC --- INX SBC NOP --- CPX SBC INC ---
Fx  | BEQ SBC --- --- --- SBC INC --- SED SBC --- --- --- SBC INC ---
```

## Detailed Opcode Table

### $00-$0F
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $00 | BRK | Implied | 1 | 7 |
| $01 | ORA | (Indirect,X) | 2 | 6 |
| $05 | ORA | Zero Page | 2 | 3 |
| $06 | ASL | Zero Page | 2 | 5 |
| $08 | PHP | Implied | 1 | 3 |
| $09 | ORA | Immediate | 2 | 2 |
| $0A | ASL | Accumulator | 1 | 2 |
| $0D | ORA | Absolute | 3 | 4 |
| $0E | ASL | Absolute | 3 | 6 |

### $10-$1F
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $10 | BPL | Relative | 2 | 2+ |
| $11 | ORA | (Indirect),Y | 2 | 5+ |
| $15 | ORA | Zero Page,X | 2 | 4 |
| $16 | ASL | Zero Page,X | 2 | 6 |
| $18 | CLC | Implied | 1 | 2 |
| $19 | ORA | Absolute,Y | 3 | 4+ |
| $1D | ORA | Absolute,X | 3 | 4+ |
| $1E | ASL | Absolute,X | 3 | 7 |

### $20-$2F
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $20 | JSR | Absolute | 3 | 6 |
| $21 | AND | (Indirect,X) | 2 | 6 |
| $24 | BIT | Zero Page | 2 | 3 |
| $25 | AND | Zero Page | 2 | 3 |
| $26 | ROL | Zero Page | 2 | 5 |
| $28 | PLP | Implied | 1 | 4 |
| $29 | AND | Immediate | 2 | 2 |
| $2A | ROL | Accumulator | 1 | 2 |
| $2C | BIT | Absolute | 3 | 4 |
| $2D | AND | Absolute | 3 | 4 |
| $2E | ROL | Absolute | 3 | 6 |

### $30-$3F
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $30 | BMI | Relative | 2 | 2+ |
| $31 | AND | (Indirect),Y | 2 | 5+ |
| $35 | AND | Zero Page,X | 2 | 4 |
| $36 | ROL | Zero Page,X | 2 | 6 |
| $38 | SEC | Implied | 1 | 2 |
| $39 | AND | Absolute,Y | 3 | 4+ |
| $3D | AND | Absolute,X | 3 | 4+ |
| $3E | ROL | Absolute,X | 3 | 7 |

### $40-$4F
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $40 | RTI | Implied | 1 | 6 |
| $41 | EOR | (Indirect,X) | 2 | 6 |
| $45 | EOR | Zero Page | 2 | 3 |
| $46 | LSR | Zero Page | 2 | 5 |
| $48 | PHA | Implied | 1 | 3 |
| $49 | EOR | Immediate | 2 | 2 |
| $4A | LSR | Accumulator | 1 | 2 |
| $4C | JMP | Absolute | 3 | 3 |
| $4D | EOR | Absolute | 3 | 4 |
| $4E | LSR | Absolute | 3 | 6 |

### $50-$5F
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $50 | BVC | Relative | 2 | 2+ |
| $51 | EOR | (Indirect),Y | 2 | 5+ |
| $55 | EOR | Zero Page,X | 2 | 4 |
| $56 | LSR | Zero Page,X | 2 | 6 |
| $58 | CLI | Implied | 1 | 2 |
| $59 | EOR | Absolute,Y | 3 | 4+ |
| $5D | EOR | Absolute,X | 3 | 4+ |
| $5E | LSR | Absolute,X | 3 | 7 |

### $60-$6F
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $60 | RTS | Implied | 1 | 6 |
| $61 | ADC | (Indirect,X) | 2 | 6 |
| $65 | ADC | Zero Page | 2 | 3 |
| $66 | ROR | Zero Page | 2 | 5 |
| $68 | PLA | Implied | 1 | 4 |
| $69 | ADC | Immediate | 2 | 2 |
| $6A | ROR | Accumulator | 1 | 2 |
| $6C | JMP | (Indirect) | 3 | 5 |
| $6D | ADC | Absolute | 3 | 4 |
| $6E | ROR | Absolute | 3 | 6 |

### $70-$7F
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $70 | BVS | Relative | 2 | 2+ |
| $71 | ADC | (Indirect),Y | 2 | 5+ |
| $75 | ADC | Zero Page,X | 2 | 4 |
| $76 | ROR | Zero Page,X | 2 | 6 |
| $78 | SEI | Implied | 1 | 2 |
| $79 | ADC | Absolute,Y | 3 | 4+ |
| $7D | ADC | Absolute,X | 3 | 4+ |
| $7E | ROR | Absolute,X | 3 | 7 |

### $80-$8F
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $81 | STA | (Indirect,X) | 2 | 6 |
| $84 | STY | Zero Page | 2 | 3 |
| $85 | STA | Zero Page | 2 | 3 |
| $86 | STX | Zero Page | 2 | 3 |
| $88 | DEY | Implied | 1 | 2 |
| $8A | TXA | Implied | 1 | 2 |
| $8C | STY | Absolute | 3 | 4 |
| $8D | STA | Absolute | 3 | 4 |
| $8E | STX | Absolute | 3 | 4 |

### $90-$9F
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $90 | BCC | Relative | 2 | 2+ |
| $91 | STA | (Indirect),Y | 2 | 6 |
| $94 | STY | Zero Page,X | 2 | 4 |
| $95 | STA | Zero Page,X | 2 | 4 |
| $96 | STX | Zero Page,Y | 2 | 4 |
| $98 | TYA | Implied | 1 | 2 |
| $99 | STA | Absolute,Y | 3 | 5 |
| $9A | TXS | Implied | 1 | 2 |
| $9D | STA | Absolute,X | 3 | 5 |

### $A0-$AF
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $A0 | LDY | Immediate | 2 | 2 |
| $A1 | LDA | (Indirect,X) | 2 | 6 |
| $A2 | LDX | Immediate | 2 | 2 |
| $A4 | LDY | Zero Page | 2 | 3 |
| $A5 | LDA | Zero Page | 2 | 3 |
| $A6 | LDX | Zero Page | 2 | 3 |
| $A8 | TAY | Implied | 1 | 2 |
| $A9 | LDA | Immediate | 2 | 2 |
| $AA | TAX | Implied | 1 | 2 |
| $AC | LDY | Absolute | 3 | 4 |
| $AD | LDA | Absolute | 3 | 4 |
| $AE | LDX | Absolute | 3 | 4 |

### $B0-$BF
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $B0 | BCS | Relative | 2 | 2+ |
| $B1 | LDA | (Indirect),Y | 2 | 5+ |
| $B4 | LDY | Zero Page,X | 2 | 4 |
| $B5 | LDA | Zero Page,X | 2 | 4 |
| $B6 | LDX | Zero Page,Y | 2 | 4 |
| $B8 | CLV | Implied | 1 | 2 |
| $B9 | LDA | Absolute,Y | 3 | 4+ |
| $BA | TSX | Implied | 1 | 2 |
| $BC | LDY | Absolute,X | 3 | 4+ |
| $BD | LDA | Absolute,X | 3 | 4+ |
| $BE | LDX | Absolute,Y | 3 | 4+ |

### $C0-$CF
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $C0 | CPY | Immediate | 2 | 2 |
| $C1 | CMP | (Indirect,X) | 2 | 6 |
| $C4 | CPY | Zero Page | 2 | 3 |
| $C5 | CMP | Zero Page | 2 | 3 |
| $C6 | DEC | Zero Page | 2 | 5 |
| $C8 | INY | Implied | 1 | 2 |
| $C9 | CMP | Immediate | 2 | 2 |
| $CA | DEX | Implied | 1 | 2 |
| $CC | CPY | Absolute | 3 | 4 |
| $CD | CMP | Absolute | 3 | 4 |
| $CE | DEC | Absolute | 3 | 6 |

### $D0-$DF
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $D0 | BNE | Relative | 2 | 2+ |
| $D1 | CMP | (Indirect),Y | 2 | 5+ |
| $D5 | CMP | Zero Page,X | 2 | 4 |
| $D6 | DEC | Zero Page,X | 2 | 6 |
| $D8 | CLD | Implied | 1 | 2 |
| $D9 | CMP | Absolute,Y | 3 | 4+ |
| $DD | CMP | Absolute,X | 3 | 4+ |
| $DE | DEC | Absolute,X | 3 | 7 |

### $E0-$EF
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $E0 | CPX | Immediate | 2 | 2 |
| $E1 | SBC | (Indirect,X) | 2 | 6 |
| $E4 | CPX | Zero Page | 2 | 3 |
| $E5 | SBC | Zero Page | 2 | 3 |
| $E6 | INC | Zero Page | 2 | 5 |
| $E8 | INX | Implied | 1 | 2 |
| $E9 | SBC | Immediate | 2 | 2 |
| $EA | NOP | Implied | 1 | 2 |
| $EC | CPX | Absolute | 3 | 4 |
| $ED | SBC | Absolute | 3 | 4 |
| $EE | INC | Absolute | 3 | 6 |

### $F0-$FF
| Hex | Instruction | Mode | Bytes | Cycles |
|-----|-------------|------|-------|--------|
| $F0 | BEQ | Relative | 2 | 2+ |
| $F1 | SBC | (Indirect),Y | 2 | 5+ |
| $F5 | SBC | Zero Page,X | 2 | 4 |
| $F6 | INC | Zero Page,X | 2 | 6 |
| $F8 | SED | Implied | 1 | 2 |
| $F9 | SBC | Absolute,Y | 3 | 4+ |
| $FD | SBC | Absolute,X | 3 | 4+ |
| $FE | INC | Absolute,X | 3 | 7 |

## Notes

- Cycles marked with `+` take an extra cycle if a page boundary is crossed
- Branch instructions take 2 cycles if not taken, 3 if taken (same page), 4 if taken (different page)
- The 6502 has a bug where JMP ($xxFF) reads the low byte from $xxFF and high byte from $xx00 (not $xx00+1)
- BRK sets the B flag and pushes PC+2 (not PC+1)
- Stack operations always use page $01 ($0100-$01FF)

## Sources

This reference is compiled from publicly available 6502 documentation:
- MOS Technology 6502 Programming Manual
- Synertek SY6500 Hardware Manual
- Various published 6502 references
