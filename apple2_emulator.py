"""
Apple II ROM Emulator and Testing Framework

This module provides a 6502-based Apple II emulator for testing
and validating ROM functionality. It uses the py65 library for
CPU emulation and adds Apple II-specific hardware emulation.
"""

import os
from py65.devices.mpu6502 import MPU as MPU6502


class Apple2Memory:
    """
    Apple II memory map implementation.
    
    Memory Map:
    $0000-$00FF: Zero Page
    $0100-$01FF: Stack
    $0200-$02FF: Input buffer
    $0300-$03FF: Vectors and other system locations
    $0400-$07FF: Text page 1 / Lo-res graphics page 1
    $0800-$0BFF: Text page 2 / Lo-res graphics page 2
    $0C00-$1FFF: Free RAM
    $2000-$3FFF: Hi-res graphics page 1
    $4000-$5FFF: Hi-res graphics page 2
    $6000-$BFFF: Free RAM (or Language Card RAM)
    $C000-$C0FF: I/O soft switches
    $C100-$C7FF: Peripheral card ROM space
    $C800-$CFFF: Expansion ROM space
    $D000-$DFFF: BASIC ROM (Integer or Applesoft)
    $E000-$F7FF: BASIC ROM continued
    $F800-$FFFF: Monitor ROM
    """
    
    def __init__(self):
        self.memory = bytearray(65536)
        self.output_buffer = []  # Capture character output
        self.input_buffer = []   # Characters to be read
        self.keyboard_char = 0   # Last key pressed
        self.keyboard_strobe = 0 # High bit set when key available
        
        # Soft switch states
        self.text_mode = True
        self.mixed_mode = False
        self.page2 = False
        self.hires = False
        self.annunciator = [False, False, False, False]
        
    def __getitem__(self, address):
        """Read from memory or I/O."""
        address = address & 0xFFFF
        
        # I/O soft switches ($C000-$C0FF)
        if 0xC000 <= address <= 0xC0FF:
            return self._read_io(address)
        
        return self.memory[address]
    
    def __setitem__(self, address, value):
        """Write to memory or I/O."""
        address = address & 0xFFFF
        value = value & 0xFF
        
        # I/O soft switches
        if 0xC000 <= address <= 0xC0FF:
            self._write_io(address, value)
            return
        
        # ROM area is not writable
        if address >= 0xD000:
            return
            
        self.memory[address] = value
    
    def _read_io(self, address):
        """Handle I/O read operations."""
        # $C000 - Keyboard data (key + $80 when strobe set)
        if address == 0xC000:
            return self.keyboard_char | self.keyboard_strobe
        
        # $C010 - Clear keyboard strobe
        if address == 0xC010:
            self.keyboard_strobe = 0
            return 0
        
        # $C030 - Speaker toggle (just return 0)
        if address == 0xC030:
            return 0
        
        # Text/graphics switches (reading returns current state)
        if address == 0xC050:  # TXTCLR - Graphics mode
            self.text_mode = False
            return 0
        if address == 0xC051:  # TXTSET - Text mode
            self.text_mode = True
            return 0
        if address == 0xC052:  # MIXCLR - Full screen
            self.mixed_mode = False
            return 0
        if address == 0xC053:  # MIXSET - Mixed mode
            self.mixed_mode = True
            return 0
        if address == 0xC054:  # PAGE1
            self.page2 = False
            return 0
        if address == 0xC055:  # PAGE2
            self.page2 = True
            return 0
        if address == 0xC056:  # LORES
            self.hires = False
            return 0
        if address == 0xC057:  # HIRES
            self.hires = True
            return 0
        
        return 0
    
    def _write_io(self, address, value):
        """Handle I/O write operations."""
        # Most Apple II I/O is read-triggered, not write
        pass
    
    def load_rom(self, data, start_address):
        """Load ROM data into memory."""
        for i, byte in enumerate(data):
            self.memory[start_address + i] = byte
    
    def type_string(self, s):
        """Queue a string to be typed into the keyboard buffer."""
        for char in s:
            if char == '\n':
                self.input_buffer.append(0x8D)  # Return key
            else:
                self.input_buffer.append(ord(char.upper()) | 0x80)
    
    def press_key(self, char):
        """Press a single key."""
        if isinstance(char, str):
            if char == '\n':
                self.keyboard_char = 0x0D
            else:
                self.keyboard_char = ord(char.upper()) & 0x7F
        else:
            self.keyboard_char = char & 0x7F
        self.keyboard_strobe = 0x80
    
    def get_text_screen(self):
        """Get the contents of text page 1 as a string."""
        lines = []
        base = 0x0400
        # Apple II text screen line address table
        line_addrs = [
            0x400, 0x480, 0x500, 0x580, 0x600, 0x680, 0x700, 0x780,
            0x428, 0x4A8, 0x528, 0x5A8, 0x628, 0x6A8, 0x728, 0x7A8,
            0x450, 0x4D0, 0x550, 0x5D0, 0x650, 0x6D0, 0x750, 0x7D0
        ]
        for addr in line_addrs:
            line = ""
            for col in range(40):
                char = self.memory[addr + col]
                # Convert Apple II character to ASCII
                if char >= 0xC0:  # Inverse uppercase
                    line += chr((char & 0x3F) + 0x40)
                elif char >= 0x80:  # Normal characters
                    line += chr(char & 0x7F)
                elif char >= 0x40:  # Flashing uppercase
                    line += chr(char)
                else:  # Inverse symbols/numbers
                    line += chr(char + 0x40)
            lines.append(line.rstrip())
        return "\n".join(lines)


class Apple2Emulator:
    """
    Apple II Emulator for ROM testing.
    """
    
    def __init__(self):
        self.memory = Apple2Memory()
        self.cpu = MPU6502(memory=self.memory)
        self.output_log = []
        self.cycle_count = 0
        self.max_cycles = 1000000  # Safety limit
        
        # Hook COUT routine for output capture
        self._original_cout = None
        
    def load_rom_file(self, filepath, address):
        """Load a ROM file at the specified address."""
        with open(filepath, 'rb') as f:
            data = f.read()
        self.memory.load_rom(data, address)
        return len(data)
    
    def load_apple2_roms(self, rom_dir):
        """Load complete Apple II ROM set."""
        roms = {
            "APPLE II - 341-0001 - INTEGER BASIC E000 - 2716.bin": 0xE000,
            "APPLE II - 341-0002 - INTEGER BASIC E800 - 2716.bin": 0xE800,
            "APPLE II - 341-0003 - INTEGER BASIC F000 - 2716.bin": 0xF000,
            "APPLE II - 341-0004 - INTEGER BASIC MONITOR F800 - 2716.bin": 0xF800,
        }
        
        loaded = []
        for filename, address in roms.items():
            path = os.path.join(rom_dir, filename)
            if os.path.exists(path):
                size = self.load_rom_file(path, address)
                loaded.append((filename, address, size))
        
        return loaded
    
    def load_apple2plus_roms(self, rom_dir):
        """Load complete Apple II+ ROM set."""
        roms = {
            "APPLE II+ - 341-0011 - APPLESOFT BASIC D000 - 2716.bin": 0xD000,
            "APPLE II+ - 341-0012 - APPLESOFT BASIC D800 - 2716.bin": 0xD800,
            "APPLE II+ - 341-0013 - APPLESOFT BASIC E000 - 2716.bin": 0xE000,
            "APPLE II+ - 341-0014 - APPLESOFT BASIC E800 - 2716.bin": 0xE800,
            "APPLE II+ - 341-0015 - APPLESOFT BASIC F000 - 2716.bin": 0xF000,
            "APPLE II+ - 341-0020 - APPLESOFT BASIC AUTOSTART MONITOR F800 - 2716.bin": 0xF800,
        }
        
        loaded = []
        for filename, address in roms.items():
            path = os.path.join(rom_dir, filename)
            if os.path.exists(path):
                size = self.load_rom_file(path, address)
                loaded.append((filename, address, size))
        
        return loaded
    
    def reset(self):
        """Reset the CPU."""
        # Read reset vector from $FFFC-$FFFD
        low = self.memory[0xFFFC]
        high = self.memory[0xFFFD]
        self.cpu.pc = (high << 8) | low
        self.cpu.sp = 0xFF
        self.cpu.a = 0
        self.cpu.x = 0
        self.cpu.y = 0
        self.cpu.p = 0x24  # IRQ disabled
        self.cycle_count = 0
    
    def step(self):
        """Execute one instruction."""
        self.cpu.step()
        self.cycle_count += 1
    
    def run_until(self, address, max_cycles=None):
        """Run until reaching a specific address."""
        if max_cycles is None:
            max_cycles = self.max_cycles
            
        cycles = 0
        while self.cpu.pc != address and cycles < max_cycles:
            self.step()
            cycles += 1
        
        return cycles < max_cycles
    
    def run_cycles(self, count):
        """Run for a specific number of cycles."""
        for _ in range(count):
            self.step()
    
    def call_subroutine(self, address, a=None, x=None, y=None, return_addr=None):
        """
        Call a subroutine and return when it executes RTS.
        Returns the register values after the call.
        
        Args:
            address: Subroutine address to call
            a, x, y: Optional register values to set before call
            return_addr: Optional custom return address (default $0380)
        """
        # Set up registers if specified
        if a is not None:
            self.cpu.a = a
        if x is not None:
            self.cpu.x = x
        if y is not None:
            self.cpu.y = y
        
        # Push return address - 1 (as JSR does)
        # Use $0380 by default - well after any capture routines at $0300-$030F
        if return_addr is None:
            return_addr = 0x0380
        
        self.cpu.sp = (self.cpu.sp - 1) & 0xFF
        self.memory.memory[0x100 + ((self.cpu.sp + 1) & 0xFF)] = (return_addr - 1) >> 8
        self.cpu.sp = (self.cpu.sp - 1) & 0xFF
        self.memory.memory[0x100 + ((self.cpu.sp + 1) & 0xFF)] = (return_addr - 1) & 0xFF
        
        # Set PC to subroutine address
        self.cpu.pc = address
        
        # Run until we return
        cycles = 0
        while self.cpu.pc != return_addr and cycles < self.max_cycles:
            self.step()
            cycles += 1
        
        return {
            'a': self.cpu.a,
            'x': self.cpu.x,
            'y': self.cpu.y,
            'p': self.cpu.p,
            'cycles': cycles,
            'completed': cycles < self.max_cycles
        }
    
    def get_memory(self, start, length):
        """Get a range of memory."""
        return bytes([self.memory[start + i] for i in range(length)])
    
    def set_memory(self, start, data):
        """Set a range of memory."""
        for i, byte in enumerate(data):
            self.memory.memory[start + i] = byte
    
    def dump_state(self):
        """Return current CPU state as a string."""
        return (f"PC=${self.cpu.pc:04X} A=${self.cpu.a:02X} "
                f"X=${self.cpu.x:02X} Y=${self.cpu.y:02X} "
                f"SP=${self.cpu.sp:02X} P=${self.cpu.p:02X}")


def test_original_roms():
    """Test that the original ROMs load and basic functions work."""
    print("=" * 60)
    print("Apple II Original ROM Test Suite")
    print("=" * 60)
    
    emu = Apple2Emulator()
    
    # Test Apple II ROMs
    print("\n--- Loading Apple II ROMs ---")
    rom_dir = "/workspace/original_source/APPLE II"
    loaded = emu.load_apple2_roms(rom_dir)
    
    for name, addr, size in loaded:
        print(f"  Loaded {name}")
        print(f"    Address: ${addr:04X}, Size: {size} bytes")
    
    # Check reset vector
    reset_low = emu.memory[0xFFFC]
    reset_high = emu.memory[0xFFFD]
    reset_vector = (reset_high << 8) | reset_low
    print(f"\n  Reset vector: ${reset_vector:04X}")
    
    # Check IRQ/BRK vector
    irq_low = emu.memory[0xFFFE]
    irq_high = emu.memory[0xFFFF]
    irq_vector = (irq_high << 8) | irq_low
    print(f"  IRQ/BRK vector: ${irq_vector:04X}")
    
    # Test reset
    print("\n--- Testing Reset ---")
    emu.reset()
    print(f"  After reset: {emu.dump_state()}")
    
    # Test a few cycles of execution
    print("\n--- Running a few instructions ---")
    for i in range(10):
        old_pc = emu.cpu.pc
        emu.step()
        print(f"  Step {i+1}: ${old_pc:04X} -> {emu.dump_state()}")
    
    print("\n" + "=" * 60)
    print("Apple II+ ROM Test")
    print("=" * 60)
    
    emu2 = Apple2Emulator()
    
    print("\n--- Loading Apple II+ ROMs ---")
    rom_dir_plus = "/workspace/original_source/APPLE II+"
    loaded = emu2.load_apple2plus_roms(rom_dir_plus)
    
    for name, addr, size in loaded:
        print(f"  Loaded {name}")
        print(f"    Address: ${addr:04X}, Size: {size} bytes")
    
    # Check reset vector
    reset_low = emu2.memory[0xFFFC]
    reset_high = emu2.memory[0xFFFD]
    reset_vector = (reset_high << 8) | reset_low
    print(f"\n  Reset vector: ${reset_vector:04X}")
    
    # Test reset
    print("\n--- Testing Reset ---")
    emu2.reset()
    print(f"  After reset: {emu2.dump_state()}")
    
    # Test a few cycles of execution
    print("\n--- Running a few instructions ---")
    for i in range(10):
        old_pc = emu2.cpu.pc
        emu2.step()
        print(f"  Step {i+1}: ${old_pc:04X} -> {emu2.dump_state()}")
    
    print("\n" + "=" * 60)
    print("ROM Tests Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_original_roms()
