"""
Apple II Monitor ROM Test Suite

This module tests the functionality of the Apple II Monitor ROM ($F800-$FFFF).
These tests verify that both original and cleanroom ROMs produce identical results.
"""

import os
import sys
import hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apple2_emulator import Apple2Emulator, Apple2Memory


# ============================================================================
# Monitor ROM Entry Points (Apple II with Integer BASIC)
# ============================================================================

MONITOR_VECTORS = {
    # Core entry points from disassembly
    'PRBYTE':   0xFDDA,  # Print A as two hex digits
    'PRHEX':    0xFDE3,  # Print low nibble (AND #$0F first)
    'PRHEXZ':   0xFDE5,  # Print low nibble (assumes masked)
    'COUT':     0xFDED,  # JMP ($0036) - character output
    'COUT1':    0xFDF0,  # Actual output routine
    'BASCALC':  0xFBC1,  # Calculate screen base address
    'WAIT':     0xFCA8,  # Delay routine
    'SETINV':   0xFE80,  # Set inverse mode
    'SETNORM':  0xFE84,  # Set normal mode
    'INIT':     0xFB2F,  # Initialize system
    'BELL':     0xFBDD,  # Ring bell
    'HOME':     0xFC58,  # Clear screen
    'VTAB':     0xFC22,  # Set vertical tab
    'CROUT':    0xFD8E,  # Print carriage return
    'RESET':    0xFF59,  # Reset entry point
}


class MonitorROMTest:
    """Test harness for Apple II Monitor ROM."""
    
    def __init__(self, rom_path, description="Monitor ROM"):
        self.rom_path = rom_path
        self.description = description
        self.emu = None
        self.results = []
        self.output_chars = []
    
    def setup(self):
        """Initialize emulator and load ROM."""
        self.emu = Apple2Emulator()
        
        # Load the monitor ROM at $F800
        if os.path.exists(self.rom_path):
            self.emu.load_rom_file(self.rom_path, 0xF800)
            
            # Set up COUT vector to capture output
            # We'll create a small capture routine at $0300
            self._setup_output_capture()
            
            return True
        return False
    
    def _setup_output_capture(self):
        """Set up output capture routine at $0300."""
        # Create a routine that:
        # 1. Stores character to output buffer
        # 2. Writes to screen at (BASL),Y position  
        # 3. Increments CH (cursor position)
        # 4. Returns via RTS
        #
        # $0300: LDX $2E       ; Get output index
        # $0302: STA $0350,X   ; Store to output buffer
        # $0305: INC $2E       ; Increment index
        # $0307: STA ($28),Y   ; Store to screen
        # $0309: INC $24       ; Increment CH
        # $030B: RTS
        capture_code = [
            0xA6, 0x2E,              # LDX $2E (use $2E as output index)
            0x9D, 0x50, 0x03,        # STA $0350,X  
            0xE6, 0x2E,              # INC $2E
            0x91, 0x28,              # STA ($28),Y
            0xE6, 0x24,              # INC $24
            0x60                     # RTS
        ]
        for i, byte in enumerate(capture_code):
            self.emu.memory.memory[0x0300 + i] = byte
        
        # Clear output buffer index
        self.emu.memory.memory[0x2E] = 0
        
        # Set COUT vector (CSWL/CSWH at $36-$37) to our capture routine
        self.emu.memory.memory[0x36] = 0x00
        self.emu.memory.memory[0x37] = 0x03
    
    def reset_emulator(self):
        """Reset emulator to known state."""
        self.output_chars = []
        
        # Initialize zero page variables
        self.emu.memory.memory[0x20] = 0     # WNDLFT
        self.emu.memory.memory[0x21] = 40    # WNDWDTH  
        self.emu.memory.memory[0x22] = 0     # WNDTOP
        self.emu.memory.memory[0x23] = 24    # WNDBTM
        self.emu.memory.memory[0x24] = 0     # CH
        self.emu.memory.memory[0x25] = 0     # CV
        self.emu.memory.memory[0x28] = 0x00  # BASL
        self.emu.memory.memory[0x29] = 0x04  # BASH (screen page 1)
        self.emu.memory.memory[0x2E] = 0     # Output buffer index
        self.emu.memory.memory[0x32] = 0xFF  # INVFLG (normal mode)
        self.emu.memory.memory[0x33] = 0xAA  # PROMPT ('*')
        self.emu.memory.memory[0x35] = 0x00  # YSAV1
        
        # Set COUT vector
        self.emu.memory.memory[0x36] = 0x00
        self.emu.memory.memory[0x37] = 0x03
        
        # Clear text screen
        for addr in range(0x400, 0x800):
            self.emu.memory.memory[addr] = 0xA0  # Space
        
        # Clear output buffer
        for addr in range(0x350, 0x380):
            self.emu.memory.memory[addr] = 0
        
        # Reset CPU state
        self.emu.cpu.sp = 0xFF
        self.emu.cpu.p = 0x24
        self.emu.cpu.a = 0
        self.emu.cpu.x = 0
        self.emu.cpu.y = 0
    
    def record_result(self, test_name, passed, expected, actual, details=""):
        """Record a test result."""
        self.results.append({
            'test': test_name,
            'passed': passed,
            'expected': expected,
            'actual': actual,
            'details': details
        })
    
    def get_rom_checksum(self):
        """Calculate MD5 checksum of ROM."""
        with open(self.rom_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def run_all_tests(self):
        """Run all monitor ROM tests."""
        if not self.setup():
            print(f"ERROR: Could not load ROM from {self.rom_path}")
            return False
        
        print(f"\n{'='*60}")
        print(f"Testing: {self.description}")
        print(f"ROM Path: {self.rom_path}")
        print(f"ROM MD5:  {self.get_rom_checksum()}")
        print(f"{'='*60}")
        
        # Run each test category
        self.test_vectors()
        self.test_bascalc()
        self.test_prhex_algorithm()
        self.test_prbyte_algorithm()
        self.test_setinv_setnorm()
        self.test_wait_timing()
        
        # Print summary
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print(f"\n{'-'*60}")
        print(f"Results: {passed}/{total} tests passed")
        print(f"{'-'*60}")
        
        for r in self.results:
            status = "✓ PASS" if r['passed'] else "✗ FAIL"
            print(f"  {status}: {r['test']}")
            if not r['passed']:
                print(f"         Expected: {r['expected']}")
                print(f"         Actual:   {r['actual']}")
            if r['details']:
                print(f"         Details:  {r['details']}")
        
        return all(r['passed'] for r in self.results)
    
    def test_vectors(self):
        """Verify system vectors."""
        print("\n--- Testing System Vectors ---")
        
        # Check reset vector
        reset_low = self.emu.memory[0xFFFC]
        reset_high = self.emu.memory[0xFFFD]
        reset_vector = (reset_high << 8) | reset_low
        
        valid = 0xF800 <= reset_vector <= 0xFFFF
        self.record_result(
            "Reset vector in ROM range",
            valid,
            "$F800-$FFFF",
            f"${reset_vector:04X}"
        )
        
        # Check IRQ/BRK vector  
        irq_low = self.emu.memory[0xFFFE]
        irq_high = self.emu.memory[0xFFFF]
        irq_vector = (irq_high << 8) | irq_low
        
        valid = 0xF800 <= irq_vector <= 0xFFFF
        self.record_result(
            "IRQ/BRK vector in ROM range",
            valid,
            "$F800-$FFFF", 
            f"${irq_vector:04X}"
        )
        
        # Check PRBYTE starts with PHA
        opcode = self.emu.memory[MONITOR_VECTORS['PRBYTE']]
        self.record_result(
            "PRBYTE starts with PHA ($48)",
            opcode == 0x48,
            "$48",
            f"${opcode:02X}"
        )
        
        # Check BASCALC starts with PHA
        opcode = self.emu.memory[MONITOR_VECTORS['BASCALC']]
        self.record_result(
            "BASCALC starts with PHA ($48)",
            opcode == 0x48,
            "$48",
            f"${opcode:02X}"
        )
        
        # Check WAIT starts with SEC
        opcode = self.emu.memory[MONITOR_VECTORS['WAIT']]
        self.record_result(
            "WAIT starts with SEC ($38)",
            opcode == 0x38,
            "$38",
            f"${opcode:02X}"
        )
    
    def test_bascalc(self):
        """Test BASCALC routine - screen address calculation."""
        print("\n--- Testing BASCALC ---")
        
        # Expected base addresses for each line (Apple II screen layout)
        expected_bases = [
            0x0400, 0x0480, 0x0500, 0x0580, 0x0600, 0x0680, 0x0700, 0x0780,
            0x0428, 0x04A8, 0x0528, 0x05A8, 0x0628, 0x06A8, 0x0728, 0x07A8,
            0x0450, 0x04D0, 0x0550, 0x05D0, 0x0650, 0x06D0, 0x0750, 0x07D0,
        ]
        
        for line, expected_addr in enumerate(expected_bases):
            self.reset_emulator()
            
            # Call BASCALC with line number in A
            result = self.emu.call_subroutine(MONITOR_VECTORS['BASCALC'], a=line)
            
            if result['completed']:
                basl = self.emu.memory[0x28]
                bash = self.emu.memory[0x29]
                actual_addr = (bash << 8) | basl
                
                passed = actual_addr == expected_addr
                self.record_result(
                    f"BASCALC line {line}",
                    passed,
                    f"${expected_addr:04X}",
                    f"${actual_addr:04X}",
                    f"Cycles: {result['cycles']}"
                )
            else:
                self.record_result(
                    f"BASCALC line {line}",
                    False,
                    f"${expected_addr:04X}",
                    "TIMEOUT"
                )
    
    def test_prhex_algorithm(self):
        """Test PRHEX by examining algorithm behavior."""
        print("\n--- Testing PRHEX Algorithm ---")
        
        # PRHEX algorithm at $FDE3:
        #   AND #$0F      ; Mask to low nibble
        #   ORA #$B0      ; Convert to '0'-'9' range + $80
        #   CMP #$BA      ; Is it > '9'?
        #   BCC COUT      ; No, output
        #   ADC #$06      ; Yes, add 6 (+ 1 for carry = 7) to get 'A'-'F'
        #   JMP COUT
        
        # Expected output characters (with high bit set)
        expected = {
            0x00: 0xB0, 0x01: 0xB1, 0x02: 0xB2, 0x03: 0xB3,
            0x04: 0xB4, 0x05: 0xB5, 0x06: 0xB6, 0x07: 0xB7,
            0x08: 0xB8, 0x09: 0xB9, 0x0A: 0xC1, 0x0B: 0xC2,
            0x0C: 0xC3, 0x0D: 0xC4, 0x0E: 0xC5, 0x0F: 0xC6,
        }
        
        for value, expected_char in expected.items():
            self.reset_emulator()
            
            # Call PRHEX entry point
            result = self.emu.call_subroutine(MONITOR_VECTORS['PRHEX'], a=value, y=0)
            
            if result['completed']:
                # Get character from output buffer at $0350
                actual_char = self.emu.memory[0x0350]
                
                # Fallback: check screen location at $0400
                if actual_char == 0:
                    actual_char = self.emu.memory[0x0400]
                
                expected_ascii = chr(expected_char & 0x7F)
                actual_ascii = chr(actual_char & 0x7F) if actual_char else '?'
                
                passed = (actual_char & 0x7F) == (expected_char & 0x7F)
                self.record_result(
                    f"PRHEX(${value:X})",
                    passed,
                    f"'{expected_ascii}' (${expected_char:02X})",
                    f"'{actual_ascii}' (${actual_char:02X})",
                    f"Cycles: {result['cycles']}"
                )
            else:
                self.record_result(
                    f"PRHEX(${value:X})",
                    False,
                    f"${expected_char:02X}",
                    "TIMEOUT"
                )
    
    def test_prbyte_algorithm(self):
        """Test PRBYTE output."""
        print("\n--- Testing PRBYTE ---")
        
        test_cases = [
            (0x00, "00"), (0x0F, "0F"), (0xF0, "F0"), (0xFF, "FF"),
            (0x12, "12"), (0xAB, "AB"), (0x7E, "7E"), (0xA5, "A5"),
        ]
        
        for value, expected in test_cases:
            self.reset_emulator()
            
            # Call PRBYTE
            result = self.emu.call_subroutine(MONITOR_VECTORS['PRBYTE'], a=value, y=0)
            
            if result['completed']:
                # Read two characters from output buffer
                char1 = self.emu.memory[0x0350]
                char2 = self.emu.memory[0x0351]
                
                # Fallback: read from screen
                if char1 == 0:
                    char1 = self.emu.memory[0x400]
                    char2 = self.emu.memory[0x401]
                
                actual = chr(char1 & 0x7F) + chr(char2 & 0x7F)
                
                passed = actual == expected
                self.record_result(
                    f"PRBYTE(${value:02X})",
                    passed,
                    expected,
                    actual,
                    f"Cycles: {result['cycles']}"
                )
            else:
                self.record_result(
                    f"PRBYTE(${value:02X})",
                    False,
                    expected,
                    "TIMEOUT"
                )
    
    def test_setinv_setnorm(self):
        """Test display mode routines."""
        print("\n--- Testing SETINV/SETNORM ---")
        
        # Test SETNORM
        self.reset_emulator()
        self.emu.memory.memory[0x32] = 0x00  # Start with different value
        
        result = self.emu.call_subroutine(MONITOR_VECTORS['SETNORM'])
        
        if result['completed']:
            invflg = self.emu.memory[0x32]
            self.record_result(
                "SETNORM sets INVFLG",
                invflg == 0xFF,
                "$FF",
                f"${invflg:02X}",
                f"Cycles: {result['cycles']}"
            )
        else:
            self.record_result("SETNORM", False, "$FF", "TIMEOUT")
        
        # Test SETINV
        self.reset_emulator()
        self.emu.memory.memory[0x32] = 0xFF
        
        result = self.emu.call_subroutine(MONITOR_VECTORS['SETINV'])
        
        if result['completed']:
            invflg = self.emu.memory[0x32]
            self.record_result(
                "SETINV sets INVFLG",
                invflg == 0x3F,
                "$3F",
                f"${invflg:02X}",
                f"Cycles: {result['cycles']}"
            )
        else:
            self.record_result("SETINV", False, "$3F", "TIMEOUT")
    
    def test_wait_timing(self):
        """Test WAIT routine timing."""
        print("\n--- Testing WAIT Timing ---")
        
        # WAIT algorithm:
        #   SEC
        # WAIT2: PHA
        # WAIT3: SBC #$01
        #   BNE WAIT3
        #   PLA
        #   SBC #$01  
        #   BNE WAIT2
        #   RTS
        #
        # Inner loop: (A-1) * 5 cycles each iteration = 5*(A-1)+4 per outer
        # Outer loop: PHA(3) + inner + PLA(4) + SBC(2) + BNE(3) = varies
        
        test_values = [1, 2, 5, 10, 20]
        
        for value in test_values:
            self.reset_emulator()
            
            result = self.emu.call_subroutine(MONITOR_VECTORS['WAIT'], a=value)
            
            if result['completed']:
                # Just verify it completes - exact timing varies
                self.record_result(
                    f"WAIT({value})",
                    True,
                    "Completes",
                    f"{result['cycles']} cycles"
                )
            else:
                self.record_result(
                    f"WAIT({value})",
                    False,
                    "Completes",
                    "TIMEOUT"
                )


def compare_roms(original_path, cleanroom_path):
    """Compare behavior of original and cleanroom ROMs."""
    print("\n" + "="*60)
    print("ROM COMPARISON TEST")
    print("="*60)
    
    original_test = MonitorROMTest(original_path, "Original Monitor ROM")
    cleanroom_test = MonitorROMTest(cleanroom_path, "Cleanroom Monitor ROM")
    
    original_test.run_all_tests()
    cleanroom_test.run_all_tests()
    
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    
    # Compare results
    orig_results = {r['test']: r for r in original_test.results}
    clean_results = {r['test']: r for r in cleanroom_test.results}
    
    all_match = True
    for test_name in sorted(orig_results.keys()):
        orig = orig_results[test_name]
        clean = clean_results.get(test_name)
        
        if clean is None:
            print(f"  MISSING: {test_name}")
            all_match = False
        elif orig['actual'] != clean['actual']:
            print(f"  MISMATCH: {test_name}")
            print(f"    Original:  {orig['actual']}")
            print(f"    Cleanroom: {clean['actual']}")
            all_match = False
        else:
            print(f"  ✓ MATCH: {test_name}")
    
    print(f"\n{'='*60}")
    if all_match:
        print("SUCCESS: All tests produce identical results!")
    else:
        print("FAILURE: Some tests produced different results")
    print("="*60)
    
    return all_match


def main():
    """Run monitor ROM tests."""
    original_path = "/workspace/original_source/APPLE II/APPLE II - 341-0004 - INTEGER BASIC MONITOR F800 - 2716.bin"
    
    test = MonitorROMTest(original_path, "Original Apple II Monitor ROM")
    test.run_all_tests()
    
    # Check for cleanroom ROM
    cleanroom_path = "/workspace/cleanroom_roms/monitor_f800.bin"
    if os.path.exists(cleanroom_path):
        compare_roms(original_path, cleanroom_path)


if __name__ == "__main__":
    main()
