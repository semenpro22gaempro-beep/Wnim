<img width="500" height="500" alt="WNim Editor" src="https://github.com/user-attachments/assets/8fc765b0-dd93-4af3-8fea-8d3fb321b93c" />

# WNim — Console Code Editor for Windows and Linux

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/semenpro22gaempro-beep/Wnim)

> Легковесный консольный редактор кода. Сочетает минимализм Vim с привычными горячими клавишами Windows.

- 🔹 Горячие клавиши Windows по умолчанию
- 🔹 Прост для новичков
- 🔹 Высокая производительность для слабых устройств

---

## 📑 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Установка](#установка)
3. [Горячие клавиши](#горячие-клавиши)
4. [Поддерживаемые языки](#поддерживаемые-языки)
5. [Плагины](#плагины)
6. [Документация](#документация)
7. [Связь](#связь)

---

## 🚀 Быстрый старт

```bash
# Установка
git clone https://github.com/semenpro22gaempro-beep/Wnim.git
cd Wnim/Main

# Windows
.\install.ps1

# Linux
chmod +x install.sh && ./install.sh

# Запуск после установки
wnim filename.py
```

---

## 📦 Установка

### Вариант 1: Автоматический (Рекомендуется)

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

### Вариант 2: Ручная установка

1. Установите Python 3.8+ из [python.org](https://python.org)
2. Установите зависимости:
   ```powershell
   # Windows
   pip install windows-curses pyperclip
   
   # Linux
   pip3 install pyperclip
   ```
3. Запустите редактор:
   ```bash
   python editor.py filename.py
   ```

### Linux — дополнительные зависимости
```bash
# Для буфера обмена
sudo apt install xclip xsel  # Debian/Ubuntu
sudo dnf install xclip xsel  # Fedora

# Для поддержки плагинов (Lua)
pip3 install lupa
```

---

## ⌨️ Горячие клавиши

### Навигация
| Клавиша | Действие |
|---------|----------|
| `Ctrl+Space` | Автодополнение |
| `Ctrl+F` | Поиск |
| `Ctrl+G` | Переход к строке |
| `Home` / `End` | Начало / конец строки |
| `PgUp` / `PgDn` | Прокрутка на страницу |
| `←` `→` `↑` `↓` | Перемещение курсора |

### Работа с файлами
| Клавиша | Действие |
|---------|----------|
| `Ctrl+N` | Новый файл |
| `Ctrl+O` | Открыть файл |
| `Ctrl+S` | Сохранить |
| `Ctrl+R` | Сохранить как |
| `Ctrl+Q` | Выйти |

### Редактирование
| Клавиша | Действие |
|---------|----------|
| `Ctrl+Z` | Отменить |
| `Ctrl+Y` | Вернуть |
| `Ctrl+C` | Копировать строку |
| `Ctrl+X` | Вырезать строку |
| `Ctrl+V` | Вставить |
| `Ctrl+K` | Удалить строку (удерживать для нескольких) |
| `Tab` | Увеличить отступ |
| `Shift+Tab` | Уменьшить отступ |

### Вкладки (табы)
| Клавиша | Действие |
|---------|----------|
| `Ctrl+T` | Новая вкладка |
| `Ctrl+W` | Закрыть вкладку |
| `F1` | Предыдущая вкладка |
| `F2` | Следующая вкладка |

### Дополнительное
| Клавиша | Действие |
|---------|----------|
| `Ctrl+A` | Статистика файла |
| `Ctrl+L` | Загрузить плагин |
| `Ctrl+U` | Выгрузить плагин |
| `Ctrl+P` | Список плагинов |

---

## 🌐 Поддерживаемые языки

Подсветка синтаксиса доступна для:

| Язык | Расширения | Язык | Расширения |
|------|------------|------|------------|
| Python | `.py` | Kotlin | `.kt`, `.kts` |
| JavaScript | `.js`, `.jsx` | Bash | `.sh`, `.bash`, `.zsh` |
| TypeScript | `.ts`, `.tsx` | Ruby | `.rb`, `.erb` |
| PHP | `.php` | Lua | `.lua` |
| Go | `.go` | PowerShell | `.ps1`, `.psm1`, `.psd1` |
| Rust | `.rs`, `.rlib` | Java | `.java` |
| C | `.c`, `.h` | Zig | `.zig` |
| C++ | `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh` | Assembly | `.asm`, `.s`, `.S` |
| C# | `.cs` | HTML | `.html`, `.htm`, `.xhtml` |
| CSS | `.css` | | |

---

## 🔌 Плагины

WNim поддерживает плагины на языке Lua.

### Установка
```bash
pip install lupa
```

### Встроенные плагины

#### smart_indent.lua
- `Ctrl+M` — Увеличить отступ строки
- `Ctrl+]` — Уменьшить отступ строки
- `Ctrl+D` — Дублировать строку

#### theme_changer.lua
- `Ctrl+1` — Тёмная тема
- `Ctrl+2` — Светлая тема
- `Ctrl+3` — Midnight тема
- `Ctrl+4` — Monokai тема
- `Ctrl+5` — Показать текущую тему

### Управление плагинами
- `Ctrl+L` — Загрузить плагин
- `Ctrl+U` — Выгрузить плагин
- `Ctrl+P` — Показать список плагинов

Подробное руководство: [docs/plugins.md](../docs/plugins.md)

---

## 📚 Документация

- [docs/basics.md](../docs/basics.md) — Основы работы с редактором
- [docs/shortcuts.md](../docs/shortcuts.md) — Справка по горячим клавишам
- [docs/plugins.md](../docs/plugins.md) — Руководство по разработке плагинов
- [docs/linux.md](../docs/linux.md) — Оптимизация для Linux
- [plugins/README.md](plugins/README.md) — Документация по плагинам

---

## 📞 Связь

- **Telegram**: [@Loexez](https://t.me/Loexez)
- **GitHub**: [semenpro22gaempro-beep/Wnim](https://github.com/semenpro22gaempro-beep/Wnim)

---

## 📄 Лицензия

MIT License — свободное использование и модификация.

---

<div align="center">

**Сделано с ❤️ для разработчиков**

</div>