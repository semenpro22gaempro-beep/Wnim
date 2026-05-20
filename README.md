<img width="500" height="500" alt="1000022824 (1)" src="https://github.com/user-attachments/assets/8fc765b0-dd93-4af3-8fea-8d3fb321b93c" />

# WNim — Console Code Editor for Windows

Wnim is a lightweight command-line text editor. It combines the minimalism of the classic Vim editor with the familiar ergonomics of the Windows operating system. The project is designed for users who value the speed of working in the terminal but don't want to spend time memorizing complex Vim key combinations.
- Defoult windows hotkeys
- Simple for noobs
- Performance for low-end devices

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)



##  Installation

### Option 1: Automatic Installer (Recommended)

1. Clone or download this repository:
```powershell
git clone git@github.com:semenpro22gaempro-beep/Wnim.git
cd Wnim
```

2. Run the installer:
```powershell
.\install.ps1
```

3. Restart your terminal and run:
```powershell
wnim filename.py
```

### Option 2: Manual Installation

1. Install Python 3.8+ from [python.org](https://python.org)

2. Install dependencies:
```powershell
pip install windows-curses pyperclip
```

3. Run the editor:
```powershell
python editor.py filename.py
```

## ⌨️ Hotkeys

| Key | Action |
|-----|--------|
| `Ctrl+Space` | Autocomplete |
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save |
| `Ctrl+W` | Save as |
| `Ctrl+Q` | Quit |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+A` | File stats |
| `Ctrl+C` | Copy line |
| `Ctrl+X` | Cut line |
| `Ctrl+V` | Paste |
| `Ctrl+F` | Find |
| `Ctrl+G` | Go to line |
| `Home/End` | Start/End of line |
| `PgUp/PgDn` | Page up/down |
| `Tab` | Indent |
| `Shift+Tab` | Unindent |

##  Supported Languages

| Language | Extensions |
|----------|------------|
| Python | `.py` |
| JavaScript/TypeScript | `.js`, `.jsx`, `.ts`, `.tsx` |
| C | `.c`, `.h` |
| C++ | `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh` |
| C# | `.cs` |
| Bash | `.sh`, `.bash`, `.zsh` |
| Ruby | `.rb`, `.erb` |
| Lua | `.lua` |
| PowerShell | `.ps1`, `.psm1`, `.psd1` |
| Java | `.java` |
| Zig | `.zig` |
| Assembly | `.asm`, `.s`, `.S` |
| HTML | `.html`, `.htm`, `.xhtml` |
| CSS | `.css` |

##  Usage Examples

```powershell
# Open existing file
wnim script.py

# Create new file
wnim

# Open C# file
wnim Program.cs

# Open Java file
wnim Main.java

# Open HTML file
wnim index.html

# Open Zig file
wnim main.zig
```

##  Development

### Project Structure

```
wnim/
├── editor.py          # Main editor code
├── wnim.py            # Command-line entry point
├── install.ps1        # Windows installer script
└── README_WNIM.md     # This file
```

### Modify and Test

1. Edit `editor.py`
2. Test changes:
```powershell
python editor.py test.py
```

3. Reinstall to update:
```powershell
.\install.ps1
```

##  Requirements

- **Windows 10/11**
- **Python 3.8+**
- **windows-curses** (auto-installed)
- **pyperclip** (auto-installed, optional for clipboard)

##  Troubleshooting

### "ModuleNotFoundError: No module named '_curses'"
```powershell
pip install windows-curses
```

### "wnim: command not found"
- Restart your terminal after installation
- Or add to PATH manually: `%LOCALAPPDATA%\Microsoft\WindowsApps`

### Clipboard not working
```powershell
pip install --upgrade pyperclip
```

## 📄 License

MIT License — feel free to use and modify.
