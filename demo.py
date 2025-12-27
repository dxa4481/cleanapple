#!/usr/bin/env python3
"""
Apple II Cleanroom ROM Demo - Authentic Character ROM Display

Renders ALL text using the cleanroom character generator ROM.
Uses raw terminal input to render keypresses through the character ROM.
"""

import os
import sys
import time
import tty
import termios

# ANSI escape codes
ESC = "\033"
CLEAR = f"{ESC}[2J{ESC}[H"
RESET = f"{ESC}[0m"
HIDE_CURSOR = f"{ESC}[?25l"
SHOW_CURSOR = f"{ESC}[?25h"

# Apple II phosphor green
GREEN = f"{ESC}[38;2;51;255;51m"
DIM = f"{ESC}[38;2;20;80;20m"
BG = f"{ESC}[48;2;2;12;2m"


class CharacterROM:
    """Load and use the cleanroom character generator ROM."""
    
    def __init__(self):
        self.patterns = {}
        self.load_rom()
    
    def load_rom(self):
        """Load character patterns from ROM file."""
        base = os.path.dirname(os.path.abspath(__file__))
        rom_path = os.path.join(base, 'cleanroom_roms/chargen.bin')
        
        if os.path.exists(rom_path):
            with open(rom_path, 'rb') as f:
                rom = f.read()
            for i in range(64):
                self.patterns[i] = list(rom[i*8:(i+1)*8])
        else:
            for i in range(64):
                self.patterns[i] = [0] * 8
    
    def get_pattern(self, char):
        """Get 8-byte pattern for a character."""
        c = ord(char) if isinstance(char, str) else char
        
        if 64 <= c <= 95:      # @ through _
            idx = c - 64
        elif 32 <= c <= 63:    # space through ?
            idx = c
        elif 97 <= c <= 122:   # lowercase -> uppercase
            idx = c - 97 + 1
        else:
            idx = 32           # space
        
        return self.patterns.get(idx, [0]*8)


class PixelDisplay:
    """
    Renders Apple II screen using actual character ROM pixels.
    Double-width pixels for correct aspect ratio.
    """
    
    # Half-block characters for 2 vertical pixels per cell
    BLOCKS = {
        (0, 0): ' ',
        (1, 0): '▀',
        (0, 1): '▄',
        (1, 1): '█',
    }
    
    def __init__(self, charrom, cols=40, rows=24, double_wide=True):
        self.charrom = charrom
        self.cols = cols
        self.rows = rows
        self.double_wide = double_wide  # Double horizontal pixels for aspect ratio
        self.screen = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.cx, self.cy = 0, 0
    
    def clear(self):
        self.screen = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.cx, self.cy = 0, 0
    
    def scroll(self):
        self.screen.pop(0)
        self.screen.append([' ' for _ in range(self.cols)])
        self.cy = self.rows - 1
    
    def newline(self):
        self.cx = 0
        self.cy += 1
        if self.cy >= self.rows:
            self.scroll()
    
    def putchar(self, ch):
        if ch == '\n':
            self.newline()
        elif ch == '\r':
            self.cx = 0
        elif ch == '\b' or ch == '\x7f':
            if self.cx > 0:
                self.cx -= 1
                self.screen[self.cy][self.cx] = ' '
        else:
            if 0 <= self.cy < self.rows and 0 <= self.cx < self.cols:
                self.screen[self.cy][self.cx] = ch.upper() if ch.isalpha() else ch
                self.cx += 1
                if self.cx >= self.cols:
                    self.newline()
    
    def write(self, text):
        for ch in text:
            self.putchar(ch)
    
    def render(self, blink_cursor=True):
        """Render screen using character ROM pixels."""
        # Each char is 7 wide x 8 tall pixels
        pw = self.cols * 7
        ph = self.rows * 8
        pixels = [[0 for _ in range(pw)] for _ in range(ph)]
        
        # Render all characters to pixel buffer
        for ty in range(self.rows):
            for tx in range(self.cols):
                ch = self.screen[ty][tx]
                # Cursor: solid block
                if blink_cursor and tx == self.cx and ty == self.cy:
                    pattern = [0x7F] * 8
                else:
                    pattern = self.charrom.get_pattern(ch)
                
                px = tx * 7
                py = ty * 8
                for row in range(8):
                    byte_val = pattern[row]
                    for bit in range(7):
                        if byte_val & (1 << bit):
                            pixels[py + row][px + bit] = 1
        
        # Output to terminal
        print(CLEAR + HIDE_CURSOR, end='')
        print(f"{GREEN}{BG}")
        
        # Border width depends on double_wide mode
        bw = pw * 2 + 2 if self.double_wide else pw + 2
        print("╔" + "═" * bw + "╗")
        
        # Render 2 pixel rows at a time using half-blocks
        for y in range(0, ph, 2):
            print("║ ", end="")
            for x in range(pw):
                top = pixels[y][x] if y < ph else 0
                bot = pixels[y+1][x] if y+1 < ph else 0
                block = self.BLOCKS[(top, bot)]
                if self.double_wide:
                    print(block * 2, end="")  # Double width for aspect ratio
                else:
                    print(block, end="")
            print(" ║")
        
        print("╚" + "═" * bw + "╝")
        print(f"{DIM}  [APPLE II CLEANROOM - CHARACTER ROM]{RESET}")
        sys.stdout.flush()


class SimpleDisplay:
    """Simple 40x24 text display with green styling."""
    
    def __init__(self, cols=40, rows=24):
        self.cols = cols
        self.rows = rows
        self.screen = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.cx, self.cy = 0, 0
    
    def clear(self):
        self.screen = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.cx, self.cy = 0, 0
    
    def scroll(self):
        self.screen.pop(0)
        self.screen.append([' ' for _ in range(self.cols)])
        self.cy = self.rows - 1
    
    def newline(self):
        self.cx = 0
        self.cy += 1
        if self.cy >= self.rows:
            self.scroll()
    
    def putchar(self, ch):
        if ch == '\n':
            self.newline()
        elif ch == '\r':
            self.cx = 0
        elif ch == '\b' or ch == '\x7f':
            if self.cx > 0:
                self.cx -= 1
                self.screen[self.cy][self.cx] = ' '
        else:
            if 0 <= self.cy < self.rows and 0 <= self.cx < self.cols:
                self.screen[self.cy][self.cx] = ch.upper() if ch.isalpha() else ch
                self.cx += 1
                if self.cx >= self.cols:
                    self.newline()
    
    def write(self, text):
        for ch in text:
            self.putchar(ch)
    
    def render(self, blink_cursor=True):
        print(CLEAR + HIDE_CURSOR, end='')
        print(f"{GREEN}{BG}")
        print("┌" + "─" * 42 + "┐")
        for y, row in enumerate(self.screen):
            line = ''.join(row)
            if blink_cursor and y == self.cy and self.cx < self.cols:
                line = line[:self.cx] + '█' + line[self.cx+1:]
            print(f"│ {line} │")
        print("└" + "─" * 42 + "┘")
        print(f"{DIM}     [APPLE II CLEANROOM]{RESET}")
        sys.stdout.flush()


class RawInput:
    """Handle raw terminal input for character-by-character reading."""
    
    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = None
    
    def __enter__(self):
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setraw(self.fd)
        return self
    
    def __exit__(self, *args):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
    
    def getch(self):
        """Read a single character."""
        return sys.stdin.read(1)


class Apple2:
    """Apple II BASIC interpreter with pixel-perfect display."""
    
    def __init__(self, display):
        self.display = display
        self.variables = {}
        self.program = {}
    
    def run(self):
        self.display.clear()
        self.display.write("APPLE II CLEANROOM BASIC\n")
        self.display.write("\n]")
        self.display.render()
        
        try:
            with RawInput():
                self._main_loop()
        except Exception as e:
            print(f"{RESET}{SHOW_CURSOR}")
            raise
    
    def _main_loop(self):
        """Main loop with raw input handling."""
        line_buffer = ""
        
        while True:
            ch = sys.stdin.read(1)
            
            if ch == '\x03':  # Ctrl+C
                print(f"{RESET}{SHOW_CURSOR}")
                sys.exit(0)
            elif ch == '\x04':  # Ctrl+D
                print(f"{RESET}{SHOW_CURSOR}")
                sys.exit(0)
            elif ch == '\r' or ch == '\n':  # Enter
                self.display.putchar('\n')
                
                cmd = line_buffer.upper().strip()
                line_buffer = ""
                
                if cmd in ('QUIT', 'EXIT', 'BYE'):
                    self.display.write("GOODBYE\n")
                    self.display.render()
                    time.sleep(0.5)
                    print(f"{RESET}{SHOW_CURSOR}")
                    return
                
                if cmd:
                    result = self.execute(cmd)
                    if result:
                        self.display.write(result)
                
                self.display.write("]")
                self.display.render()
                
            elif ch == '\x7f' or ch == '\b':  # Backspace
                if line_buffer:
                    line_buffer = line_buffer[:-1]
                    self.display.putchar('\b')
                    self.display.render()
            elif ch == '\x1b':  # Escape sequence (arrow keys etc)
                # Read and discard escape sequences
                sys.stdin.read(2)
            elif 32 <= ord(ch) <= 126:  # Printable ASCII
                line_buffer += ch
                self.display.putchar(ch)
                self.display.render()
    
    def execute(self, line):
        if not line:
            return None
        
        # Line number = store program
        if line[0].isdigit():
            parts = line.split(None, 1)
            num = int(parts[0])
            if len(parts) > 1:
                self.program[num] = parts[1]
            elif num in self.program:
                del self.program[num]
            return None
        
        cmd = line.split()[0] if line.split() else ''
        args = line[len(cmd):].strip()
        
        if cmd in ('PRINT', '?'):
            return self.do_print(args)
        elif cmd == 'LIST':
            return self.do_list()
        elif cmd == 'RUN':
            return self.do_run()
        elif cmd == 'NEW':
            self.program.clear()
            self.variables.clear()
            return None
        elif cmd == 'CLR':
            self.variables.clear()
            return None
        elif cmd == 'HOME':
            self.display.clear()
            return None
        elif '=' in line:
            return self.do_let(line)
        else:
            return "?SYNTAX ERROR\n"
    
    def do_print(self, args):
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
                s = ''
                while i < len(args) and args[i] != '"':
                    s += args[i]
                    i += 1
                result.append(s)
                i += 1
            elif args[i] in ';,':
                if args[i] == ',':
                    result.append('        ')
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
                    result.append('0')
        
        return ''.join(result) + '\n'
    
    def do_let(self, line):
        if line.startswith('LET '):
            line = line[4:]
        try:
            var, expr = line.split('=', 1)
            self.variables[var.strip()] = eval(expr.strip(), {"__builtins__": {}}, self.variables)
        except:
            return "?SYNTAX ERROR\n"
        return None
    
    def do_list(self):
        if not self.program:
            return None
        lines = []
        for n in sorted(self.program):
            lines.append(f" {n}  {self.program[n]}")
        return '\n'.join(lines) + '\n'
    
    def do_run(self):
        if not self.program:
            return None
        
        out = []
        self.variables.clear()
        lines = sorted(self.program.keys())
        pc = 0
        stack = []
        
        for _ in range(10000):
            if pc >= len(lines):
                break
            
            num = lines[pc]
            code = self.program[num]
            cmd = code.split()[0] if code.split() else ''
            args = code[len(cmd):].strip()
            
            if cmd in ('PRINT', '?'):
                out.append(self.do_print(args))
                pc += 1
            elif cmd == 'GOTO':
                target = int(args)
                pc = lines.index(target) if target in lines else len(lines)
            elif cmd == 'FOR':
                p = args.replace('=', ' ').split()
                var = p[0]
                start = int(p[1])
                end_idx = p.index('TO') + 1
                end = int(p[end_idx])
                step = 1
                if 'STEP' in p:
                    step = int(p[p.index('STEP') + 1])
                self.variables[var] = start
                stack.append((var, end, step, pc))
                pc += 1
            elif cmd == 'NEXT':
                if stack:
                    var, end, step, fpc = stack[-1]
                    self.variables[var] += step
                    if (step > 0 and self.variables[var] <= end) or \
                       (step < 0 and self.variables[var] >= end):
                        pc = fpc + 1
                    else:
                        stack.pop()
                        pc += 1
                else:
                    pc += 1
            elif cmd == 'IF':
                cond_end = code.find(' THEN ')
                cond = code[2:cond_end].strip()
                then = code[cond_end+6:].strip()
                cond = cond.replace('=', '==').replace('<>', '!=').replace('><', '!=')
                cond = cond.replace('<==', '<=').replace('>==', '>=')
                try:
                    if eval(cond, {"__builtins__": {}}, self.variables):
                        target = int(then)
                        pc = lines.index(target) if target in lines else len(lines)
                    else:
                        pc += 1
                except:
                    pc += 1
            elif '=' in code and not code.startswith('IF'):
                self.do_let(code)
                pc += 1
            elif cmd == 'REM':
                pc += 1
            elif cmd in ('END', 'STOP'):
                break
            else:
                pc += 1
        
        return ''.join(out)


def boot_screen():
    """Show boot animation."""
    print(CLEAR, end='')
    print(f"{GREEN}{BG}")
    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║                                                      ║")
    print("  ║     █████╗ ██████╗ ██████╗ ██╗     ███████╗         ║")
    print("  ║    ██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝         ║")
    print("  ║    ███████║██████╔╝██████╔╝██║     █████╗           ║")
    print("  ║    ██╔══██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝           ║")
    print("  ║    ██║  ██║██║     ██║     ███████╗███████╗         ║")
    print("  ║    ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚══════╝         ║")
    print("  ║                                                      ║")
    print("  ║              ][  CLEANROOM EDITION                   ║")
    print("  ║                                                      ║")
    print("  ║      100% Implemented from Published Specs           ║")
    print("  ║         No Original Apple Code Used                  ║")
    print("  ║                                                      ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()


def load_roms():
    """Load and display ROM status."""
    base = os.path.dirname(os.path.abspath(__file__))
    roms = [
        ('cleanroom_roms/chargen.bin', 'CHARACTER GENERATOR', 2048),
        ('cleanroom_roms/monitor_f800.bin', 'MONITOR ROM', 2048),
        ('cleanroom_roms/applesoft.bin', 'APPLESOFT BASIC', 10240),
        ('cleanroom_roms/disk_ii_p5a.bin', 'DISK II BOOT ROM', 256),
        ('cleanroom_roms/disk_ii_p6a.bin', 'DISK II GCR TABLE', 256),
    ]
    
    print("  Loading cleanroom ROMs...")
    print()
    
    for path, name, expected_size in roms:
        full = os.path.join(base, path)
        if os.path.exists(full):
            size = os.path.getsize(full)
            status = "✓" if size == expected_size else "?"
            print(f"    {status} {name} ({size} bytes)")
            time.sleep(0.08)
        else:
            print(f"    ✗ {name} - NOT FOUND")


def main():
    boot_screen()
    load_roms()
    
    print()
    print("  Select display mode:")
    print()
    print("    1. Simple    - 40x24 text, green phosphor")
    print("    2. Pixel     - Character ROM, double-wide (560x96)")
    print("    3. Pixel 1:1 - Character ROM, single-wide (280x96)")
    print()
    print(f"{RESET}", end='')
    
    try:
        choice = input("  Choice [1]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{SHOW_CURSOR}Goodbye!")
        return
    
    print()
    
    if choice == '2':
        charrom = CharacterROM()
        display = PixelDisplay(charrom, double_wide=True)
        print("  Pixel mode (double-wide) - needs ~565 column terminal")
    elif choice == '3':
        charrom = CharacterROM()
        display = PixelDisplay(charrom, double_wide=False)
        print("  Pixel mode (1:1) - needs ~285 column terminal")
    else:
        display = SimpleDisplay()
        print("  Simple mode - works in any terminal")
    
    print("  Type QUIT to exit")
    print()
    time.sleep(0.5)
    
    apple = Apple2(display)
    apple.run()


if __name__ == "__main__":
    main()
