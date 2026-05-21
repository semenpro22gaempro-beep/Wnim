#!/usr/bin/env pwsh
# WNim Console Editor Installer for Windows

$ErrorActionPreference = "Stop"

$InstallDir = "$env:LOCALAPPDATA\Programs\wnim"
$BinDir = "$env:LOCALAPPDATA\Microsoft\WindowsApps"

Write-Host "=== WNim Installer ===" -ForegroundColor Cyan
Write-Host ""

# Check for Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Error "Python not found. Install Python 3.8+ from https://python.org"
    exit 1
}

$pyVersion = & $python.Source --version 2>&1
Write-Host "Found Python: $pyVersion" -ForegroundColor Green

# Install dependencies
Write-Host "Installing dependencies (windows-curses, pyperclip)..." -ForegroundColor Yellow
& $python.Source -m pip install --quiet windows-curses pyperclip
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
$Files = @("editor.py", "wnim.py", "README_WNIM.md")
foreach ($file in $Files) {
    $src = Join-Path $ScriptDir $file
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $InstallDir -Force
        Write-Host "  Copied: $file" -ForegroundColor Gray
    } else {
        Write-Error "File not found: $file (run installer from source folder)"
        exit 1
    }
}

# Copy plugins folder
$PluginsDir = Join-Path $ScriptDir "plugins"
if (Test-Path $PluginsDir) {
    $DestPlugins = Join-Path $InstallDir "plugins"
    Copy-Item -Path "$PluginsDir\*" -Destination $DestPlugins -Recurse -Force
    Write-Host "  Copied: plugins/" -ForegroundColor Gray
}

# Create wnim.bat
$BatContent = "@echo off`npython `"$InstallDir\wnim.py`" %*"
$BatPath = "$BinDir\wnim.bat"
[IO.File]::WriteAllText($BatPath, $BatContent, [Text.Encoding]::ASCII)
Write-Host "  Created: $BatPath" -ForegroundColor Gray

# Create wnim.ps1
$PsContent = "param(`$args)`n& python `"$InstallDir\wnim.py`" `$args"
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
