#!/usr/bin/env python3
"""
Apple II Cleanroom ROM Demo

Full 40x24 character display with EVERY character rendered using
the actual pixel patterns from the cleanroom character generator ROM.

Display: 40 columns × 24 rows = 280×192 pixels
Rendered using Unicode half-blocks (▀▄█) = 280×96 terminal cells

Requires a wide terminal (~285 columns) for proper display.
"""

import os
import sys
import time
import signal

# ANSI escape sequences
class Term:
    CLEAR = "\033[2J\033[H"
    RESET = "\033[0m"
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"
    HOME = "\033[H"
    
    # Colors - Apple II green phosphor P1
    GREEN_BRIGHT = "\033[38;2;51;255;51m"
    GREEN_DIM = "\033[38;2;20;100;20m"
    GREEN_DARK = "\033[38;2;5;40;5m"
    BG_BLACK = "\033[48;2;0;10;0m"


class CharacterGeneratorROM:
    """
    Cleanroom Character Generator ROM
    
    Loads the 2KB character ROM and provides pixel patterns for all 64 characters.
    Each character is 7 pixels wide × 8 pixels tall.
    
    ROM Layout (from our cleanroom implementation):
    - 64 characters, 8 bytes each
    - Index 0-31: ASCII 64-95 (@ A B C ... Z [ \\ ] ^ _)
    - Index 32-63: ASCII 32-63 (space ! " # ... < = > ?)
    - Each byte is one row, bit 0 = leftmost pixel, bit 6 = rightmost
    """
    
    def __init__(self, rom_path):
        self.patterns = {}
        self.rom_data = None
        self.load(rom_path)
    
    def load(self, rom_path):
        """Load character patterns from ROM file."""
        if not os.path.exists(rom_path):
            print(f"ERROR: Character ROM not found: {rom_path}")
            print("Run: python3 cleanroom_roms/build_chargen.py")
            sys.exit(1)
        
        with open(rom_path, 'rb') as f:
            self.rom_data = f.read()
        
        if len(self.rom_data) < 512:
            print(f"ERROR: Character ROM too small: {len(self.rom_data)} bytes")
            sys.exit(1)
        
        # Extract patterns from bank 0 (first 512 bytes = 64 chars × 8 bytes)
        for char_index in range(64):
            offset = char_index * 8
            self.patterns[char_index] = list(self.rom_data[offset:offset + 8])
    
    def ascii_to_rom_index(self, ascii_code):
        """Convert ASCII code to ROM character index."""
        if 64 <= ascii_code <= 95:
            # @ A B C ... Z [ \ ] ^ _
            return ascii_code - 64
        elif 32 <= ascii_code <= 63:
            # space ! " # $ % & ' ( ) * + , - . / 0-9 : ; < = > ?
            return ascii_code
        elif 97 <= ascii_code <= 122:
            # Lowercase a-z maps to uppercase A-Z
            return ascii_code - 97 + 1
        else:
            # Unknown characters become space
            return 32
    
    def get_pattern(self, char):
        """
        Get the 8-byte pixel pattern for a character.
        
        Args:
            char: Single character string or ASCII code
            
        Returns:
            List of 8 bytes, each byte represents one row.
            Bit 0 = leftmost pixel, Bit 6 = rightmost pixel.
        """
        if isinstance(char, str):
            if len(char) == 0:
                ascii_code = 32  # space
            else:
                ascii_code = ord(char[0])
        else:
            ascii_code = char
        
        rom_index = self.ascii_to_rom_index(ascii_code)
        return self.patterns.get(rom_index, [0] * 8)


class Apple2TextDisplay:
    """
    Apple II 40×24 Text Display
    
    Renders every character using actual pixel data from the character ROM.
    Output is 280 pixels wide × 192 pixels tall.
    Uses Unicode half-blocks to render 2 vertical pixels per terminal cell.
    Final output: 280 columns × 96 rows of terminal characters.
    """
    
    # Unicode half-block characters for rendering 2 vertical pixels
    HALF_BLOCKS = {
        (False, False): ' ',  # Neither pixel lit
        (True, False): '▀',   # Top pixel lit
        (False, True): '▄',   # Bottom pixel lit
        (True, True): '█',    # Both pixels lit
    }
    
    def __init__(self, character_rom):
        self.char_rom = character_rom
        
        # Display dimensions
        self.text_cols = 40
        self.text_rows = 24
        
        # Pixel dimensions (each char is 7×8 pixels)
        self.pixel_width = self.text_cols * 7   # 280
        self.pixel_height = self.text_rows * 8  # 192
        
        # Text buffer (what characters are on screen)
        self.text_buffer = []
        for row in range(self.text_rows):
            self.text_buffer.append([' '] * self.text_cols)
        
        # Cursor position
        self.cursor_col = 0
        self.cursor_row = 0
        self.cursor_visible = True
        self.cursor_blink_state = True
    
    def clear_screen(self):
        """Clear the entire screen."""
        for row in range(self.text_rows):
            for col in range(self.text_cols):
                self.text_buffer[row][col] = ' '
        self.cursor_col = 0
        self.cursor_row = 0
    
    def scroll_up(self):
        """Scroll the screen up by one line."""
        # Remove top line
        self.text_buffer.pop(0)
        # Add blank line at bottom
        self.text_buffer.append([' '] * self.text_cols)
    
    def newline(self):
        """Move cursor to start of next line, scrolling if needed."""
        self.cursor_col = 0
        self.cursor_row += 1
        if self.cursor_row >= self.text_rows:
            self.scroll_up()
            self.cursor_row = self.text_rows - 1
    
    def carriage_return(self):
        """Move cursor to start of current line."""
        self.cursor_col = 0
    
    def backspace(self):
        """Move cursor back one position and erase character."""
        if self.cursor_col > 0:
            self.cursor_col -= 1
            self.text_buffer[self.cursor_row][self.cursor_col] = ' '
    
    def put_char(self, char):
        """
        Put a character at the cursor position and advance cursor.
        Handles special characters: newline, carriage return, backspace.
        """
        if char == '\n':
            self.newline()
        elif char == '\r':
            self.carriage_return()
        elif char == '\b' or char == '\x7f':
            self.backspace()
        elif char == '\t':
            # Tab to next 8-column boundary
            spaces = 8 - (self.cursor_col % 8)
            for _ in range(spaces):
                self.put_char(' ')
        else:
            # Regular character - convert to uppercase for authenticity
            display_char = char.upper() if char.isalpha() else char
            
            # Place character in buffer
            if 0 <= self.cursor_row < self.text_rows and 0 <= self.cursor_col < self.text_cols:
                self.text_buffer[self.cursor_row][self.cursor_col] = display_char
                self.cursor_col += 1
                
                # Wrap to next line if past end
                if self.cursor_col >= self.text_cols:
                    self.newline()
    
    def write(self, text):
        """Write a string to the display."""
        for char in text:
            self.put_char(char)
    
    def render_to_pixels(self):
        """
        Render the entire text buffer to a pixel buffer.
        
        Returns:
            2D list of booleans, [row][col], True = pixel lit
        """
        # Create pixel buffer
        pixels = []
        for y in range(self.pixel_height):
            pixels.append([False] * self.pixel_width)
        
        # Render each character
        for text_row in range(self.text_rows):
            for text_col in range(self.text_cols):
                char = self.text_buffer[text_row][text_col]
                
                # Check if this is the cursor position
                is_cursor = (text_row == self.cursor_row and 
                           text_col == self.cursor_col and 
                           self.cursor_visible and 
                           self.cursor_blink_state)
                
                if is_cursor:
                    # Cursor is a solid block
                    pattern = [0x7F, 0x7F, 0x7F, 0x7F, 0x7F, 0x7F, 0x7F, 0x7F]
                else:
                    # Get pattern from ROM
                    pattern = self.char_rom.get_pattern(char)
                
                # Calculate pixel position for this character
                pixel_x = text_col * 7
                pixel_y = text_row * 8
                
                # Plot pixels
                for row_offset in range(8):
                    row_byte = pattern[row_offset]
                    for bit in range(7):
                        if row_byte & (1 << bit):
                            px = pixel_x + bit
                            py = pixel_y + row_offset
                            if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                                pixels[py][px] = True
        
        return pixels
    
    def render(self):
        """
        Render the display to the terminal.
        Uses half-block characters to show 2 vertical pixels per terminal cell.
        """
        pixels = self.render_to_pixels()
        
        # Build output string
        output_lines = []
        
        # Top border
        border_char = "═"
        corner_tl = "╔"
        corner_tr = "╗"
        corner_bl = "╚"
        corner_br = "╝"
        side = "║"
        
        output_lines.append(f"{Term.GREEN_DIM}{corner_tl}{border_char * (self.pixel_width + 2)}{corner_tr}")
        output_lines.append(f"{side} {' ' * self.pixel_width} {side}")
        
        # Render pixels using half-blocks (2 rows at a time)
        for y in range(0, self.pixel_height, 2):
            line = f"{Term.GREEN_DIM}{side} {Term.GREEN_BRIGHT}"
            
            for x in range(self.pixel_width):
                top_pixel = pixels[y][x]
                bottom_pixel = pixels[y + 1][x] if (y + 1) < self.pixel_height else False
                
                block_char = self.HALF_BLOCKS[(top_pixel, bottom_pixel)]
                line += block_char
            
            line += f" {Term.GREEN_DIM}{side}"
            output_lines.append(line)
        
        # Bottom border
        output_lines.append(f"{side} {' ' * self.pixel_width} {side}")
        output_lines.append(f"{corner_bl}{border_char * (self.pixel_width + 2)}{corner_br}")
        
        # Status line
        output_lines.append(f"{Term.GREEN_DIM}  [APPLE II CLEANROOM - 40×24 CHARS - 280×192 PIXELS - ALL FROM CHARACTER ROM]{Term.RESET}")
        
        # Output everything
        sys.stdout.write(Term.CLEAR)
        sys.stdout.write(Term.HIDE_CURSOR)
        sys.stdout.write(f"{Term.BG_BLACK}")
        sys.stdout.write('\n'.join(output_lines))
        sys.stdout.write(Term.RESET)
        sys.stdout.write('\n')
        sys.stdout.flush()


class Apple2BasicInterpreter:
    """
    Simple BASIC interpreter for the Apple II demo.
    """
    
    def __init__(self, display):
        self.display = display
        self.variables = {}
        self.program = {}  # Line number -> code
        self.running = True
    
    def print_startup_message(self):
        """Display startup message."""
        self.display.write("APPLE II CLEANROOM BASIC\n")
        self.display.write("\n")
        self.display.write("ALL TEXT RENDERED FROM\n")
        self.display.write("CHARACTER GENERATOR ROM\n")
        self.display.write("\n")
        self.display.write("TYPE 'HELP' FOR COMMANDS\n")
        self.display.write("\n")
    
    def prompt(self):
        """Show the ] prompt."""
        self.display.write("]")
    
    def execute_line(self, line):
        """Execute a line of BASIC."""
        line = line.strip()
        if not line:
            return None
        
        # Check for line number (program entry)
        if line[0].isdigit():
            return self.store_program_line(line)
        
        # Parse command
        parts = line.split(None, 1)
        command = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ""
        
        # Command dispatch
        commands = {
            'PRINT': self.cmd_print,
            '?': self.cmd_print,
            'LIST': self.cmd_list,
            'RUN': self.cmd_run,
            'NEW': self.cmd_new,
            'CLR': self.cmd_clr,
            'HOME': self.cmd_home,
            'HELP': self.cmd_help,
            'QUIT': self.cmd_quit,
            'EXIT': self.cmd_quit,
            'BYE': self.cmd_quit,
        }
        
        if command in commands:
            return commands[command](args)
        elif '=' in line:
            return self.cmd_let(line)
        else:
            return "?SYNTAX ERROR\n"
    
    def store_program_line(self, line):
        """Store a numbered line in the program."""
        parts = line.split(None, 1)
        try:
            line_num = int(parts[0])
        except ValueError:
            return "?SYNTAX ERROR\n"
        
        if len(parts) > 1:
            self.program[line_num] = parts[1]
        elif line_num in self.program:
            del self.program[line_num]
        
        return None
    
    def cmd_print(self, args):
        """PRINT statement."""
        if not args:
            return "\n"
        
        result = []
        i = 0
        
        while i < len(args):
            # Skip whitespace
            while i < len(args) and args[i] == ' ':
                i += 1
            
            if i >= len(args):
                break
            
            if args[i] == '"':
                # String literal
                i += 1
                string_val = ""
                while i < len(args) and args[i] != '"':
                    string_val += args[i]
                    i += 1
                result.append(string_val)
                if i < len(args):
                    i += 1  # Skip closing quote
            
            elif args[i] == ';':
                # Semicolon - no separator
                i += 1
            
            elif args[i] == ',':
                # Comma - tab separator
                result.append("        ")  # 8 spaces for tab
                i += 1
            
            else:
                # Expression or variable
                expr_start = i
                while i < len(args) and args[i] not in ' ;,"':
                    i += 1
                expr = args[expr_start:i]
                
                try:
                    value = eval(expr, {"__builtins__": {}}, self.variables)
                    result.append(str(value))
                except:
                    result.append("0")
        
        return ''.join(result) + "\n"
    
    def cmd_list(self, args):
        """LIST command."""
        if not self.program:
            return None
        
        lines = []
        for line_num in sorted(self.program.keys()):
            lines.append(f" {line_num}  {self.program[line_num]}")
        
        return '\n'.join(lines) + "\n"
    
    def cmd_run(self, args):
        """RUN command - execute the stored program."""
        if not self.program:
            return None
        
        output = []
        self.variables.clear()
        
        line_numbers = sorted(self.program.keys())
        program_counter = 0
        for_stack = []  # Stack for FOR/NEXT loops
        
        iteration_limit = 10000
        iterations = 0
        
        while program_counter < len(line_numbers) and iterations < iteration_limit:
            iterations += 1
            
            current_line_num = line_numbers[program_counter]
            code = self.program[current_line_num]
            
            # Parse the statement
            parts = code.split(None, 1)
            cmd = parts[0].upper() if parts else ""
            cmd_args = parts[1] if len(parts) > 1 else ""
            
            if cmd in ('PRINT', '?'):
                result = self.cmd_print(cmd_args)
                if result:
                    output.append(result.rstrip('\n'))
                program_counter += 1
            
            elif cmd == 'GOTO':
                try:
                    target = int(cmd_args.strip())
                    if target in line_numbers:
                        program_counter = line_numbers.index(target)
                    else:
                        output.append("?UNDEF'D STATEMENT ERROR")
                        break
                except:
                    output.append("?SYNTAX ERROR")
                    break
            
            elif cmd == 'FOR':
                # FOR I = 1 TO 10 [STEP 1]
                try:
                    # Parse: VAR = START TO END [STEP S]
                    for_parts = cmd_args.replace('=', ' ').upper().split()
                    var_name = for_parts[0]
                    start_val = int(for_parts[1])
                    to_index = for_parts.index('TO')
                    end_val = int(for_parts[to_index + 1])
                    
                    step_val = 1
                    if 'STEP' in for_parts:
                        step_index = for_parts.index('STEP')
                        step_val = int(for_parts[step_index + 1])
                    
                    self.variables[var_name] = start_val
                    for_stack.append((var_name, end_val, step_val, program_counter))
                    program_counter += 1
                except:
                    output.append("?SYNTAX ERROR")
                    break
            
            elif cmd == 'NEXT':
                if not for_stack:
                    output.append("?NEXT WITHOUT FOR ERROR")
                    break
                
                var_name, end_val, step_val, for_pc = for_stack[-1]
                self.variables[var_name] += step_val
                
                # Check if loop continues
                if step_val > 0:
                    loop_continues = self.variables[var_name] <= end_val
                else:
                    loop_continues = self.variables[var_name] >= end_val
                
                if loop_continues:
                    program_counter = for_pc + 1
                else:
                    for_stack.pop()
                    program_counter += 1
            
            elif cmd == 'IF':
                # IF condition THEN line_number
                try:
                    then_index = code.upper().find(' THEN ')
                    condition = code[2:then_index].strip()
                    target = int(code[then_index + 6:].strip())
                    
                    # Convert BASIC comparison operators
                    condition = condition.replace('=', '==')
                    condition = condition.replace('<>', '!=')
                    condition = condition.replace('><', '!=')
                    # Fix <= and >= that got messed up
                    condition = condition.replace('<==', '<=')
                    condition = condition.replace('>==', '>=')
                    
                    if eval(condition, {"__builtins__": {}}, self.variables):
                        if target in line_numbers:
                            program_counter = line_numbers.index(target)
                        else:
                            output.append("?UNDEF'D STATEMENT ERROR")
                            break
                    else:
                        program_counter += 1
                except:
                    output.append("?SYNTAX ERROR")
                    break
            
            elif cmd == 'LET' or '=' in code:
                let_result = self.cmd_let(code)
                if let_result:
                    output.append(let_result.rstrip('\n'))
                program_counter += 1
            
            elif cmd == 'REM':
                # Comment - skip
                program_counter += 1
            
            elif cmd == 'END' or cmd == 'STOP':
                break
            
            else:
                # Unknown command - skip
                program_counter += 1
        
        if iterations >= iteration_limit:
            output.append("?BREAK")
        
        return '\n'.join(output) + "\n" if output else None
    
    def cmd_new(self, args):
        """NEW command - clear program."""
        self.program.clear()
        self.variables.clear()
        return None
    
    def cmd_clr(self, args):
        """CLR command - clear variables."""
        self.variables.clear()
        return None
    
    def cmd_home(self, args):
        """HOME command - clear screen."""
        self.display.clear_screen()
        return None
    
    def cmd_help(self, args):
        """HELP command."""
        return ("COMMANDS:\n"
                " PRINT \"TEXT\"\n"
                " LIST\n"
                " RUN\n"
                " NEW\n"
                " HOME\n"
                " QUIT\n"
                "\n"
                "EXAMPLE:\n"
                " 10 PRINT \"HI\"\n"
                " 20 GOTO 10\n"
                " RUN\n")
    
    def cmd_quit(self, args):
        """QUIT command."""
        self.running = False
        return "BYE\n"
    
    def cmd_let(self, line):
        """LET/assignment statement."""
        # Remove LET keyword if present
        if line.upper().startswith('LET '):
            line = line[4:]
        
        try:
            var, expr = line.split('=', 1)
            var = var.strip().upper()
            value = eval(expr.strip(), {"__builtins__": {}}, self.variables)
            self.variables[var] = value
            return None
        except:
            return "?SYNTAX ERROR\n"
    
    def run(self):
        """Main interpreter loop."""
        self.print_startup_message()
        self.prompt()
        self.display.render()
        
        while self.running:
            try:
                # Show input prompt below the screen
                sys.stdout.write(f"{Term.GREEN_BRIGHT}COMMAND> {Term.RESET}")
                sys.stdout.flush()
                
                user_input = input()
                
                # Echo to display
                self.display.write(user_input.upper() + "\n")
                
                # Execute
                result = self.execute_line(user_input.upper())
                
                if result:
                    self.display.write(result)
                
                if self.running:
                    self.prompt()
                    self.display.render()
                
            except KeyboardInterrupt:
                self.display.write("\n?BREAK\n")
                self.prompt()
                self.display.render()
            
            except EOFError:
                self.running = False
        
        # Cleanup
        sys.stdout.write(Term.SHOW_CURSOR)
        sys.stdout.write(Term.RESET)
        sys.stdout.flush()


def show_boot_screen():
    """Show boot/title screen."""
    sys.stdout.write(Term.CLEAR)
    sys.stdout.write(f"{Term.GREEN_BRIGHT}{Term.BG_BLACK}")
    
    print()
    print("  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║                                                              ║")
    print("  ║     █████╗ ██████╗ ██████╗ ██╗     ███████╗    ][           ║")
    print("  ║    ██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝                  ║")
    print("  ║    ███████║██████╔╝██████╔╝██║     █████╗                    ║")
    print("  ║    ██╔══██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝                    ║")
    print("  ║    ██║  ██║██║     ██║     ███████╗███████╗                  ║")
    print("  ║    ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚══════╝                  ║")
    print("  ║                                                              ║")
    print("  ║                  CLEANROOM EDITION                           ║")
    print("  ║                                                              ║")
    print("  ║    Every character on screen is rendered using actual       ║")
    print("  ║    pixel data from the cleanroom Character Generator ROM    ║")
    print("  ║                                                              ║")
    print("  ║    Display: 40 columns × 24 rows = 280 × 192 pixels         ║")
    print("  ║    Each character: 7 × 8 pixels from ROM                    ║")
    print("  ║                                                              ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print()
    
    sys.stdout.write(Term.RESET)


def load_roms():
    """Load and verify ROMs."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    roms = {
        'chargen': os.path.join(base_path, 'cleanroom_roms/chargen.bin'),
        'monitor': os.path.join(base_path, 'cleanroom_roms/monitor_f800.bin'),
        'applesoft': os.path.join(base_path, 'cleanroom_roms/applesoft.bin'),
        'disk_p5a': os.path.join(base_path, 'cleanroom_roms/disk_ii_p5a.bin'),
        'disk_p6a': os.path.join(base_path, 'cleanroom_roms/disk_ii_p6a.bin'),
    }
    
    print(f"{Term.GREEN_BRIGHT}  Loading cleanroom ROMs...{Term.RESET}")
    print()
    
    for name, path in roms.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"{Term.GREEN_BRIGHT}    ✓ {name}: {size} bytes{Term.RESET}")
        else:
            print(f"{Term.GREEN_DIM}    ✗ {name}: NOT FOUND{Term.RESET}")
    
    print()
    
    return roms['chargen']


def check_terminal_size():
    """Check if terminal is wide enough."""
    try:
        import shutil
        cols, rows = shutil.get_terminal_size()
        
        required_cols = 285
        required_rows = 100
        
        print(f"{Term.GREEN_BRIGHT}  Terminal size: {cols} × {rows}{Term.RESET}")
        print(f"  Required: {required_cols} × {required_rows}")
        print()
        
        if cols < required_cols:
            print(f"{Term.GREEN_DIM}  WARNING: Terminal may be too narrow!")
            print(f"  Try making your terminal window wider,")
            print(f"  or reduce font size.{Term.RESET}")
            print()
        
        return cols >= required_cols
    except:
        return True


def main():
    """Main entry point."""
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        sys.stdout.write(Term.SHOW_CURSOR)
        sys.stdout.write(Term.RESET)
        sys.stdout.write("\n")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Boot screen
    show_boot_screen()
    
    # Load ROMs
    chargen_path = load_roms()
    
    # Check terminal
    check_terminal_size()
    
    # Wait for user
    print(f"{Term.GREEN_BRIGHT}  Press Enter to start...{Term.RESET}")
    input()
    
    # Create character ROM
    char_rom = CharacterGeneratorROM(chargen_path)
    
    # Create display
    display = Apple2TextDisplay(char_rom)
    
    # Create and run interpreter
    basic = Apple2BasicInterpreter(display)
    basic.run()
    
    print(f"{Term.RESET}Goodbye!")


if __name__ == "__main__":
    main()
