#!/bin/bash
# WNim Console Editor Installer for Linux

set -e

INSTALL_DIR="$HOME/.local/share/wnim"
BIN_DIR="$HOME/.local/bin"

echo "=== WNim Installer (Linux) ==="
echo ""

# Check for Python
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "Error: Python not found. Install Python 3.8+ first."
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1)
echo "Found Python: $PY_VERSION"

# Install dependencies
echo "Installing dependencies (windows-curses, pyperclip, lupa)..."
$PYTHON -m pip install --user --quiet windows-curses pyperclip lupa || {
    echo "Error: Failed to install dependencies"
    exit 1
}
echo "Dependencies installed"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$HOME/.config/wnim"

echo "Install directory: $INSTALL_DIR"
echo "Config directory: $HOME/.config/wnim"

# Copy files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for file in editor.py wnim.py README_WNIM.md requirements.txt; do
    src="$SCRIPT_DIR/$file"
    if [ -f "$src" ]; then
        cp "$src" "$INSTALL_DIR/"
        echo "  Copied: $file"
    else
        echo "  Warning: File not found: $file (skipping)"
    fi
done

# Copy plugins folder
if [ -d "$SCRIPT_DIR/plugins" ]; then
    mkdir -p "$INSTALL_DIR/plugins"
    cp -r "$SCRIPT_DIR/plugins/"* "$INSTALL_DIR/plugins/" 2>/dev/null || true
    echo "  Copied: plugins/"
fi

# Copy docs folder
if [ -d "$SCRIPT_DIR/docs" ]; then
    mkdir -p "$INSTALL_DIR/docs"
    cp -r "$SCRIPT_DIR/docs/"* "$INSTALL_DIR/docs/" 2>/dev/null || true
    echo "  Copied: docs/"
fi

# Create wrapper script
WRAPPER_CONTENT="#!/bin/bash
$PYTHON \"$INSTALL_DIR/wnim.py\" \"\$@\""

WRAPPER_PATH="$BIN_DIR/wnim"
echo "$WRAPPER_CONTENT" > "$WRAPPER_PATH"
chmod +x "$WRAPPER_PATH"
echo "  Created: $WRAPPER_PATH"

# Add to PATH if needed
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    SHELL_CONFIG=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -f "$HOME/.profile" ]; then
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    if [ -n "$SHELL_CONFIG" ] && ! grep -q "export PATH=\"\$HOME/.local/bin:\$PATH\"" "$SHELL_CONFIG"; then
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_CONFIG"
        echo "  Added $BIN_DIR to PATH in $SHELL_CONFIG"
    fi
fi

echo ""
echo "Installation complete!"
echo ""
echo "Usage:"
echo "  wnim                    - new file"
echo "  wnim filename.py        - open Python file"
echo "  wnim filename.js        - open JavaScript file"
echo "  wnim filename.ts        - open TypeScript file"
echo "  wnim filename.c         - open C file"
echo "  wnim filename.cpp       - open C++ file"
echo "  wnim filename.cs        - open C# file"
echo "  wnim filename.java      - open Java file"
echo "  wnim filename.go        - open Go file"
echo "  wnim filename.rs        - open Rust file"
echo "  wnim filename.php       - open PHP file"
echo "  wnim filename.html      - open HTML file"
echo "  wnim filename.css       - open CSS file"
echo "  wnim filename.rb        - open Ruby file"
echo "  wnim filename.lua       - open Lua file"
echo "  wnim filename.ps1       - open PowerShell file"
echo "  wnim filename.zig       - open Zig file"
echo "  wnim filename.sh        - open Bash file"
echo ""
echo "If 'wnim' command is not found, run: source $SHELL_CONFIG"
echo "Or restart your terminal."
