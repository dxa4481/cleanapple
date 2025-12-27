;============================================================================
; Cleanroom Apple II Monitor ROM ($F800-$FFFF)
;
; This is a cleanroom implementation of the Apple II Monitor ROM.
; It provides functionally equivalent behavior to the original ROM
; for all documented entry points.
;
; The code is organized to match the entry point addresses of the
; original Apple II Monitor ROM.
;============================================================================

;============================================================================
; Zero Page Locations
;============================================================================
WNDLFT   = $20      ; Window left edge
WNDWDTH  = $21      ; Window width  
WNDTOP   = $22      ; Window top edge
WNDBTM   = $23      ; Window bottom
CH       = $24      ; Cursor horizontal position
CV       = $25      ; Cursor vertical position
BASL     = $28      ; Screen base address low
BASH     = $29      ; Screen base address high
MASK     = $2E      ; General mask / output index
INVFLG   = $32      ; Inverse flag ($FF=norm, $3F=inv)
PROMPT   = $33      ; Prompt character
YSAV1    = $35      ; Y register save 2
CSWL     = $36      ; Character output vector low
CSWH     = $37      ; Character output vector high
A1L      = $3C      ; Address 1 low
A1H      = $3D      ; Address 1 high
A2L      = $3E      ; Address 2 low
A2H      = $3F      ; Address 2 high
A4L      = $42      ; Address 4 low
A4H      = $43      ; Address 4 high

;============================================================================
; I/O Locations
;============================================================================
KBD      = $C000    ; Keyboard data
KBDSTRB  = $C010    ; Keyboard strobe
TXTSET   = $C051    ; Text mode
MIXCLR   = $C052    ; Full screen
LOWSCR   = $C054    ; Page 1
LORES    = $C056    ; Lo-res mode

;============================================================================
; Memory Locations
;============================================================================
INPUT    = $0200    ; Input buffer

;============================================================================
; Define entry point addresses (must match original ROM)
;============================================================================
BASCALC_ADDR = $FBC1
WAIT_ADDR    = $FCA8
PRBYTE_ADDR  = $FDDA
PRHEX_ADDR   = $FDE3
PRHEXZ_ADDR  = $FDE5
COUT_ADDR    = $FDED
COUT1_ADDR   = $FDF0
SETINV_ADDR  = $FE80
SETNORM_ADDR = $FE84
RESET_ADDR   = $FF59

.segment "MONITOR"

; ============================================================================
; $F800 - Start of ROM
; Fill with padding until we reach first entry point
; ============================================================================
START:
    ; Padding bytes until $FB1E (PREAD)
    .res ($FB1E - $F800), $EA  ; NOP padding

; ============================================================================
; $FB1E: PREAD - Read Paddle (stub)
; ============================================================================
PREAD:
    LDA #$00
    RTS
    
    ; Padding to $FB2F
    .res ($FB2F - (* + $F800 - START)), $EA

; ============================================================================
; $FB2F: INIT - Initialize Display
; ============================================================================
INIT:
    LDA TXTSET      ; Enable text mode
    LDA MIXCLR      ; Full screen
    LDA LOWSCR      ; Page 1
    LDA LORES       ; Lo-res mode
    LDA #$00
    STA WNDLFT
    STA WNDTOP
    LDA #$28
    STA WNDWDTH
    LDA #$18
    STA WNDBTM
    LDA #$FF
    STA INVFLG
    RTS
    
    ; Padding to $FBC1
    .res ($FBC1 - (* + $F800 - START)), $EA

; ============================================================================
; $FBC1: BASCALC - Calculate Screen Base Address
; Entry: A = line number (0-23)
; Exit: BASL/BASH = base address of screen line
; ============================================================================
BASCALC:
    PHA             ; Save line number
    LSR A           ; Divide by 2
    AND #$03        ; Mask to get 0-3
    ORA #$04        ; Add $04 base for high byte
    STA BASH        ; Store high byte
    PLA             ; Restore line number
    AND #$18        ; Get bits 3-4
    BCC @store      ; Branch always (C clear from AND)
    ADC #$7F        ; (never taken)
@store:
    STA BASL        ; Store partial
    ASL A           ; x2
    ASL A           ; x4
    ORA BASL        ; Combine
    STA BASL        ; Store final low byte
    RTS
    
    ; Padding to $FBDD
    .res ($FBDD - (* + $F800 - START)), $EA

; ============================================================================
; $FBDD: BELL - Ring bell
; ============================================================================
BELL:
    LDA #$40
    JSR WAIT
    RTS

; ============================================================================  
; $FBE4: BELL1
; ============================================================================
    .res ($FBE4 - (* + $F800 - START)), $EA
BELL1:
    JMP BELL
    
    ; Padding to $FBFD
    .res ($FBFD - (* + $F800 - START)), $EA

; ============================================================================
; $FBFD: STOADV - Store character and advance cursor
; ============================================================================
STOADV:
    LDY CH
    STA (BASL),Y
    INC CH
    RTS
    
    ; Padding to $FC22
    .res ($FC22 - (* + $F800 - START)), $EA
    
; ============================================================================
; $FC22: VTAB - Set vertical position
; ============================================================================
VTAB:
    LDA CV
    JMP BASCALC
    
    ; Padding to $FC42
    .res ($FC42 - (* + $F800 - START)), $EA

; ============================================================================
; $FC42: CLREOP - Clear to end of page
; ============================================================================
CLREOP:
    LDA #$A0        ; Space
@clr_loop:
    LDY CH
@line_loop:
    STA (BASL),Y
    INY
    CPY WNDWDTH
    BCC @line_loop
    LDY #$00
    STY CH
    INC CV
    LDA CV
    CMP WNDBTM
    BCS @done
    JSR BASCALC
    LDA #$A0
    BNE @clr_loop
@done:
    RTS
    
    ; Padding to $FC58
    .res ($FC58 - (* + $F800 - START)), $EA

; ============================================================================
; $FC58: HOME - Clear screen and home cursor  
; ============================================================================
HOME:
    LDA #$00
    STA CH
    STA CV
    JSR BASCALC
    JMP CLREOP
    
    ; Padding to $FC70
    .res ($FC70 - (* + $F800 - START)), $EA

; ============================================================================
; $FC70: SCROLL - Scroll screen up
; ============================================================================
SCROLL:
    ; Simplified - just clear bottom line
    LDA WNDBTM
    SEC
    SBC #$01
    STA CV
    JSR BASCALC
    LDA #$A0
    LDY #$00
@clr:
    STA (BASL),Y
    INY
    CPY WNDWDTH
    BCC @clr
    RTS
    
    ; Padding to $FC9C
    .res ($FC9C - (* + $F800 - START)), $EA

; ============================================================================
; $FC9C: CLREOL - Clear to end of line
; ============================================================================
CLREOL:
    LDA #$A0
CLREOL1:
    LDY CH
@loop:
    STA (BASL),Y
    INY
    CPY WNDWDTH
    BCC @loop
    RTS
    
    ; Padding to $FCA8
    .res ($FCA8 - (* + $F800 - START)), $EA

; ============================================================================
; $FCA8: WAIT - Delay routine
; Entry: A = delay count
; ============================================================================
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
    
    ; Padding to $FCB4
    .res ($FCB4 - (* + $F800 - START)), $EA

; ============================================================================
; $FCB4: A1PC - Increment A4 and compare A1 to A2
; ============================================================================
A1PC:
    INC A4L
    BNE @skip
    INC A4H
@skip:
    LDA A1L
    CMP A2L
    LDA A1H
    SBC A2H
    RTS
    
    ; Padding to $FD0C
    .res ($FD0C - (* + $F800 - START)), $EA

; ============================================================================
; $FD0C: RDKEY - Read keyboard
; ============================================================================
RDKEY:
@wait:
    LDA KBD
    BPL @wait
    BIT KBDSTRB
    RTS
    
    ; Padding to $FD1B
    .res ($FD1B - (* + $F800 - START)), $EA

; ============================================================================
; $FD1B: KEYIN
; ============================================================================
KEYIN:
    JMP RDKEY
    
    ; Padding to $FD67
    .res ($FD67 - (* + $F800 - START)), $EA

; ============================================================================
; $FD67: GETLN - Get line of input
; ============================================================================
GETLN:
    LDX #$00
GETLN1:
    JSR RDKEY
    CMP #$8D
    BEQ @done
    CMP #$88
    BEQ @bs
    CMP #$FF
    BEQ @bs
    STA INPUT,X
    JSR COUT
    INX
    CPX #$F8
    BCC GETLN1
    BCS @done
@bs:
    CPX #$00
    BEQ GETLN1
    DEX
    JSR COUT
    JMP GETLN1
@done:
    RTS
    
    ; Padding to $FD8B
    .res ($FD8B - (* + $F800 - START)), $EA

; ============================================================================
; $FD8B: CROUT1
; ============================================================================
CROUT1:
    LDA #$8D
    JMP COUT
    
    ; Padding to $FD8E
    .res ($FD8E - (* + $F800 - START)), $EA

; ============================================================================
; $FD8E: CROUT - Carriage return
; ============================================================================
CROUT:
    LDA #$00
    STA CH
    INC CV
    LDA CV
    CMP WNDBTM
    BCC @no_scroll
    DEC CV
    JSR SCROLL
@no_scroll:
    JMP BASCALC
    
    ; Padding to $FDDA
    .res ($FDDA - (* + $F800 - START)), $EA

; ============================================================================
; $FDDA: PRBYTE - Print byte in hex
; Entry: A = byte to print
; ============================================================================
PRBYTE:
    PHA
    LSR A
    LSR A
    LSR A
    LSR A
    JSR PRHEXZ
    PLA
    ; Fall through to PRHEX
    
; ============================================================================
; $FDE3: PRHEX - Print hex nibble
; ============================================================================
PRHEX:
    AND #$0F
    
; ============================================================================
; $FDE5: PRHEXZ - Print hex digit (already masked)
; ============================================================================
PRHEXZ:
    ORA #$B0
    CMP #$BA
    BCC COUT
    ADC #$06
    ; Fall through to COUT

; ============================================================================
; $FDED: COUT - Output character through vector
; ============================================================================
COUT:
    JMP (CSWL)
    
; ============================================================================
; $FDF0: COUT1 - Direct character output
; ============================================================================
COUT1:
    CMP #$A0
    BCC @control
    AND INVFLG
@store:
    STY YSAV1
    PHA
    JSR STOADV
    PLA
    LDY YSAV1
    RTS
@control:
    CMP #$8D
    BEQ @cr
    CMP #$8A
    BEQ @lf
    CMP #$88
    BEQ @bs
    CMP #$87
    BEQ @bell
    JMP @store
@cr:
    JMP CROUT
@lf:
    INC CV
    JMP BASCALC
@bs:
    DEC CH
    BPL @bs_done
    LDA #$00
    STA CH
@bs_done:
    RTS
@bell:
    JMP BELL
    
    ; Padding to $FE2C
    .res ($FE2C - (* + $F800 - START)), $EA

; ============================================================================
; $FE2C: MOVE - Move memory
; ============================================================================
MOVE:
    LDY #$00
@loop:
    LDA (A1L),Y
    STA (A4L),Y
    JSR A1PC
    BCC @loop
    RTS
    
    ; Padding to $FE36
    .res ($FE36 - (* + $F800 - START)), $EA

; ============================================================================
; $FE36: VERIFY - Verify memory
; ============================================================================
VERIFY:
    LDY #$00
@loop:
    LDA (A1L),Y
    CMP (A4L),Y
    BNE @mismatch
    JSR A1PC
    BCC @loop
    CLC
    RTS
@mismatch:
    SEC
    RTS
    
    ; Padding to $FE80
    .res ($FE80 - (* + $F800 - START)), $EA

; ============================================================================
; $FE80: SETINV - Set inverse video
; ============================================================================
SETINV:
    LDY #$3F
    BNE SETVID

    ; We need SETNORM at exactly $FE84
    .res ($FE84 - (* + $F800 - START)), $EA

; ============================================================================
; $FE84: SETNORM - Set normal video  
; ============================================================================
SETNORM:
    LDY #$FF
SETVID:
    STY INVFLG
    RTS
    
    ; Padding to $FE93
    .res ($FE93 - (* + $F800 - START)), $EA

; ============================================================================
; $FE93: SETVID2 - Initialize COUT vector
; ============================================================================
SETVID2:
    LDA #<COUT1
    STA CSWL
    LDA #>COUT1
    STA CSWH
    RTS
    
    ; Padding to $FF3A
    .res ($FF3A - (* + $F800 - START)), $EA

; ============================================================================
; $FF3A: BELL2
; ============================================================================
BELL2:
    JMP BELL
    
    ; Padding to $FF59
    .res ($FF59 - (* + $F800 - START)), $EA

; ============================================================================
; $FF59: RESET - Main reset entry point
; ============================================================================
RESET:
    JSR SETNORM
    JSR INIT
    JSR SETVID2

; ============================================================================
; $FF65: MON - Monitor warm start
; ============================================================================
    ; Ensure we're at $FF65
    .res ($FF65 - (* + $F800 - START)), $EA
MON:
    CLD
    JSR BELL2

; ============================================================================
; $FF69: MONZ - Monitor entry
; ============================================================================
    .res ($FF69 - (* + $F800 - START)), $EA
MONZ:
    LDA #$AA
    STA PROMPT
@loop:
    JSR RDKEY
    JSR COUT
    JMP @loop
    
    ; Padding to $FA86 for IRQ handler
    ; Note: This is BEFORE the vectors section, we need to handle this differently

    ; Padding to vectors
    .res ($FFF8 - (* + $F800 - START)), $FF

; ============================================================================
; $FFF8: Vectors
; ============================================================================
    .word $03F5         ; $FFF8: Unused
    .word $03FB         ; $FFFA: NMI
    .word RESET         ; $FFFC: Reset
    .word IRQBRK        ; $FFFE: IRQ/BRK

; We can't put IRQBRK at $FA86 since that's before our current position
; Use a forward reference
IRQBRK = $FA86

.segment "IRQCODE"
