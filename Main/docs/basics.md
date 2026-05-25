# WNim Basics

## Installation

### Minimum Requirements

- Windows 10/11
- Python 3.8 or higher

### Installing Dependencies

```powershell
pip install windows-curses pyperclip
```

### Running

```powershell
python editor.py [files...]
```

Examples:

```powershell
python editor.py script.py
python editor.py file1.py file2.js
python editor.py
```

## Interface

### Status Bar

The bottom of the screen displays:
- List of open tabs
- Save status (* - unsaved changes)
- Cursor position (line:column)
- Editor message

### Line Numbers

Line numbers are displayed on the left. Width - 6 characters.

## Basic Operations

### Creating a File

1. Start the editor without arguments
2. Begin typing text
3. Save via Ctrl+S or Ctrl+R

### Opening a File

1. Press Ctrl+O
2. Enter file path
3. Press Enter

### Saving

- Ctrl+S - save current file
- Ctrl+R - save with new name

### Exiting

- Ctrl+Q - exit editor
- Unsaved changes require confirmation

## Text Editing

### Typing

All printable characters are entered directly. Unicode is supported.

### Auto-close Brackets

Closing pairs are automatically added when typing:
- `()` - round brackets
- `[]` - square brackets
- `{}` - curly brackets
- `""` - double quotes
- `''` - single quotes

### Auto-indent

Indentation increases automatically after:
- `:` (Python)
- `{` (C-style languages)
- `[` (arrays)

### Cursor Movement

- Arrows - move one character/line
- Home/End - start/end of line
- PgUp/PgDn - move one screen

### Text Selection

Selection is not supported in the current version. For text operations, use copy/paste lines.

## Multiple Tabs

### Tab Management

- Ctrl+T - create new tab
- Ctrl+W - close current tab
- F1 - go to previous tab
- F2 - go to next tab

### Switching Between Files

Each tab represents a separate file or new buffer. Switching is done via F1/F2.

## Search and Navigation

### Find Text

1. Press Ctrl+F
2. Enter search query
3. Press Enter

Search starts from current cursor position.

### Go to Line

1. Press Ctrl+G
2. Enter line number
3. Press Enter

## Plugins

### Installing Lua

The lupa library is required for plugin support:

```powershell
pip install lupa
```

### Plugin Management

- Ctrl+L - load plugin
- Ctrl+U - unload plugin
- Ctrl+P - show plugin list

See docs/plugins.md for details.

## Supported Languages

Syntax highlighting is available for:

- Python (.py)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- C (.c, .h)
- C++ (.cpp, .cc, .cxx, .hpp, .hh)
- C# (.cs)
- PHP (.php)
- Go (.go)
- Rust (.rs)
- Kotlin (.kt, .kts)
- Bash (.sh, .bash, .zsh)
- Ruby (.rb, .erb)
- Lua (.lua)
- PowerShell (.ps1, .psm1, .psd1)
- Java (.java)
- Zig (.zig)
- Assembly (.asm, .s, .S)
- HTML (.html, .htm, .xhtml)
- CSS (.css)

## Configuration

Configuration file location:

- Windows: %USERPROFILE%\.config\wnim\config.json
- Linux/Mac: ~/.config/wnim/config.json

Example configuration:

```json
{
    "theme": "dark",
    "tab_size": 4,
    "line_numbers": true,
    "auto_close_brackets": true,
    "auto_indent": true
}
```

## Tips

1. Use Ctrl+K for quick line deletion
2. Hold Ctrl+K to delete multiple lines in sequence
3. Autocomplete is triggered via Ctrl+Space
4. Use tabs for working with multiple files
5. Plugins extend editor functionality
