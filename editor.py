
# -*- coding: utf-8 -*-
"""
Консольный редактор кода для Windows с подсветкой синтаксиса.

Требования (Windows):
    pip install windows-curses pyperclip

Запуск:
    python editor.py [файл]

Поддерживаемые языки: Python, JavaScript, C, C++, Bash

Горячие клавиши (Windows-style):
    Ctrl+N      — новый файл
    Ctrl+O      — открыть файл
    Ctrl+S      — сохранить
    Ctrl+W      — сохранить как
    Ctrl+Q      — выйти
    Ctrl+Z      — отменить
    Ctrl+Y      — повторить (redo)
    Ctrl+A      — статистика файла
    Ctrl+C      — копировать строку
    Ctrl+X      — вырезать строку
    Ctrl+V      — вставить
    Ctrl+F      — найти
    Ctrl+G      — перейти к строке
    Home/End    — начало/конец строки
    PgUp/PgDn   — страница вверх/вниз
    Tab         — отступ
    Shift+Tab   — убрать отступ

Авто-функции:
    - Авто-закрытие скобок: () [] {} "" ''
    - Авто-отступ после { : и т.д.
"""

import curses
import os
import sys
import re

try:
    import pyperclip
    HAS_PYPERCLIP = True
except Exception:
    HAS_PYPERCLIP = False


# ─── Подсветка синтаксиса ─────────────────────────────

class BaseHighlighter:
    TOKEN_SPECS = [
        ("COMMENT", r"#.*|//.*|/\*.*?\*/"),
        ("STRING", r"('''(?:[^'\\]|\\.|'(?!''))*'''|\"\"\"(?:[^" + '"' + r"\\]|\\.|" + '"' + r"(?!" + '""' + r"))*" + '"""' + r"|'(?:[^'\\]|\\.)*'|\"(?:[^" + '"' + r"\\]|\\.)*\")"),
        ("NUMBER", r"\b(?:0[xXoObB][0-9a-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?[jJfF]?)\b"),
        ("OPERATOR", r"[+\-*/%=<>!&|^~]+|::|->|=>|\+\+|--"),
        ("PAREN", r"[()\[\]{}]"),
        ("WHITESPACE", r"\s+"),
        ("OTHER", r"."),
    ]

    def __init__(self, keywords, builtins=None, extra_specs=None):
        self.keywords = set(keywords)
        self.builtins = set(builtins) if builtins else set()
        specs = list(self.TOKEN_SPECS)
        if extra_specs:
            for name, pattern in extra_specs:
                specs.insert(-3, (name, pattern))
        # вставляем ключевые слова и встроенные
        kw_pattern = r"\b(?:" + "|".join(sorted(self.keywords)) + r")\b"
        bi_pattern = r"\b(?:" + "|".join(sorted(self.builtins)) + r")\b" if self.builtins else r"$^"
        specs.insert(-3, ("BUILTIN", bi_pattern))
        specs.insert(-3, ("KEYWORD", kw_pattern))
        self.token_re = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in specs), re.DOTALL)

    def tokenize(self, line):
        pos = 0
        tokens = []
        while pos < len(line):
            m = self.token_re.match(line, pos)
            if not m:
                tokens.append(("OTHER", line[pos:]))
                break
            kind = m.lastgroup
            value = m.group()
            tokens.append((kind, value))
            pos = m.end()
        return tokens


class PythonHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "class", "continue", "def", "del", "elif", "else", "except",
            "finally", "for", "from", "global", "if", "import", "in", "is",
            "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
            "try", "while", "with", "yield",
        }
        builtins = {
            "abs", "all", "any", "bin", "bool", "bytearray", "bytes", "callable",
            "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir",
            "divmod", "enumerate", "eval", "exec", "filter", "float", "format",
            "frozenset", "getattr", "globals", "hasattr", "hash", "help", "hex",
            "id", "input", "int", "isinstance", "issubclass", "iter", "len",
            "list", "locals", "map", "max", "memoryview", "min", "next", "object",
            "oct", "open", "ord", "pow", "print", "property", "range", "repr",
            "reversed", "round", "set", "setattr", "slice", "sorted", "staticmethod",
            "str", "sum", "super", "tuple", "type", "vars", "zip", "__import__",
        }
        extra = [
            ("COMMENT", r"#[^\n]*"),
            ("DECORATOR", r"@[a-zA-Z_]\w*"),
            ("SELF", r"\bself\b"),
            ("CLASSNAME", r"\b[A-Z][a-zA-Z0-9_]*\b"),
            ("FUNCNAME", r"\b[a-z_][a-zA-Z0-9_]*(?=\s*\()"),
        ]
        super().__init__(keywords, builtins, extra)


class JavaScriptHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "async", "await", "break", "case", "catch", "class", "const",
            "continue", "debugger", "default", "delete", "do", "else",
            "export", "extends", "false", "finally", "for", "function",
            "if", "import", "in", "instanceof", "let", "new", "null",
            "return", "super", "switch", "this", "throw", "true", "try",
            "typeof", "undefined", "var", "void", "while", "with", "yield",
        }
        builtins = {
            "Array", "Boolean", "Date", "Error", "Function", "JSON",
            "Math", "Number", "Object", "Promise", "RegExp", "String",
            "console", "document", "window", "alert", "setTimeout",
            "setInterval", "clearTimeout", "clearInterval", "parseInt",
            "parseFloat", "isNaN", "eval",
        }
        extra = [
            ("COMMENT", r"//[^\n]*|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/"),
            ("TEMPLATE", r"`(?:[^`\\]|\\.|\\\n)*`"),
            ("CLASSNAME", r"\b[A-Z][a-zA-Z0-9_]*\b"),
            ("FUNCNAME", r"\b[a-zA-Z_$][a-zA-Z0-9_$]*(?=\s*\()"),
        ]
        super().__init__(keywords, builtins, extra)


class CHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "auto", "break", "case", "char", "const", "continue", "default",
            "do", "double", "else", "enum", "extern", "float", "for", "goto",
            "if", "int", "long", "register", "return", "short", "signed",
            "sizeof", "static", "struct", "switch", "typedef", "union",
            "unsigned", "void", "volatile", "while", "_Bool", "_Complex",
            "_Imaginary", "inline", "restrict",
        }
        builtins = {
            "printf", "scanf", "malloc", "free", "memcpy", "memset",
            "strlen", "strcpy", "strcmp", "fopen", "fclose", "fread",
            "fwrite", "fprintf", "sprintf", "exit", "atoi", "atof",
            "NULL", "EOF", "stdout", "stderr", "stdin",
        }
        extra = [
            ("COMMENT", r"//[^\n]*|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/"),
            ("PREPROC", r"#[ \t]*(?:include|define|ifdef|ifndef|endif|pragma|if|else|elif)\b[^\n]*"),
            ("MACRO", r"\b[A-Z_][A-Z0-9_]*\b"),
            ("FUNCNAME", r"\b[a-zA-Z_]\w*(?=\s*\()"),
        ]
        super().__init__(keywords, builtins, extra)


class CppHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand",
            "bitor", "bool", "break", "case", "catch", "char", "char8_t",
            "char16_t", "char32_t", "class", "compl", "concept", "const",
            "consteval", "constexpr", "constinit", "const_cast", "continue",
            "co_await", "co_return", "co_yield", "decltype", "default",
            "delete", "do", "double", "dynamic_cast", "else", "enum",
            "explicit", "export", "extern", "false", "float", "for",
            "friend", "goto", "if", "inline", "int", "long", "mutable",
            "namespace", "new", "noexcept", "not", "not_eq", "nullptr",
            "operator", "or", "or_eq", "private", "protected", "public",
            "register", "reinterpret_cast", "requires", "return", "short",
            "signed", "sizeof", "static", "static_assert", "static_cast",
            "struct", "switch", "template", "this", "thread_local", "throw",
            "true", "try", "typedef", "typeid", "typename", "union",
            "unsigned", "using", "virtual", "void", "volatile", "wchar_t",
            "while", "xor", "xor_eq",
        }
        builtins = {
            "std", "cout", "cin", "cerr", "endl", "string", "vector",
            "map", "set", "queue", "stack", "array", "tuple", "pair",
            "make_shared", "make_unique", "shared_ptr", "unique_ptr",
            "nullptr", "NULL", "true", "false",
        }
        extra = [
            ("COMMENT", r"//[^\n]*|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/"),
            ("PREPROC", r"#[ \t]*(?:include|define|ifdef|ifndef|endif|pragma|if|else|elif)\b[^\n]*"),
            ("MACRO", r"\b[A-Z_][A-Z0-9_]*\b"),
            ("CLASSNAME", r"\b[A-Z][a-zA-Z0-9_]*\b"),
            ("FUNCNAME", r"\b[a-zA-Z_]\w*(?=\s*\()"),
        ]
        super().__init__(keywords, builtins, extra)


class BashHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "if", "then", "else", "elif", "fi", "case", "esac", "for",
            "while", "until", "do", "done", "in", "function", "return",
            "break", "continue", "shift", "exit", "export", "local",
            "readonly", "unset", "declare", "typeset", "source", "alias",
        }
        builtins = {
            "echo", "printf", "read", "cd", "pwd", "ls", "cat", "grep",
            "sed", "awk", "cut", "sort", "uniq", "head", "tail", "find",
            "chmod", "chown", "mkdir", "rm", "cp", "mv", "ln", "touch",
            "test", "[", "[[", "]", "]]", "true", "false", "sleep", "wait",
            "kill", "trap", "exec", "eval", "command", "builtin", "type",
            "jobs", "fg", "bg", "disown", "getopts", "set", "shopt",
        }
        extra = [
            ("COMMENT", r"#[^\n]*"),
            ("VAR", r"\$\{[^}]*\}|\$[A-Za-z_][A-Za-z0-9_]*|\$\d+|\$\@|\$\*"),
            ("SUBSHELL", r"\$\([^)]*\)"),
            ("SHEBANG", r"^#!.*$"),
        ]
        super().__init__(keywords, builtins, extra)


def get_highlighter(filename):
    if not filename:
        return None
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".py":
        return PythonHighlighter()
    elif ext in (".js", ".jsx", ".ts", ".tsx"):
        return JavaScriptHighlighter()
    elif ext in (".c", ".h"):
        return CHighlighter()
    elif ext in (".cpp", ".cc", ".cxx", ".hpp", ".hh"):
        return CppHighlighter()
    elif ext in (".sh", ".bash", ".zsh"):
        return BashHighlighter()
    return None


class Editor:
    def __init__(self, filename=None):
        self.filename = filename
        self.lines = [""]
        self.cursor_y = 0
        self.cursor_x = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.clipboard = []
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo = 50
        self.dirty = False
        self.message = ""
        self._quit_confirm = False
        # выделение (для Ctrl+A)
        self.sel_start = None
        self.sel_end = None

        if filename and os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    text = f.read()
                self.lines = text.split("\n") if text else [""]
                if not self.lines:
                    self.lines = [""]
            except Exception as e:
                self.message = f"Ошибка открытия: {e}"
        self.save_undo()

    # ─── Undo / Redo ──────────────────────────────────────

    def save_undo(self):
        self.undo_stack.append((self.lines.copy(), self.cursor_y, self.cursor_x))
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if len(self.undo_stack) > 1:
            state = self.undo_stack.pop()
            self.redo_stack.append(state)
            lines, cy, cx = self.undo_stack[-1]
            self.lines = lines.copy()
            self.cursor_y, self.cursor_x = cy, cx
            self.dirty = True
            self.message = "Отменено"
        else:
            self.message = "Нечего отменять"

    def redo(self):
        if self.redo_stack:
            lines, cy, cx = self.redo_stack.pop()
            self.undo_stack.append((lines.copy(), cy, cx))
            self.lines = lines.copy()
            self.cursor_y, self.cursor_x = cy, cx
            self.dirty = True
            self.message = "Повторено"
        else:
            self.message = "Нечего повторять"

    # ─── Файл ─────────────────────────────────────────────

    def save(self, stdscr=None):
        if not self.filename:
            if stdscr:
                self.save_as(stdscr)
            else:
                self.message = "Нет имени файла — используйте Ctrl+W (Сохранить как)"
            return
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.lines))
            self.dirty = False
            self.message = "Сохранено"
        except Exception as e:
            self.message = f"Ошибка сохранения: {e}"

    def save_as(self, stdscr):
        new_name = self.prompt(stdscr, "Сохранить как: ")
        if not new_name:
            self.message = "Отменено"
            return
        self.filename = new_name
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.lines))
            self.dirty = False
            self.message = f"Сохранено как {self.filename}"
        except Exception as e:
            self.message = f"Ошибка сохранения: {e}"

    def open_file(self, stdscr):
        if self.dirty:
            self.message = "Сначала сохраните изменения (Ctrl+S)"
            return
        new_name = self.prompt(stdscr, "Открыть файл: ")
        if not new_name:
            self.message = "Отменено"
            return
        if not os.path.exists(new_name):
            self.message = f"Файл не найден: {new_name}"
            return
        try:
            with open(new_name, "r", encoding="utf-8") as f:
                text = f.read()
            self.lines = text.split("\n") if text else [""]
            if not self.lines:
                self.lines = [""]
            self.filename = new_name
            self.cursor_y = 0
            self.cursor_x = 0
            self.scroll_y = 0
            self.scroll_x = 0
            self.dirty = False
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.save_undo()
            self.message = f"Открыт: {self.filename}"
        except Exception as e:
            self.message = f"Ошибка открытия: {e}"

    def new_file(self):
        if self.dirty:
            self.message = "Сначала сохраните изменения (Ctrl+S)"
            return
        self.filename = None
        self.lines = [""]
        self.cursor_y = 0
        self.cursor_x = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.dirty = False
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.save_undo()
        self.message = "Новый файл"

    # ─── Редактирование ───────────────────────────────────

    BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}", "\"": "\"", "'": "'"}

    def _get_indent(self, line):
        """Возвращает текущий отступ строки в пробелах."""
        stripped = line.lstrip(" ")
        return len(line) - len(stripped)

    def _should_increase_indent(self, line):
        """Проверяет, нужно ли увеличить отступ (заканчивается на : или { или [)."""
        stripped = line.rstrip()
        if not stripped:
            return False
        return stripped[-1] in ":{["

    def insert_char(self, ch):
        self.save_undo()
        line = self.lines[self.cursor_y]
        self.lines[self.cursor_y] = line[: self.cursor_x] + ch + line[self.cursor_x :]
        self.cursor_x += len(ch)
        # авто-закрытие скобок/кавычек
        if ch in self.BRACKET_PAIRS:
            closing = self.BRACKET_PAIRS[ch]
            self.lines[self.cursor_y] = (
                line[: self.cursor_x - 1] + ch + closing + line[self.cursor_x - 1 :]
            )
        self.dirty = True

    def insert_newline(self):
        self.save_undo()
        line = self.lines[self.cursor_y]
        before = line[: self.cursor_x]
        after = line[self.cursor_x :]

        # определяем базовый отступ
        current_indent = self._get_indent(line)
        new_indent = current_indent

        # если строка заканчивается на {, [ или : — увеличиваем отступ
        if self._should_increase_indent(before):
            new_indent += 4

        # если после курсора только закрывающая скобка — создаём промежуточную строку
        if after.strip() in ")}]" and self._should_increase_indent(before):
            self.lines[self.cursor_y] = before
            middle = " " * new_indent
            self.lines.insert(self.cursor_y + 1, middle)
            self.lines.insert(self.cursor_y + 2, " " * current_indent + after)
            self.cursor_y += 1
            self.cursor_x = new_indent
            self.dirty = True
            return

        self.lines[self.cursor_y] = before
        self.lines.insert(self.cursor_y + 1, " " * new_indent + after.lstrip(" "))
        self.cursor_y += 1
        self.cursor_x = new_indent
        self.dirty = True

    def backspace(self):
        if self.cursor_x > 0:
            self.save_undo()
            line = self.lines[self.cursor_y]
            self.lines[self.cursor_y] = line[: self.cursor_x - 1] + line[self.cursor_x :]
            self.cursor_x -= 1
            self.dirty = True
        elif self.cursor_y > 0:
            self.save_undo()
            prev_len = len(self.lines[self.cursor_y - 1])
            self.lines[self.cursor_y - 1] += self.lines[self.cursor_y]
            del self.lines[self.cursor_y]
            self.cursor_y -= 1
            self.cursor_x = prev_len
            self.dirty = True

    def delete(self):
        line = self.lines[self.cursor_y]
        if self.cursor_x < len(line):
            self.save_undo()
            self.lines[self.cursor_y] = line[: self.cursor_x] + line[self.cursor_x + 1 :]
            self.dirty = True
        elif self.cursor_y < len(self.lines) - 1:
            self.save_undo()
            self.lines[self.cursor_y] += self.lines[self.cursor_y + 1]
            del self.lines[self.cursor_y + 1]
            self.dirty = True

    def indent(self):
        self.save_undo()
        line = self.lines[self.cursor_y]
        spaces = 4 - (self.cursor_x % 4)
        self.lines[self.cursor_y] = line[: self.cursor_x] + " " * spaces + line[self.cursor_x :]
        self.cursor_x += spaces
        self.dirty = True

    def unindent(self):
        self.save_undo()
        line = self.lines[self.cursor_y]
        # удалить до 4 пробелов слева от курсора
        spaces = 0
        start = max(0, self.cursor_x - 4)
        for i in range(self.cursor_x - 1, start - 1, -1):
            if i >= 0 and line[i] == " ":
                spaces += 1
            else:
                break
        if spaces > 0:
            self.lines[self.cursor_y] = line[: self.cursor_x - spaces] + line[self.cursor_x :]
            self.cursor_x -= spaces
            self.dirty = True

    # ─── Буфер обмена ─────────────────────────────────────

    def copy(self):
        text = self.lines[self.cursor_y]
        if HAS_PYPERCLIP:
            try:
                pyperclip.copy(text)
            except Exception:
                pass
        self.clipboard = [text]
        self.message = "Строка скопирована"

    def cut(self):
        if len(self.lines) == 1 and self.lines[0] == "":
            self.message = "Нечего вырезать"
            return
        self.save_undo()
        text = self.lines[self.cursor_y]
        if HAS_PYPERCLIP:
            try:
                pyperclip.copy(text)
            except Exception:
                pass
        self.clipboard = [text]
        del self.lines[self.cursor_y]
        if not self.lines:
            self.lines = [""]
        if self.cursor_y >= len(self.lines):
            self.cursor_y = len(self.lines) - 1
        self.cursor_x = 0
        self.dirty = True
        self.message = "Строка вырезана"

    def paste(self):
        self.save_undo()
        if HAS_PYPERCLIP:
            try:
                clip = pyperclip.paste()
                if clip is not None:
                    self.clipboard = clip.split("\n")
            except Exception:
                pass
        if not self.clipboard:
            self.message = "Буфер пуст"
            return

        line = self.lines[self.cursor_y]
        before = line[: self.cursor_x]
        after = line[self.cursor_x :]

        if len(self.clipboard) == 1:
            self.lines[self.cursor_y] = before + self.clipboard[0] + after
            self.cursor_x = len(before) + len(self.clipboard[0])
        else:
            self.lines[self.cursor_y] = before + self.clipboard[0]
            for i, cl in enumerate(self.clipboard[1:-1], 1):
                self.lines.insert(self.cursor_y + i, cl)
            insert_pos = self.cursor_y + len(self.clipboard) - 1
            self.lines.insert(insert_pos, self.clipboard[-1] + after)
            self.cursor_y = insert_pos
            self.cursor_x = len(self.clipboard[-1])
        self.dirty = True
        self.message = "Вставлено"

    # ─── Поиск / Переход ──────────────────────────────────

    def prompt(self, stdscr, prompt_text):
        max_y, max_x = stdscr.getmaxyx()
        s = ""
        while True:
            line = (prompt_text + s)[: max_x - 1]
            stdscr.addstr(max_y - 1, 0, line, curses.color_pair(1))
            stdscr.clrtoeol()
            stdscr.refresh()
            try:
                key = stdscr.get_wch()
            except curses.error:
                continue
            if isinstance(key, str):
                code = ord(key)
            else:
                code = key
            if code in (10, 13):
                return s
            elif code == 27:  # Esc
                return None
            elif code in (8, 127, curses.KEY_BACKSPACE):
                s = s[:-1]
            elif isinstance(key, str) and code >= 32:
                s += key

    def find(self, stdscr):
        query = self.prompt(stdscr, "Найти: ")
        if query is None:
            self.message = "Поиск отменён"
            return
        if not query:
            return
        total = len(self.lines)
        for offset in range(total):
            idx = (self.cursor_y + offset) % total
            line = self.lines[idx]
            start = self.cursor_x + 1 if offset == 0 else 0
            pos = line.find(query, start)
            if pos != -1:
                self.cursor_y = idx
                self.cursor_x = pos
                self.message = f"Найдено: строка {idx + 1}"
                return
        self.message = "Не найдено"

    def goto(self, stdscr):
        s = self.prompt(stdscr, "Перейти к строке: ")
        if s and s.isdigit():
            num = int(s) - 1
            if 0 <= num < len(self.lines):
                self.cursor_y = num
                self.cursor_x = 0
            else:
                self.message = "Неверный номер строки"

    # ─── Отрисовка ────────────────────────────────────────

    def _color_for_token(self, kind):
        mapping = {
            "KEYWORD": 3,
            "BUILTIN": 4,
            "SELF": 5,
            "FUNCNAME": 6,
            "CLASSNAME": 7,
            "STRING": 8,
            "FSTRING": 8,
            "TEMPLATE": 8,
            "NUMBER": 9,
            "COMMENT": 10,
            "DECORATOR": 11,
            "PREPROC": 11,
            "MACRO": 11,
            "SHEBANG": 11,
            "OPERATOR": 12,
            "PAREN": 13,
            "VAR": 14,
            "SUBSHELL": 14,
        }
        return curses.color_pair(mapping.get(kind, 0))

    def _draw_line(self, stdscr, y, x_start, line, offset, width, highlighter):
        if not line:
            return
        tokens = highlighter.tokenize(line)
        col = 0
        for kind, text in tokens:
            if col >= offset + width:
                break
            if col + len(text) <= offset:
                col += len(text)
                continue
            # часть токена попадает в видимую область
            start = max(0, offset - col)
            end = min(len(text), offset + width - col)
            visible_text = text[start:end]
            screen_col = x_start + (col - offset) + start
            try:
                stdscr.addstr(y, screen_col, visible_text, self._color_for_token(kind))
            except curses.error:
                pass
            col += len(text)

    def draw(self, stdscr):
        max_y, max_x = stdscr.getmaxyx()
        if max_y < 3 or max_x < 10:
            return

        line_num_width = 6   # ширина номера строки
        gutter = 1           # пробел между номером и кодом
        code_x = line_num_width + gutter
        text_width = max_x - code_x

        # корректировка прокрутки
        if self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y
        elif self.cursor_y >= self.scroll_y + max_y - 1:
            self.scroll_y = self.cursor_y - (max_y - 2)

        if self.cursor_x < self.scroll_x:
            self.scroll_x = self.cursor_x
        elif self.cursor_x >= self.scroll_x + text_width:
            self.scroll_x = self.cursor_x - text_width + 1

        highlighter = get_highlighter(self.filename)

        for i in range(max_y - 1):
            # полностью очищаем строку перед отрисовкой
            try:
                stdscr.move(i, 0)
                stdscr.clrtoeol()
            except curses.error:
                pass

            line_idx = self.scroll_y + i
            if line_idx >= len(self.lines):
                continue

            # номер строки (всегда рисуем для существующих строк)
            num_str = str(line_idx + 1).rjust(line_num_width)[:line_num_width]
            try:
                stdscr.addstr(i, 0, num_str, curses.color_pair(2))
            except curses.error:
                pass

            line = self.lines[line_idx]
            remaining = max_x - code_x

            if highlighter and remaining > 0:
                self._draw_line(stdscr, i, code_x, line, self.scroll_x, text_width, highlighter)
            elif remaining > 0:
                visible = line[self.scroll_x : self.scroll_x + text_width]
                visible = visible.replace("\t", "    ")
                try:
                    stdscr.addstr(i, code_x, visible[:remaining])
                except curses.error:
                    pass

        # статусная строка — тоже очищаем перед выводом
        status = (
            f" {'*' if self.dirty else ' '} "
            f"{self.filename or '[Новый файл]'} | "
            f"{self.cursor_y + 1}:{self.cursor_x + 1} | {self.message}"
        )
        status = status.ljust(max_x - 1)[: max_x - 1]
        try:
            stdscr.move(max_y - 1, 0)
            stdscr.clrtoeol()
            stdscr.addstr(max_y - 1, 0, status, curses.color_pair(1))
        except curses.error:
            pass

        cur_screen_y = self.cursor_y - self.scroll_y
        cur_screen_x = code_x + (self.cursor_x - self.scroll_x)
        if 0 <= cur_screen_y < max_y - 1 and 0 <= cur_screen_x < max_x:
            try:
                stdscr.move(cur_screen_y, cur_screen_x)
            except curses.error:
                pass
        stdscr.refresh()

    # ─── Главный цикл ─────────────────────────────────────

    def run(self, stdscr):
        curses.curs_set(1)
        stdscr.keypad(True)
        curses.start_color()
        curses.use_default_colors()
        # 1: статусная строка
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        # 2: номера строк
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        # 3: ключевые слова
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        # 4: встроенные функции
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # 5: self
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        # 6: имена функций
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        # 7: имена классов
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        # 8: строки
        curses.init_pair(8, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # 9: числа
        curses.init_pair(9, curses.COLOR_CYAN, curses.COLOR_BLACK)
        # 10: комментарии
        curses.init_pair(10, curses.COLOR_RED, curses.COLOR_BLACK)
        # 11: декораторы
        curses.init_pair(11, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        # 12: операторы
        curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_BLACK)
        # 13: скобки
        curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_BLACK)
        # 14: переменные/подстановки
        curses.init_pair(14, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        while True:
            self.draw(stdscr)
            try:
                key = stdscr.get_wch()
            except (curses.error, KeyboardInterrupt):
                continue

            if isinstance(key, str):
                code = ord(key)
            else:
                code = key

            self.message = ""

            if code == curses.KEY_RESIZE:
                continue

            # ── Выход ──
            if code == 17:  # Ctrl+Q
                if self.dirty:
                    if self._quit_confirm:
                        break
                    self.message = "Несохранённые изменения! Ctrl+Q ещё раз для выхода, Ctrl+S для сохранения"
                    self._quit_confirm = True
                    continue
                break
            self._quit_confirm = False

            # ── Файл ──
            if code == 19:  # Ctrl+S
                self.save(stdscr)
            elif code == 23:  # Ctrl+W
                self.save_as(stdscr)
            elif code == 15:  # Ctrl+O
                self.open_file(stdscr)
            elif code == 14:  # Ctrl+N
                self.new_file()
            # ── Undo / Redo ──
            elif code == 26:  # Ctrl+Z
                self.undo()
            elif code == 25:  # Ctrl+Y
                self.redo()
            # ── Буфер обмена ──
            elif code == 3:  # Ctrl+C
                self.copy()
            elif code == 24:  # Ctrl+X
                self.cut()
            elif code == 22:  # Ctrl+V
                self.paste()
            elif code == 1:  # Ctrl+A
                self.message = f"Всего строк: {len(self.lines)}, символов: {sum(len(l) for l in self.lines)}"
            # ── Навигация / Поиск ──
            elif code == 6:  # Ctrl+F
                self.find(stdscr)
            elif code == 7:  # Ctrl+G
                self.goto(stdscr)
            # ── Спец. клавиши ──
            elif code == 9:  # Tab
                self.indent()
            elif code == 353:  # Shift+Tab (KEY_BTAB)
                self.unindent()
            elif code in (curses.KEY_BACKSPACE, 8, 127):
                self.backspace()
            elif code == curses.KEY_DC:
                self.delete()
            elif code in (10, 13):
                self.insert_newline()
            elif code == curses.KEY_LEFT:
                if self.cursor_x > 0:
                    self.cursor_x -= 1
                elif self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = len(self.lines[self.cursor_y])
            elif code == curses.KEY_RIGHT:
                if self.cursor_x < len(self.lines[self.cursor_y]):
                    self.cursor_x += 1
                elif self.cursor_y < len(self.lines) - 1:
                    self.cursor_y += 1
                    self.cursor_x = 0
            elif code == curses.KEY_UP:
                if self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            elif code == curses.KEY_DOWN:
                if self.cursor_y < len(self.lines) - 1:
                    self.cursor_y += 1
                    self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            elif code == curses.KEY_HOME:
                self.cursor_x = 0
            elif code == curses.KEY_END:
                self.cursor_x = len(self.lines[self.cursor_y])
            elif code == curses.KEY_PPAGE:
                max_y, _ = stdscr.getmaxyx()
                self.cursor_y = max(0, self.cursor_y - (max_y - 2))
                self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            elif code == curses.KEY_NPAGE:
                max_y, _ = stdscr.getmaxyx()
                self.cursor_y = min(len(self.lines) - 1, self.cursor_y + (max_y - 2))
                self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            # ── Печатные символы (включая Unicode) ──
            elif isinstance(key, str) and code >= 32 and code != 127:
                self.insert_char(key)


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    editor = Editor(filename)
    curses.wrapper(editor.run)


if __name__ == "__main__":
    main()

