
# Wnim - vim for windows
Wnim is a lightweight command-line text editor. It combines the minimalism of the classic Vim editor with the familiar ergonomics of the Windows operating system. The project is designed for users who value the speed of working in the terminal but don't want to spend time memorizing complex Vim key combinations.
- Defoult windows hotkeys
- Simple for noobs
- Performance for low-end devices
## Install
##  Installation

### Option 1: Automatic Installer (Recommended)

1. Clone or download this repository:
```powershell
git clone <repository-url>
cd <repository-folder>
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

## 🚀 Usage Examples

```powershell
# Open existing file
wnim script.py

# Create new file
wnim

# Open C# file
wnim Program.cs

# Open JavaScript file
wnim app.js
```

## 🛠️ Development

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
## Sreenshots
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/00eba18e-51cd-4ca9-b9b3-24c427502100" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/55f67aa8-6182-45bb-806f-eda3da966044" />

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

MIT License — feel free to usey. and modif

