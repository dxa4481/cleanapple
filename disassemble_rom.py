"""
Disassemble Apple II Monitor ROM to understand structure.
"""

import os
from py65.devices.mpu6502 import MPU as MPU6502
from py65.disassembler import Disassembler


def load_rom(filepath, start_address):
    """Load ROM file into memory."""
    memory = bytearray(65536)
    with open(filepath, 'rb') as f:
        data = f.read()
    for i, byte in enumerate(data):
        memory[start_address + i] = byte
    return memory


def disassemble_range(memory, start, end):
    """Disassemble a range of memory."""
    mpu = MPU6502()
    dis = Disassembler(mpu)
    
    # Need to copy memory to the MPU
    for i in range(65536):
        mpu.memory[i] = memory[i]
    
    addr = start
    output = []
    while addr <= end:
        # Disassemble one instruction
        try:
            length, disasm = dis.instruction_at(addr)
            output.append(f"${addr:04X}: {disasm}")
            addr += length
        except:
            output.append(f"${addr:04X}: .byte ${memory[addr]:02X}")
            addr += 1
    
    return output


def find_entry_points(memory, rom_start, rom_end):
    """Find likely entry points by looking for JSR/JMP targets within ROM."""
    # Look at reset and IRQ vectors
    reset_addr = memory[0xFFFC] | (memory[0xFFFD] << 8)
    irq_addr = memory[0xFFFE] | (memory[0xFFFF] << 8)
    
    print(f"Reset vector: ${reset_addr:04X}")
    print(f"IRQ/BRK vector: ${irq_addr:04X}")
    
    # Scan for JSR and JMP instructions and collect targets
    targets = set()
    addr = rom_start
    while addr < rom_end - 2:
        opcode = memory[addr]
        # JSR absolute: 0x20
        # JMP absolute: 0x4C
        # JMP indirect: 0x6C
        if opcode == 0x20 or opcode == 0x4C:
            target = memory[addr + 1] | (memory[addr + 2] << 8)
            if rom_start <= target <= rom_end:
                targets.add(target)
        addr += 1
    
    return sorted(targets)


def analyze_rom(filepath, start_address):
    """Analyze ROM structure."""
    memory = load_rom(filepath, start_address)
    
    print(f"\nAnalyzing ROM: {os.path.basename(filepath)}")
    print(f"Loaded at: ${start_address:04X}")
    print(f"Size: {len(open(filepath, 'rb').read())} bytes")
    print("="*60)
    
    # Get vectors
    end_address = start_address + 0x7FF  # 2KB ROM
    
    # Find entry points
    print("\nSubroutine entry points found:")
    entry_points = find_entry_points(memory, start_address, end_address)
    for ep in entry_points[:30]:  # First 30
        print(f"  ${ep:04X}")
    
    # Disassemble reset routine
    reset_addr = memory[0xFFFC] | (memory[0xFFFD] << 8)
    print(f"\n--- Reset routine at ${reset_addr:04X} ---")
    for line in disassemble_range(memory, reset_addr, reset_addr + 0x40)[:20]:
        print(line)
    
    # Disassemble key monitor routines - looking at standard addresses
    # COUT is typically at $FDED in Apple II
    print(f"\n--- Area near $FDDA (PRBYTE) ---")
    for line in disassemble_range(memory, 0xFDDA, 0xFDFF):
        print(line)
    
    print(f"\n--- Area near $FBC1 (BASCALC) ---")
    for line in disassemble_range(memory, 0xFBC1, 0xFBE0):
        print(line)
    
    print(f"\n--- Area near $FCA8 (WAIT) ---")
    for line in disassemble_range(memory, 0xFCA8, 0xFCC0):
        print(line)
    
    print(f"\n--- Area near $FE80 (SETINV/SETNORM) ---")
    for line in disassemble_range(memory, 0xFE80, 0xFE90):
        print(line)
    
    return memory


def main():
    # Analyze Apple II Monitor ROM
    rom_path = "/workspace/original_source/APPLE II/APPLE II - 341-0004 - INTEGER BASIC MONITOR F800 - 2716.bin"
    print("\n" + "="*60)
    print("APPLE II MONITOR ROM ANALYSIS")
    print("="*60)
    memory = analyze_rom(rom_path, 0xF800)
    
    # Also show vectors area at end of ROM
    print("\n--- Vectors at $FFF8-$FFFF ---")
    for addr in range(0xFFF8, 0x10000, 2):
        low = memory[addr]
        high = memory[addr + 1]
        vector = (high << 8) | low
        print(f"${addr:04X}: ${low:02X} ${high:02X} -> ${vector:04X}")


if __name__ == "__main__":
    main()
