# WNim — Console Code Editor

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

> A lightweight console code editor for Windows and Linux. Combines Vim's minimalism with familiar Windows keyboard shortcuts.


## 📑 Table of Contents

1. [Features](#-features)
2. [Requirements](#-requirements)
3. [Installation](#-installation)
4. [Usage](#-usage)
5. [Keyboard Shortcuts](#-keyboard-shortcuts)
6. [Supported Languages](#-supported-languages)
7. [Plugins](#-plugins)
8. [Project Structure](#-project-structure)
9. [Documentation](#-documentation)
10. [Configuration](#-configuration)
11. [Troubleshooting](#-troubleshooting)
12. [Contact](#-contact)

---

## ✨ Features

- **Cross-platform**: Windows 10/11 and Linux
- **Minimalistic interface**: Terminal-based, no GUI dependencies
- **Syntax highlighting**: 20+ programming languages
- **Multi-tab support**: Work with multiple files simultaneously
- **Auto-completion**: Built-in code completion system
- **Lua plugins**: Extensible architecture via Lua plugins
- **Undo/Redo**: Up to 50 levels of undo
- **Smart input**:
  - Auto-closing brackets: `()`, `[]`, `{}`, `""`, `''`
  - Automatic indentation after `:`, `{`, `[`
- **Clipboard**: Full support for system clipboard

---

## 📦 Requirements

### Minimum

| Platform | Requirement |
|-----------|------------|
| Windows | Windows 10/11, Python 3.8+ |
| Linux | Any distribution with Python 3.8+, terminal with curses support |

### Dependencies

| Platform | Installation Command |
|-----------|-------------------|
| Windows | `pip install windows-curses pyperclip` |
| Linux | `pip3 install pyperclip` (curses is built into Python) |
| Plugins | `pip install lupa` (optional) |
| Clipboard Linux | `sudo apt install xclip xsel` (optional) |

---

## 🚀 Installation

### Automatic Installation (Recommended)

#### Windows
```powershell
git clone https://github.com/semenpro22gaempro-beep/Wnim.git
cd Wnim\Main
.\install.ps1
```

#### Linux
```bash
git clone https://github.com/semenpro22gaempro-beep/Wnim.git
cd Wnim/Main
chmod +x install.sh
./install.sh
```

### Manual Installation

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   # Windows
   pip install windows-curses pyperclip
   
   # Linux
   pip3 install pyperclip
   ```
3. Run the editor:
   ```bash
   python editor.py filename.py
   ```

---

## ▶️ Usage

```bash
# New file
wnim

# Open file
wnim script.py

# Open multiple files
wnim file1.py file2.js file3.txt

# Run without installation
python editor.py filename.py
```

---

## ⌨️ Keyboard Shortcuts

### Navigation
| Key | Action |
|---------|----------|
| `←` `→` `↑` `↓` | Move cursor |
| `Home` / `End` | Beginning / end of line |
| `PgUp` / `PgDn` | Scroll page up/down |
| `Ctrl+F` | Search |
| `Ctrl+G` | Go to line |
| `Ctrl+E` | File menu (left side) |

### File Operations
| Key | Action |
|---------|----------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save |
| `Ctrl+R` | Save as |
| `Ctrl+Q` | Exit |

### Editing
| Key | Action |
|---------|----------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+C` | Copy line |
| `Ctrl+X` | Cut line |
| `Ctrl+V` | Paste |
| `Ctrl+K` | Delete line |
| `Tab` | Increase indent |
| `Shift+Tab` | Decrease indent |

### Tabs
| Key | Action |
|---------|----------|
| `Ctrl+T` | New tab |
| `Ctrl+W` | Close tab |
| `F1` | Previous tab |
| `F2` | Next tab |

### Additional Functions
| Key | Action |
|---------|----------|
| `Ctrl+Space` | Auto-completion |
| `Ctrl+E` | File menu (navigate ↑↓, Enter to open, Esc to close) |
| `Ctrl+A` | File statistics |
| `Ctrl+L` | Load plugin |
| `Ctrl+U` | Unload plugin |
| `Ctrl+P` | List plugins |

---

## 🌐 Supported Languages

| Extension | Language | Extension | Language |
|------------|------|------------|------|
| `.py` | Python | `.kt`, `.kts` | Kotlin |
| `.js`, `.jsx` | JavaScript | `.sh`, `.bash`, `.zsh` | Bash |
| `.ts`, `.tsx` | TypeScript | `.rb`, `.erb` | Ruby |
| `.php` | PHP | `.lua` | Lua |
| `.go` | Go | `.ps1`, `.psm1`, `.psd1` | PowerShell |
| `.rs`, `.rlib` | Rust | `.java` | Java |
| `.c`, `.h` | C | `.zig` | Zig |
| `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh` | C++ | `.asm`, `.s`, `.S` | Assembly |
| `.cs` | C# | `.html`, `.htm`, `.xhtml` | HTML |
| `.css` | CSS | | |

---

## 🔌 Plugins

WNim supports plugins written in Lua via the `lupa` library.

### Installing Plugin Support
```bash
pip install lupa
```

### Built-in Plugins

#### smart_indent.lua
- `Ctrl+M` — Increase line indentation
- `Ctrl+]` — Decrease line indentation
- `Ctrl+D` — Duplicate line

#### theme_changer.lua
- `Ctrl+1` — Dark theme
- `Ctrl+2` — Light theme
- `Ctrl+3` — Midnight theme
- `Ctrl+4` — Monokai theme
- `Ctrl+5` — Show current theme

### Creating Plugins

See [docs/plugins.md](docs/plugins.md) for a detailed guide.

Example of a simple plugin:
```lua
local plugin = {}

function plugin.on_load(api)
    api.editor.message("Plugin loaded!")
end

function plugin.on_key(code)
    if code == 65 then  -- Ctrl+A
        api.editor.message("Ctrl+A pressed")
        return true
    end
    return false
end

return plugin
```

---

## 📁 Project Structure

```
Wnim/
├── Main/                           # Main editor code
│   ├── editor.py                   # Main editor file (~1400 lines)
│   ├── wnim.py                     # Entry point for running
│   ├── README.md                   # README for GitHub (this page)
│   ├── install.ps1                 # Installer for Windows
│   ├── install.sh                  # Installer for Linux
│   ├── editor_settings.json        # Editor settings
│   └── plugins/                    # Plugin system
│       ├── __init__.py
│       ├── plugin_manager.py       # Plugin manager
│       ├── README.md               # Plugin documentation
│       ├── smart_indent.lua        # Smart indentation plugin
│       └── theme_changer.lua       # Theme changer plugin
│
└── docs/                           # Documentation
    ├── README.md                   # Documentation index
    ├── basics.md                   # Getting started
    ├── shortcuts.md                # Keyboard shortcuts reference
    ├── plugins.md                  # Plugin development guide
    └── linux.md                    # Linux optimization
```

---

## 📚 Documentation

| File | Description |
|------|----------|
| [docs/basics.md](docs/basics.md) | Getting started with the editor |
| [docs/shortcuts.md](docs/shortcuts.md) | Complete keyboard shortcuts reference |
| [docs/plugins.md](docs/plugins.md) | Plugin development guide |
| [docs/linux.md](docs/linux.md) | Linux optimization |
| [Main/plugins/README.md](Main/plugins/README.md) | Plugin documentation |

---

## ⚙️ Configuration

Configuration file locations:
- **Windows**: `%USERPROFILE%\.config\wnim\config.json`
- **Linux**: `~/.config/wnim/config.json`

Example configuration:
```json
{
    "theme": "dark",
    "tab_size": 4,
    "line_numbers": true,
    "auto_close_brackets": true,
    "auto_indent": true,
    "plugins_auto_load": ["smart_indent", "theme_changer"]
}
```

---

## 🛠 Troubleshooting

### "ModuleNotFoundError: No module named 'curses'"
**Linux**: curses is built into Python. Install the module:
```bash
sudo apt install python3-curses  # Ubuntu/Debian
sudo dnf install python3-curses  # Fedora
```
**Important**: Do NOT install `windows-curses` on Linux!

### Clipboard issues on Linux
```bash
sudo apt install xclip xsel  # Ubuntu/Debian
sudo dnf install xclip xsel  # Fedora
```

### "No display name" on startup
Set the environment variable:
```bash
export DISPLAY=:0
```

### Keyboard shortcuts not working in tmux
Configure tmux to forward `Ctrl+key` combinations in `~/.tmux.conf`.

### Slow performance with large files
1. Open files with less than 10,000 lines
2. Use a less resource-intensive theme
3. Temporarily disable plugins

---

## 📞 Contact

- **Telegram**: [@Loexez](https://t.me/Loexez)
- **GitHub Issues**: [Open an issue](https://github.com/semenpro22gaempro-beep/Wnim/issues)

---

## 📄 License

MIT License — free to use and modify.

---

## 🤝 Contributing

All contributions are welcome! Create pull requests or open issues for bugs and new features.

---

<div align="center">

**Made with ❤️ for developers**

</div>
