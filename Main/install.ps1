#!/usr/bin/env pwsh
# WNim Console Editor Installer for Windows

$ErrorActionPreference = "Stop"

$InstallDir = "$env:LOCALAPPDATA\Programs\wnim"
$BinDir = "$env:LOCALAPPDATA\Microsoft\WindowsApps"

Write-Host "=== WNim Installer ===" -ForegroundColor Cyan
Write-Host ""

# Check for Python
$pythonExe = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = "py"
}

if (-not $pythonExe) {
    Write-Error "Python not found. Install Python 3.8+ from https://python.org"
    exit 1
}

$pyVersion = & $pythonExe --version 2>&1
Write-Host "Found Python: $pyVersion" -ForegroundColor Green

# Install dependencies
Write-Host "Installing dependencies (windows-curses, pyperclip, lupa)..." -ForegroundColor Yellow
& $pythonExe -m pip install --quiet windows-curses pyperclip lupa
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies"
    exit 1
}
Write-Host "Dependencies installed" -ForegroundColor Green

# Create directories
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Write-Host "Install directory: $InstallDir" -ForegroundColor Gray

# Copy files
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { $PWD.Path }
$Files = @("editor.py", "wnim.py", "README_WNIM.md", "requirements.txt")
foreach ($file in $Files) {
    $src = Join-Path $ScriptDir $file
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $InstallDir -Force
        Write-Host "  Copied: $file" -ForegroundColor Gray
    } else {
        Write-Warning "File not found: $file (skipping)"
    }
}

# Copy plugins folder
$PluginsDir = Join-Path $ScriptDir "plugins"
if (Test-Path $PluginsDir) {
    $DestPlugins = Join-Path $InstallDir "plugins"
    New-Item -ItemType Directory -Force -Path $DestPlugins | Out-Null
    Copy-Item -Path "$PluginsDir\*" -Destination $DestPlugins -Recurse -Force
    Write-Host "  Copied: plugins/" -ForegroundColor Gray
}

# Copy docs folder
$DocsDir = Join-Path $ScriptDir "docs"
if (Test-Path $DocsDir) {
    $DestDocs = Join-Path $InstallDir "docs"
    New-Item -ItemType Directory -Force -Path $DestDocs | Out-Null
    Copy-Item -Path "$DocsDir\*" -Destination $DestDocs -Recurse -Force
    Write-Host "  Copied: docs/" -ForegroundColor Gray
}

# Create config folder
$ConfigDir = "$env:USERPROFILE\.config\wnim"
New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
Write-Host "  Created: $ConfigDir" -ForegroundColor Gray

# Create wnim.bat
$BatContent = "@echo off`n$pythonExe `"$InstallDir\wnim.py`" %*"
$BatPath = "$BinDir\wnim.bat"
[IO.File]::WriteAllText($BatPath, $BatContent, [Text.Encoding]::ASCII)
Write-Host "  Created: $BatPath" -ForegroundColor Gray

# Create wnim.ps1 wrapper
$PsContent = "& $pythonExe `"$InstallDir\wnim.py`" `$args"
$PsPath = "$BinDir\wnim.ps1"
[IO.File]::WriteAllText($PsPath, $PsContent, [Text.Encoding]::UTF8)
Write-Host "  Created: $PsPath" -ForegroundColor Gray

# Add to PATH if needed
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
    Write-Host "  Added $BinDir to PATH" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  wnim                    - new file"
Write-Host "  wnim filename.py        - open Python file"
Write-Host "  wnim filename.cs        - open C# file"
Write-Host "  wnim filename.java      - open Java file"
Write-Host "  wnim filename.html      - open HTML file"
Write-Host "  wnim filename.css       - open CSS file"
Write-Host "  wnim filename.rb        - open Ruby file"
Write-Host "  wnim filename.lua       - open Lua file"
Write-Host "  wnim filename.ps1       - open PowerShell file"
Write-Host "  wnim filename.zig       - open Zig file"
Write-Host ""
Write-Host "Restart terminal if 'wnim' command is not found." -ForegroundColor Yellow
