# WNim — Console Code Editor

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

> Lightweight console-based code editor for Windows and Linux. Combines the minimalism of Vim with the familiar Windows hotkeys.

## 📑 Content

1. [Features](#-features)
2. [Requirements](#-requirements)
3. [Installation](#-installation)
4. [Launch](#-launch)
5. [Keyboard Shortcuts](#-shortcuts)
6. [Supported languages](#-supported-languages)
7. [Plugins](#-plugins)
8. [Documentation](#-documentation)
9. [Configuration](#-configuration)


---

##  Features

- **Cross-platform**: Windows 10/11 and Linux
- **Minimalistic interface**: Work in the terminal without graphical dependencies
- **Syntax Highlighting**: 20+ programming languages
- **Multi-debugging**: Working with multiple files at the same time
- **Auto-completion**: Built-in auto-completion code system
- **Lua Plugins**: Extensible architecture through Lua plugins
- **Undo/Redo**: Up to 50 undo levels
- **Intelligent input**:
- Auto-closing brackets: `()`, `[]`, `{}`, `""`, `"
- Automatic indentation after `:`, `{`, `[`
- **Clipboard**: Full system buffer support

---

##  Requirements

### Minimal

| Platform | Requirement |
|-----------|------------|
| Windows | Windows 10/11, Python 3.8+ |
| Linux | Any version with Python 3.8+, terminal with curses support |

### Dependencies

| Platform | Installation Command |
|-----------|-------------------|
| Windows | `pip install windows-curses pyperclip` |
| Linux | `pip3 install pyperclip` (curses is built into Python) |
| Plugins | `pip install lupa` (optional) |
| Clipboard Linux | `sudo apt install xclip xsel' (optional) |

---

## , Installation

### Automatic installation (Recommended)

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

### Manual installation

1. Install Python 3.8+
2. Install the dependencies:
``bash
   # Windows
   pip install windows-curses pyperclip
   
   # Linux
   pip3 install pyperclip
   ```
3. Launch the editor:
   ```bash
   python editor.py filename.py
   ```

---

##  Launch

```bash
# New file
wnim

# Open the file
wnim script.py

# Open multiple files
wnim file1.py file2.js file3.txt

# Running without installing
python editor.py filename.py
``

---

## ⌨️ Keyboard shortcuts

### Navigation
| Key | Action |
|---------|----------|
| `←` `→` `↑` `↓` | Moving the cursor |
| `Home` / `End` | Beginning / end of line |
| `PgUp` / `PgDn` | Scroll to the page |
| `Ctrl+F` | Search |
| `Ctrl+G` | Jump to the line |

### Working with files
| Key | Action |
|---------|----------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open the file |
| `Ctrl+S` | Save |
| `Ctrl+R` | Save as |
| `Ctrl+Q` | Exit |

### Editing
| Key | Action |
|---------|----------|
| `Ctrl+Z` | Cancel |
| `Ctrl+Y` | Return |
| `Ctrl+C` | Copy a line |
| `Ctrl+X` | Cut a line |
| `Ctrl+V` | Insert |
| `Ctrl+K` | Delete a line |
| `Tab` | Increase the indentation |
| `Shift+Tab` | Reduce the indentation |

### Tabs (tabs)
| Key | Action |
|---------|----------|
| `Ctrl+T` | New tab |
| `Ctrl+W` | Close the tab |
| `F1` | Previous tab |
| `F2` | Next tab |

### Additional functions
| Key | Action |
|---------|----------|
| `Ctrl+Space` | Auto-completion |
| `Ctrl+A` | File statistics |
| `Ctrl+L` | Download the plugin |
| `Ctrl+U` | To download the plugin |
| `Ctrl+P` | List of plugins |

---

##  Supported languages

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

WNim supports plugins in the Lua language through the `lupa` library.

### Installing plugin support
```bash
pip install lupa
```

### Built-in plugins

#### smart_indent.lua
- `Ctrl+M` — Increase line indentation
- `Ctrl+]` — Reduce line indentation
- `Ctrl+D' — Duplicate line

#### theme_changer.lua
- `Ctrl+1' — Dark theme
- `Ctrl+2` is a light theme
- `Ctrl+3' — Midnight theme
- `Ctrl+4' — Monokai theme
- `Ctrl+5` — Show the current theme

### Creating plugins

See [docs/plugins.md](docs/plugins.md) for a detailed guide.

An example of a simple plugin:
``lua
local plugin = {}

function plugin.on_load(api)
    api.editor.message("The plugin is loaded!")
end

function plugin.on_key(code)
    if code == 65 then  -- Ctrl+A
        api.editor.message("Ctrl+A is pressed")
return true
    end
    return false
end

return plugin
```

---

## 📁 Project structure

```
Wnim/
├── Main/                           # The main code of the editor
│   ├── editor.py # Main editor file (~1400 lines)
│ ├── wnim.py # Entry point for launch
,── README.md # README for GitHub (this page)
,── install.ps1 # Installer for Windows
,── install.sh # Installer for Linux
│   ├── editor_settings.json # Editor Settings
│   └── plugins/                    # Plugin system
│       ├── __init__.py
│       ├── plugin_manager.py # Plugin Manager
,── README.md # Plugin documentation
,── smart_indent.lua # Smart margins plugin
│ └── theme_changer.lua # Theme changer plugin
│
└── docs/                           # Documentation
    ,── README.md # Documentation index
├── basics.md # Basics of work
    ,── shortcuts.md # Hotkey Help
    ,── plugins.md # Plugin Development Guide
    ,── linux.md # Optimization for Linux
``

---

## , Documentation

| File | Description |
|------|----------|
| [docs/basics.md](docs/basics.md) | Basics of working with the editor |
| [docs/shortcuts.md](docs/shortcuts.md) | Full Hotkey Help |
| [docs/plugins.md](docs/plugins.md) | Plugin Development Guide |
| [docs/linux.md](docs/linux.md) | Optimization for Linux |
| [Main/plugins/README.md](Main/plugins/README.md) | Plugin documentation |

---

## ⚙️ Configuration

Configuration file:
- **Windows**: `%USERPROFILE%\.config\wnim\config.json`
- **Linux**: `~/.config/wnim/config.json`

Configuration example:
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

## 🛠 Problem solving

### "ModuleNotFoundError: No module named 'curses'"
**Linux**: curses is built into Python. Install the module:
```bash
sudo apt install python3-curses  # Ubuntu/Debian
sudo dnf install python3-curses  # Fedora
```
**Important**: Do not install `windows-curses` on Linux!

### Clipboard issues on Linux
```bash
sudo apt install xclip xsel  # Ubuntu/Debian
sudo dnf install xclip xsel  # Fedora
```

### "No display name" at startup
Set the environment variable:
```bash
export DISPLAY=:0
```

### Keyboard shortcuts don't work in tmux
Configure tmux to run through the 'Ctrl+key` combinations in the `~/.tmux.conf` configuration.

### Slow work with large files
1. Open less than 10,000 lines
2. Use a less resource-intensive theme.
3. Temporarily disable plugins

---

##  Connection

- **Telegram**: [@Loexez](https://t.me/Loexez )
- **GitHub Issues**: [Open issue](https://github.com/semenpro22gaempro-beep/Wnim/issues )

---

## 📄 License

MIT License — free use and modification.



---

<div align="center">

**Lol**

</div>
