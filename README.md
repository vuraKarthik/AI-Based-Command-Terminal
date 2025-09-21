# Python Terminal

A fully functional Python-based command terminal that mimics a real system terminal. This terminal executes standard commands, handles errors, and supports AI-driven natural language commands.

## Features

### Core Features
- File and directory operations:
  - `ls` - List directory contents
  - `cd <dir>` - Change directory
  - `pwd` - Print current working directory
  - `mkdir <dir>` - Create a new directory
  - `rm [-r] <file/dir>` - Remove file or directory
  - `cat <file>` - Display file contents
  - `head <file>` - Display first lines of a file
- System monitoring:
  - `cpu` - Show CPU usage
  - `memory` - Show memory usage
  - `ps` - List running processes
- Error handling for invalid commands or paths
- Cross-platform compatibility (Linux, macOS, Windows)

### Enhanced Features
- Natural language command processing with the `nl` command
- Command history and auto-completion (using Tab key)
- Color-coded outputs for improved readability
- Multi-level directory navigation
- File preview capabilities

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)

### Setup

1. Clone the repository or download the source code:
```
git clone https://github.com/yourusername/python-terminal.git
cd python-terminal
```

2. Install the required dependencies:
```
pip install psutil colorama
```

3. Make the main script executable (Linux/macOS):
```
chmod +x main.py
```

## Usage

### Starting the Terminal

Run the terminal using Python:
```
python main.py
```

Or directly (Linux/macOS):
```
./main.py
```

### Basic Commands

- List files in the current directory:
```
ls
```

- Change to another directory:
```
cd path/to/directory
```

- Show current directory:
```
pwd
```

- Create a new directory:
```
mkdir new_directory
```

- Remove a file or directory:
```
rm file.txt
rm -r directory
```

- View file contents:
```
cat file.txt
```

- View first lines of a file:
```
head file.txt
```

### System Monitoring

- Show CPU usage:
```
cpu
```

- Show memory usage:
```
memory
```

- List running processes:
```
ps
```

### Natural Language Commands

The terminal supports natural language commands using the `nl` prefix:

```
nl create a folder called projects
nl show the current directory
nl list files in the current directory
nl show cpu usage
nl create a folder called docs and move report.txt into it
```

## Architecture

The Python Terminal is built with a modular architecture:

1. **Main Terminal Interface** (`main.py`):
   - Handles user input and command execution
   - Manages the terminal environment and state
   - Provides core command functionality

2. **Natural Language Processor** (`nlp_commands.py`):
   - Converts natural language commands to terminal operations
   - Uses pattern matching to identify command intent
   - Executes corresponding terminal functions

## Cross-Platform Compatibility

The terminal is designed to work across different operating systems:

- Uses `os` and `platform` modules to handle system-specific operations
- Implements platform-specific commands (like `clear` vs `cls`)
- Uses `colorama` for cross-platform colored output

## Future Enhancements

Potential areas for future development:

- More advanced natural language processing using machine learning
- Network commands and remote file operations
- Plugin system for extending functionality
- GUI interface option
- More advanced file operations (copy, move, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.