#!/usr/bin/env python3
"""
Python Terminal - A fully functional command terminal implemented in Python
"""

import os
import sys
import shutil
import platform
import psutil
import readline
import glob
import fnmatch
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter
from colorama import Fore, Back, Style, init

# Import natural language command processor
try:
    from nlp_commands import NLCommandProcessor
except ImportError:
    # Will be initialized later if available
    NLCommandProcessor = None

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

class PythonTerminal:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.command_history = []
        self.running = True
        self.commands = {
            'ls': self.list_directory,
            'cd': self.change_directory,
            'pwd': self.print_working_directory,
            'mkdir': self.make_directory,
            'rm': self.remove_file_or_directory,
            'mv': self.move_file,
            'exit': self.exit_terminal,
            'help': self.show_help,
            'cpu': self.show_cpu_usage,
            'memory': self.show_memory_usage,
            'ps': self.list_processes,
            'cat': self.cat_file,
            'head': self.head_file,
            'find': self.find_files,
            'export_history': self.export_history,
            'clear': self.clear_screen,
            'nl': self.process_natural_language,
            'write': self.write_to_file,
        }
        
        # Setup readline for command history and tab completion
        readline.set_completer(self.completer)
        readline.parse_and_bind("tab: complete")
        
        # Initialize natural language processor if available
        self.nlp = None
        if NLCommandProcessor is not None:
            self.nlp = NLCommandProcessor(self)
        
    def completer(self, text, state):
        """Tab completion function for readline"""
        line = readline.get_line_buffer()
        stripped = line.lstrip()
        
        # If we're at the start of the line, complete commands
        if not stripped:
            commands = list(self.commands.keys())
            results = [c + ' ' for c in commands if c.startswith(text)] + [None]
            return results[state]
            
        # If we have a command, complete files/directories
        cmd = line.split()[0]
        if cmd in ['cd', 'ls', 'rm', 'cat', 'head', 'mkdir']:
            path = text
            if not path:
                path = './'
            matches = glob.glob(os.path.join(self.current_dir, path) + '*')
            results = [os.path.basename(match) + ('/' if os.path.isdir(match) else ' ') 
                      for match in matches if os.path.basename(match).startswith(text)]
            return results[state] if state < len(results) else None
            
        return None
        
    def run(self):
        """Main terminal loop"""
        print(f"{Fore.GREEN}Python Terminal v1.0{Style.RESET_ALL}")
        print(f"Type {Fore.CYAN}help{Style.RESET_ALL} for a list of commands")
        
        while self.running:
            try:
                # Display prompt with current directory
                prompt = f"{Fore.BLUE}{os.path.basename(self.current_dir)}{Fore.GREEN}$ {Style.RESET_ALL}"
                user_input = input(prompt)
                
                if not user_input.strip():
                    continue
                    
                # Add command to history
                self.command_history.append(user_input)
                
                # Parse the command
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                # Execute the command
                if command in self.commands:
                    self.commands[command](args)
                else:
                    print(f"{Fore.RED}Error: Unknown command '{command}'{Style.RESET_ALL}")
                    print(f"Type {Fore.CYAN}help{Style.RESET_ALL} for a list of available commands")
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit the terminal")
            except Exception as e:
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    
    def list_directory(self, args):
        """List directory contents (ls command)"""
        target_dir = self.current_dir
        pattern = None

        # Check for a pattern in the arguments
        parts = args.split(maxsplit=1)
        if len(parts) > 0:
            if '*' in parts[0] or '?' in parts[0] or '[' in parts[0]:
                pattern = parts[0]
                if len(parts) > 1:
                    target_dir = parts[1]
            else:
                target_dir = parts[0]

        # Resolve target_dir to an absolute path
        if not target_dir.startswith('/'):
            target_dir = os.path.join(self.current_dir, target_dir)
        target_dir = os.path.normpath(target_dir)

        try:
            items = os.listdir(target_dir)
            filtered_items = []

            if pattern:
                # Filter items based on the glob pattern
                for item in items:
                    if fnmatch.fnmatch(item, pattern):
                        filtered_items.append(item)
            else:
                filtered_items = items

            for item in sorted(filtered_items):
                full_path = os.path.join(target_dir, item)
                if os.path.isdir(full_path):
                    print(f"{Fore.BLUE}{item}/{Style.RESET_ALL}")
                elif os.access(full_path, os.X_OK):
                    print(f"{Fore.GREEN}{item}{Style.RESET_ALL}")
                else:
                    print(item)
        except FileNotFoundError:
            print(f"{Fore.RED}Error: Directory '{target_dir}' not found{Style.RESET_ALL}")
        except PermissionError:
            print(f"{Fore.RED}Error: Permission denied for '{target_dir}'{Style.RESET_ALL}")

    def find_files(self, args):
        """Search for files in the current directory and its subdirectories."""
        parts = args.split(maxsplit=1)
        if not parts:
            print(f"{Fore.RED}Error: Please provide a search term.{Style.RESET_ALL}")
            return

        search_term = parts[0]
        target_dir = self.current_dir

        if len(parts) > 1:
            target_dir = parts[1]

        # Resolve target_dir to an absolute path
        if not target_dir.startswith('/'):
            target_dir = os.path.join(self.current_dir, target_dir)
        target_dir = os.path.normpath(target_dir)

        if not os.path.isdir(target_dir):
            print(f"{Fore.RED}Error: Directory '{target_dir}' not found.{Style.RESET_ALL}")
            return

        print(f"Searching for '{search_term}' in '{target_dir}'...")
        found_files = []
        try:
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if fnmatch.fnmatch(file, search_term):
                        found_files.append(os.path.join(root, file))
            
            if found_files:
                for f in sorted(found_files):
                    print(f)
            else:
                print(f"No files found matching '{search_term}' in '{target_dir}'.")
        except PermissionError:
            print(f"{Fore.RED}Error: Permission denied to access '{target_dir}'.{Style.RESET_ALL}")

    def export_history(self, args):
        """Export command history to a .txt file."""
        if not args:
            print(f"{Fore.RED}Error: Please provide a filename to export history to.{Style.RESET_ALL}")
            return

        filename = args
        if not filename.endswith(".txt"):
            filename += ".txt"

        file_path = os.path.join(self.current_dir, filename)

        try:
            with open(file_path, 'w') as f:
                for i in range(readline.get_current_history_length()):
                    f.write(readline.get_history_item(i + 1) + '\n')
            print(f"Command history exported to '{file_path}'{Style.RESET_ALL}")
        except IOError:
            print(f"{Fore.RED}Error: Could not write to file '{file_path}'{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"{Fore.RED}Error: Directory '{target_dir}' not found{Style.RESET_ALL}")
        except PermissionError:
            print(f"{Fore.RED}Error: Permission denied for '{target_dir}'{Style.RESET_ALL}")
    
    def change_directory(self, args):
        """Change current directory (cd command)"""
        if not args:
            # Default to home directory if no args
            target_dir = os.path.expanduser("~")
        else:
            # Handle relative paths
            if args.startswith('/'):
                target_dir = args
            else:
                target_dir = os.path.join(self.current_dir, args)
                
        # Normalize path
        target_dir = os.path.normpath(target_dir)
        
        try:
            os.chdir(target_dir)
            self.current_dir = os.getcwd()
        except FileNotFoundError:
            print(f"{Fore.RED}Error: Directory '{args}' not found{Style.RESET_ALL}")
        except NotADirectoryError:
            print(f"{Fore.RED}Error: '{args}' is not a directory{Style.RESET_ALL}")
        except PermissionError:
            print(f"{Fore.RED}Error: Permission denied for '{args}'{Style.RESET_ALL}")
    
    def print_working_directory(self, args):
        """Print current working directory (pwd command)"""
        print(self.current_dir)
    
    def make_directory(self, args):
        """Create a new directory (mkdir command)"""
        if not args:
            print(f"{Fore.RED}Error: Directory name not specified{Style.RESET_ALL}")
            return
            
        try:
            # Handle multiple directories
            dirs = args.split()
            for dir_name in dirs:
                if dir_name.startswith('/'):
                    # Absolute path
                    os.makedirs(dir_name, exist_ok=True)
                else:
                    # Relative path
                    os.makedirs(os.path.join(self.current_dir, dir_name), exist_ok=True)
        except PermissionError:
            print(f"{Fore.RED}Error: Permission denied{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error creating directory: {str(e)}{Style.RESET_ALL}")
    
    def remove_file_or_directory(self, args):
        """Remove file or directory (rm command)"""
        if not args:
            print(f"{Fore.RED}Error: File or directory not specified{Style.RESET_ALL}")
            return
            
        # Parse arguments for recursive flag
        recursive = False
        force = False
        parts = args.split()
        
        # Check for flags
        if '-r' in parts or '-rf' in parts or '-fr' in parts:
            recursive = True
            parts = [p for p in parts if p not in ['-r', '-rf', '-fr']]
        
        if '-f' in parts:
            force = True
            parts = [p for p in parts if p != '-f']
            
        if not parts:
            print(f"{Fore.RED}Error: File or directory not specified{Style.RESET_ALL}")
            return
            
        target = parts[0]
        if not target.startswith('/'):
            target = os.path.join(self.current_dir, target)
            
        try:
            if os.path.isdir(target):
                if recursive:
                    shutil.rmtree(target)
                else:
                    os.rmdir(target)
            else:
                os.remove(target)
        except FileNotFoundError:
            if not force:
                print(f"{Fore.RED}Error: '{parts[0]}' not found{Style.RESET_ALL}")
        except IsADirectoryError:
            print(f"{Fore.RED}Error: '{parts[0]}' is a directory. Use -r flag to remove directories{Style.RESET_ALL}")
        except OSError as e:
            if not force:
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

    def move_file(self, args):
        """Move a file or directory (mv command)."""
        parts = args.split()
        if len(parts) != 2:
            print(f"{Fore.RED}Usage: mv <source> <destination>{Style.RESET_ALL}")
            return

        source_arg, dest_arg = parts[0], parts[1]

        # Resolve source path
        if source_arg.startswith('/'):
            source_path = source_arg
        else:
            source_path = os.path.join(self.current_dir, source_arg)
        
        # Resolve destination path
        if dest_arg.startswith('/'):
            dest_path = dest_arg
        else:
            dest_path = os.path.join(self.current_dir, dest_arg)

        try:
            shutil.move(source_path, dest_path)
            print(f"{Fore.GREEN}Moved '{source_arg}' to '{dest_arg}'{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"{Fore.RED}Error: Source '{source_arg}' not found.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error moving file: {e}{Style.RESET_ALL}")

    def move_file(self, args):
        """Move a file or directory (mv command)."""
        parts = args.split()
        if len(parts) != 2:
            print(f"{Fore.RED}Usage: mv <source> <destination>{Style.RESET_ALL}")
            return

        source_arg, dest_arg = parts[0], parts[1]

        # Resolve source path
        if source_arg.startswith('/'):
            source_path = source_arg
        else:
            source_path = os.path.join(self.current_dir, source_arg)
        
        # Resolve destination path
        if dest_arg.startswith('/'):
            dest_path = dest_arg
        else:
            dest_path = os.path.join(self.current_dir, dest_arg)

        try:
            shutil.move(source_path, dest_path)
            print(f"{Fore.GREEN}Moved '{source_arg}' to '{dest_arg}'{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"{Fore.RED}Error: Source '{source_arg}' not found.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error moving file: {e}{Style.RESET_ALL}")
    
    def exit_terminal(self, args):
        """Exit the terminal"""
        print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
        self.running = False
    
    def show_help(self, args):
        """Show help information"""
        print(f"{Fore.GREEN}Available commands:{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}ls{Style.RESET_ALL}              - List directory contents")
        print(f"  {Fore.CYAN}cd <dir>{Style.RESET_ALL}        - Change directory")
        print(f"  {Fore.CYAN}pwd{Style.RESET_ALL}             - Print current working directory")
        print(f"  {Fore.CYAN}mkdir <dir>{Style.RESET_ALL}     - Create a new directory")
        print(f"  {Fore.CYAN}rm [-r] <file/dir>{Style.RESET_ALL} - Remove file or directory (-r for recursive)")
        print(f"  {Fore.CYAN}mv <source> <destination>{Style.RESET_ALL} - Move a file or directory")
        print(f"  {Fore.CYAN}cat <file>{Style.RESET_ALL}      - Display file contents")
        print(f"  {Fore.CYAN}head <file>{Style.RESET_ALL}     - Display first 10 lines of a file")
        print(f"  {Fore.CYAN}find <pattern> [dir]{Style.RESET_ALL} - Search for files by pattern")
        print(f"  {Fore.CYAN}export_history <file>{Style.RESET_ALL} - Export command history to file")
        print(f"  {Fore.CYAN}cpu{Style.RESET_ALL}             - Show CPU usage")
        print(f"  {Fore.CYAN}memory{Style.RESET_ALL}          - Show memory usage")
        print(f"  {Fore.CYAN}ps{Style.RESET_ALL}              - List running processes")
        print(f"  {Fore.CYAN}clear{Style.RESET_ALL}           - Clear the screen")
        print(f"  {Fore.CYAN}nl <text>{Style.RESET_ALL}       - Process natural language command")
        print(f"  {Fore.CYAN}write <file> <content>{Style.RESET_ALL} - Write content to a file")
        print(f"  {Fore.CYAN}exit{Style.RESET_ALL}            - Exit the terminal")
        print(f"  {Fore.CYAN}help{Style.RESET_ALL}            - Show this help message")
        
    def show_cpu_usage(self, args):
        """Show CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        print(f"CPU Usage: {Fore.YELLOW}{cpu_percent}%{Style.RESET_ALL}")
        print(f"CPU Cores: {cpu_count}")
        
    def show_memory_usage(self, args):
        """Show memory usage"""
        memory = psutil.virtual_memory()
        
        print(f"Memory Usage: {Fore.YELLOW}{memory.percent}%{Style.RESET_ALL}")
        print(f"Total: {self._format_bytes(memory.total)}")
        print(f"Available: {self._format_bytes(memory.available)}")
        print(f"Used: {self._format_bytes(memory.used)}")
        
    def list_processes(self, args):
        """List running processes"""
        print(f"{Fore.GREEN}{'PID':<10} {'CPU%':<10} {'MEM%':<10} {'NAME':<30}{Style.RESET_ALL}")
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                pid = info.get('pid', '---')
                cpu_percent_val = info.get('cpu_percent')
                memory_percent_val = info.get('memory_percent')
                
                cpu_percent = cpu_percent_val if cpu_percent_val is not None else 0.0
                memory_percent = memory_percent_val if memory_percent_val is not None else 0.0
                
                name = info.get('name', '---')
                print(f"{pid:<10} {cpu_percent:<10.1f} {memory_percent:<10.1f} {name:<30}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
    def cat_file(self, args):
        """Display file contents (cat command)"""
        if not args:
            print(f"{Fore.RED}Error: File not specified{Style.RESET_ALL}")
            return
            
        file_path = args
        if not file_path.startswith('/'):
            file_path = os.path.join(self.current_dir, file_path)
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Pygments integration
                try:
                    # Try to get lexer by file extension
                    ext = os.path.splitext(file_path)[1].lstrip('.')
                    if ext:
                        lexer = get_lexer_by_name(ext)
                    else:
                        lexer = guess_lexer(content) # Fallback to guess if no extension
                except Exception: # Catch any error during lexer determination
                    lexer = guess_lexer(content) # Fallback to guess
                print(highlight(content, lexer, TerminalFormatter()))
        except FileNotFoundError:
            print(f"{Fore.RED}Error: File '{args}' not found{Style.RESET_ALL}")
        except IsADirectoryError:
            print(f"{Fore.RED}Error: '{args}' is a directory{Style.RESET_ALL}")
        except PermissionError:
            print(f"{Fore.RED}Error: Permission denied for '{args}'{Style.RESET_ALL}")
        except UnicodeDecodeError:
            print(f"{Fore.RED}Error: '{args}' appears to be a binary file{Style.RESET_ALL}")
            
    def head_file(self, args):
        """Display first 10 lines of a file (head command)"""
        parts = args.split()
        file_path = parts[-1]
        
        # Default number of lines
        num_lines = 10
        
        # Check if -n flag is present
        if len(parts) > 1 and parts[0] == '-n' and len(parts) >= 3:
            try:
                num_lines = int(parts[1])
                file_path = parts[2]
            except ValueError:
                print(f"{Fore.RED}Error: Invalid number of lines{Style.RESET_ALL}")
                return
                
        if not file_path.startswith('/'):
            file_path = os.path.join(self.current_dir, file_path)
            
        try:
            with open(file_path, 'r') as f:
                lines = [f.readline() for _ in range(num_lines)]
                content = "".join(lines)
                try:
                    ext = os.path.splitext(file_path)[1].lstrip('.')
                    if ext:
                        lexer = get_lexer_by_name(ext)
                    else:
                        lexer = guess_lexer(content)
                except Exception:
                    lexer = guess_lexer(content)
                print(highlight(content, lexer, TerminalFormatter()))
        except FileNotFoundError:
            print(f"{Fore.RED}Error: File '{file_path}' not found{Style.RESET_ALL}")
        except IsADirectoryError:
            print(f"{Fore.RED}Error: '{file_path}' is a directory{Style.RESET_ALL}")
        except PermissionError:
            print(f"{Fore.RED}Error: Permission denied for '{file_path}'{Style.RESET_ALL}")
        except UnicodeDecodeError:
            print(f"{Fore.RED}Error: '{file_path}' appears to be a binary file{Style.RESET_ALL}")
            
    def clear_screen(self, args):
        """Clear the terminal screen"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')

    def write_to_file(self, args):
        """Write content to a file (write command)"""
        try:
            filename, content = args.split(maxsplit=1)
            with open(os.path.join(self.current_dir, filename), 'w') as f:
                f.write(content)
            print(f"Content written to '{filename}'")
        except ValueError:
            print(f"{Fore.RED}Error: Invalid arguments. Usage: write <filename> <content>{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error writing to file: {e}{Style.RESET_ALL}")
    
    def process_natural_language(self, args):
        """Process natural language commands"""
        if not args:
            print(f"{Fore.RED}Error: No natural language command provided{Style.RESET_ALL}")
            print(f"Usage: nl <natural language command>")
            print(f"Example: nl create a folder called test")
            return
            
        if self.nlp is None:
            print(f"{Fore.RED}Error: Natural language processing is not available{Style.RESET_ALL}")
            print(f"Make sure the nlp_commands.py file is in the same directory")
            return
            
        success, message = self.nlp.process(args)
        if success:
            print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{message}{Style.RESET_ALL}")
        
    def _format_bytes(self, bytes):
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} PB"

if __name__ == "__main__":
    terminal = PythonTerminal()
    terminal.run()