#!/usr/bin/env python3
"""
Apple II Cleanroom ROM Demo

Full 40x24 character display with EVERY character rendered using
the actual pixel patterns from the cleanroom character generator ROM.

Characters appear on screen AS YOU TYPE - just like a real Apple II.
Each keystroke is immediately rendered through the character ROM.

Display: 40 columns × 24 rows = 280×192 pixels
Rendered using Unicode half-blocks (▀▄█) = 280×96 terminal cells

Requires a wide terminal (~285 columns) for proper display.
"""

import os
import sys
import time
import signal
import tty
import termios


class Term:
    """Terminal control sequences."""
    CLEAR = "\033[2J\033[H"
    RESET = "\033[0m"
    HIDE_CURSOR = "\033[?25l"
    SHOW_CURSOR = "\033[?25h"
    
    # Apple II green phosphor
    GREEN = "\033[38;2;51;255;51m"
    GREEN_DIM = "\033[38;2;20;100;20m"
    BG = "\033[48;2;0;10;0m"


class RawTerminal:
    """Context manager for raw terminal input."""
    
    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = None
    
    def __enter__(self):
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setraw(self.fd)
        return self
    
    def __exit__(self, *args):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
        sys.stdout.write(Term.SHOW_CURSOR)
        sys.stdout.write(Term.RESET)
        sys.stdout.flush()
    
    def getch(self):
        """Read a single character."""
        ch = sys.stdin.read(1)
        # Handle escape sequences (arrow keys, etc.)
        if ch == '\x1b':
            # Read the rest of the escape sequence
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                sys.stdin.read(1)  # Read and discard the final character
            return None  # Ignore escape sequences
        return ch


class CharacterROM:
    """
    Cleanroom Character Generator ROM.
    
    Each character is 7 pixels wide × 8 pixels tall.
    ROM has 64 characters, 8 bytes each.
    """
    
    def __init__(self, rom_path):
        self.patterns = {}
        
        if not os.path.exists(rom_path):
            raise FileNotFoundError(f"Character ROM not found: {rom_path}")
        
        with open(rom_path, 'rb') as f:
            rom_data = f.read()
        
        # Load 64 character patterns from bank 0
        for i in range(64):
            self.patterns[i] = list(rom_data[i * 8:(i + 1) * 8])
    
    def get_pattern(self, char):
        """Get 8-byte pixel pattern for a character."""
        if isinstance(char, str):
            code = ord(char[0]) if char else 32
        else:
            code = char
        
        # Map ASCII to ROM index
        if 64 <= code <= 95:      # @ A-Z [ \ ] ^ _
            idx = code - 64
        elif 32 <= code <= 63:    # space to ?
            idx = code
        elif 97 <= code <= 122:   # lowercase -> uppercase
            idx = code - 97 + 1
        else:
            idx = 32  # space
        
        return self.patterns.get(idx, [0] * 8)


class Display:
    """
    Apple II 40×24 text display.
    
    Every character rendered using actual ROM pixel data.
    """
    
    BLOCKS = {
        (0, 0): ' ',
        (1, 0): '▀',
        (0, 1): '▄',
        (1, 1): '█',
    }
    
    def __init__(self, char_rom, cols=40, rows=24):
        self.rom = char_rom
        self.cols = cols
        self.rows = rows
        self.buffer = [[' '] * self.cols for _ in range(self.rows)]
        self.cx = 0
        self.cy = 0
    
    def clear(self):
        """Clear screen and home cursor."""
        self.buffer = [[' '] * self.cols for _ in range(self.rows)]
        self.cx = 0
        self.cy = 0
    
    def scroll(self):
        """Scroll screen up one line."""
        self.buffer.pop(0)
        self.buffer.append([' '] * self.cols)
        self.cy = self.rows - 1
    
    def putch(self, ch):
        """
        Put a character at cursor and advance.
        This is what happens when you press a key on a real Apple II.
        """
        if ch == '\n' or ch == '\r':
            self.cx = 0
            self.cy += 1
            if self.cy >= self.rows:
                self.scroll()
        elif ch == '\b' or ch == '\x7f':
            if self.cx > 0:
                self.cx -= 1
                self.buffer[self.cy][self.cx] = ' '
        elif ch >= ' ' and ch <= '~':
            # Printable character - convert to uppercase like Apple II
            display_ch = ch.upper() if ch.isalpha() else ch
            self.buffer[self.cy][self.cx] = display_ch
            self.cx += 1
            if self.cx >= self.cols:
                self.cx = 0
                self.cy += 1
                if self.cy >= self.rows:
                    self.scroll()
    
    def write(self, text):
        """Write string to display."""
        for ch in text:
            self.putch(ch)
    
    def render(self, full_clear=False):
        """Render entire display using character ROM pixels."""
        # Pixel buffer: 280 wide × 192 tall
        pw = self.cols * 7
        ph = self.rows * 8
        pixels = [[0] * pw for _ in range(ph)]
        
        # Render each character from ROM
        for row in range(self.rows):
            for col in range(self.cols):
                ch = self.buffer[row][col]
                
                # Cursor = solid block
                if row == self.cy and col == self.cx:
                    pattern = [0x7F] * 8
                else:
                    pattern = self.rom.get_pattern(ch)
                
                # Plot pixels
                px = col * 7
                py = row * 8
                for y in range(8):
                    byte = pattern[y]
                    for x in range(7):
                        if byte & (1 << x):
                            pixels[py + y][px + x] = 1
        
        # Output to terminal - just go home, don't clear (prevents flicker)
        out = []
        if full_clear:
            out.append(Term.CLEAR)
        else:
            out.append("\033[H")  # Just move cursor to home
        out.append(Term.HIDE_CURSOR)
        out.append(Term.BG)
        
        # Top border
        out.append(f"{Term.GREEN_DIM}╔{'═' * (pw + 2)}╗\n")
        out.append(f"║ {' ' * pw} ║\n")
        
        # Pixels using half-blocks
        for y in range(0, ph, 2):
            out.append(f"{Term.GREEN_DIM}║ {Term.GREEN}")
            for x in range(pw):
                top = pixels[y][x]
                bot = pixels[y + 1][x] if y + 1 < ph else 0
                out.append(self.BLOCKS[(top, bot)])
            out.append(f" {Term.GREEN_DIM}║\n")
        
        # Bottom border
        out.append(f"║ {' ' * pw} ║\n")
        out.append(f"╚{'═' * (pw + 2)}╝\n")
        out.append(f"{Term.GREEN_DIM}  [APPLE II CLEANROOM - ALL TEXT FROM CHARACTER ROM]{Term.RESET}")
        out.append("\033[K\n")  # Clear to end of line
        
        sys.stdout.write(''.join(out))
        sys.stdout.flush()


class Apple2:
    """
    Apple II with character-by-character input.
    
    Just like a real Apple II, each keypress immediately
    appears on screen, rendered through the character ROM.
    """
    
    def __init__(self, display):
        self.display = display
        self.variables = {}
        self.program = {}
        self.running = True
    
    def show_startup(self):
        """Display startup message."""
        self.display.write("APPLE II CLEANROOM\n")
        self.display.write("\n")
        self.display.write("EVERY CHARACTER RENDERED\n")
        self.display.write("FROM THE CHARACTER ROM\n")
        self.display.write("\n")
    
    def run(self):
        """Main loop with character-by-character input."""
        self.show_startup()
        self.display.write("]")
        self.display.render(full_clear=True)
        
        # Check if we have a real terminal
        if not sys.stdin.isatty():
            self.run_line_mode()
            return
        
        self.run_char_mode()
    
    def run_line_mode(self):
        """Fallback line-by-line input for non-interactive use."""
        while self.running:
            try:
                line = input()
                self.display.write(line.upper() + "\n")
                
                cmd = line.strip().upper()
                if cmd:
                    result = self.execute(cmd)
                    if result:
                        self.display.write(result)
                
                if self.running:
                    self.display.write("]")
                    self.display.render(full_clear=True)
            except EOFError:
                break
    
    def run_char_mode(self):
        """Character-by-character input for real terminals."""
        line_buffer = ""
        
        with RawTerminal() as term:
            while self.running:
                ch = term.getch()
                
                if ch is None:
                    continue
                
                if ch == '\x03' or ch == '\x04':  # Ctrl+C or Ctrl+D
                    self.running = False
                    break
                
                if ch == '\r' or ch == '\n':
                    self.display.putch('\n')
                    
                    cmd = line_buffer.strip().upper()
                    line_buffer = ""
                    
                    if cmd:
                        result = self.execute(cmd)
                        if result:
                            self.display.write(result)
                    
                    if self.running:
                        self.display.write("]")
                    
                    self.display.render(full_clear=True)
                
                elif ch == '\x7f' or ch == '\b':
                    if line_buffer:
                        line_buffer = line_buffer[:-1]
                        self.display.putch('\b')
                        self.display.render()
                
                elif ch >= ' ' and ch <= '~':
                    line_buffer += ch
                    self.display.putch(ch)
                    self.display.render()
    
    def execute(self, line):
        """Execute a BASIC line."""
        if not line:
            return None
        
        # Line number = program storage
        if line[0].isdigit():
            parts = line.split(None, 1)
            try:
                num = int(parts[0])
                if len(parts) > 1:
                    self.program[num] = parts[1]
                elif num in self.program:
                    del self.program[num]
            except:
                return "?SYNTAX ERROR\n"
            return None
        
        # Commands
        cmd = line.split()[0]
        args = line[len(cmd):].strip()
        
        if cmd in ('PRINT', '?'):
            return self.cmd_print(args)
        elif cmd == 'LIST':
            return self.cmd_list()
        elif cmd == 'RUN':
            return self.cmd_run()
        elif cmd == 'NEW':
            self.program.clear()
            self.variables.clear()
            return None
        elif cmd == 'HOME':
            self.display.clear()
            return None
        elif cmd in ('QUIT', 'EXIT', 'BYE'):
            self.running = False
            return "BYE\n"
        elif '=' in line:
            return self.cmd_let(line)
        else:
            return "?SYNTAX ERROR\n"
    
    def cmd_print(self, args):
        """PRINT statement."""
        if not args:
            return "\n"
        
        result = []
        i = 0
        while i < len(args):
            while i < len(args) and args[i] == ' ':
                i += 1
            if i >= len(args):
                break
            
            if args[i] == '"':
                i += 1
                s = ""
                while i < len(args) and args[i] != '"':
                    s += args[i]
                    i += 1
                result.append(s)
                i += 1
            elif args[i] in ';,':
                if args[i] == ',':
                    result.append("        ")
                i += 1
            else:
                j = i
                while j < len(args) and args[j] not in ' ;,"':
                    j += 1
                expr = args[i:j]
                i = j
                try:
                    val = eval(expr, {"__builtins__": {}}, self.variables)
                    result.append(str(val))
                except:
                    result.append("0")
        
        return ''.join(result) + "\n"
    
    def cmd_let(self, line):
        """Variable assignment."""
        if line.startswith("LET "):
            line = line[4:]
        try:
            var, expr = line.split('=', 1)
            self.variables[var.strip()] = eval(expr.strip(), {"__builtins__": {}}, self.variables)
        except:
            return "?SYNTAX ERROR\n"
        return None
    
    def cmd_list(self):
        """LIST program."""
        if not self.program:
            return None
        lines = []
        for num in sorted(self.program.keys()):
            lines.append(f" {num}  {self.program[num]}")
        return '\n'.join(lines) + "\n"
    
    def cmd_run(self):
        """RUN program."""
        if not self.program:
            return None
        
        output = []
        self.variables.clear()
        lines = sorted(self.program.keys())
        pc = 0
        stack = []
        
        for _ in range(10000):
            if pc >= len(lines):
                break
            
            code = self.program[lines[pc]]
            cmd = code.split()[0] if code.split() else ""
            args = code[len(cmd):].strip()
            
            if cmd in ('PRINT', '?'):
                r = self.cmd_print(args)
                if r and r.strip():
                    output.append(r.rstrip('\n'))
                pc += 1
            
            elif cmd == 'GOTO':
                try:
                    target = int(args)
                    pc = lines.index(target) if target in lines else len(lines)
                except:
                    break
            
            elif cmd == 'FOR':
                try:
                    parts = args.replace('=', ' ').upper().split()
                    var = parts[0]
                    start = int(parts[1])
                    end = int(parts[parts.index('TO') + 1])
                    step = 1
                    if 'STEP' in parts:
                        step = int(parts[parts.index('STEP') + 1])
                    self.variables[var] = start
                    stack.append((var, end, step, pc))
                    pc += 1
                except:
                    break
            
            elif cmd == 'NEXT':
                if stack:
                    var, end, step, fpc = stack[-1]
                    self.variables[var] += step
                    done = (step > 0 and self.variables[var] > end) or \
                           (step < 0 and self.variables[var] < end)
                    if done:
                        stack.pop()
                        pc += 1
                    else:
                        pc = fpc + 1
                else:
                    pc += 1
            
            elif cmd == 'IF':
                try:
                    idx = code.upper().find(' THEN ')
                    cond = code[2:idx]
                    target = int(code[idx + 6:].strip())
                    cond = cond.replace('=', '==').replace('<>', '!=')
                    cond = cond.replace('<==', '<=').replace('>==', '>=')
                    if eval(cond, {"__builtins__": {}}, self.variables):
                        pc = lines.index(target) if target in lines else len(lines)
                    else:
                        pc += 1
                except:
                    pc += 1
            
            elif '=' in code:
                self.cmd_let(code)
                pc += 1
            
            elif cmd == 'REM':
                pc += 1
            
            elif cmd in ('END', 'STOP'):
                break
            
            else:
                pc += 1
        
        return '\n'.join(output) + "\n" if output else None


def get_terminal_size():
    """Get terminal dimensions."""
    try:
        import shutil
        cols, rows = shutil.get_terminal_size()
        return cols, rows
    except:
        return 80, 24


def boot():
    """Show boot screen and choose display size."""
    sys.stdout.write(Term.CLEAR)
    sys.stdout.write(f"{Term.GREEN}{Term.BG}")
    
    cols, rows = get_terminal_size()
    
    print()
    print("  ╔════════════════════════════════════════════════════════════╗")
    print("  ║                                                            ║")
    print("  ║     █████╗ ██████╗ ██████╗ ██╗     ███████╗   ][          ║")
    print("  ║    ██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝               ║")
    print("  ║    ███████║██████╔╝██████╔╝██║     █████╗                 ║")
    print("  ║    ██╔══██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝                 ║")
    print("  ║    ██║  ██║██║     ██║     ███████╗███████╗               ║")
    print("  ║    ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚══════╝               ║")
    print("  ║                                                            ║")
    print("  ║                 CLEANROOM EDITION                          ║")
    print("  ║                                                            ║")
    print("  ║   Every character rendered from Character Generator ROM    ║")
    print("  ║                                                            ║")
    print("  ╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Load ROMs
    base = os.path.dirname(os.path.abspath(__file__))
    roms = [
        'cleanroom_roms/chargen.bin',
        'cleanroom_roms/monitor_f800.bin',
        'cleanroom_roms/applesoft.bin',
        'cleanroom_roms/disk_ii_p5a.bin',
    ]
    
    print("  Cleanroom ROMs:")
    for rom in roms:
        path = os.path.join(base, rom)
        if os.path.exists(path):
            print(f"    ✓ {os.path.basename(rom)} ({os.path.getsize(path)} bytes)")
    
    print()
    print(f"  Terminal: {cols}×{rows}")
    print()
    
    # Calculate what fits
    # Each char = 7 pixels, plus 4 for borders
    max_chars = (cols - 4) // 7
    
    print("  Display options:")
    print(f"    1. Full 40×24  (needs 285 cols) {'✓' if cols >= 285 else '✗ TOO WIDE'}")
    print(f"    2. Half 20×12  (needs 145 cols) {'✓' if cols >= 145 else '✗ TOO WIDE'}")
    print(f"    3. Mini 10×6   (needs 75 cols)  {'✓' if cols >= 75 else '✗ TOO WIDE'}")
    print()
    
    print(f"{Term.RESET}")
    
    choice = input("  Choose [1/2/3]: ").strip()
    
    if choice == '2':
        display_cols, display_rows = 20, 12
    elif choice == '3':
        display_cols, display_rows = 10, 6
    else:
        display_cols, display_rows = 40, 24
    
    required_width = display_cols * 7 + 4
    if cols < required_width:
        print(f"\n  ERROR: Terminal too narrow! Need {required_width} columns, have {cols}")
        print("  Try: making terminal wider, or reducing font size")
        print()
        sys.exit(1)
    
    return os.path.join(base, 'cleanroom_roms/chargen.bin'), display_cols, display_rows


def main():
    # Handle signals
    def cleanup(sig, frame):
        sys.stdout.write(Term.SHOW_CURSOR)
        sys.stdout.write(Term.RESET)
        sys.stdout.write("\n")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup)
    
    # Boot and get display size
    rom_path, disp_cols, disp_rows = boot()
    
    input("  Press Enter to start...")
    
    # Create display with character ROM
    char_rom = CharacterROM(rom_path)
    display = Display(char_rom, cols=disp_cols, rows=disp_rows)
    
    # Run
    apple = Apple2(display)
    apple.run()
    
    print(f"{Term.RESET}Goodbye!")


if __name__ == "__main__":
    main()
