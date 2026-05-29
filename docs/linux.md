# Linux Optimization Guide for WNim

## Overview

WNim is now fully optimized for Linux with cross-platform support for curses, clipboard, and plugin system.

## Requirements

### Minimum

- **Python 3.8+**
- **Terminal with curses support** (most Linux terminals support this)

### Recommended

- **pyperclip** - for system clipboard integration
- **xclip** or **xsel** - for clipboard support in headless environments
- **lupa** - for Lua plugin support

**Note:** `curses` is built into Python on Linux. You do NOT need to install `windows-curses` on Linux - that package is Windows-only.

## Installation

### Ubuntu/Debian

```bash
# Install Python
sudo apt update
sudo apt install python3 python3-pip

# Install clipboard utilities (optional but recommended)
sudo apt install xclip xsel

# Install Python dependencies
pip3 install pyperclip lupa
```

### Fedora

```bash
# Install Python
sudo dnf install python3 python3-pip

# Install clipboard utilities
sudo dnf install xclip xsel

# Install Python dependencies
pip3 install pyperclip lupa
```

### Arch Linux

```bash
# Install Python
sudo pacman -S python python-pip

# Install clipboard utilities
sudo pacman -S xclip xsel

# Install Python dependencies
pip3 install pyperclip lupa
```

### Alpine Linux

```bash
# Install Python
apk add python3 py3-pip

# Install clipboard utilities
apk add xclip xsel

# Install Python dependencies
pip3 install pyperclip lupa
```

## Clipboard Support

WNim uses the following clipboard fallback chain on Linux:

1. **pyperclip** (preferred) - works in most environments
2. **xclip** - X11 clipboard utility
3. **xsel** - Alternative X11 clipboard utility

If none are available, clipboard operations will be skipped with a warning message.

### Testing Clipboard

```bash
# Test xclip
echo "test" | xclip -selection clipboard
xclip -selection clipboard -o

# Test xsel
echo "test" | xsel --clipboard
xsel --clipboard --output
```

## Terminal Requirements

### Minimum Terminal Size

- **Width:** 80 characters
- **Height:** 24 lines

### Recommended Terminal Settings

```bash
# Set UTF-8 encoding
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Set terminal type
export TERM=xterm-256color
```

### Supported Terminals

- **bash** - Full support
- **zsh** - Full support
- **tmux** - Full support
- **screen** - Full support
- **GNOME Terminal** - Recommended
- **KDE Konsole** - Recommended
- **xterm** - Supported
- **st** - Supported

## Performance Optimizations

### File Loading

For large files (>10,000 lines):

1. Syntax highlighting may be slower
2. Consider using a lighter theme
3. Disable plugins temporarily

### Memory Usage

WNim keeps all open files in memory. For very large projects:

1. Use tabs selectively
2. Close unused files
3. Consider splitting large files

### Startup Time

To improve startup time:

1. Minimize plugin count
2. Auto-load only essential plugins
3. Use `pip install --upgrade` for dependencies

## Known Issues

### Unicode Characters

Some terminal fonts may not display all Unicode characters correctly.

**Solution:** Install a Nerd Font or Monaco font.

### Color Support

Limited color support in some terminals.

**Solution:** Set `TERM=xterm-256color` in your shell config.

### Clipboard in SSH

Clipboard may not work over SSH without X11 forwarding.

**Solution:** 
- Use `ssh -X` for X11 forwarding
- Or use local clipboard with xclip

### Tmux Integration

When using tmux, some hotkeys may conflict.

**Solution:** Configure tmux to pass through Ctrl+key combinations.

## Configuration

### Environment Variables

```bash
# Terminal encoding
export PYTHONIOENCODING=utf-8

# Force color output
export TERM=xterm-256color

# Plugin directory
export WNIM_PLUGIN_DIR=~/.config/wnim/plugins
```

### Shell Integration

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# WNim alias
alias wnim='python3 -m editor'

# Or use wrapper script
export PATH="$HOME/.local/bin:$PATH"
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'curses'"

On Linux, curses is built into Python. If you get this error:

```bash
# Reinstall Python or install curses module
sudo apt install python3-curses  # Ubuntu/Debian
sudo dnf install python3-curses  # Fedora
sudo pacman -S python-curses     # Arch
```

**Important:** Do NOT install `windows-curses` on Linux - it is Windows-only!

### "No display name" Error

When running in headless environment:

```bash
# Set virtual display
export DISPLAY=:0

# Or run without GUI clipboard
# (clipboard will be disabled)
```

### Slow Performance

1. Check terminal size: `stty size`
2. Disable syntax highlighting for large files
3. Reduce number of open tabs
4. Update dependencies: `pip3 install --upgrade windows-curses pyperclip lupa`

### Plugin Errors

1. Check lupa installation: `python3 -c "import lupa; print(lupa.__version__)"`
2. Verify Lua plugin syntax
3. Check plugin logs in console

## Development on Linux

### Running from Source

```bash
# Clone repository
git clone <repository-url>
cd wnim

# Run editor
python3 editor.py test.py

# Or use wrapper
python3 wnim.py test.py
```

### Testing

```bash
# Syntax check
python3 -m py_compile editor.py wnim.py

# Run with test file
python3 editor.py README_WNIM.md
```

### Debugging

```bash
# Enable verbose output
python3 -u editor.py file.py

# Trace imports
python3 -v editor.py 2>&1 | grep wnim
```

## Tips

1. **Use tmux** for session persistence
2. **Install a Nerd Font** for better character display
3. **Configure xclip** for clipboard in scripts
4. **Use plugins** to extend functionality
5. **Keep terminal at 80+ width** for optimal experience

## Comparing Windows vs Linux

| Feature | Windows | Linux |
|---------|---------|-------|
| Curses | windows-curses | curses (built-in) |
| Clipboard | pyperclip (native) | pyperclip + xclip/xsel |
| Terminal | CMD/PowerShell | bash/zsh/tmux |
| PATH | WindowsApps | ~/.local/bin |
| Config | %USERPROFILE%\.config | ~/.config |
| Plugins | Same | Same |

## Support

For Linux-specific issues:

1. Check this guide first
2. Verify terminal settings
3. Test clipboard utilities
4. Check Python version: `python3 --version`
5. Open issue on GitHub
