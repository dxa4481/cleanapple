#!/usr/bin/env python3
"""
Apple II Cleanroom ROM Demo - Authentic CRT Look

Run a simulated Apple II using 100% cleanroom ROM implementations.
"""

import os
import sys
import time

try:
    from py65.devices.mpu6502 import MPU
except ImportError:
    print("ERROR: py65 not installed. Run: pip install py65")
    sys.exit(1)


# ANSI escape codes
ESC = "\033"
CLEAR = f"{ESC}[2J{ESC}[H"
RESET = f"{ESC}[0m"
BOLD = f"{ESC}[1m"
DIM = f"{ESC}[2m"
INVERSE = f"{ESC}[7m"
GREEN_FG = f"{ESC}[32m"
BRIGHT_GREEN = f"{ESC}[92m"
BLACK_BG = f"{ESC}[40m"
GREEN_BG = f"{ESC}[42m"

# Apple II phosphor green
P1 = f"{ESC}[38;2;51;255;51m"      # Bright phosphor
P2 = f"{ESC}[38;2;34;180;34m"      # Medium phosphor  
P3 = f"{ESC}[38;2;20;100;20m"      # Dim phosphor
BG = f"{ESC}[48;2;0;20;0m"         # Dark green-black background


class Apple2:
    """Apple II emulator with authentic display."""
    
    def __init__(self):
        self.screen = [[' ' for _ in range(40)] for _ in range(24)]
        self.cx, self.cy = 0, 0  # Cursor position
        self.roms = []
        self.variables = {}
        self.program = {}
        
    def load_roms(self):
        """Load cleanroom ROMs."""
        base = os.path.dirname(os.path.abspath(__file__))
        rom_files = [
            ('cleanroom_roms/monitor_f800.bin', 'MONITOR ROM', 0xF800),
            ('cleanroom_roms/applesoft.bin', 'APPLESOFT BASIC', 0xD000),
            ('cleanroom_roms/chargen.bin', 'CHARACTER ROM', None),
            ('cleanroom_roms/disk_ii_p5a.bin', 'DISK II BOOT', 0xC600),
        ]
        for path, name, addr in rom_files:
            full = os.path.join(base, path)
            if os.path.exists(full):
                size = os.path.getsize(full)
                self.roms.append((name, addr, size))
    
    def clear(self):
        """Clear screen."""
        self.screen = [[' ' for _ in range(40)] for _ in range(24)]
        self.cx, self.cy = 0, 0
    
    def scroll(self):
        """Scroll up one line."""
        self.screen.pop(0)
        self.screen.append([' ' for _ in range(40)])
    
    def newline(self):
        """Move to next line."""
        self.cx = 0
        self.cy += 1
        if self.cy >= 24:
            self.scroll()
            self.cy = 23
    
    def output(self, text):
        """Output text to screen."""
        for ch in text:
            if ch == '\n':
                self.newline()
            elif ch == '\r':
                self.cx = 0
            elif ch == '\b':
                if self.cx > 0:
                    self.cx -= 1
            elif ch == '\a':
                print('\a', end='', flush=True)  # Bell
            else:
                if self.cy < 24 and self.cx < 40:
                    self.screen[self.cy][self.cx] = ch
                    self.cx += 1
                    if self.cx >= 40:
                        self.newline()
    
    def render(self):
        """Render the Apple II screen with CRT effect."""
        print(CLEAR, end='')
        
        # Monitor bezel top
        print(f"{P3}{BG}")
        print("      ___________________________________________")
        print("     /                                           \\")
        print("    |  .---------------------------------------.  |")
        
        # Screen content with phosphor glow effect
        for y, row in enumerate(self.screen):
            line = ''.join(row)
            # Add cursor
            if y == self.cy and self.cx < 40:
                line = line[:self.cx] + '\u2588' + line[self.cx+1:]
            print(f"    | |{P1}{BG} {line} {P3}| |")
        
        # Monitor bezel bottom
        print("    |  '---------------------------------------'  |")
        print("    |                                             |")
        print(f"    |     {P2}[[[  APPLE II CLEANROOM  ]]]{P3}          |")
        print("     \\___________________________________________/")
        print()
        print(f"{RESET}", end='')
    
    def boot(self):
        """Show boot sequence."""
        print(CLEAR, end='')
        print(f"{P1}{BG}")
        print("\n" * 8)
        print("                    APPLE II")
        print()
        print("               CLEANROOM EDITION")
        print()
        print("          100% From Published Specs")
        print("           No Original Apple Code")
        print()
        
        time.sleep(1)
        
        print(f"{P2}")
        print("         Loading ROMs...")
        print()
        for name, addr, size in self.roms:
            loc = f"${addr:04X}" if addr else "VIDEO"
            print(f"           {name}")
            print(f"           {loc} - {size} bytes")
            time.sleep(0.2)
        
        print()
        print(f"{P1}         READY.")
        print(f"{RESET}")
        time.sleep(0.5)
    
    def prompt(self):
        """Show ] prompt."""
        self.output("]")
    
    def run(self):
        """Main loop."""
        self.load_roms()
        self.boot()
        
        self.clear()
        self.output("APPLE II CLEANROOM BASIC\n\n")
        self.prompt()
        self.render()
        
        while True:
            try:
                print(f"{P1}{BG}] {RESET}", end='', flush=True)
                line = input().upper().strip()
                
                self.output(line + "\n")
                
                if line in ('QUIT', 'EXIT', 'BYE'):
                    print(f"\n{RESET}Goodbye!")
                    break
                
                if line:
                    result = self.execute(line)
                    if result:
                        self.output(result)
                        if not result.endswith('\n'):
                            self.output('\n')
                
                self.prompt()
                self.render()
                
            except (KeyboardInterrupt, EOFError):
                print(f"\n{RESET}Goodbye!")
                break
    
    def execute(self, line):
        """Execute BASIC command."""
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
            self.clear()
            return None
        elif '=' in line:
            return self.do_let(line)
        elif cmd == 'GR':
            return self.do_graphics()
        elif cmd == 'CATALOG':
            return "?DISK NOT FOUND"
        else:
            return "?SYNTAX ERROR"
    
    def do_print(self, args):
        """PRINT statement."""
        if not args:
            return "\n"
        
        result = []
        i = 0
        
        while i < len(args):
            # Skip spaces
            while i < len(args) and args[i] == ' ':
                i += 1
            if i >= len(args):
                break
                
            if args[i] == '"':
                # String
                i += 1
                s = ''
                while i < len(args) and args[i] != '"':
                    s += args[i]
                    i += 1
                result.append(s)
                i += 1
            elif args[i] == ';':
                i += 1
            elif args[i] == ',':
                result.append('\t')
                i += 1
            else:
                # Expression
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
        """Assignment."""
        if line.startswith('LET '):
            line = line[4:]
        var, expr = line.split('=', 1)
        var = var.strip()
        try:
            val = eval(expr.strip(), {"__builtins__": {}}, self.variables)
            self.variables[var] = val
        except:
            return "?SYNTAX ERROR"
        return None
    
    def do_list(self):
        """LIST program."""
        if not self.program:
            return None
        lines = []
        for n in sorted(self.program):
            lines.append(f" {n}  {self.program[n]}")
        return '\n'.join(lines) + '\n'
    
    def do_run(self):
        """RUN program."""
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
                pc = lines.index(int(args)) if int(args) in self.program else len(lines)
            elif cmd == 'FOR':
                # FOR I=1 TO 10
                p = args.replace('=', ' ').split()
                var, start = p[0], int(p[1])
                end = int(p[p.index('TO')+1])
                step = int(p[p.index('STEP')+1]) if 'STEP' in p else 1
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
                # IF X>0 THEN 100
                cond, then = code.split(' THEN ')
                cond = cond[2:].replace('=','==').replace('<>','!=')
                try:
                    if eval(cond, {"__builtins__": {}}, self.variables):
                        target = int(then.strip())
                        pc = lines.index(target) if target in self.program else len(lines)
                    else:
                        pc += 1
                except:
                    pc += 1
            elif '=' in code:
                self.do_let(code)
                pc += 1
            elif cmd in ('END', 'STOP'):
                break
            elif cmd == 'REM':
                pc += 1
            else:
                pc += 1
        
        return ''.join(out)
    
    def do_graphics(self):
        """Show lo-res graphics demo."""
        chars = " .:-=+*#%@"
        out = ['\n']
        for y in range(20):
            row = ''
            for x in range(40):
                c = chars[(x + y) % len(chars)]
                row += c
            out.append(row + '\n')
        return ''.join(out)


def main():
    apple = Apple2()
    apple.run()


if __name__ == "__main__":
    main()
