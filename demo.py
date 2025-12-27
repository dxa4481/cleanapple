#!/usr/bin/env python3
"""
Apple II Cleanroom ROM Demo

ALL text rendered using actual character ROM pixels.
Uses a 20x12 character display (140x96 pixels) to fit in ~150 column terminal.
"""

import os
import sys
import time

# ANSI 
ESC = "\033"
CLEAR = f"{ESC}[2J{ESC}[H"
RESET = f"{ESC}[0m"

# Apple II green phosphor
GREEN = f"{ESC}[38;2;51;255;51m"
DARK = f"{ESC}[38;2;0;40;0m"
BG = f"{ESC}[48;2;0;15;0m"
DIM = f"{ESC}[2m"


class CharacterROM:
    """Cleanroom character generator ROM."""
    
    def __init__(self):
        self.patterns = {}
        base = os.path.dirname(os.path.abspath(__file__))
        rom_path = os.path.join(base, 'cleanroom_roms/chargen.bin')
        
        if os.path.exists(rom_path):
            with open(rom_path, 'rb') as f:
                rom = f.read()
            for i in range(64):
                self.patterns[i] = list(rom[i*8:(i+1)*8])
        else:
            # Fallback - empty patterns
            for i in range(64):
                self.patterns[i] = [0] * 8
    
    def get_pattern(self, char):
        """Get 8-row pixel pattern for a character."""
        c = ord(char) if isinstance(char, str) else char
        
        if 64 <= c <= 95:      # @ through _
            idx = c - 64
        elif 32 <= c <= 63:    # space through ?
            idx = c
        elif 97 <= c <= 122:   # lowercase -> uppercase
            idx = c - 97 + 1
        else:
            idx = 32           # default to space
        
        return self.patterns.get(idx, [0]*8)


class PixelScreen:
    """Screen that renders ALL text using character ROM pixels."""
    
    # Half-blocks for 2 vertical pixels per terminal character
    BLOCK = {
        (0, 0): ' ',
        (1, 0): '▀',
        (0, 1): '▄',
        (1, 1): '█',
    }
    
    def __init__(self, charrom, cols=20, rows=12):
        self.charrom = charrom
        self.cols = cols
        self.rows = rows
        self.text = [[' '] * cols for _ in range(rows)]
        self.cx, self.cy = 0, 0
    
    def clear(self):
        self.text = [[' '] * self.cols for _ in range(self.rows)]
        self.cx, self.cy = 0, 0
    
    def scroll(self):
        self.text.pop(0)
        self.text.append([' '] * self.cols)
        self.cy = self.rows - 1
    
    def newline(self):
        self.cx = 0
        self.cy += 1
        if self.cy >= self.rows:
            self.scroll()
    
    def putc(self, ch):
        if ch == '\n':
            self.newline()
        elif ch == '\r':
            self.cx = 0
        elif ch == '\b' or ch == '\x7f':
            if self.cx > 0:
                self.cx -= 1
                self.text[self.cy][self.cx] = ' '
        else:
            if 0 <= self.cy < self.rows and 0 <= self.cx < self.cols:
                # Convert to uppercase for Apple II authenticity
                self.text[self.cy][self.cx] = ch.upper() if ch.isalpha() else ch
                self.cx += 1
                if self.cx >= self.cols:
                    self.newline()
    
    def write(self, s):
        for ch in s:
            self.putc(ch)
    
    def render(self):
        """Render entire screen using character ROM pixels."""
        # Build pixel buffer: cols*7 wide, rows*8 tall
        pw = self.cols * 7
        ph = self.rows * 8
        pixels = [[0] * pw for _ in range(ph)]
        
        # Render each character from ROM
        for ty in range(self.rows):
            for tx in range(self.cols):
                ch = self.text[ty][tx]
                
                # Cursor = solid block
                if tx == self.cx and ty == self.cy:
                    pattern = [0x7F] * 8  # All pixels on
                else:
                    pattern = self.charrom.get_pattern(ch)
                
                # Plot to pixel buffer
                for row in range(8):
                    for bit in range(7):
                        if pattern[row] & (1 << bit):
                            pixels[ty * 8 + row][tx * 7 + bit] = 1
        
        # Render to terminal using half-blocks
        print(CLEAR, end='')
        print(f"{GREEN}{BG}")
        
        # Top border
        border_w = pw + 4
        print("  ╔" + "═" * border_w + "╗")
        print("  ║  " + " " * pw + "  ║")
        
        # Pixel rows (2 at a time with half-blocks)
        for y in range(0, ph, 2):
            print("  ║  ", end="")
            for x in range(pw):
                top = pixels[y][x]
                bot = pixels[y + 1][x] if y + 1 < ph else 0
                print(self.BLOCK[(top, bot)], end="")
            print("  ║")
        
        # Bottom border
        print("  ║  " + " " * pw + "  ║")
        print("  ╚" + "═" * border_w + "╝")
        print(f"{DIM}     [APPLE II CLEANROOM - ALL PIXELS FROM ROM]{RESET}")
        sys.stdout.flush()


class Apple2:
    """Apple II with pixel-perfect character ROM display."""
    
    def __init__(self, screen):
        self.screen = screen
        self.variables = {}
        self.program = {}
    
    def run(self):
        self.screen.write("APPLE II CLEANROOM\n")
        self.screen.write("]")
        self.screen.render()
        
        while True:
            try:
                # Show prompt outside the pixel area
                print(f"{GREEN}>{RESET} ", end='', flush=True)
                line = input().strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{RESET}")
                break
            
            # Echo input to pixel screen
            self.screen.write(line.upper() + "\n")
            
            cmd = line.upper().strip()
            
            if cmd in ('QUIT', 'EXIT', 'BYE'):
                self.screen.write("BYE\n")
                self.screen.render()
                break
            
            if cmd:
                result = self.execute(cmd)
                if result:
                    self.screen.write(result)
                    if not result.endswith('\n'):
                        self.screen.write('\n')
            
            self.screen.write("]")
            self.screen.render()
    
    def execute(self, line):
        # Line number = store program
        if line and line[0].isdigit():
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
            self.screen.clear()
            return None
        elif '=' in line:
            return self.cmd_let(line)
        else:
            return "?SYNTAX ERROR"
    
    def cmd_print(self, args):
        if not args:
            return "\n"
        out = []
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
                out.append(s)
                i += 1
            elif args[i] in ';,':
                i += 1
            else:
                j = i
                while j < len(args) and args[j] not in ' ;,"':
                    j += 1
                expr = args[i:j]
                i = j
                try:
                    out.append(str(eval(expr, {"__builtins__": {}}, self.variables)))
                except:
                    out.append('0')
        return ''.join(out) + '\n'
    
    def cmd_let(self, line):
        if line.startswith('LET '):
            line = line[4:]
        try:
            var, expr = line.split('=', 1)
            self.variables[var.strip()] = eval(expr.strip(), {"__builtins__": {}}, self.variables)
        except:
            return "?SYNTAX ERROR"
        return None
    
    def cmd_list(self):
        if not self.program:
            return None
        lines = [f"{n} {self.program[n]}" for n in sorted(self.program)]
        return '\n'.join(lines) + '\n'
    
    def cmd_run(self):
        if not self.program:
            return None
        out = []
        self.variables.clear()
        lines = sorted(self.program.keys())
        pc, stack = 0, []
        
        for _ in range(10000):
            if pc >= len(lines):
                break
            code = self.program[lines[pc]]
            cmd = code.split()[0] if code.split() else ''
            args = code[len(cmd):].strip()
            
            if cmd in ('PRINT', '?'):
                r = self.cmd_print(args)
                if r and r.strip():
                    out.append(r.rstrip('\n'))
                pc += 1
            elif cmd == 'GOTO':
                pc = lines.index(int(args)) if int(args) in lines else len(lines)
            elif cmd == 'FOR':
                p = args.replace('=', ' ').split()
                var, start = p[0], int(p[1])
                end = int(p[p.index('TO') + 1])
                self.variables[var] = start
                stack.append((var, end, pc))
                pc += 1
            elif cmd == 'NEXT':
                if stack:
                    var, end, fpc = stack[-1]
                    self.variables[var] += 1
                    if self.variables[var] <= end:
                        pc = fpc + 1
                    else:
                        stack.pop()
                        pc += 1
                else:
                    pc += 1
            elif cmd == 'IF':
                idx = code.find(' THEN ')
                cond = code[2:idx].replace('=', '==').replace('<>', '!=')
                then = int(code[idx+6:].strip())
                try:
                    if eval(cond, {"__builtins__": {}}, self.variables):
                        pc = lines.index(then) if then in lines else len(lines)
                    else:
                        pc += 1
                except:
                    pc += 1
            elif '=' in code:
                self.cmd_let(code)
                pc += 1
            elif cmd in ('END', 'STOP'):
                break
            elif cmd == 'REM':
                pc += 1
            else:
                pc += 1
        
        return '\n'.join(out) + '\n' if out else None


def main():
    print(CLEAR, end='')
    print(f"{GREEN}{BG}")
    print()
    print("   █████╗ ██████╗ ██████╗ ██╗     ███████╗  ][")
    print("  ██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝")
    print("  ███████║██████╔╝██████╔╝██║     █████╗")
    print("  ██╔══██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝")
    print("  ██║  ██║██║     ██║     ███████╗███████╗")
    print("  ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚══════╝")
    print()
    print("         CLEANROOM EDITION")
    print()
    print("  All text rendered using pixels from")
    print("  the cleanroom character generator ROM")
    print()
    
    # Load ROM
    charrom = CharacterROM()
    
    base = os.path.dirname(os.path.abspath(__file__))
    rom_path = os.path.join(base, 'cleanroom_roms/chargen.bin')
    if os.path.exists(rom_path):
        print(f"  ✓ Character ROM loaded ({os.path.getsize(rom_path)} bytes)")
    else:
        print("  ✗ Character ROM not found!")
    
    print()
    print("  Display: 20x12 chars = 140x96 pixels")
    print("  (Needs ~150 column terminal)")
    print()
    print(f"{RESET}")
    input("  Press Enter to start...")
    
    screen = PixelScreen(charrom, cols=20, rows=12)
    apple = Apple2(screen)
    apple.run()
    print(f"{RESET}")


if __name__ == "__main__":
    main()
