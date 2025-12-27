#!/usr/bin/env python3
"""
Apple II Cleanroom ROM Demo

Simple, working demo with green phosphor look.
Type CHARSET to see the actual character ROM patterns.
"""

import os
import sys
import time

# ANSI escape codes
ESC = "\033"
CLEAR = f"{ESC}[2J{ESC}[H"
RESET = f"{ESC}[0m"

# Apple II green phosphor
GREEN = f"{ESC}[32m"
BRIGHT = f"{ESC}[92m"
BG = f"{ESC}[40m"
DIM = f"{ESC}[2m"


class CharacterROM:
    """Load the cleanroom character generator ROM."""
    
    def __init__(self):
        self.patterns = {}
        base = os.path.dirname(os.path.abspath(__file__))
        rom_path = os.path.join(base, 'cleanroom_roms/chargen.bin')
        
        if os.path.exists(rom_path):
            with open(rom_path, 'rb') as f:
                rom = f.read()
            for i in range(64):
                self.patterns[i] = list(rom[i*8:(i+1)*8])
    
    def get_char_for_index(self, idx):
        """Get ASCII character for ROM index."""
        if 0 <= idx <= 31:
            return chr(idx + 64)  # @ A B C ... _ 
        elif 32 <= idx <= 63:
            return chr(idx)       # space ! " # ... ?
        return '?'
    
    def render_charset(self):
        """Render all 64 characters from the ROM as pixel art."""
        lines = []
        lines.append(f"{BRIGHT}╔════════════════════════════════════════════════════════════════════════╗")
        lines.append(f"║  CLEANROOM CHARACTER GENERATOR ROM - 64 CHARACTERS (7x8 PIXELS EACH)   ║")
        lines.append(f"╚════════════════════════════════════════════════════════════════════════╝{GREEN}")
        lines.append("")
        
        # Render 8 characters per row, 8 rows total
        for row in range(8):
            # Each character is 8 pixels tall, render 2 at a time with half-blocks
            for pixel_row in range(0, 8, 2):
                line = "  "
                for col in range(8):
                    idx = row * 8 + col
                    pattern = self.patterns.get(idx, [0]*8)
                    
                    # Render this character's pixels for these 2 rows
                    for bit in range(7):
                        top = 1 if pattern[pixel_row] & (1 << bit) else 0
                        bot = 1 if pattern[pixel_row + 1] & (1 << bit) else 0
                        
                        if top and bot:
                            line += "█"
                        elif top:
                            line += "▀"
                        elif bot:
                            line += "▄"
                        else:
                            line += " "
                    line += "  "  # Space between chars
                lines.append(line)
            
            # Character labels
            label_line = "  "
            for col in range(8):
                idx = row * 8 + col
                ch = self.get_char_for_index(idx)
                label_line += f"  {ch}      "
            lines.append(f"{DIM}{label_line}{RESET}{GREEN}")
            lines.append("")
        
        return '\n'.join(lines)


class Apple2:
    """Simple Apple II BASIC interpreter."""
    
    def __init__(self):
        self.charrom = CharacterROM()
        self.screen = []
        self.variables = {}
        self.program = {}
        self.max_lines = 20
    
    def output(self, text):
        """Add text to screen buffer."""
        for line in text.split('\n'):
            self.screen.append(line)
        # Keep only last N lines
        while len(self.screen) > self.max_lines:
            self.screen.pop(0)
    
    def render(self):
        """Render the screen."""
        print(CLEAR, end='')
        print(f"{BRIGHT}{BG}")
        print("╔══════════════════════════════════════════╗")
        print("║{:^42}║".format("APPLE ][ CLEANROOM"))
        print("╠══════════════════════════════════════════╣")
        
        # Show screen content
        for i in range(self.max_lines):
            if i < len(self.screen):
                line = self.screen[i][:40]
            else:
                line = ""
            print(f"║ {GREEN}{line:<40}{BRIGHT} ║")
        
        print("╠══════════════════════════════════════════╣")
        print(f"║{DIM} QUIT EXIT  CHARSET  NEW RUN LIST {RESET}{BRIGHT}      ║")
        print("╚══════════════════════════════════════════╝")
        print(f"{RESET}")
    
    def run(self):
        """Main loop."""
        self.output("APPLE II CLEANROOM BASIC")
        self.output("TYPE 'CHARSET' TO VIEW CHARACTER ROM")
        self.output("")
        
        while True:
            self.render()
            
            try:
                print(f"{GREEN}]{RESET} ", end='', flush=True)
                line = input().strip().upper()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{RESET}")
                break
            
            if not line:
                self.output("]")
                continue
            
            self.output("]" + line)
            
            if line in ('QUIT', 'EXIT', 'BYE'):
                self.output("GOODBYE")
                self.render()
                break
            
            if line == 'CHARSET':
                # Show character ROM
                print(CLEAR, end='')
                print(f"{GREEN}{BG}")
                print(self.charrom.render_charset())
                print(f"\n{DIM}  Press Enter to continue...{RESET}")
                input()
                continue
            
            result = self.execute(line)
            if result:
                self.output(result.rstrip('\n'))
    
    def execute(self, line):
        """Execute a BASIC line."""
        # Line number = store
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
        
        commands = {
            'PRINT': self.do_print,
            '?': self.do_print,
            'LIST': lambda a: self.do_list(),
            'RUN': lambda a: self.do_run(),
            'NEW': lambda a: self.do_new(),
            'CLR': lambda a: self.do_new(),
            'HOME': lambda a: self.do_home(),
        }
        
        if cmd in commands:
            return commands[cmd](args)
        elif '=' in line:
            return self.do_let(line)
        else:
            return "?SYNTAX ERROR"
    
    def do_print(self, args):
        if not args:
            return ""
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
                    result.append('   ')
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
        return ''.join(result)
    
    def do_let(self, line):
        if line.startswith('LET '):
            line = line[4:]
        try:
            var, expr = line.split('=', 1)
            self.variables[var.strip()] = eval(
                expr.strip(), {"__builtins__": {}}, self.variables
            )
        except:
            return "?SYNTAX ERROR"
        return None
    
    def do_list(self):
        if not self.program:
            return None
        return '\n'.join(f" {n}  {self.program[n]}" for n in sorted(self.program))
    
    def do_new(self):
        self.program.clear()
        self.variables.clear()
        return None
    
    def do_home(self):
        self.screen.clear()
        return None
    
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
            
            code = self.program[lines[pc]]
            cmd = code.split()[0] if code.split() else ''
            args = code[len(cmd):].strip()
            
            if cmd in ('PRINT', '?'):
                r = self.do_print(args)
                if r:
                    out.append(r)
                pc += 1
            elif cmd == 'GOTO':
                target = int(args)
                pc = lines.index(target) if target in lines else len(lines)
            elif cmd == 'FOR':
                p = args.replace('=', ' ').split()
                var, start = p[0], int(p[1])
                end = int(p[p.index('TO') + 1])
                self.variables[var] = start
                stack.append((var, end, 1, pc))
                pc += 1
            elif cmd == 'NEXT':
                if stack:
                    var, end, step, fpc = stack[-1]
                    self.variables[var] += step
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
                then = code[idx+6:].strip()
                try:
                    if eval(cond, {"__builtins__": {}}, self.variables):
                        pc = lines.index(int(then))
                    else:
                        pc += 1
                except:
                    pc += 1
            elif '=' in code:
                self.do_let(code)
                pc += 1
            elif cmd in ('END', 'STOP', 'REM'):
                if cmd == 'REM':
                    pc += 1
                else:
                    break
            else:
                pc += 1
        
        return '\n'.join(out) if out else None


def main():
    print(CLEAR, end='')
    print(f"{BRIGHT}{BG}")
    print()
    print("      █████╗ ██████╗ ██████╗ ██╗     ███████╗")
    print("     ██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝")
    print("     ███████║██████╔╝██████╔╝██║     █████╗  ")
    print("     ██╔══██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝  ")
    print("     ██║  ██║██║     ██║     ███████╗███████╗")
    print("     ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚══════╝")
    print()
    print("            ][ CLEANROOM EDITION")
    print()
    print(f"{GREEN}     100% Implemented from Published Specs")
    print("        No Original Apple Code Used")
    print()
    
    # Show ROMs
    base = os.path.dirname(os.path.abspath(__file__))
    roms = [
        'cleanroom_roms/chargen.bin',
        'cleanroom_roms/monitor_f800.bin', 
        'cleanroom_roms/applesoft.bin',
        'cleanroom_roms/disk_ii_p5a.bin',
    ]
    
    print(f"{DIM}     Cleanroom ROMs loaded:{RESET}{GREEN}")
    for rom in roms:
        path = os.path.join(base, rom)
        if os.path.exists(path):
            name = os.path.basename(rom)
            size = os.path.getsize(path)
            print(f"       ✓ {name} ({size} bytes)")
    
    print()
    print(f"{RESET}")
    input("     Press Enter to start...")
    
    apple = Apple2()
    apple.run()
    print(f"{RESET}")


if __name__ == "__main__":
    main()
