# WNim — Console Code Editor

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

> Легковесный консольный редактор кода для Windows и Linux. Сочетает минимализм Vim с привычными горячими клавишами Windows.

![WNim Editor](https://github.com/semenpro22gaempro-beep/Wnim/blob/main/Main/README.md?raw=true)

## 📑 Содержание

1. [Особенности](#-особенности)
2. [Требования](#-требования)
3. [Установка](#-установка)
4. [Запуск](#-запуск)
5. [Горячие клавиши](#-горячие-клавиши)
6. [Поддерживаемые языки](#-поддерживаемые-языки)
7. [Плагины](#-плагины)
8. [Структура проекта](#-структура-проекта)
9. [Документация](#-документация)
10. [Конфигурация](#-конфигурация)
11. [Решение проблем](#-решение-проблем)
12. [Связь](#-связь)

---

## ✨ Особенности

- **Кроссплатформенность**: Windows 10/11 и Linux
- **Минималистичный интерфейс**: Работа в терминале без графических зависимостей
- **Подсветка синтаксиса**: 20+ языков программирования
- **Многовкладочность**: Работа с несколькими файлами одновременно
- **Автодополнение**: Встроенная система автодополнения кода
- **Плагины на Lua**: Расширяемая архитектура через Lua-плагины
- **Undo/Redo**: До 50 уровней отмены изменений
- **Интеллектуальный ввод**:
  - Автозакрытие скобок: `()`, `[]`, `{}`, `""`, `''`
  - Автоматический отступ после `:`, `{`, `[`
- **Буфер обмена**: Полная поддержка системного буфера

---

## 📦 Требования

### Минимальные

| Платформа | Требование |
|-----------|------------|
| Windows | Windows 10/11, Python 3.8+ |
| Linux | Любая дистриция с Python 3.8+, терминал с поддержкой curses |

### Зависимости

| Платформа | Команда установки |
|-----------|-------------------|
| Windows | `pip install windows-curses pyperclip` |
| Linux | `pip3 install pyperclip` (curses встроен в Python) |
| Плагины | `pip install lupa` (опционально) |
| Clipboard Linux | `sudo apt install xclip xsel` (опционально) |

---

## 🚀 Установка

### Автоматическая установка (Рекомендуется)

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

### Ручная установка

1. Установите Python 3.8+
2. Установите зависимости:
   ```bash
   # Windows
   pip install windows-curses pyperclip
   
   # Linux
   pip3 install pyperclip
   ```
3. Запустите редактор:
   ```bash
   python editor.py filename.py
   ```

---

## ▶️ Запуск

```bash
# Новый файл
wnim

# Открыть файл
wnim script.py

# Открыть несколько файлов
wnim file1.py file2.js file3.txt

# Запуск без установки
python editor.py filename.py
```

---

## ⌨️ Горячие клавиши

### Навигация
| Клавиша | Действие |
|---------|----------|
| `←` `→` `↑` `↓` | Перемещение курсора |
| `Home` / `End` | Начало / конец строки |
| `PgUp` / `PgDn` | Прокрутка на страницу |
| `Ctrl+F` | Поиск |
| `Ctrl+G` | Переход к строке |

### Работа с файлами
| Клавиша | Действие |
|---------|----------|
| `Ctrl+N` | Новый файл |
| `Ctrl+O` | Открыть файл |
| `Ctrl+S` | Сохранить |
| `Ctrl+R` | Сохранить как |
| `Ctrl+Q` | Выход |

### Редактирование
| Клавиша | Действие |
|---------|----------|
| `Ctrl+Z` | Отменить |
| `Ctrl+Y` | Вернуть |
| `Ctrl+C` | Копировать строку |
| `Ctrl+X` | Вырезать строку |
| `Ctrl+V` | Вставить |
| `Ctrl+K` | Удалить строку |
| `Tab` | Увеличить отступ |
| `Shift+Tab` | Уменьшить отступ |

### Вкладки (табы)
| Клавиша | Действие |
|---------|----------|
| `Ctrl+T` | Новая вкладка |
| `Ctrl+W` | Закрыть вкладку |
| `F1` | Предыдущая вкладка |
| `F2` | Следующая вкладка |

### Дополнительные функции
| Клавиша | Действие |
|---------|----------|
| `Ctrl+Space` | Автодополнение |
| `Ctrl+A` | Статистика файла |
| `Ctrl+L` | Загрузить плагин |
| `Ctrl+U` | Выгрузить плагин |
| `Ctrl+P` | Список плагинов |

---

## 🌐 Поддерживаемые языки

| Расширение | Язык | Расширение | Язык |
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

## 🔌 Плагины

WNim поддерживает плагины на языке Lua через библиотеку `lupa`.

### Установка поддержки плагинов
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

### Создание плагинов

См. [docs/plugins.md](docs/plugins.md) для подробного руководства.

Пример простого плагина:
```lua
local plugin = {}

function plugin.on_load(api)
    api.editor.message("Плагин загружен!")
end

function plugin.on_key(code)
    if code == 65 then  -- Ctrl+A
        api.editor.message("Нажат Ctrl+A")
        return true
    end
    return false
end

return plugin
```

---

## 📁 Структура проекта

```
Wnim/
├── Main/                           # Основной код редактора
│   ├── editor.py                   # Главный файл редактора (~1400 строк)
│   ├── wnim.py                     # Точка входа для запуска
│   ├── README.md                   # README для GitHub (эта страница)
│   ├── install.ps1                 # Инсталлятор для Windows
│   ├── install.sh                  # Инсталлятор для Linux
│   ├── editor_settings.json        # Настройки редактора
│   └── plugins/                    # Система плагинов
│       ├── __init__.py
│       ├── plugin_manager.py       # Менеджер плагинов
│       ├── README.md               # Документация по плагинам
│       ├── smart_indent.lua        # Плагин умных отступов
│       └── theme_changer.lua       # Плагин смены тем
│
└── docs/                           # Документация
    ├── README.md                   # Индекс документации
    ├── basics.md                   # Основы работы
    ├── shortcuts.md                # Справка по горячим клавишам
    ├── plugins.md                  # Руководство по разработке плагинов
    └── linux.md                    # Оптимизация для Linux
```

---

## 📚 Документация

| Файл | Описание |
|------|----------|
| [docs/basics.md](docs/basics.md) | Основы работы с редактором |
| [docs/shortcuts.md](docs/shortcuts.md) | Полная справка по горячим клавишам |
| [docs/plugins.md](docs/plugins.md) | Руководство по разработке плагинов |
| [docs/linux.md](docs/linux.md) | Оптимизация для Linux |
| [Main/plugins/README.md](Main/plugins/README.md) | Документация по плагинам |

---

## ⚙️ Конфигурация

Конфигурационный файл:
- **Windows**: `%USERPROFILE%\.config\wnim\config.json`
- **Linux**: `~/.config/wnim/config.json`

Пример конфигурации:
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

## 🛠 Решение проблем

### "ModuleNotFoundError: No module named 'curses'"
**Linux**: curses встроен в Python. Установите модуль:
```bash
sudo apt install python3-curses  # Ubuntu/Debian
sudo dnf install python3-curses  # Fedora
```
**Важно**: Не устанавливайте `windows-curses` на Linux!

### Проблемы с буфером обмена на Linux
```bash
sudo apt install xclip xsel  # Ubuntu/Debian
sudo dnf install xclip xsel  # Fedora
```

### "No display name" при запуске
Установите переменную окружения:
```bash
export DISPLAY=:0
```

### Не работают горячие клавиши в tmux
Настройте tmux для проброса `Ctrl+key` комбинаций в конфигурации `~/.tmux.conf`.

### Медленная работа с большими файлами
1. Откройте менее чем 10,000 строк
2. Используйте менее ресурсоёмкую тему
3. Временно отключите плагины

---

## 📞 Связь

- **Telegram**: [@Loexez](https://t.me/Loexez)
- **GitHub Issues**: [Открыть issue](https://github.com/semenpro22gaempro-beep/Wnim/issues)

---

## 📄 Лицензия

MIT License — свободное использование и модификация.

---

## 🤝 Вклад

Все предложения приветствуются! Создавайте pull requests или открывайте issues для багов и новых функций.

---

<div align="center">

**Сделано с ❤️ для разработчиков**

</div>
