#!/usr/bin/env pwsh
# Установщик WNim — консольного редактора кода для Windows

$ErrorActionPreference = "Stop"

$InstallDir = "$env:LOCALAPPDATA\Programs\wnim"
$BinDir = "$env:LOCALAPPDATA\Microsoft\WindowsApps"

Write-Host "=== WNim Installer ===" -ForegroundColor Cyan
Write-Host ""

# Проверка Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Error "Python не найден. Установите Python 3.8+ с https://python.org"
    exit 1
}

$pyVersion = & $python.Source --version 2>&1
Write-Host "Найден Python: $pyVersion" -ForegroundColor Green

# Проверка/установка зависимостей
Write-Host "Установка зависимостей (windows-curses, pyperclip)..." -ForegroundColor Yellow
& $python.Source -m pip install --quiet windows-curses pyperclip
if ($LASTEXITCODE -ne 0) {
    Write-Error "Не удалось установить зависимости"
    exit 1
}
Write-Host "Зависимости установлены" -ForegroundColor Green

# Создание директорий
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Write-Host "Директория установки: $InstallDir" -ForegroundColor Gray

# Копирование файлов
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Files = @("editor.py", "wnim.py")
foreach ($file in $Files) {
    $src = Join-Path $ScriptDir $file
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $InstallDir -Force
        Write-Host "  Скопирован: $file" -ForegroundColor Gray
    } else {
        Write-Error "Файл не найден: $file (запустите установщик из папки с исходниками)"
        exit 1
    }
}

# Создание wnim.bat
$BatContent = @"
@echo off
python "$InstallDir\wnim.py" %*
"@
$BatPath = "$BinDir\wnim.bat"
Set-Content -Path $BatPath -Value $BatContent -Encoding ASCII
Write-Host "  Создан: $BatPath" -ForegroundColor Gray

# Создание wnim.ps1 (для PowerShell)
$PsContent = @"
param([Parameter(ValueFromRemainingArguments=`$true)] `$Args)
& python "$InstallDir\wnim.py" @Args
"@
$PsPath = "$BinDir\wnim.ps1"
Set-Content -Path $PsPath -Value $PsContent -Encoding UTF8
Write-Host "  Создан: $PsPath" -ForegroundColor Gray

# Добавление в PATH (если нужно)
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
    Write-Host "  Папка $BinDir добавлена в PATH" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Установка завершена!" -ForegroundColor Green
Write-Host ""
Write-Host "Запуск:" -ForegroundColor Cyan
Write-Host "  wnim                    — новый файл"
Write-Host "  wnim filename.py        — открыть файл"
Write-Host "  wnim filename.cs        — открыть C# файл"
Write-Host ""
Write-Host "Перезапустите PowerShell/Terminal, если команда 'wnim' не найдена." -ForegroundColor Yellow
