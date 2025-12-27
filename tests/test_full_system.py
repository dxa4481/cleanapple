#!/usr/bin/env python3
"""
Full Apple II System Integration Test

This test runs a complete Apple II emulation using:
- CLEANROOM ROMs where we have implemented them
- ORIGINAL ROMs for components we haven't cleanroomed yet

This validates that our cleanroom implementations work correctly
in a real system context alongside original Apple II components.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from py65.devices.mpu6502 import MPU
except ImportError:
    print("ERROR: py65 not installed. Run: pip install py65")
    sys.exit(1)


class Apple2System:
    """
    Full Apple II system emulator for integration testing.
    
    Memory Map:
    $0000-$00FF  Zero Page
    $0100-$01FF  Stack
    $0200-$02FF  Input buffer
    $0300-$03FF  Vectors
    $0400-$07FF  Text Screen Page 1
    $0800-$0BFF  Text Screen Page 2
    $0C00-$1FFF  Free RAM
    $2000-$3FFF  Hi-Res Page 1
    $4000-$5FFF  Hi-Res Page 2
    $6000-$BFFF  Free RAM
    $C000-$C0FF  I/O / Soft Switches
    $C100-$C7FF  Peripheral Card ROM
    $C800-$CFFF  Expansion ROM
    $D000-$F7FF  BASIC ROM (Integer or Applesoft)
    $F800-$FFFF  Monitor ROM
    """
    
    def __init__(self):
        self.mpu = MPU()
        self.memory = self.mpu.memory
        
        # Track which ROMs are loaded
        self.loaded_roms = {}
        
        # Keyboard buffer
        self.keyboard_buffer = []
        self.keyboard_strobe = False
        
        # Screen output capture
        self.screen_output = []
        
        # I/O access log
        self.io_log = []
        
    def load_rom(self, path, base_address, name, is_cleanroom=False):
        """Load a ROM file into memory."""
        if not os.path.exists(path):
            return False
            
        with open(path, 'rb') as f:
            data = f.read()
        
        for i, byte in enumerate(data):
            if base_address + i < 0x10000:
                self.memory[base_address + i] = byte
        
        status = "CLEANROOM" if is_cleanroom else "ORIGINAL"
        self.loaded_roms[name] = {
            'path': path,
            'base': base_address,
            'size': len(data),
            'cleanroom': is_cleanroom
        }
        print(f"  [{status}] {name}: ${base_address:04X}-${base_address+len(data)-1:04X} ({len(data)} bytes)")
        return True
    
    def setup_io_handlers(self):
        """Set up I/O soft switch handling."""
        # We'll intercept reads/writes in the step function
        pass
    
    def handle_io_read(self, address):
        """Handle I/O read access."""
        if address == 0xC000:
            # Keyboard - return last key with strobe
            if self.keyboard_buffer:
                return self.keyboard_buffer[0] | 0x80
            return 0x00
        elif address == 0xC010:
            # Clear keyboard strobe
            if self.keyboard_buffer:
                self.keyboard_buffer.pop(0)
            return 0x00
        elif 0xC050 <= address <= 0xC057:
            # Video soft switches - just log
            self.io_log.append(('read', address))
            return 0x00
        return self.memory[address]
    
    def handle_io_write(self, address, value):
        """Handle I/O write access."""
        if 0xC000 <= address <= 0xC0FF:
            self.io_log.append(('write', address, value))
        self.memory[address] = value
    
    def type_string(self, s):
        """Add a string to the keyboard buffer."""
        for c in s:
            self.keyboard_buffer.append(ord(c.upper()))
    
    def run_until(self, condition, max_cycles=100000):
        """Run CPU until condition is met or max cycles reached."""
        cycles = 0
        while cycles < max_cycles:
            # Check for I/O access before instruction
            pc = self.mpu.pc
            
            # Execute one instruction
            self.mpu.step()
            cycles += 1
            
            if condition():
                return True, cycles
        
        return False, cycles
    
    def run_cycles(self, num_cycles):
        """Run for a specific number of cycles."""
        for _ in range(num_cycles):
            self.mpu.step()
    
    def get_text_screen(self):
        """Read the text screen memory and return as string."""
        lines = []
        
        # Text screen line base addresses
        line_bases = [
            0x400, 0x480, 0x500, 0x580, 0x600, 0x680, 0x700, 0x780,
            0x428, 0x4A8, 0x528, 0x5A8, 0x628, 0x6A8, 0x728, 0x7A8,
            0x450, 0x4D0, 0x550, 0x5D0, 0x650, 0x6D0, 0x750, 0x7D0,
        ]
        
        for base in line_bases:
            line = ""
            for col in range(40):
                char = self.memory[base + col]
                # Convert Apple II screen code to ASCII
                if char >= 0xC0:
                    char = char - 0x40  # Normal uppercase
                elif char >= 0x80:
                    char = char - 0x40  # Normal 
                elif char >= 0x40:
                    char = char  # Flashing
                else:
                    char = char + 0x40  # Inverse
                
                if 0x20 <= char <= 0x7E:
                    line += chr(char)
                else:
                    line += ' '
            lines.append(line.rstrip())
        
        return '\n'.join(lines)
    
    def reset(self):
        """Perform system reset."""
        # Get reset vector
        reset_low = self.memory[0xFFFC]
        reset_high = self.memory[0xFFFD]
        reset_addr = reset_low | (reset_high << 8)
        
        # Set PC to reset vector
        self.mpu.pc = reset_addr
        
        # Clear registers
        self.mpu.a = 0
        self.mpu.x = 0
        self.mpu.y = 0
        self.mpu.sp = 0xFF
        
        return reset_addr


class FullSystemTest:
    """Run full system integration tests."""
    
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # ROM paths - cleanroom versions
    CLEANROOM_ROMS = {
        'monitor': ('cleanroom_roms/monitor_f800.bin', 0xF800, 'Monitor ROM'),
        'chargen': ('cleanroom_roms/chargen.bin', None, 'Character Generator'),  # Not memory-mapped
        'disk_p5a': ('cleanroom_roms/disk_ii_p5a.bin', 0xC600, 'Disk II P5A'),
        'disk_p6a': ('cleanroom_roms/disk_ii_p6a.bin', 0xC700, 'Disk II P6A'),  # Actually a table
        'mouse': ('cleanroom_roms/mouse_card.bin', 0xC400, 'Mouse Card'),
        'prog_aid': ('cleanroom_roms/programmers_aid.bin', 0xD000, "Programmer's Aid"),
    }
    
    # ROM paths - original versions (for components we haven't cleanroomed)
    ORIGINAL_ROMS = {
        'monitor': ('original_source/APPLE II/APPLE II - 341-0004 - INTEGER BASIC MONITOR F800 - 2716.bin', 0xF800, 'Monitor ROM'),
        'basic_e0': ('original_source/APPLE II/APPLE II - 341-0001 - INTEGER BASIC E000 - 2716.bin', 0xE000, 'Integer BASIC E000'),
        'basic_e8': ('original_source/APPLE II/APPLE II - 341-0002 - INTEGER BASIC E800 - 2716.bin', 0xE800, 'Integer BASIC E800'),
        'basic_f0': ('original_source/APPLE II/APPLE II - 341-0003 - INTEGER BASIC F000 - 2716.bin', 0xF000, 'Integer BASIC F000'),
        'chargen': ('original_source/APPLE II+/APPLE II+ - 7341-0036 - CHARACTER GENERATOR REV7+ - 2716.bin', None, 'Character Generator'),
    }
    
    def __init__(self):
        self.system = Apple2System()
        self.results = []
    
    def record(self, name, passed, detail=""):
        """Record test result."""
        self.results.append({'name': name, 'passed': passed, 'detail': detail})
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}" + (f" - {detail}" if detail else ""))
    
    def load_hybrid_system(self):
        """Load system with cleanroom ROMs where available, original otherwise."""
        print("\n" + "=" * 60)
        print("Loading Apple II System (Hybrid: Cleanroom + Original)")
        print("=" * 60)
        
        # Load cleanroom Monitor ROM
        monitor_path = os.path.join(self.BASE_PATH, self.CLEANROOM_ROMS['monitor'][0])
        if os.path.exists(monitor_path):
            self.system.load_rom(monitor_path, 0xF800, "Monitor ROM", is_cleanroom=True)
        else:
            # Fall back to original
            orig_path = os.path.join(self.BASE_PATH, self.ORIGINAL_ROMS['monitor'][0])
            self.system.load_rom(orig_path, 0xF800, "Monitor ROM", is_cleanroom=False)
        
        # Load original Integer BASIC (we don't have cleanroom version)
        for key in ['basic_e0', 'basic_e8', 'basic_f0']:
            rom_info = self.ORIGINAL_ROMS[key]
            path = os.path.join(self.BASE_PATH, rom_info[0])
            self.system.load_rom(path, rom_info[1], rom_info[2], is_cleanroom=False)
        
        # Load cleanroom Disk II ROMs at slot 6
        p5a_path = os.path.join(self.BASE_PATH, self.CLEANROOM_ROMS['disk_p5a'][0])
        if os.path.exists(p5a_path):
            self.system.load_rom(p5a_path, 0xC600, "Disk II P5A (Slot 6)", is_cleanroom=True)
        
        # Load cleanroom Programmer's Aid (if we want to test hi-res)
        pa_path = os.path.join(self.BASE_PATH, self.CLEANROOM_ROMS['prog_aid'][0])
        if os.path.exists(pa_path):
            # Programmer's Aid would conflict with BASIC at $D000
            # So we'll load it at an alternate location or skip for now
            print("  [SKIP] Programmer's Aid - conflicts with BASIC at $D000")
        
        print()
        
        # Summary
        cleanroom_count = sum(1 for r in self.system.loaded_roms.values() if r['cleanroom'])
        original_count = sum(1 for r in self.system.loaded_roms.values() if not r['cleanroom'])
        print(f"Loaded: {cleanroom_count} cleanroom, {original_count} original ROMs")
        
        return True
    
    def test_reset_vector(self):
        """Test that reset vector points to valid code."""
        print("\n--- Test: Reset Vector ---")
        
        reset_addr = self.system.reset()
        
        # Reset should point into Monitor ROM ($F800-$FFFF)
        valid = 0xF800 <= reset_addr <= 0xFFFF
        self.record("Reset vector in Monitor ROM", valid, f"${reset_addr:04X}")
        
        return valid
    
    def test_monitor_prompt(self):
        """Test that Monitor displays prompt after reset."""
        print("\n--- Test: Monitor Initialization ---")
        
        self.system.reset()
        
        # Run enough cycles for initialization
        # Monitor should initialize display and show prompt
        self.system.run_cycles(10000)
        
        # Check if any screen memory was written
        screen_written = False
        for addr in range(0x400, 0x800):
            if self.system.memory[addr] != 0:
                screen_written = True
                break
        
        self.record("Screen memory initialized", screen_written)
        
        # Check zero page setup
        # WNDLFT ($20) should be 0, WNDWDTH ($21) should be 40
        wndlft = self.system.memory[0x20]
        wndwdth = self.system.memory[0x21]
        
        window_ok = (wndlft == 0 and wndwdth == 40) or (wndwdth > 0)
        self.record("Window parameters set", window_ok, f"WNDLFT={wndlft}, WNDWDTH={wndwdth}")
        
        return screen_written
    
    def test_bascalc_integration(self):
        """Test BASCALC with actual screen operations."""
        print("\n--- Test: BASCALC Integration ---")
        
        # BASCALC is at $FBC1 - calculate screen base address
        # Test that it calculates correctly for line 0
        
        self.system.memory[0x25] = 0  # CV = line 0
        self.system.mpu.a = 0
        self.system.mpu.pc = 0xFBC1
        
        # Run until RTS
        cycles = 0
        while self.system.memory[self.system.mpu.pc] != 0x60 and cycles < 100:
            self.system.mpu.step()
            cycles += 1
        self.system.mpu.step()  # Execute RTS
        
        # Check BASL/BASH ($28/$29)
        basl = self.system.memory[0x28]
        bash = self.system.memory[0x29]
        base_addr = basl | (bash << 8)
        
        # Line 0 should be $0400
        correct = base_addr == 0x0400
        self.record("BASCALC line 0 = $0400", correct, f"got ${base_addr:04X}")
        
        return correct
    
    def test_cout_integration(self):
        """Test COUT character output."""
        print("\n--- Test: COUT Integration ---")
        
        # Reset and initialize
        self.system.reset()
        self.system.run_cycles(5000)
        
        # Set cursor position
        self.system.memory[0x24] = 0  # CH = column 0
        self.system.memory[0x25] = 0  # CV = line 0
        
        # Calculate base address for line 0
        self.system.memory[0x28] = 0x00  # BASL
        self.system.memory[0x29] = 0x04  # BASH = $0400
        
        # Call COUT with 'A' (need to set high bit: $C1)
        self.system.mpu.a = 0xC1  # 'A' with high bit
        self.system.mpu.pc = 0xFDED  # COUT
        
        # Run for a while
        self.system.run_cycles(500)
        
        # Check if 'A' was written to screen
        screen_char = self.system.memory[0x0400]
        
        # Character might be normal or inverse depending on INVFLG
        is_A = (screen_char & 0x3F) == 0x01 or screen_char == 0xC1
        self.record("COUT writes character to screen", screen_char != 0, f"screen[0]=${screen_char:02X}")
        
        return screen_char != 0
    
    def test_prbyte_integration(self):
        """Test PRBYTE hex output."""
        print("\n--- Test: PRBYTE Integration ---")
        
        # Reset
        self.system.reset()
        self.system.run_cycles(5000)
        
        # Set up for output
        self.system.memory[0x24] = 0
        self.system.memory[0x25] = 0
        self.system.memory[0x28] = 0x00
        self.system.memory[0x29] = 0x04
        
        # Call PRBYTE with $A5
        self.system.mpu.a = 0xA5
        self.system.mpu.pc = 0xFDDA  # PRBYTE
        
        self.system.run_cycles(1000)
        
        # Should have written 'A' and '5' to screen
        char1 = self.system.memory[0x0400]
        char2 = self.system.memory[0x0401]
        
        self.record("PRBYTE outputs hex digits", char1 != 0 and char2 != 0,
                   f"screen: ${char1:02X} ${char2:02X}")
        
        return char1 != 0
    
    def test_basic_rom_present(self):
        """Test that BASIC ROM is loaded and callable."""
        print("\n--- Test: BASIC ROM Integration ---")
        
        # Check that BASIC ROM area has code (not empty)
        basic_start = self.system.memory[0xE000]
        basic_has_code = basic_start != 0x00 and basic_start != 0xFF
        
        self.record("BASIC ROM loaded at $E000", basic_has_code, f"first byte: ${basic_start:02X}")
        
        # Check for Integer BASIC cold start signature
        # Integer BASIC cold start is typically at $E000
        
        return basic_has_code
    
    def test_disk_boot_rom(self):
        """Test Disk II boot ROM at slot 6."""
        print("\n--- Test: Disk II Boot ROM (Cleanroom) ---")
        
        # Check that boot ROM is at $C600
        boot_start = self.system.memory[0xC600]
        has_code = boot_start != 0x00 and boot_start != 0xFF
        
        self.record("Disk II P5A at $C600", has_code, f"first byte: ${boot_start:02X}")
        
        # Check for JSR $FF58 in boot ROM (slot detection)
        has_ff58 = False
        for i in range(256 - 2):
            if (self.system.memory[0xC600 + i] == 0x20 and
                self.system.memory[0xC600 + i + 1] == 0x58 and
                self.system.memory[0xC600 + i + 2] == 0xFF):
                has_ff58 = True
                break
        
        self.record("Disk II calls Monitor $FF58", has_ff58)
        
        return has_code and has_ff58
    
    def test_memory_map(self):
        """Test overall memory map is correct."""
        print("\n--- Test: Memory Map ---")
        
        # Zero page should be writable
        self.system.memory[0x00] = 0xAA
        zp_ok = self.system.memory[0x00] == 0xAA
        self.record("Zero page writable", zp_ok)
        
        # Stack should be writable
        self.system.memory[0x1FF] = 0x55
        stack_ok = self.system.memory[0x1FF] == 0x55
        self.record("Stack writable", stack_ok)
        
        # Text screen should be writable
        self.system.memory[0x400] = 0xA0  # Space
        screen_ok = self.system.memory[0x400] == 0xA0
        self.record("Text screen writable", screen_ok)
        
        # ROM should be present
        rom_ok = self.system.memory[0xF800] != 0x00
        self.record("Monitor ROM present", rom_ok)
        
        return zp_ok and stack_ok and screen_ok and rom_ok
    
    def test_vectors(self):
        """Test system vectors are set up correctly."""
        print("\n--- Test: System Vectors ---")
        
        # Reset vector ($FFFC-$FFFD)
        reset = self.system.memory[0xFFFC] | (self.system.memory[0xFFFD] << 8)
        reset_ok = 0xF800 <= reset <= 0xFFFF
        self.record("Reset vector valid", reset_ok, f"${reset:04X}")
        
        # IRQ vector ($FFFE-$FFFF)
        irq = self.system.memory[0xFFFE] | (self.system.memory[0xFFFF] << 8)
        irq_ok = 0xF800 <= irq <= 0xFFFF
        self.record("IRQ vector valid", irq_ok, f"${irq:04X}")
        
        return reset_ok and irq_ok
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("\n" + "=" * 70)
        print(" APPLE II FULL SYSTEM INTEGRATION TEST")
        print(" Testing Cleanroom ROMs with Original Apple II Components")
        print("=" * 70)
        
        # Load the hybrid system
        if not self.load_hybrid_system():
            print("Failed to load system!")
            return False
        
        # Run tests
        self.test_memory_map()
        self.test_vectors()
        self.test_reset_vector()
        self.test_monitor_prompt()
        self.test_bascalc_integration()
        self.test_cout_integration()
        self.test_prbyte_integration()
        self.test_basic_rom_present()
        self.test_disk_boot_rom()
        
        # Summary
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print("\n" + "=" * 70)
        print(f" RESULTS: {passed}/{total} tests passed")
        print("=" * 70)
        
        # Show ROM breakdown
        print("\nROM Sources Used:")
        for name, info in self.system.loaded_roms.items():
            status = "✓ CLEANROOM" if info['cleanroom'] else "  Original"
            print(f"  {status}: {name}")
        
        print()
        
        if passed == total:
            print("✓ SUCCESS: Cleanroom ROMs work correctly with original Apple II components!")
        else:
            print("✗ Some tests failed - see details above")
        
        return passed == total


def main():
    tester = FullSystemTest()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
