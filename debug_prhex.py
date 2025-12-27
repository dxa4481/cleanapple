"""Debug PRHEX execution."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apple2_emulator import Apple2Emulator

def debug_prhex():
    emu = Apple2Emulator()
    
    # Load monitor ROM
    rom_path = "/workspace/original_source/APPLE II/APPLE II - 341-0004 - INTEGER BASIC MONITOR F800 - 2716.bin"
    emu.load_rom_file(rom_path, 0xF800)
    
    # Set up output capture routine at $0300
    capture_code = [
        0xA6, 0x2E,              # LDX $2E
        0x9D, 0x50, 0x03,        # STA $0350,X  
        0xE6, 0x2E,              # INC $2E
        0x91, 0x28,              # STA ($28),Y
        0xE6, 0x24,              # INC $24
        0x60                     # RTS
    ]
    for i, byte in enumerate(capture_code):
        emu.memory.memory[0x0300 + i] = byte
    
    # Initialize zero page
    emu.memory.memory[0x24] = 0     # CH
    emu.memory.memory[0x25] = 0     # CV
    emu.memory.memory[0x28] = 0x00  # BASL
    emu.memory.memory[0x29] = 0x04  # BASH
    emu.memory.memory[0x2E] = 0     # Output index
    emu.memory.memory[0x32] = 0xFF  # INVFLG
    
    # Set COUT vector to our capture routine
    emu.memory.memory[0x36] = 0x00
    emu.memory.memory[0x37] = 0x03
    
    # Clear screen and output buffer
    for addr in range(0x400, 0x800):
        emu.memory.memory[addr] = 0xA0
    for addr in range(0x350, 0x380):
        emu.memory.memory[addr] = 0x00
    
    # Set up to call PRHEX with A=5
    # Push return address - 1 onto stack
    return_addr = 0x0320
    emu.cpu.sp = 0xFF
    emu.cpu.sp -= 1
    emu.memory.memory[0x100 + emu.cpu.sp + 1] = (return_addr - 1) >> 8
    emu.cpu.sp -= 1
    emu.memory.memory[0x100 + emu.cpu.sp + 1] = (return_addr - 1) & 0xFF
    
    # Set registers
    emu.cpu.a = 0x05  # Test value
    emu.cpu.x = 0
    emu.cpu.y = 0
    emu.cpu.pc = 0xFDE3  # PRHEX
    emu.cpu.p = 0x24
    
    print("Starting execution at PRHEX ($FDE3) with A=$05")
    print(f"Return address: ${return_addr:04X}")
    print(f"COUT vector ($36-$37): ${emu.memory[0x36]:02X} ${emu.memory[0x37]:02X}")
    print()
    
    # Trace execution
    for i in range(50):
        pc = emu.cpu.pc
        opcode = emu.memory[pc]
        
        # Get instruction length for display
        state = f"PC=${pc:04X} A=${emu.cpu.a:02X} X=${emu.cpu.x:02X} Y=${emu.cpu.y:02X} SP=${emu.cpu.sp:02X} P=${emu.cpu.p:02X}"
        print(f"Step {i+1:2d}: {state} [${opcode:02X}]")
        
        if pc == return_addr:
            print(f"\nReached return address ${return_addr:04X}")
            break
        
        emu.step()
    
    print()
    print("=== Results ===")
    print(f"Output buffer ($0350): ${emu.memory[0x0350]:02X} = '{chr(emu.memory[0x0350] & 0x7F)}'")
    print(f"Screen ($0400): ${emu.memory[0x0400]:02X} = '{chr(emu.memory[0x0400] & 0x7F)}'")
    print(f"CH ($24): {emu.memory[0x24]}")


if __name__ == "__main__":
    debug_prhex()
