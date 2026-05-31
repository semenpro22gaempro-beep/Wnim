
# -*- coding: utf-8 -*-
"""
WNim - Cross-platform Console Code Editor with syntax highlighting.

Requirements:
    Windows: pip install windows-curses pyperclip
    Linux:   pip install pyperclip (xclip or xsel recommended for clipboard)

Usage:
    python editor.py [files...]
    wnim file1.py file2.py file3.txt

Supported languages: Python, JavaScript, TypeScript, C, C++, C#, Bash, Ruby, Lua, PowerShell, Java, Zig, ASM, HTML, CSS, PHP, Go, Rust, Kotlin

Hotkeys:
    Ctrl+Space  - autocomplete
    Ctrl+T      - new tab
    Ctrl+W      - close tab
    F1          - previous tab
    F2          - next tab
    Ctrl+N      - new file
    Ctrl+S      - save
    Ctrl+R      - save as
    Ctrl+Q      - quit
    Ctrl+Z      - undo
    Ctrl+Y      - redo
    Ctrl+A      - file stats
    Ctrl+C      - copy line
    Ctrl+X      - cut line
    Ctrl+V      - paste
    Ctrl+K      - delete line (hold for multiple)
    Ctrl+F      - find
    Ctrl+G      - go to line
    Home/End    - start/end of line
    PgUp/PgDn   - page up/down
    Tab         - indent
    Shift+Tab   - unindent

Auto-features:
    - Auto-close brackets: () [] {} "" ''
    - Auto-indent after { : etc.
"""

import curses
import os
import sys
import re
import platform

# Cross-platform detection
IS_WINDOWS = platform.system() == "Windows"

# Curses import - Windows needs windows-curses, Linux has built-in curses
try:
    if IS_WINDOWS:
        try:
            import windows_curses
        except ImportError:
            print("Warning: windows-curses not installed. Install with: pip install windows-curses")
    # Linux curses is built into Python
except ImportError as e:
    print(f"Error: Cannot import curses module: {e}")
    print("On Linux, ensure you have python3-curses installed.")
    print("On Windows, install windows-curses: pip install windows-curses")
    sys.exit(1)

# Clipboard
try:
    import pyperclip
    HAS_PYPERCLIP = True
except Exception:
    HAS_PYPERCLIP = False
    if IS_WINDOWS:
        print("Warning: pyperclip not installed. Install with: pip install pyperclip")
    else:
        print("Warning: pyperclip not installed. Install with: pip install pyperclip")
        print("For Linux clipboard, also consider: sudo apt install xclip xsel")

# Plugin system
try:
    from plugins.plugin_manager import PluginManager
    HAS_PLUGINS = True
except Exception:
    HAS_PLUGINS = False
    PluginManager = None


# ─── Clipboard utilities for Linux ────────────────────────

def linux_clipboard_get():
    """Fallback clipboard getter for Linux using xclip/xsel."""
    try:
        import subprocess
        result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                capture_output=True, text=True, timeout=1)
        return result.stdout
    except Exception:
        try:
            import subprocess
            result = subprocess.run(['xsel', '--clipboard', '--output'], 
                                    capture_output=True, text=True, timeout=1)
            return result.stdout
        except Exception:
            return None


def linux_clipboard_set(text):
    """Fallback clipboard setter for Linux using xclip/xsel."""
    try:
        import subprocess
        process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                   stdin=subprocess.PIPE, timeout=1)
        process.communicate(input=text.encode('utf-8'))
        return True
    except Exception:
        try:
            import subprocess
            process = subprocess.Popen(['xsel', '--clipboard', '--input'], 
                                       stdin=subprocess.PIPE, timeout=1)
            process.communicate(input=text.encode('utf-8'))
            return True
        except Exception:
            return False


# ─── Syntax Highlighting ─────────────────────────────

class BaseHighlighter:
    BASE_SPECS = [
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
        specs = []
        # first extra_specs (comments, decorators, etc.)
        if extra_specs:
            specs.extend(extra_specs)
        # then basics
        specs.extend(self.BASE_SPECS)
        # insert keywords and builtins
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


class CSharpHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "abstract", "as", "base", "bool", "break", "byte", "case",
            "catch", "char", "checked", "class", "const", "continue",
            "decimal", "default", "delegate", "do", "double", "else",
            "enum", "event", "explicit", "extern", "false", "finally",
            "fixed", "float", "for", "foreach", "goto", "if", "implicit",
            "in", "int", "interface", "internal", "is", "lock", "long",
            "namespace", "new", "null", "object", "operator", "out",
            "override", "params", "private", "protected", "public",
            "readonly", "ref", "return", "sbyte", "sealed", "short",
            "sizeof", "stackalloc", "static", "string", "struct", "switch",
            "this", "throw", "true", "try", "typeof", "uint", "ulong",
            "unchecked", "unsafe", "ushort", "using", "virtual", "void",
            "volatile", "while", "add", "alias", "ascending", "descending",
            "dynamic", "from", "get", "global", "group", "into", "join",
            "let", "orderby", "partial", "remove", "select", "set",
            "value", "var", "where", "yield", "await", "async",
        }
        builtins = {
            "Console", "String", "Int32", "Convert", "Math", "Array",
            "List", "Dictionary", "Enumerable", "Task", "DateTime", "Guid",
            "Exception", "Environment", "File", "Directory", "Path", "Debug",
            "Trace", "ConsoleColor", "IEnumerable", "ICollection", "IList",
            "Object", "Boolean", "Byte", "SByte", "Char", "Decimal",
            "Double", "Single", "Int16", "Int64", "UInt16", "UInt32",
            "UInt64", "Nullable", "ValueTuple", "Action", "Func",
            "StringBuilder", "Stream", "StreamReader", "StreamWriter",
            "HttpClient", "JsonSerializer", "Regex", "Match", "Group",
        }
        extra = [
            ("COMMENT", r"//[^\n]*|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/"),
            ("PREPROC", r"#[ \t]*(?:region|endregion|if|else|elif|endif|define|undef|warning|error|line|pragma|nullable)\b[^\n]*"),
            ("ATTRIBUTE", r"\[[a-zA-Z_]\w*(?:\([^\)]*\))?\]"),
            ("CLASSNAME", r"\b[A-Z][a-zA-Z0-9_]*\b"),
            ("FUNCNAME", r"\b[a-zA-Z_]\w*(?=\s*\()"),
        ]
        super().__init__(keywords, builtins, extra)


class TypeScriptHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "async", "await", "break", "case", "catch", "class", "const",
            "continue", "debugger", "default", "delete", "do", "else",
            "enum", "export", "extends", "false", "finally", "for", "function",
            "if", "import", "in", "instanceof", "interface", "let", "new", "null",
            "return", "super", "switch", "this", "throw", "true", "try",
            "typeof", "undefined", "var", "void", "while", "with", "yield",
            "readonly", "abstract", "implements", "type", "namespace", "module",
            "declare", "public", "private", "protected", "static", "get", "set",
            "keyof", "infer", "unique", "symbol", "unknown", "never", "any",
            "as", "is", "satisfies", "asserts", "using",
        }
        builtins = {
            "Array", "Boolean", "Date", "Error", "Function", "JSON",
            "Math", "Number", "Object", "Promise", "RegExp", "String",
            "console", "document", "window", "alert", "setTimeout",
            "setInterval", "clearTimeout", "clearInterval", "parseInt",
            "parseFloat", "isNaN", "eval", "Map", "Set", "WeakMap",
            "WeakSet", "Proxy", "Reflect", "Symbol", "Record", "Partial",
            "Required", "Readonly", "Pick", "Omit", "Exclude", "Extract",
            "NonNullable", "Parameters", "ReturnType", "InstanceType",
            "ThisParameterType", "OmitThisParameter", "ThisType",
            "Uppercase", "Lowercase", "Capitalize", "Uncapitalize",
            "ArrayBuffer", "Uint8Array", "Int8Array", "Float32Array",
            "console", "process", "Buffer", "globalThis",
        }
        extra = [
            ("COMMENT", r"//[^\n]*|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/"),
            ("TEMPLATE", r"`(?:[^`\\]|\\.|\\\n)*`"),
            ("TYPE", r"\b[A-Z][a-zA-Z0-9_]*\b"),
            ("FUNCNAME", r"\b[a-zA-Z_$][a-zA-Z0-9_$]*(?=\s*\()"),
        ]
        super().__init__(keywords, builtins, extra)


class PHPHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "abstract", "and", "array", "as", "break", "callable", "case",
            "catch", "class", "clone", "const", "continue", "declare",
            "default", "die", "do", "echo", "else", "elseif", "empty",
            "enddeclare", "endfor", "endforeach", "endif", "endswitch",
            "endwhile", "eval", "exit", "extends", "final", "finally",
            "fn", "for", "foreach", "function", "global", "goto", "if",
            "implements", "include", "include_once", "instanceof",
            "insteadof", "interface", "isset", "list", "match", "namespace",
            "new", "or", "print", "private", "protected", "public",
            "readonly", "require", "require_once", "return", "static",
            "switch", "throw", "trait", "try", "unset", "use", "var",
            "while", "xor", "yield", "yield from", "true", "false", "null",
            "self", "parent", "static",
        }
        builtins = {
            "strlen", "strpos", "substr", "str_replace", "explode", "implode",
            "trim", "ltrim", "rtrim", "strtolower", "strtoupper", "preg_match",
            "preg_replace", "preg_split", "array_merge", "array_push", "array_pop",
            "array_shift", "array_unshift", "in_array", "count", "sort", "ksort",
            "file_get_contents", "file_put_contents", "fopen", "fclose", "fread",
            "fwrite", "json_encode", "json_decode", "serialize", "unserialize",
            "date", "time", "strtotime", "md5", "sha1", "base64_encode",
            "base64_decode", "htmlspecialchars", "strip_tags", "header",
            "session_start", "setcookie", "die", "exit", "isset", "empty",
            "unset", "define", "defined", "constant", "var_dump", "print_r",
            "error_log", "trigger_error", "debug_backtrace", "spl_autoload_register",
            "mysqli", "PDO", "SimpleXMLElement", "DOMDocument", "DateTime",
            "Exception", "Throwable", "stdClass", "Closure", "Generator",
        }
        extra = [
            ("COMMENT", r"//[^\n]*|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/|#[^\n]*"),
            ("VAR", r"\$[a-zA-Z_][a-zA-Z0-9_]*|\$\{[^}]*\}"),
            ("HEREDOC", r"<<<[a-zA-Z_][a-zA-Z0-9_]*\n[\s\S]*?\n[a-zA-Z_][a-zA-Z0-9_]*;?"),
            ("CONST", r"\b[A-Z][A-Z0-9_]*\b"),
            ("FUNCNAME", r"\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()"),
        ]
        super().__init__(keywords, builtins, extra)


class GoHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "break", "case", "chan", "const", "continue", "default", "defer",
            "else", "fallthrough", "for", "func", "go", "goto", "if",
            "import", "interface", "map", "package", "range", "return",
            "select", "struct", "switch", "type", "var",
        }
        builtins = {
            "append", "cap", "close", "complex", "copy", "delete", "imag",
            "len", "make", "new", "panic", "print", "println", "real",
            "recover", "bool", "byte", "complex64", "complex128", "error",
            "float32", "float64", "int", "int8", "int16", "int32", "int64",
            "rune", "string", "uint", "uint8", "uint16", "uint32", "uint64",
            "uintptr", "any", "comparable", "nil", "true", "false",
            "fmt", "Println", "Printf", "Sprintf", "Errorf", "Scanln",
            "os", "io", "strings", "strconv", "time", "http", "json",
            "sync", "context", "testing", "reflect", "sort", "bytes",
            "bufio", "log", "errors", "regexp", "path", "filepath",
        }
        extra = [
            ("COMMENT", r"//[^\n]*|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/"),
            ("RUNE", r"'(?:[^'\\]|\\.)'"),
            ("RAWSTRING", r"`[^`]*`"),
            ("TYPE", r"\b[A-Z][a-zA-Z0-9_]*\b"),
            ("FUNCNAME", r"\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()"),
        ]
        super().__init__(keywords, builtins, extra)


class RustHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "as", "async", "await", "break", "const", "continue", "crate",
            "dyn", "else", "enum", "extern", "false", "fn", "for", "if",
            "impl", "in", "let", "loop", "match", "mod", "move", "mut",
            "pub", "ref", "return", "self", "Self", "static", "struct",
            "super", "trait", "true", "type", "unsafe", "use", "where",
            "while", "abstract", "become", "box", "do", "final", "macro",
            "override", "priv", "typeof", "unsized", "virtual", "yield",
            "try", "union",
        }
        builtins = {
            "Option", "Some", "None", "Result", "Ok", "Err", "Vec", "String",
            "Box", "Rc", "Arc", "Cell", "RefCell", "Mutex", "RwLock",
            "HashMap", "BTreeMap", "HashSet", "BTreeSet", "LinkedList",
            "VecDeque", "BinaryHeap", "Cow", "Pin", "PhantomData", "MaybeUninit",
            "Drop", "Clone", "Copy", "PartialEq", "Eq", "PartialOrd", "Ord",
            "Debug", "Display", "Default", "Send", "Sync", "Sized",
            "println!", "print!", "eprintln!", "eprint!", "format!",
            "panic!", "assert!", "assert_eq!", "assert_ne!", "debug_assert!",
            "vec!", "vec", "mem", "slice", "str", "char", "bool", "i8",
            "i16", "i32", "i64", "i128", "isize", "u8", "u16", "u32",
            "u64", "u128", "usize", "f32", "f64", "never", "unit",
            "std", "core", "alloc", "collections", "io", "fs", "path",
            "thread", "time", "net", "sync", "fmt", "ops", "cmp",
            "iter", "convert", "any", "borrow", "clone", "default",
            "hash", "marker", "mem", "num", "ptr", "slice", "str",
        }
        extra = [
            ("COMMENT", r"//[^\n]*|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/"),
            ("DOC", r"///[^\n]*|//!"),
            ("LIFETIME", r"'[a-zA-Z_][a-zA-Z0-9_]*"),
            ("MACRO", r"[a-zA-Z_][a-zA-Z0-9_]*!"),
            ("TYPE", r"\b[A-Z][a-zA-Z0-9_]*\b"),
            ("FUNCNAME", r"\b[a-z_][a-zA-Z0-9_]*(?=\s*\()"),
        ]
        super().__init__(keywords, builtins, extra)


class KotlinHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {
            "abstract", "actual", "annotation", "as", "break", "by", "catch",
            "class", "companion", "const", "constructor", "continue", "crossinline",
            "data", "delegate", "do", "dynamic", "else", "enum", "expect",
            "external", "false", "field", "file", "final", "finally", "for",
            "fun", "get", "if", "import", "in", "infix", "init", "inline",
            "inner", "interface", "internal", "is", "lateinit", "noinline",
            "null", "object", "open", "operator", "out", "override", "package",
            "param", "private", "property", "protected", "public", "receiver",
            "reified", "return", "sealed", "set", "setparam", "super", "suspend",
            "tailrec", "this", "throw", "true", "try", "typealias", "typeof",
            "val", "var", "vararg", "when", "where", "while",
        }
        builtins = {
            "println", "print", "readLine", "readln", "readlnOrNull",
            "Array", "List", "MutableList", "Set", "MutableSet", "Map",
            "MutableMap", "String", "Int", "Long", "Short", "Byte", "Float",
            "Double", "Boolean", "Char", "Unit", "Nothing", "Any", "Comparable",
            "Number", "Iterable", "Sequence", "Collection", "MutableCollection",
            "Range", "IntRange", "LongRange", "CharRange", "ClosedRange",
            "Pair", "Triple", "Result", "Lazy", "lazy", "run", "let", "apply",
            "also", "with", "takeIf", "takeUnless", "repeat", "require",
            "requireNotNull", "check", "checkNotNull", "error", "TODO",
            "emptyList", "listOf", "mutableListOf", "setOf", "mutableSetOf",
            "mapOf", "mutableMapOf", "arrayOf", "emptyArray", "byteArrayOf",
            "charArrayOf", "shortArrayOf", "intArrayOf", "longArrayOf",
            "floatArrayOf", "doubleArrayOf", "booleanArrayOf",
            "CoroutineScope", "launch", "async", "await", "delay", "yield",
            "Flow", "flow", "collect", "emit", "map", "filter", "reduce",
        }
        extra = [
            ("COMMENT", r"//[^\n]*|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/"),
            ("DOC", r"/\*\*[^*]*\*+(?:[^/*][^*]*\*+)*/"),
            ("ANNOTATION", r"@[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?"),
            ("INTERPOLATION", r"\$\{[^}]*\}|\$[a-zA-Z_]\w*"),
            ("CLASSNAME", r"\b[A-Z][a-zA-Z0-9_]*\b"),
            ("FUNCNAME", r"\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()"),
        ]
        super().__init__(keywords, builtins, extra)


class BashHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {"if", "then", "else", "elif", "fi", "case", "esac", "for", "while", "until", "do", "done", "in", "function", "return", "break", "continue", "shift", "exit", "export", "local", "readonly", "unset", "declare", "source", "alias"}
        builtins = {"echo", "printf", "read", "cd", "pwd", "ls", "cat", "grep", "sed", "awk", "cut", "sort", "uniq", "head", "tail", "find", "chmod", "chown", "mkdir", "rm", "cp", "mv", "ln", "touch", "test", "true", "false", "sleep", "wait", "kill", "trap", "exec", "eval"}
        extra = [("COMMENT", r"#[^\n]*"), ("VAR", r"\$\{[^}]*\}|\$[A-Za-z_][A-Za-z0-9_]*|\$\d+"), ("SHEBANG", r"^#!.*$")]
        super().__init__(keywords, builtins, extra)


class RubyHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {"BEGIN", "END", "alias", "and", "begin", "break", "case", "class", "def", "defined?", "do", "else", "elsif", "end", "ensure", "false", "for", "if", "in", "module", "next", "nil", "not", "or", "redo", "rescue", "retry", "return", "self", "super", "then", "true", "undef", "unless", "until", "when", "while", "yield"}
        builtins = {"puts", "print", "printf", "warn", "raise", "require", "load", "include", "extend", "attr_reader", "attr_writer", "attr_accessor", "initialize", "new", "class", "module", "def", "super", "yield", "block_given?", "caller", "exit", "abort", "loop", "proc", "lambda", "gem"}
        extra = [("COMMENT", r"#[^\n]*"), ("SYMBOL", r":[a-zA-Z_]\w*"), ("CONST", r"\b[A-Z][a-zA-Z0-9_]*\b")]
        super().__init__(keywords, builtins, extra)


class LuaHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "goto", "if", "in", "local", "nil", "not", "or", "repeat", "return", "then", "true", "until", "while"}
        builtins = {"print", "type", "tonumber", "tostring", "select", "ipairs", "pairs", "next", "pcall", "xpcall", "error", "assert", "load", "rawget", "rawset", "require", "module", "setmetatable", "getmetatable", "collectgarbage", "dofile", "loadfile", "coroutine", "string", "table", "math", "io", "os", "debug"}
        extra = [("COMMENT", r"--[^\n]*|--\[\[[\s\S]*?\]\]"), ("STRING", r"(?:\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')")]
        super().__init__(keywords, builtins, extra)


class PowerShellHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {"if", "then", "else", "elseif", "switch", "for", "foreach", "while", "do", "until", "break", "continue", "return", "exit", "try", "catch", "finally", "throw", "trap", "param", "begin", "process", "end", "in", "function", "filter", "class", "enum", "workflow", "configuration", "dynamicparam", "data", "var"}
        builtins = {"Write-Host", "Write-Output", "Write-Verbose", "Write-Warning", "Write-Error", "Get-Command", "Get-Help", "Get-Process", "Get-Service", "Set-Location", "Get-ChildItem", "Copy-Item", "Move-Item", "Remove-Item", "New-Item", "Test-Path", "Select-String", "Select-Object", "Where-Object", "ForEach-Object", "Sort-Object", "Group-Object", "Measure-Object", "Invoke-Expression", "Invoke-Command", "Start-Process", "Stop-Process", "Get-Content", "Set-Content", "Add-Content", "Clear-Content", "Out-File", "Out-Null", "Out-String"}
        extra = [("COMMENT", r"#[^\n]*"), ("VAR", r"\$[A-Za-z_][A-Za-z0-9_]*"), ("CMDLET", r"\b[A-Z][a-zA-Z]*-[A-Z][a-zA-Z]*\b")]
        super().__init__(keywords, builtins, extra)


class JavaHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {"abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const", "continue", "default", "do", "double", "else", "enum", "extends", "final", "finally", "float", "for", "goto", "if", "implements", "import", "instanceof", "int", "interface", "long", "native", "new", "package", "private", "protected", "public", "return", "short", "static", "strictfp", "super", "switch", "synchronized", "this", "throw", "throws", "transient", "try", "void", "volatile", "while", "var", "true", "false", "null"}
        builtins = {"System", "Object", "String", "Integer", "Long", "Double", "Float", "Boolean", "Character", "Byte", "Short", "Number", "Class", "Math", "Thread", "Runnable", "Exception", "RuntimeException", "Error", "Throwable", "Cloneable", "Comparable", "StringBuilder", "StringBuffer", "ArrayList", "LinkedList", "HashMap", "HashSet", "TreeMap", "TreeSet", "Collections", "Arrays", "Arrays", "Optional", "Stream", "Files", "Paths", "Path", "File", "InputStream", "OutputStream", "Reader", "Writer", "BufferedReader", "BufferedWriter", "PrintWriter", "Scanner", "Date", "Calendar", "LocalDate", "LocalTime", "LocalDateTime", "Instant", "ZoneId", "Duration", "Period", "UUID", "Random", "BigInteger", "BigDecimal", "Pattern", "Matcher", "URL", "URI", "HttpURLConnection", "HttpClient", "WebSocket", "JSON", "JSONArray", "JSONObject"}
        extra = [("COMMENT", r"//[^\n]*|/\*[^*]*\*+(?:[^/*][^*]*\*+)*/"), ("ANNOTATION", r"@[a-zA-Z_]\w*"), ("CLASSNAME", r"\b[A-Z][a-zA-Z0-9_]*\b"), ("FUNCNAME", r"\b[a-zA-Z_]\w*(?=\s*\()")]
        super().__init__(keywords, builtins, extra)


class ZigHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {"align", "and", "asm", "async", "await", "break", "catch", "comptime", "const", "continue", "defer", "else", "enum", "errdefer", "error", "export", "extern", "fn", "for", "if", "inline", "noalias", "nosuspend", "opaque", "or", "orelse", "pack", "pub", "resume", "return", "linksection", "struct", "suspend", "switch", "test", "threadlocal", "try", "union", "unreachable", "usingnamespace", "var", "volatile", "while"}
        builtins = {"i8", "i16", "i32", "i64", "i128", "u8", "u16", "u32", "u64", "u128", "f16", "f32", "f64", "f80", "f128", "bool", "void", "noreturn", "type", "anyerror", "anyframe", "isize", "usize", "c_short", "c_int", "c_long", "c_longlong", "c_float", "c_double", "c_void", "std", "print", "debug", "warn", "err", "alloc", "malloc", "free", "memcpy", "memset", "strlen", "printf", "sprintf", "exit", "abort", "panic", "assert", "unreachable"}
        extra = [("COMMENT", r"//[^\n]*"), ("PREPROC", r"#[ \t]*[a-zA-Z_]\w*"), ("NUMBER", r"\b(?:0[xX][0-9a-fA-F]+|\d+)\b")]
        super().__init__(keywords, builtins, extra)


class AsmHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {"mov", "add", "sub", "mul", "div", "imul", "idiv", "and", "or", "xor", "not", "neg", "inc", "dec", "cmp", "test", "jmp", "je", "jne", "jz", "jnz", "jg", "jl", "jge", "jle", "ja", "jb", "jae", "jbe", "call", "ret", "push", "pop", "lea", "nop", "hlt", "int", "cli", "sti", "cbw", "cwd", "cdq", "cqo", "bswap", "xchg", "xlat", "lodsb", "lodsw", "lodsd", "lodsq", "stosb", "stosw", "stosd", "stosq", "movsb", "movsw", "movsd", "movsq", "cmpsb", "cmpsw", "cmpsd", "cmpsq", "scasb", "scasw", "scasd", "scasq", "rep", "repe", "repne", "lock", "in", "out", "cli", "sti", "iret", "iretd", "iretq", "lidt", "sidt", "lgdt", "sgdt", "lldt", "sldt", "ltr", "str", "lar", "lsl", "verr", "verw", "arpl", "clts", "smsw", "lmsw", "invd", "wbinvd", "rdmsr", "wrmsr", "rdtsc", "rdtscp", "rdpmc", "cpuid", "xgetbv", "xsetbv", "vmcall", "vmlaunch", "vmresume", "vmxoff"}
        builtins = {"eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eip", "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "rip", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", "al", "ah", "bl", "bh", "cl", "ch", "dl", "dh", "ax", "bx", "cx", "dx", "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7", "ymm0", "ymm1", "ymm2", "ymm3", "ymm4", "ymm5", "ymm6", "ymm7", "cs", "ds", "es", "fs", "gs", "ss", "st0", "st1", "st2", "st3", "st4", "st5", "st6", "st7", "cr0", "cr1", "cr2", "cr3", "cr4", "cr8", "dr0", "dr1", "dr2", "dr3", "dr6", "dr7"}
        extra = [("COMMENT", r";[^\n]*"), ("LABEL", r"^\s*[a-zA-Z_]\w*:"), ("DIRECTIVE", r"^\s*\.[a-zA-Z_]\w*"), ("REGISTER", r"\b(?:[er][ax-z]{2}|[rx][0-9]{1,2}|[xyz]mm[0-9]+|st[0-7]|[cdesfgs]s|cr[0-8]|dr[0-7])\b")]
        super().__init__(keywords, builtins, extra)


class HTMLHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {"html", "head", "body", "div", "span", "p", "a", "img", "ul", "ol", "li", "table", "tr", "td", "th", "thead", "tbody", "tfoot", "form", "input", "button", "select", "option", "textarea", "label", "fieldset", "legend", "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr", "pre", "code", "blockquote", "q", "cite", "abbr", "address", "b", "i", "u", "s", "strong", "em", "mark", "small", "del", "ins", "sub", "sup", "time", "nav", "header", "footer", "main", "section", "article", "aside", "figure", "figcaption", "details", "summary", "dialog", "template", "slot", "script", "style", "link", "meta", "title", "base", "style", "canvas", "svg", "video", "audio", "source", "track", "iframe", "object", "embed", "param", "map", "area", "picture", "wbr", "ruby", "rt", "rp", "bdi", "bdo", "data", "datalist", "optgroup", "output", "progress", "meter", "noscript"}
        extra = [("COMMENT", r"<!--[\s\S]*?-->"), ("TAG", r"</?[a-zA-Z][a-zA-Z0-9]*"), ("ATTR", r"\s[a-zA-Z][a-zA-Z0-9-]*="), ("ENTITY", r"&[a-zA-Z]+;|&#\d+;")]
        super().__init__(set(), set(), extra)


class CSSHighlighter(BaseHighlighter):
    def __init__(self):
        keywords = {"display", "position", "top", "right", "bottom", "left", "z-index", "width", "height", "min-width", "max-width", "min-height", "max-height", "padding", "margin", "border", "border-width", "border-style", "border-color", "border-radius", "background", "background-color", "background-image", "background-position", "background-size", "color", "font", "font-family", "font-size", "font-weight", "font-style", "line-height", "text-align", "text-decoration", "text-transform", "letter-spacing", "word-spacing", "white-space", "visibility", "opacity", "overflow", "float", "clear", "flex", "flex-direction", "flex-wrap", "justify-content", "align-items", "align-content", "grid", "grid-template-columns", "grid-template-rows", "gap", "transform", "transition", "animation", "keyframes", "box-shadow", "text-shadow", "cursor", "user-select", "pointer-events", "resize", "scrollbar-width", "scrollbar-color"}
        extra = [("COMMENT", r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/"), ("SELECTOR", r"[.#]?[a-zA-Z_][a-zA-Z0-9_-]*(?:\s*,\s*[.#]?[a-zA-Z_][a-zA-Z0-9_-]*)*\s*\{"), ("PROPERTY", r"[a-z-]+\s*:"), ("VALUE", r":\s*[^;]+;")]
        super().__init__(set(), set(), extra)


def get_highlighter(filename):
    if not filename:
        return None
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".py":
        return PythonHighlighter()
    elif ext in (".js", ".jsx"):
        return JavaScriptHighlighter()
    elif ext in (".ts", ".tsx"):
        return TypeScriptHighlighter()
    elif ext == ".php":
        return PHPHighlighter()
    elif ext == ".go":
        return GoHighlighter()
    elif ext in (".rs", ".rlib"):
        return RustHighlighter()
    elif ext in (".kt", ".kts"):
        return KotlinHighlighter()
    elif ext in (".c", ".h"):
        return CHighlighter()
    elif ext in (".cpp", ".cc", ".cxx", ".hpp", ".hh"):
        return CppHighlighter()
    elif ext == ".cs":
        return CSharpHighlighter()
    elif ext in (".sh", ".bash", ".zsh"):
        return BashHighlighter()
    elif ext in (".rb", ".erb"):
        return RubyHighlighter()
    elif ext == ".lua":
        return LuaHighlighter()
    elif ext in (".ps1", ".psm1", ".psd1"):
        return PowerShellHighlighter()
    elif ext == ".java":
        return JavaHighlighter()
    elif ext == ".zig":
        return ZigHighlighter()
    elif ext in (".asm", ".s", ".S"):
        return AsmHighlighter()
    elif ext in (".html", ".htm", ".xhtml"):
        return HTMLHighlighter()
    elif ext == ".css":
        return CSSHighlighter()
    return None


# ─── Keyword dictionaries for autocomplete ─────────────────────────────

KEYWORDS = {
    ".py": {
        "keywords": ["False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "class", "continue", "def", "del", "elif", "else", "except",
            "finally", "for", "from", "global", "if", "import", "in", "is",
            "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
            "try", "while", "with", "yield"],
        "builtins": ["abs", "all", "any", "bin", "bool", "bytearray", "bytes", "callable",
            "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir",
            "divmod", "enumerate", "eval", "exec", "filter", "float", "format",
            "frozenset", "getattr", "globals", "hasattr", "hash", "help", "hex",
            "id", "input", "int", "isinstance", "issubclass", "iter", "len",
            "list", "locals", "map", "max", "memoryview", "min", "next", "object",
            "oct", "open", "ord", "pow", "print", "property", "range", "repr",
            "reversed", "round", "set", "setattr", "slice", "sorted", "staticmethod",
            "str", "sum", "super", "tuple", "type", "vars", "zip", "__import__",
            "open", "input", "len", "range", "print", "str", "int", "float", "bool", "list", "dict", "set", "tuple"]
    },
    ".js": {
        "keywords": ["async", "await", "break", "case", "catch", "class", "const",
            "continue", "debugger", "default", "delete", "do", "else",
            "export", "extends", "false", "finally", "for", "function",
            "if", "import", "in", "instanceof", "let", "new", "null",
            "return", "super", "switch", "this", "throw", "true", "try",
            "typeof", "undefined", "var", "void", "while", "with", "yield"],
        "builtins": ["Array", "Boolean", "Date", "Error", "Function", "JSON",
            "Math", "Number", "Object", "Promise", "RegExp", "String",
            "console", "document", "window", "alert", "setTimeout",
            "setInterval", "clearTimeout", "clearInterval", "parseInt",
            "parseFloat", "isNaN", "eval"]
    },
    ".jsx": {
        "keywords": ["async", "await", "break", "case", "catch", "class", "const",
            "continue", "debugger", "default", "delete", "do", "else",
            "export", "extends", "false", "finally", "for", "function",
            "if", "import", "in", "instanceof", "let", "new", "null",
            "return", "super", "switch", "this", "throw", "true", "try",
            "typeof", "undefined", "var", "void", "while", "with", "yield"],
        "builtins": ["Array", "Boolean", "Date", "Error", "Function", "JSON",
            "Math", "Number", "Object", "Promise", "RegExp", "String",
            "console", "document", "window", "alert", "setTimeout",
            "setInterval", "clearTimeout", "clearInterval", "parseInt",
            "parseFloat", "isNaN", "eval"]
    },
    ".ts": {
        "keywords": ["async", "await", "break", "case", "catch", "class", "const",
            "continue", "debugger", "default", "delete", "do", "else",
            "enum", "export", "extends", "false", "finally", "for", "function",
            "if", "import", "in", "instanceof", "interface", "let", "new", "null",
            "return", "super", "switch", "this", "throw", "true", "try",
            "typeof", "undefined", "var", "void", "while", "with", "yield",
            "readonly", "abstract", "implements", "type", "namespace", "module"],
        "builtins": ["Array", "Boolean", "Date", "Error", "Function", "JSON",
            "Math", "Number", "Object", "Promise", "RegExp", "String",
            "console", "document", "window", "alert", "setTimeout",
            "setInterval", "Map", "Set", "WeakMap", "WeakSet", "Proxy", "Reflect"]
    },
    ".tsx": {
        "keywords": ["async", "await", "break", "case", "catch", "class", "const",
            "continue", "debugger", "default", "delete", "do", "else",
            "enum", "export", "extends", "false", "finally", "for", "function",
            "if", "import", "in", "instanceof", "interface", "let", "new", "null",
            "return", "super", "switch", "this", "throw", "true", "try",
            "typeof", "undefined", "var", "void", "while", "with", "yield",
            "readonly", "abstract", "implements", "type", "namespace", "module"],
        "builtins": ["Array", "Boolean", "Date", "Error", "Function", "JSON",
            "Math", "Number", "Object", "Promise", "RegExp", "String",
            "console", "document", "window", "alert", "setTimeout",
            "setInterval", "Map", "Set", "WeakMap", "WeakSet", "Proxy", "Reflect"]
    },
    ".c": {
        "keywords": ["auto", "break", "case", "char", "const", "continue", "default",
            "do", "double", "else", "enum", "extern", "float", "for", "goto",
            "if", "int", "long", "register", "return", "short", "signed",
            "sizeof", "static", "struct", "switch", "typedef", "union",
            "unsigned", "void", "volatile", "while"],
        "builtins": ["printf", "scanf", "malloc", "free", "memcpy", "memset",
            "strlen", "strcpy", "strcmp", "fopen", "fclose", "fread",
            "fwrite", "fprintf", "sprintf", "exit", "atoi", "atof", "NULL", "EOF"]
    },
    ".h": {
        "keywords": ["auto", "break", "case", "char", "const", "continue", "default",
            "do", "double", "else", "enum", "extern", "float", "for", "goto",
            "if", "int", "long", "register", "return", "short", "signed",
            "sizeof", "static", "struct", "switch", "typedef", "union",
            "unsigned", "void", "volatile", "while"],
        "builtins": ["printf", "scanf", "malloc", "free", "memcpy", "memset",
            "strlen", "strcpy", "strcmp", "fopen", "fclose", "fread",
            "fwrite", "fprintf", "sprintf", "exit", "atoi", "atof", "NULL", "EOF"]
    },
    ".cpp": {
        "keywords": ["alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand",
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
            "while", "xor", "xor_eq"],
        "builtins": ["std", "cout", "cin", "cerr", "endl", "string", "vector",
            "map", "set", "queue", "stack", "array", "tuple", "pair",
            "make_shared", "make_unique", "shared_ptr", "unique_ptr", "nullptr", "NULL"]
    },
    ".cc": {
        "keywords": ["alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand",
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
            "while", "xor", "xor_eq"],
        "builtins": ["std", "cout", "cin", "cerr", "endl", "string", "vector",
            "map", "set", "queue", "stack", "array", "tuple", "pair",
            "make_shared", "make_unique", "shared_ptr", "unique_ptr", "nullptr", "NULL"]
    },
    ".cxx": {
        "keywords": ["alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand",
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
            "while", "xor", "xor_eq"],
        "builtins": ["std", "cout", "cin", "cerr", "endl", "string", "vector",
            "map", "set", "queue", "stack", "array", "tuple", "pair",
            "make_shared", "make_unique", "shared_ptr", "unique_ptr", "nullptr", "NULL"]
    },
    ".hpp": {
        "keywords": ["alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand",
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
            "while", "xor", "xor_eq"],
        "builtins": ["std", "cout", "cin", "cerr", "endl", "string", "vector",
            "map", "set", "queue", "stack", "array", "tuple", "pair",
            "make_shared", "make_unique", "shared_ptr", "unique_ptr", "nullptr", "NULL"]
    },
    ".hh": {
        "keywords": ["alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand",
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
            "while", "xor", "xor_eq"],
        "builtins": ["std", "cout", "cin", "cerr", "endl", "string", "vector",
            "map", "set", "queue", "stack", "array", "tuple", "pair",
            "make_shared", "make_unique", "shared_ptr", "unique_ptr", "nullptr", "NULL"]
    },
    ".cs": {
        "keywords": ["abstract", "as", "base", "bool", "break", "byte", "case",
            "catch", "char", "checked", "class", "const", "continue",
            "decimal", "default", "delegate", "do", "double", "else",
            "enum", "event", "explicit", "extern", "false", "finally",
            "fixed", "float", "for", "foreach", "goto", "if", "implicit",
            "in", "int", "interface", "internal", "is", "lock", "long",
            "namespace", "new", "null", "object", "operator", "out",
            "override", "params", "private", "protected", "public",
            "readonly", "ref", "return", "sbyte", "sealed", "short",
            "sizeof", "stackalloc", "static", "string", "struct", "switch",
            "this", "throw", "true", "try", "typeof", "uint", "ulong",
            "unchecked", "unsafe", "ushort", "using", "virtual", "void",
            "volatile", "while", "async", "await"],
        "builtins": ["Console", "String", "Int32", "Convert", "Math", "Array",
            "List", "Dictionary", "Enumerable", "Task", "DateTime", "Guid",
            "Exception", "Environment", "File", "Directory", "Path", "Debug"]
    },
    ".java": {
        "keywords": ["abstract", "assert", "boolean", "break", "byte", "case",
            "catch", "char", "class", "const", "continue", "default",
            "do", "double", "else", "enum", "extends", "final", "finally",
            "float", "for", "goto", "if", "implements", "import", "instanceof",
            "int", "interface", "long", "native", "new", "package", "private",
            "protected", "public", "return", "short", "static", "strictfp",
            "super", "switch", "synchronized", "this", "throw", "throws",
            "transient", "try", "void", "volatile", "while"],
        "builtins": ["System", "Object", "String", "Integer", "Long", "Double",
            "Float", "Boolean", "Character", "Byte", "Short", "Number", "Class",
            "Math", "Thread", "Runnable", "Exception", "ArrayList", "LinkedList",
            "HashMap", "HashSet", "Collections", "Arrays", "Optional", "Stream"]
    },
    ".go": {
        "keywords": ["break", "case", "chan", "const", "continue", "default", "defer",
            "else", "fallthrough", "for", "func", "go", "goto", "if",
            "import", "interface", "map", "package", "range", "return",
            "select", "struct", "switch", "type", "var"],
        "builtins": ["append", "cap", "close", "complex", "copy", "delete", "imag",
            "len", "make", "new", "panic", "print", "println", "real", "recover",
            "bool", "byte", "complex64", "complex128", "error", "float32",
            "float64", "int", "int8", "int16", "int32", "int64", "rune", "string"]
    },
    ".rs": {
        "keywords": ["as", "async", "await", "break", "const", "continue", "crate",
            "dyn", "else", "enum", "extern", "false", "fn", "for", "if",
            "impl", "in", "let", "loop", "match", "mod", "move", "mut",
            "pub", "ref", "return", "self", "Self", "static", "struct",
            "super", "trait", "true", "type", "unsafe", "use", "where",
            "while", "try", "union"],
        "builtins": ["Option", "Some", "None", "Result", "Ok", "Err", "Vec", "String",
            "Box", "Rc", "Arc", "println", "print", "eprintln", "vec", "panic", "assert"]
    },
    ".php": {
        "keywords": ["abstract", "and", "array", "as", "break", "callable", "case",
            "catch", "class", "clone", "const", "continue", "declare",
            "default", "die", "do", "echo", "else", "elseif", "empty",
            "enddeclare", "endfor", "endforeach", "endif", "endswitch",
            "endwhile", "eval", "exit", "extends", "final", "finally",
            "fn", "for", "foreach", "function", "global", "goto", "if",
            "implements", "include", "include_once", "instanceof",
            "insteadof", "interface", "isset", "list", "match", "namespace",
            "new", "or", "print", "private", "protected", "public",
            "require", "require_once", "return", "static", "switch",
            "throw", "trait", "try", "unset", "use", "var", "while", "yield"],
        "builtins": ["strlen", "strpos", "substr", "str_replace", "explode", "implode",
            "trim", "ltrim", "rtrim", "strtolower", "strtoupper", "preg_match",
            "array_merge", "array_push", "array_pop", "count", "sort", "json_encode",
            "json_decode", "file_get_contents", "file_put_contents", "date", "time"]
    },
    ".kt": {
        "keywords": ["abstract", "actual", "annotation", "as", "break", "by", "catch",
            "class", "companion", "const", "constructor", "continue", "crossinline",
            "data", "delegate", "do", "dynamic", "else", "enum", "expect",
            "external", "false", "field", "file", "final", "finally", "for",
            "fun", "get", "if", "import", "in", "infix", "init", "inline",
            "inner", "interface", "internal", "is", "lateinit", "noinline",
            "null", "object", "open", "operator", "out", "override", "package",
            "param", "private", "property", "protected", "public", "receiver",
            "reified", "return", "sealed", "set", "setparam", "super", "suspend",
            "tailrec", "this", "throw", "true", "try", "typealias", "typeof",
            "val", "var", "vararg", "when", "where", "while"],
        "builtins": ["println", "print", "readLine", "readln", "Array", "List",
            "MutableList", "Set", "MutableSet", "Map", "MutableMap", "String",
            "Int", "Long", "Short", "Byte", "Float", "Double", "Boolean", "Char",
            "Unit", "Nothing", "Any", "listOf", "mutableListOf", "setOf", "mapOf"]
    },
    ".kts": {
        "keywords": ["abstract", "actual", "annotation", "as", "break", "by", "catch",
            "class", "companion", "const", "constructor", "continue", "crossinline",
            "data", "delegate", "do", "dynamic", "else", "enum", "expect",
            "external", "false", "field", "file", "final", "finally", "for",
            "fun", "get", "if", "import", "in", "infix", "init", "inline",
            "inner", "interface", "internal", "is", "lateinit", "noinline",
            "null", "object", "open", "operator", "out", "override", "package",
            "param", "private", "property", "protected", "public", "receiver",
            "reified", "return", "sealed", "set", "setparam", "super", "suspend",
            "tailrec", "this", "throw", "true", "try", "typealias", "typeof",
            "val", "var", "vararg", "when", "where", "while"],
        "builtins": ["println", "print", "readLine", "readln", "Array", "List",
            "MutableList", "Set", "MutableSet", "Map", "MutableMap", "String",
            "Int", "Long", "Short", "Byte", "Float", "Double", "Boolean", "Char",
            "Unit", "Nothing", "Any", "listOf", "mutableListOf", "setOf", "mapOf"]
    },
    ".rb": {
        "keywords": ["BEGIN", "END", "alias", "and", "begin", "break", "case", "class",
            "def", "defined?", "do", "else", "elsif", "end", "ensure", "false",
            "for", "if", "in", "module", "next", "nil", "not", "or", "redo",
            "rescue", "retry", "return", "self", "super", "then", "true",
            "undef", "unless", "until", "when", "while", "yield"],
        "builtins": ["puts", "print", "printf", "warn", "raise", "require", "load",
            "include", "extend", "attr_reader", "attr_writer", "attr_accessor",
            "initialize", "new", "class", "module", "def", "super", "yield"]
    },
    ".erb": {
        "keywords": ["BEGIN", "END", "alias", "and", "begin", "break", "case", "class",
            "def", "defined?", "do", "else", "elsif", "end", "ensure", "false",
            "for", "if", "in", "module", "next", "nil", "not", "or", "redo",
            "rescue", "retry", "return", "self", "super", "then", "true",
            "undef", "unless", "until", "when", "while", "yield"],
        "builtins": ["puts", "print", "printf", "warn", "raise", "require", "load",
            "include", "extend", "attr_reader", "attr_writer", "attr_accessor",
            "initialize", "new", "class", "module", "def", "super", "yield"]
    },
    ".lua": {
        "keywords": ["and", "break", "do", "else", "elseif", "end", "false", "for",
            "function", "goto", "if", "in", "local", "nil", "not", "or",
            "repeat", "return", "then", "true", "until", "while"],
        "builtins": ["print", "type", "tonumber", "tostring", "select", "ipairs",
            "pairs", "next", "pcall", "xpcall", "error", "assert", "load",
            "rawget", "rawset", "require", "module", "setmetatable", "getmetatable",
            "collectgarbage", "dofile", "loadfile", "coroutine", "string", "table",
            "math", "io", "os", "debug"]
    },
    ".ps1": {
        "keywords": ["if", "then", "else", "elseif", "switch", "for", "foreach",
            "while", "do", "until", "break", "continue", "return", "exit",
            "try", "catch", "finally", "throw", "trap", "param", "begin",
            "process", "end", "in", "function", "filter", "class", "enum",
            "workflow", "configuration", "dynamicparam", "data", "var"],
        "builtins": ["Write-Host", "Write-Output", "Write-Verbose", "Write-Warning",
            "Write-Error", "Get-Command", "Get-Help", "Get-Process", "Get-Service",
            "Set-Location", "Get-ChildItem", "Copy-Item", "Move-Item", "Remove-Item",
            "New-Item", "Test-Path", "Select-String", "Select-Object", "Where-Object"]
    },
    ".psm1": {
        "keywords": ["if", "then", "else", "elseif", "switch", "for", "foreach",
            "while", "do", "until", "break", "continue", "return", "exit",
            "try", "catch", "finally", "throw", "trap", "param", "begin",
            "process", "end", "in", "function", "filter", "class", "enum",
            "workflow", "configuration", "dynamicparam", "data", "var"],
        "builtins": ["Write-Host", "Write-Output", "Write-Verbose", "Write-Warning",
            "Write-Error", "Get-Command", "Get-Help", "Get-Process", "Get-Service",
            "Set-Location", "Get-ChildItem", "Copy-Item", "Move-Item", "Remove-Item",
            "New-Item", "Test-Path", "Select-String", "Select-Object", "Where-Object"]
    },
    ".psd1": {
        "keywords": ["if", "then", "else", "elseif", "switch", "for", "foreach",
            "while", "do", "until", "break", "continue", "return", "exit",
            "try", "catch", "finally", "throw", "trap", "param", "begin",
            "process", "end", "in", "function", "filter", "class", "enum",
            "workflow", "configuration", "dynamicparam", "data", "var"],
        "builtins": ["Write-Host", "Write-Output", "Write-Verbose", "Write-Warning",
            "Write-Error", "Get-Command", "Get-Help", "Get-Process", "Get-Service",
            "Set-Location", "Get-ChildItem", "Copy-Item", "Move-Item", "Remove-Item",
            "New-Item", "Test-Path", "Select-String", "Select-Object", "Where-Object"]
    },
    ".sh": {
        "keywords": ["if", "then", "else", "elif", "fi", "case", "esac", "for",
            "while", "until", "do", "done", "in", "function", "return",
            "break", "continue", "shift", "exit", "export", "local",
            "readonly", "unset", "declare", "source", "alias"],
        "builtins": ["echo", "printf", "read", "cd", "pwd", "ls", "cat", "grep",
            "sed", "awk", "cut", "sort", "uniq", "head", "tail", "find",
            "chmod", "chown", "mkdir", "rm", "cp", "mv", "ln", "touch", "test",
            "true", "false", "sleep", "wait", "kill", "trap", "exec", "eval"]
    },
    ".bash": {
        "keywords": ["if", "then", "else", "elif", "fi", "case", "esac", "for",
            "while", "until", "do", "done", "in", "function", "return",
            "break", "continue", "shift", "exit", "export", "local",
            "readonly", "unset", "declare", "source", "alias"],
        "builtins": ["echo", "printf", "read", "cd", "pwd", "ls", "cat", "grep",
            "sed", "awk", "cut", "sort", "uniq", "head", "tail", "find",
            "chmod", "chown", "mkdir", "rm", "cp", "mv", "ln", "touch", "test",
            "true", "false", "sleep", "wait", "kill", "trap", "exec", "eval"]
    },
    ".zsh": {
        "keywords": ["if", "then", "else", "elif", "fi", "case", "esac", "for",
            "while", "until", "do", "done", "in", "function", "return",
            "break", "continue", "shift", "exit", "export", "local",
            "readonly", "unset", "declare", "source", "alias"],
        "builtins": ["echo", "printf", "read", "cd", "pwd", "ls", "cat", "grep",
            "sed", "awk", "cut", "sort", "uniq", "head", "tail", "find",
            "chmod", "chown", "mkdir", "rm", "cp", "mv", "ln", "touch", "test",
            "true", "false", "sleep", "wait", "kill", "trap", "exec", "eval"]
    },
    ".zig": {
        "keywords": ["align", "and", "asm", "async", "await", "break", "catch",
            "comptime", "const", "continue", "defer", "else", "enum", "errdefer",
            "error", "export", "extern", "fn", "for", "if", "inline", "noalias",
            "nosuspend", "opaque", "or", "orelse", "pack", "pub", "resume",
            "return", "linksection", "struct", "suspend", "switch", "test",
            "threadlocal", "try", "union", "unreachable", "usingnamespace",
            "var", "volatile", "while"],
        "builtins": ["i8", "i16", "i32", "i64", "i128", "u8", "u16", "u32", "u64",
            "u128", "f16", "f32", "f64", "f80", "f128", "bool", "void", "noreturn",
            "type", "anyerror", "anyframe", "isize", "usize", "c_short", "c_int",
            "c_long", "c_longlong", "c_float", "c_double", "c_void", "std", "print",
            "debug", "warn", "err", "alloc", "malloc", "free", "memcpy", "memset"]
    },
    ".asm": {
        "keywords": ["mov", "add", "sub", "mul", "div", "imul", "idiv", "and", "or",
            "xor", "not", "neg", "inc", "dec", "cmp", "test", "jmp", "je", "jne",
            "jz", "jnz", "jg", "jl", "jge", "jle", "ja", "jb", "jae", "jbe",
            "call", "ret", "push", "pop", "lea", "nop", "hlt", "int", "cli", "sti"],
        "builtins": ["eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eip",
            "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "rip",
            "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", "al", "ah",
            "bl", "bh", "cl", "ch", "dl", "dh", "ax", "bx", "cx", "dx"]
    },
    ".s": {
        "keywords": ["mov", "add", "sub", "mul", "div", "imul", "idiv", "and", "or",
            "xor", "not", "neg", "inc", "dec", "cmp", "test", "jmp", "je", "jne",
            "jz", "jnz", "jg", "jl", "jge", "jle", "ja", "jb", "jae", "jbe",
            "call", "ret", "push", "pop", "lea", "nop", "hlt", "int", "cli", "sti"],
        "builtins": ["eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eip",
            "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "rip",
            "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", "al", "ah",
            "bl", "bh", "cl", "ch", "dl", "dh", "ax", "bx", "cx", "dx"]
    },
    ".S": {
        "keywords": ["mov", "add", "sub", "mul", "div", "imul", "idiv", "and", "or",
            "xor", "not", "neg", "inc", "dec", "cmp", "test", "jmp", "je", "jne",
            "jz", "jnz", "jg", "jl", "jge", "jle", "ja", "jb", "jae", "jbe",
            "call", "ret", "push", "pop", "lea", "nop", "hlt", "int", "cli", "sti"],
        "builtins": ["eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eip",
            "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "rip",
            "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", "al", "ah",
            "bl", "bh", "cl", "ch", "dl", "dh", "ax", "bx", "cx", "dx"]
    },
    ".html": {
        "keywords": ["html", "head", "body", "div", "span", "p", "a", "img", "ul",
            "ol", "li", "table", "tr", "td", "th", "thead", "tbody", "tfoot",
            "form", "input", "button", "select", "option", "textarea", "label",
            "fieldset", "legend", "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr",
            "pre", "code", "blockquote", "q", "cite", "abbr", "address", "b", "i",
            "u", "s", "strong", "em", "mark", "small", "del", "ins", "sub", "sup",
            "time", "nav", "header", "footer", "main", "section", "article", "aside"],
        "builtins": []
    },
    ".htm": {
        "keywords": ["html", "head", "body", "div", "span", "p", "a", "img", "ul",
            "ol", "li", "table", "tr", "td", "th", "thead", "tbody", "tfoot",
            "form", "input", "button", "select", "option", "textarea", "label",
            "fieldset", "legend", "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr",
            "pre", "code", "blockquote", "q", "cite", "abbr", "address", "b", "i",
            "u", "s", "strong", "em", "mark", "small", "del", "ins", "sub", "sup",
            "time", "nav", "header", "footer", "main", "section", "article", "aside"],
        "builtins": []
    },
    ".xhtml": {
        "keywords": ["html", "head", "body", "div", "span", "p", "a", "img", "ul",
            "ol", "li", "table", "tr", "td", "th", "thead", "tbody", "tfoot",
            "form", "input", "button", "select", "option", "textarea", "label",
            "fieldset", "legend", "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr",
            "pre", "code", "blockquote", "q", "cite", "abbr", "address", "b", "i",
            "u", "s", "strong", "em", "mark", "small", "del", "ins", "sub", "sup",
            "time", "nav", "header", "footer", "main", "section", "article", "aside"],
        "builtins": []
    },
    ".css": {
        "keywords": ["display", "position", "top", "right", "bottom", "left",
            "z-index", "width", "height", "min-width", "max-width", "min-height",
            "max-height", "padding", "margin", "border", "border-width",
            "border-style", "border-color", "border-radius", "background",
            "background-color", "background-image", "background-position",
            "background-size", "color", "font", "font-family", "font-size",
            "font-weight", "font-style", "line-height", "text-align",
            "text-decoration", "text-transform", "letter-spacing",
            "word-spacing", "white-space", "visibility", "opacity", "overflow",
            "float", "clear", "flex", "flex-direction", "flex-wrap",
            "justify-content", "align-items", "align-content", "grid",
            "grid-template-columns", "grid-template-rows", "gap", "transform",
            "transition", "animation", "box-shadow", "text-shadow", "cursor"],
        "builtins": []
    }
}


def get_language_keywords(filename):
    """Get keywords and builtins for a given filename extension."""
    if not filename:
        return [], []
    ext = os.path.splitext(filename)[1].lower()
    if ext in KEYWORDS:
        kw = KEYWORDS[ext].get("keywords", [])
        bi = KEYWORDS[ext].get("builtins", [])
        return sorted(set(kw + bi)), []
    return [], []


class Buffer:
    """One open file/tab."""
    def __init__(self, filename=None):
        self.filename = filename
        self.lines = [""]
        self.cursor_y = 0
        self.cursor_x = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.dirty = False
        self.undo_stack = []
        self.redo_stack = []
        self.sel_start = None
        self.sel_end = None
        if filename and os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    text = f.read()
                self.lines = text.split("\n") if text else [""]
                if not self.lines:
                    self.lines = [""]
            except Exception:
                pass

    @property
    def title(self):
        if self.filename:
            return os.path.basename(self.filename)
        return "[New]"


class Editor:
    def __init__(self, filenames=None):
        self.clipboard = []
        self.max_undo = 50
        self.message = ""
        self._quit_confirm = False
        self.completions = []
        self.completion_idx = 0
        self.completion_visible = False
        self._kill_line_repeat = False  # for holding Ctrl+K
        # File menu
        self.file_menu_visible = False
        self.file_menu_files = []
        self.file_menu_idx = 0
        self.file_menu_scroll = 0
        # plugins
        self.plugin_manager = None
        if HAS_PLUGINS and PluginManager:
            self.plugin_manager = PluginManager(self)

        # Auto-complete timer (1 second delay for auto-suggestion)
        self._last_activity_time = 0
        self._auto_complete_delay = 1.0  # seconds (reduced from 5.0)
        self._pending_completion = False
        self._completion_prefix = ""
        self._completion_start_x = 0

        # Multi-buffer support
        self.buffers = []
        self.buffer_idx = 0
        if filenames:
            for fn in filenames:
                self.buffers.append(Buffer(fn))
        else:
            self.buffers.append(Buffer())
        self._sync_from_buffer()
        self.save_undo()

    # ─── Buffer sync ──────────────────────────────────────

    def _sync_from_buffer(self):
        """Copy current buffer state into Editor attributes."""
        if not self.buffers or self.buffer_idx >= len(self.buffers):
            return
        b = self.buffers[self.buffer_idx]
        self.filename = b.filename
        self.lines = b.lines
        self.cursor_y = b.cursor_y
        self.cursor_x = b.cursor_x
        self.scroll_y = b.scroll_y
        self.scroll_x = b.scroll_x
        self.dirty = b.dirty
        self.undo_stack = b.undo_stack
        self.redo_stack = b.redo_stack
        self.sel_start = b.sel_start
        self.sel_end = b.sel_end

    def _sync_to_buffer(self):
        """Copy Editor attributes back into current buffer."""
        if not self.buffers or self.buffer_idx >= len(self.buffers):
            return
        b = self.buffers[self.buffer_idx]
        b.filename = self.filename
        b.lines = self.lines
        b.cursor_y = self.cursor_y
        b.cursor_x = self.cursor_x
        b.scroll_y = self.scroll_y
        b.scroll_x = self.scroll_x
        b.dirty = self.dirty
        b.undo_stack = self.undo_stack
        b.redo_stack = self.redo_stack
        b.sel_start = self.sel_start
        b.sel_end = self.sel_end

    def switch_buffer(self, direction=1):
        """Switch to next/previous buffer."""
        if len(self.buffers) <= 1:
            return
        self._sync_to_buffer()
        self.buffer_idx = (self.buffer_idx + direction) % len(self.buffers)
        self._sync_from_buffer()
        self.message = f"Tab {self.buffer_idx + 1}/{len(self.buffers)}: {self.buffers[self.buffer_idx].title}"

    def new_buffer(self, filename=None):
        """Add a new buffer and switch to it."""
        self._sync_to_buffer()
        b = Buffer(filename)
        self.buffers.append(b)
        self.buffer_idx = len(self.buffers) - 1
        self._sync_from_buffer()
        self.save_undo()
        self.message = f"New tab: {b.title}"

    def close_buffer(self, stdscr=None, force=False):
        """Close current buffer, with save prompt if dirty."""
        if self.dirty and stdscr and not force:
            self.message = "Unsaved! Ctrl+W again to close without saving, Ctrl+S to save"
            self._quit_confirm = True
            return False
        self._quit_confirm = False
        total = len(self.buffers)
        del self.buffers[self.buffer_idx]
        if not self.buffers:
            self.buffers.append(Buffer())
            self.buffer_idx = 0
        else:
            if self.buffer_idx >= len(self.buffers):
                self.buffer_idx = len(self.buffers) - 1
        self._sync_from_buffer()
        self.message = f"Closed. Tab {self.buffer_idx + 1}/{len(self.buffers)}"
        return True

    # ─── File Menu ────────────────────────────────────────

    def toggle_file_menu(self, stdscr):
        """Toggle file menu visibility."""
        if self.file_menu_visible:
            self.file_menu_visible = False
            self.message = ""
        else:
            self.file_menu_visible = True
            self.file_menu_files = self._get_all_files_in_dir()
            self.file_menu_idx = 0
            self.file_menu_scroll = 0
            current_file = self.buffers[self.buffer_idx].filename
            if current_file and self.file_menu_files:
                for i, f in enumerate(self.file_menu_files):
                    if os.path.basename(f) == os.path.basename(current_file):
                        self.file_menu_idx = i
                        break

    def _get_all_files_in_dir(self):
        """Get list of code files in current directory."""
        current_dir = os.path.dirname(os.path.abspath(self.filename)) if self.filename else os.getcwd()
        extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.c', '.cpp', '.h', '.hpp', '.cs', 
                      '.java', '.go', '.rs', '.php', '.html', '.css', '.rb', '.lua', '.ps1', 
                      '.sh', '.bash', '.zsh', '.js', '.json', '.md', '.txt', '.yaml', '.yml', '.toml'}
        files = []
        try:
            for f in os.listdir(current_dir):
                full_path = os.path.join(current_dir, f)
                if os.path.isfile(full_path):
                    ext = os.path.splitext(f)[1].lower()
                    if ext in extensions or '.' in f:
                        files.append(full_path)
            files.sort(key=lambda x: os.path.basename(x).lower())
        except Exception:
            pass
        return files

    def navigate_file_menu(self, direction=1):
        """Navigate file menu."""
        if not self.file_menu_files:
            return
        if len(self.file_menu_files) == 0:
            return
        self.file_menu_idx = (self.file_menu_idx + direction) % len(self.file_menu_files)
        self._ensure_menu_visible()

    def _ensure_menu_visible(self):
        """Ensure selected file is visible in menu."""
        if self.file_menu_idx < self.file_menu_scroll:
            self.file_menu_scroll = self.file_menu_idx
        elif self.file_menu_idx >= self.file_menu_scroll + 10:
            self.file_menu_scroll = self.file_menu_idx - 10

    def select_file_in_menu(self, stdscr):
        """Select file from menu and open it."""
        if not self.file_menu_files:
            return
        selected_file = self.file_menu_files[self.file_menu_idx]
        # Check if file already open in a buffer
        for i, buf in enumerate(self.buffers):
            if buf.filename and os.path.abspath(buf.filename) == os.path.abspath(selected_file):
                self._sync_to_buffer()
                self.buffer_idx = i
                self._sync_from_buffer()
                self.file_menu_visible = False
                self.message = f"Opened: {os.path.basename(selected_file)}"
                return
        # Open in new buffer
        self._sync_to_buffer()
        self.buffers.append(Buffer(selected_file))
        self.buffer_idx = len(self.buffers) - 1
        self._sync_from_buffer()
        self.save_undo()
        self.file_menu_visible = False
        self.message = f"Opened: {os.path.basename(selected_file)}"

    def draw_file_menu(self, stdscr):
        """Draw file menu on the left side."""
        if not self.file_menu_visible or not self.file_menu_files:
            return
        
        max_y, max_x = stdscr.getmaxyx()
        menu_width = min(30, max_x - 5)
        menu_height = min(12, max_y - 4)
        menu_x = 2
        menu_y = 2
        
        # Draw menu border
        try:
            # Top border
            stdscr.addstr(menu_y, menu_x, "┌" + "─" * menu_width + "┐")
            # Title
            title = " Files "
            stdscr.addstr(menu_y, menu_x + (menu_width - len(title)) // 2, title, curses.A_BOLD)
            
            # Bottom border
            stdscr.addstr(menu_y + menu_height + 1, menu_x, "└" + "─" * menu_width + "┘")
            
            # File list
            for i in range(menu_height):
                file_idx = self.file_menu_scroll + i
                if file_idx >= len(self.file_menu_files):
                    break
                file_path = self.file_menu_files[file_idx]
                file_name = os.path.basename(file_path)
                if len(file_name) > menu_width - 2:
                    file_name = file_name[:menu_width - 5] + "..."
                
                is_selected = file_idx == self.file_menu_idx
                is_current = self.buffers[self.buffer_idx].filename and \
                            os.path.abspath(self.buffers[self.buffer_idx].filename) == os.path.abspath(file_path)
                
                if is_selected:
                    attr = curses.A_REVERSE | curses.A_BOLD
                elif is_current:
                    attr = curses.color_pair(4) | curses.A_BOLD
                else:
                    attr = 0
                
                stdscr.addstr(menu_y + 1 + i, menu_x + 2, file_name.ljust(menu_width - 2), attr)
            
            # Footer
            stdscr.addstr(menu_y + menu_height + 1, menu_x + 2, "Enter=open, Esc=close")
        except curses.error:
            pass
        
        stdscr.refresh()

    def close_current_file(self):
        """Close current file (for double-click behavior)."""
        if not self.buffers:
            return
        self._sync_to_buffer()
        del self.buffers[self.buffer_idx]
        if not self.buffers:
            self.buffers.append(Buffer())
            self.buffer_idx = 0
        else:
            if self.buffer_idx >= len(self.buffers):
                self.buffer_idx = len(self.buffers) - 1
        self._sync_from_buffer()
        self.message = "File closed"

    def open_file_new_buffer(self, stdscr):
        """Open a file in a new buffer/tab."""
        new_name = self.prompt(stdscr, "Open File: ")
        if not new_name:
            self.message = "Cancelled"
            return
        if not os.path.exists(new_name):
            self.message = f"File not found: {new_name}"
            return
        self._sync_to_buffer()
        b = Buffer(new_name)
        self.buffers.append(b)
        self.buffer_idx = len(self.buffers) - 1
        self._sync_from_buffer()
        self.save_undo()
        self.message = f"Opened: {self.filename}"

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
            self.message = "Undone"
        else:
            self.message = "Nothing to undo"

    def redo(self):
        if self.redo_stack:
            lines, cy, cx = self.redo_stack.pop()
            self.undo_stack.append((lines.copy(), cy, cx))
            self.lines = lines.copy()
            self.cursor_y, self.cursor_x = cy, cx
            self.dirty = True
            self.message = "Redone"
        else:
            self.message = "Nothing to redo"

    # ─── File ─────────────────────────────────────────────

    def save(self, stdscr=None):
        if not self.filename:
            if stdscr:
                self.save_as(stdscr)
            else:
                self.message = "No filename — use Ctrl+W (Save As)"
            return
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.lines))
            self.dirty = False
            self.buffers[self.buffer_idx].dirty = False
            self.message = "Saved"
        except Exception as e:
            self.message = f"Save error: {e}"

    def save_as(self, stdscr):
        new_name = self.prompt(stdscr, "Save As: ")
        if not new_name:
            self.message = "Cancelled"
            return
        self.filename = new_name
        self.buffers[self.buffer_idx].filename = new_name
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.lines))
            self.dirty = False
            self.buffers[self.buffer_idx].dirty = False
            self.message = f"Saved as {self.filename}"
        except Exception as e:
            self.message = f"Save error: {e}"

    def open_file(self, stdscr):
        self.open_file_new_buffer(stdscr)

    def new_file(self):
        self.new_buffer()

    # ─── Editing ───────────────────────────────────

    BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}", "\"": "\"", "'": "'"}

    def _get_indent(self, line):
        """Returns the current line indentation in spaces."""
        stripped = line.lstrip(" ")
        return len(line) - len(stripped)

    def _should_increase_indent(self, line):
        """Checks if indentation should be increased (ends with : or { or [)."""
        stripped = line.rstrip()
        if not stripped:
            return False
        return stripped[-1] in ":{["

    def insert_char(self, ch):
        self.save_undo()
        line = self.lines[self.cursor_y]
        
        # smart behavior for closing brackets/quotes
        if ch in ')]}':
            after_cursor = line[self.cursor_x:self.cursor_x + 1] if self.cursor_x < len(line) else ""
            if after_cursor == ch:
                # just move cursor forward
                self.cursor_x += 1
                self.dirty = True
                return
        elif ch in ('"', "'"):
            # for quotes - if same quote under cursor, just move
            after_cursor = line[self.cursor_x:self.cursor_x + 1] if self.cursor_x < len(line) else ""
            if after_cursor == ch:
                self.cursor_x += 1
                self.dirty = True
                return
        
        # auto-close brackets/quotes - only if no closing symbol after
        if ch in self.BRACKET_PAIRS:
            closing = self.BRACKET_PAIRS[ch]
            # check if closing symbol already after cursor
            after_cursor = line[self.cursor_x:self.cursor_x + 1] if self.cursor_x < len(line) else ""
            if after_cursor != closing:
                # insert bracket pair
                self.lines[self.cursor_y] = (
                    line[: self.cursor_x] + ch + closing + line[self.cursor_x :]
                )
                self.cursor_x += 1  # place cursor between brackets
            else:
                self.lines[self.cursor_y] = line[: self.cursor_x] + ch + line[self.cursor_x :]
                self.cursor_x += len(ch)
        else:
            self.lines[self.cursor_y] = line[: self.cursor_x] + ch + line[self.cursor_x :]
            self.cursor_x += len(ch)
        self.dirty = True

    def insert_newline(self):
        self.save_undo()
        line = self.lines[self.cursor_y]
        before = line[: self.cursor_x]
        after = line[self.cursor_x :]

        # determine base indentation
        current_indent = self._get_indent(line)
        new_indent = current_indent

        # if line ends with {, [ or : - increase indentation
        if self._should_increase_indent(before):
            new_indent += 4

        # if only closing bracket after cursor - create intermediate line
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
        # remove up to 4 spaces before cursor
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

    def kill_line(self):
        """Delete current line (Ctrl+K). Copies to clipboard."""
        if len(self.lines) == 1 and self.lines[0] == "":
            self.message = "Nothing to delete"
            return
        self.save_undo()
        text = self.lines[self.cursor_y]
        # copy to clipboard
        if HAS_PYPERCLIP:
            try:
                pyperclip.copy(text)
            except Exception:
                if not IS_WINDOWS:
                    linux_clipboard_set(text)
        elif not IS_WINDOWS:
            linux_clipboard_set(text)
        self.clipboard = [text]
        del self.lines[self.cursor_y]
        if not self.lines:
            self.lines = [""]
            self.cursor_y = 0
        else:
            if self.cursor_y >= len(self.lines):
                self.cursor_y = len(self.lines) - 1
        self.cursor_x = 0
        self.dirty = True
        self.message = "Line deleted"

    # ─── Clipboard ─────────────────────────────────────

    def copy(self):
        text = self.lines[self.cursor_y]
        if HAS_PYPERCLIP:
            try:
                pyperclip.copy(text)
            except Exception:
                # Fallback to Linux clipboard
                if not IS_WINDOWS:
                    linux_clipboard_set(text)
        elif not IS_WINDOWS:
            linux_clipboard_set(text)
        self.clipboard = [text]
        self.message = "Line copied"

    def cut(self):
        if len(self.lines) == 1 and self.lines[0] == "":
            self.message = "Nothing to cut"
            return
        self.save_undo()
        text = self.lines[self.cursor_y]
        if HAS_PYPERCLIP:
            try:
                pyperclip.copy(text)
            except Exception:
                if not IS_WINDOWS:
                    linux_clipboard_set(text)
        elif not IS_WINDOWS:
            linux_clipboard_set(text)
        self.clipboard = [text]
        del self.lines[self.cursor_y]
        if not self.lines:
            self.lines = [""]
        if self.cursor_y >= len(self.lines):
            self.cursor_y = len(self.lines) - 1
        self.cursor_x = 0
        self.dirty = True
        self.message = "Line cut"

    def paste(self):
        self.save_undo()
        clip_text = None

        if HAS_PYPERCLIP:
            try:
                clip_text = pyperclip.paste()
            except Exception:
                pass
        
        if not clip_text and not IS_WINDOWS:
            clip_text = linux_clipboard_get()
        
        if clip_text:
            self.clipboard = clip_text.split("\n")
        
        if not self.clipboard:
            self.message = "Clipboard empty"
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
        self.message = "Pasted"

    # ─── Autocomplete ─────────────────────────────────────

    def _get_word_prefix(self):
        line = self.lines[self.cursor_y]
        x = self.cursor_x
        start = x
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1
        return line[start:x], start

    def _collect_words(self):
        """Collect all words from current file."""
        words = set()
        for line in self.lines:
            for m in re.finditer(r"[a-zA-Z_]\w*", line):
                words.add(m.group())
        return words

    def _get_all_completions(self, prefix):
        """Get all possible completions for prefix (keywords + file words)."""
        if not prefix or len(prefix) < 1:
            return []
        
        # Get language keywords and builtins
        lang_keywords, _ = get_language_keywords(self.filename)
        
        # Collect words from current file
        file_words = self._collect_words()
        
        # Combine and filter
        all_words = set(lang_keywords) | file_words
        matches = [w for w in all_words if w.startswith(prefix) and w != prefix]
        
        # Sort: file words first (alphabetically), then keywords
        file_word_set = set(file_words)
        keyword_set = set(lang_keywords)
        
        file_matches = sorted([w for w in matches if w in file_word_set])
        keyword_matches = sorted([w for w in matches if w in keyword_set and w not in file_word_set])
        
        return file_matches + keyword_matches

    def _update_auto_complete(self, stdscr):
        """Check if auto-complete should be shown after delay."""
        import time
        current_time = time.time()
        
        # Only trigger if:
        # 1. Completion not already visible
        # 2. We have a valid prefix (at least 2 chars)
        # 3. 5 seconds have passed since last activity
        if self.completion_visible:
            return
        
        if not self._pending_completion:
            return
        
        if current_time - self._last_activity_time < self._auto_complete_delay:
            return
        
        # Show auto-complete
        prefix = self._completion_prefix
        if len(prefix) < 2:
            self._pending_completion = False
            return
        
        matches = self._get_all_completions(prefix)
        
        if matches:
            self.completions = matches[:20]  # Limit to 20 suggestions
            self.completion_idx = 0
            self.completion_visible = True
            self._pending_completion = False
            self._draw_completion_popup(stdscr)

    def _reset_auto_complete_timer(self):
        """Reset the auto-complete timer on user activity."""
        import time
        self._last_activity_time = time.time()
        self._pending_completion = False
        self._completion_prefix = ""

    def _check_and_start_auto_complete(self):
        """Check if we should start tracking for auto-complete."""
        prefix, start_x = self._get_word_prefix()
        if len(prefix) >= 2:
            self._pending_completion = True
            self._completion_prefix = prefix
            self._completion_start_x = start_x
        else:
            self._pending_completion = False

    def _update_completion_suggestions(self, stdscr):
        """Update completion suggestions immediately (for responsive UX)."""
        if not self._pending_completion:
            return
        
        prefix = self._completion_prefix
        if len(prefix) < 2:
            return
        
        # If cursor moved away from the word, stop tracking
        current_prefix, _ = self._get_word_prefix()
        if current_prefix != prefix:
            self._pending_completion = False
            self.completion_visible = False
            self.completions = []
            return
        
        # Only show if completion not already visible or prefix changed
        if self.completion_visible:
            # Update existing suggestions if prefix changed
            if self._completion_prefix != prefix:
                matches = self._get_all_completions(prefix)
                if matches:
                    self.completions = matches[:20]
                    self.completion_idx = 0
                    self._draw_completion_popup(stdscr)
            return
        
        # Show new suggestions
        matches = self._get_all_completions(prefix)
        if matches:
            self.completions = matches[:20]
            self.completion_idx = 0
            self.completion_visible = True
            self._draw_completion_popup(stdscr)

    def show_completions(self, stdscr):
        """Show completions for current word prefix (manual trigger)."""
        prefix, start_x = self._get_word_prefix()
        matches = self._get_all_completions(prefix)
        
        if not matches:
            self.message = "No completions"
            self.completion_visible = False
            return
        
        self.completions = matches[:20]
        self.completion_idx = 0
        self.completion_visible = True
        self._draw_completion_popup(stdscr)

    def _draw_completion_popup(self, stdscr):
        """Draw the autocomplete popup menu."""
        if not self.completions:
            return
            
        max_y, max_x = stdscr.getmaxyx()
        line_num_width = 6
        gutter = 1
        code_x = line_num_width + gutter
        
        # Calculate popup position
        popup_y = self.cursor_y - self.scroll_y + 1
        popup_x = code_x + (self.cursor_x - self.scroll_x)
        
        # Protection against going out of screen bounds
        if popup_x < 0:
            popup_x = 0
        if popup_x >= max_x - 15:
            popup_x = max_x - 15
            if popup_x < 0:
                popup_x = 0
        
        popup_h = min(len(self.completions), 8)
        popup_w = min(max(len(w) for w in self.completions) + 4, max_x - popup_x - 2) if self.completions else 10
        if popup_h < 1:
            popup_h = 1
        
        # Adjust position if popup goes below screen
        if popup_y + popup_h >= max_y - 2:
            popup_y = max(0, self.cursor_y - self.scroll_y - popup_h - 1)
        if popup_y < 0:
            popup_y = 0
        
        # Draw popup border
        try:
            # Top border
            stdscr.addstr(popup_y, popup_x, "┌" + "─" * (popup_w - 2) + "┐")
            
            # Completion items
            for i in range(popup_h):
                if i < len(self.completions):
                    word = self.completions[i]
                    display = word[:popup_w - 3]
                    if i == self.completion_idx:
                        attr = curses.A_REVERSE | curses.A_BOLD
                        try:
                            stdscr.addstr(popup_y + 1 + i, popup_x + 1, display.ljust(popup_w - 2), attr)
                        except curses.error:
                            pass
                    else:
                        try:
                            stdscr.addstr(popup_y + 1 + i, popup_x + 1, display.ljust(popup_w - 2))
                        except curses.error:
                            pass
            
            # Bottom border
            stdscr.addstr(popup_y + popup_h + 1, popup_x, "└" + "─" * (popup_w - 2) + "┘")
            
            # Helper text
            help_text = "↑↓ select, Enter accept, Esc close"
            if len(help_text) < popup_w - 2:
                try:
                    stdscr.addstr(popup_y + popup_h + 1, popup_x + 1, help_text[:popup_w - 3])
                except curses.error:
                    pass
        except curses.error:
            pass
        
        stdscr.refresh()

    def cycle_completion(self, stdscr, direction=1):
        if not self.completion_visible or not self.completions:
            return
        self.completion_idx = (self.completion_idx + direction) % len(self.completions)
        self._draw_completion_popup(stdscr)

    def accept_completion(self):
        if not self.completion_visible or not self.completions:
            return
        prefix, start_x = self._get_word_prefix()
        chosen = self.completions[self.completion_idx]
        line = self.lines[self.cursor_y]
        self.lines[self.cursor_y] = line[:start_x] + chosen + line[self.cursor_x:]
        self.cursor_x = start_x + len(chosen)
        self.dirty = True
        self.completion_visible = False
        self.completions = []

    # ─── Search / Goto ────────────────────────────────────

    def prompt(self, stdscr, prompt_text):
        max_y, max_x = stdscr.getmaxyx()
        if max_x < len(prompt_text) + 5:
            self.message = "Terminal too small for input"
            return None
        s = ""
        while True:
            line = (prompt_text + s)[: max_x - 1]
            try:
                stdscr.addstr(max_y - 1, 0, line, curses.color_pair(1))
                stdscr.clrtoeol()
                stdscr.refresh()
            except curses.error:
                pass
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
        query = self.prompt(stdscr, "Find: ")
        if query is None:
            self.message = "Search cancelled"
            return
        if not query:
            self.message = "Empty search"
            return
        if not self.lines or (len(self.lines) == 1 and not self.lines[0]):
            self.message = "No content to search"
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
                self.message = f"Found: line {idx + 1}"
                return
        self.message = "Not found"

    def goto(self, stdscr):
        s = self.prompt(stdscr, "Go to line: ")
        if not s:
            return
        try:
            num = int(s) - 1
            if 0 <= num < len(self.lines):
                self.cursor_y = num
                self.cursor_x = 0
                self.message = f"Line {num + 1}"
            else:
                self.message = f"Line {num + 1} out of range (1-{len(self.lines)})"
        except ValueError:
            self.message = "Invalid line number"

    def load_plugin_cmd(self, stdscr):
        if not self.plugin_manager:
            self.message = "Plugins not available. Install lupa: pip install lupa"
            return
        name = self.prompt(stdscr, "Load plugin: ")
        if not name:
            return
        self.message = self.plugin_manager.load_plugin(name)

    def unload_plugin_cmd(self, stdscr):
        if not self.plugin_manager:
            self.message = "Plugins not available"
            return
        name = self.prompt(stdscr, "Unload plugin: ")
        if not name:
            return
        self.message = self.plugin_manager.unload_plugin(name)

    def list_plugins_cmd(self, stdscr):
        if not self.plugin_manager:
            self.message = "Plugins not available"
            return
        available = self.plugin_manager.list_plugins()
        loaded = self.plugin_manager.list_loaded()
        self.message = f"Plugins: available={','.join(available)} loaded={','.join(loaded)}"

    # ─── Rendering ────────────────────────────────────────

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
            "SYMBOL": 14,
            "CONST": 7,
            "ANNOTATION": 11,
            "CMDLET": 4,
            "TAG": 3,
            "ATTR": 5,
            "ENTITY": 9,
            "SELECTOR": 6,
            "PROPERTY": 5,
            "VALUE": 8,
            "LABEL": 6,
            "DIRECTIVE": 11,
            "REGISTER": 7,
            "TYPE": 7,
            "HEREDOC": 8,
            "RUNE": 8,
            "RAWSTRING": 8,
            "DOC": 10,
            "LIFETIME": 5,
            "INTERPOLATION": 5,
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
            # part of token falls into visible area
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

        line_num_width = 6   # line number width
        gutter = 1           # space between number and code
        code_x = line_num_width + gutter
        text_width = max_x - code_x

        # adjust scrolling
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
            # completely clear line before rendering
            try:
                stdscr.move(i, 0)
                stdscr.clrtoeol()
            except curses.error:
                pass

            line_idx = self.scroll_y + i
            if line_idx >= len(self.lines):
                continue

            # line number (always draw for existing lines)
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

        # status bar - tabs + info
        tab_line = " | ".join(f"[{i+1}] {b.title}" for i, b in enumerate(self.buffers))
        if len(tab_line) > max_x - 1:
            # shorten if too long
            cur = self.buffers[self.buffer_idx]
            tab_line = f"[{self.buffer_idx+1}] {cur.title} ({len(self.buffers)} tabs)"
        status = (
            f"{tab_line} | "
            f"{'*' if self.dirty else ' '} {self.cursor_y + 1}:{self.cursor_x + 1} | {self.message}"
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
        
        # Draw file menu if visible
        self.draw_file_menu(stdscr)
        
        stdscr.refresh()

    # ─── Main Loop ─────────────────────────────────────

    def run(self, stdscr):
        import time
        curses.curs_set(1)
        stdscr.keypad(True)
        curses.start_color()
        curses.use_default_colors()
        # 1: status bar
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        # 2: line numbers
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        # 3: keywords
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        # 4: built-in functions
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # 5: self
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        # 6: function names
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        # 7: class names
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        # 8: strings
        curses.init_pair(8, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # 9: numbers
        curses.init_pair(9, curses.COLOR_CYAN, curses.COLOR_BLACK)
        # 10: comments
        curses.init_pair(10, curses.COLOR_RED, curses.COLOR_BLACK)
        # 11: decorators
        curses.init_pair(11, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        # 12: operators
        curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_BLACK)
        # 13: brackets
        curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_BLACK)
        # 14: variables/substitutions
        curses.init_pair(14, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        
        # Initialize last activity time
        self._last_activity_time = time.time()
        
        while True:
            self.draw(stdscr)
            
            # Draw completion popup if visible
            if self.completion_visible:
                self._draw_completion_popup(stdscr)
            
            # Non-blocking input with timeout for auto-complete
            # Wait up to 100ms for input, then check auto-complete
            stdscr.timeout(100)
            try:
                key = stdscr.get_wch()
            except (curses.error, KeyboardInterrupt):
                stdscr.nodelay(False)  # Block again
                # Check for auto-complete even on timeout
                self._update_auto_complete(stdscr)
                continue
            
            # Reset timeout to blocking after first keypress
            stdscr.timeout(-1)
            
            if isinstance(key, str):
                code = ord(key)
            else:
                code = key

            self.message = ""

            if code == curses.KEY_RESIZE:
                continue

            if code == 27:  # Esc
                self.completion_visible = False
                self.file_menu_visible = False
                self._kill_line_repeat = False
                continue

            # File menu specific handling
            if self.file_menu_visible:
                if code in (10, 13):  # Enter - select file
                    self.select_file_in_menu(stdscr)
                    continue
                elif code == curses.KEY_UP:
                    self.navigate_file_menu(-1)
                    continue
                elif code == curses.KEY_DOWN:
                    self.navigate_file_menu(1)
                    continue
                elif code == curses.KEY_RESIZE:
                    continue
                # Close menu on any other key
                self.file_menu_visible = False
                continue

            # Autocomplete navigation when visible
            if self.completion_visible:
                if code == curses.KEY_UP:
                    self.cycle_completion(stdscr, -1)
                    continue
                elif code == curses.KEY_DOWN:
                    self.cycle_completion(stdscr, 1)
                    continue
                elif code in (10, 13):  # Enter - accept completion
                    self.accept_completion()
                    continue
                elif code == 9:  # Tab - accept completion
                    self.accept_completion()
                    continue
                elif code == 27:  # Esc - already handled above
                    continue
                # Any other key closes completion and continues
                self.completion_visible = False

            # hide completion on most keys (except navigation)
            if code not in (0, 259, 258, 260, 261, 338, 339, 262, 360, 9):
                self.completion_visible = False
                # reset kill_line repeat for non-control keys
                if code != 11:  # 11 = Ctrl+K
                    self._kill_line_repeat = False

            # ── Quit ──
            if code == 17:  # Ctrl+Q
                if self.dirty:
                    if self._quit_confirm:
                        break
                    self.message = "Unsaved changes! Ctrl+Q again to quit, Ctrl+S to save"
                    self._quit_confirm = True
                    continue
                break
            self._quit_confirm = False

            # ── Tabs / Buffers ──
            if code == 20:  # Ctrl+T - new tab
                self.new_buffer()
            elif code == 23:  # Ctrl+W - close tab
                if not self.close_buffer(stdscr, force=self._quit_confirm):
                    pass  # waiting for confirmation
                self._quit_confirm = False
            elif code == curses.KEY_F1:  # F1 - prev tab
                self.switch_buffer(-1)
            elif code == curses.KEY_F2:  # F2 - next tab
                self.switch_buffer(1)
            # ── File ──
            elif code == 19:  # Ctrl+S
                self.save(stdscr)
            elif code == 14:  # Ctrl+N
                self.new_file()
            # ── Save As ──
            elif code == 18:  # Ctrl+R - save as
                self.save_as(stdscr)
            # ── Undo / Redo ──
            elif code == 26:  # Ctrl+Z
                self.undo()
            elif code == 25:  # Ctrl+Y
                self.redo()
            # ── Clipboard ──
            elif code == 3:  # Ctrl+C
                self.copy()
            elif code == 24:  # Ctrl+X
                self.cut()
            elif code == 22:  # Ctrl+V
                self.paste()
            elif code == 11:  # Ctrl+K - delete line (support repeat on hold)
                self._kill_line_repeat = True
                self.kill_line()
            elif code == 1:  # Ctrl+A
                self.message = f"Lines: {len(self.lines)}, Chars: {sum(len(l) for l in self.lines)}"
            # ── Autocomplete ──
            elif code == 0:  # Ctrl+Space
                if self.completion_visible:
                    self.accept_completion()
                else:
                    self.show_completions(stdscr)
            # ── File Menu ──
            elif code == 5:  # Ctrl+E - toggle file menu
                self.toggle_file_menu(stdscr)
            # ── Plugins ──
            elif code == 12:  # Ctrl+L - load plugin
                self.load_plugin_cmd(stdscr)
            elif code == 21:  # Ctrl+U - unload plugin
                self.unload_plugin_cmd(stdscr)
            elif code == 16:  # Ctrl+P - list plugins
                self.list_plugins_cmd(stdscr)
            # ── Navigation / Search ──
            elif code == 6:  # Ctrl+F
                self.find(stdscr)
            elif code == 7:  # Ctrl+G
                self.goto(stdscr)
            # ─── Special keys ──
            elif code == 9:  # Tab
                if not self.completion_visible:
                    self.indent()
                else:
                    self.accept_completion()
            elif code == 353:  # Shift+Tab (KEY_BTAB)
                self.unindent()
            elif code in (curses.KEY_BACKSPACE, 8, 127):
                self.backspace()
            elif code == curses.KEY_DC:
                self.delete()
            elif code in (10, 13):
                if self.completion_visible:
                    self.accept_completion()
                else:
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
                if self.completion_visible:
                    self.cycle_completion(stdscr, -1)
                elif self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            elif code == curses.KEY_DOWN:
                if self.completion_visible:
                    self.cycle_completion(stdscr, 1)
                elif self.cursor_y < len(self.lines) - 1:
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
            # ── Printable characters (including Unicode) ──
            elif isinstance(key, str) and code >= 32 and code != 127:
                self.insert_char(key)
                # Check if we should start auto-complete tracking
                self._check_and_start_auto_complete()
                # Update completion suggestions immediately for better UX
                if self._pending_completion:
                    self._update_completion_suggestions(stdscr)


# ─── Plugin API methods (monkey-patched at runtime) ───

def _editor_insert_text(self, text):
    self.save_undo()
    line = self.lines[self.cursor_y]
    self.lines[self.cursor_y] = line[:self.cursor_x] + text + line[self.cursor_x:]
    self.cursor_x += len(text)
    self.dirty = True


def _editor_get_line(self, y=None):
    if y is None:
        y = self.cursor_y
    return self.lines[y] if 0 <= y < len(self.lines) else ""


def _editor_set_line(self, y, text):
    if 0 <= y < len(self.lines):
        self.save_undo()
        self.lines[y] = text
        self.dirty = True


def _editor_get_cursor(self):
    return (self.cursor_y, self.cursor_x)


def _editor_set_cursor(self, y, x):
    self.cursor_y = max(0, min(y, len(self.lines) - 1))
    self.cursor_x = max(0, min(x, len(self.lines[self.cursor_y])))


def _editor_get_text(self):
    return "\n".join(self.lines)


def _editor_set_text(self, text):
    self.save_undo()
    self.lines = text.split("\n") if text else [""]
    self.cursor_y = 0
    self.cursor_x = 0
    self.dirty = True


Editor.insert_text = _editor_insert_text
Editor.get_line = _editor_get_line
Editor.set_line = _editor_set_line
Editor.get_cursor = _editor_get_cursor
Editor.set_cursor = _editor_set_cursor
Editor.get_text = _editor_get_text
Editor.set_text = _editor_set_text


def main():
    filenames = sys.argv[1:] if len(sys.argv) > 1 else None
    
    # Check for curses support
    try:
        editor = Editor(filenames)
        curses.wrapper(editor.run)
    except curses.error as e:
        print(f"Curses error: {e}")
        print("Make sure your terminal supports curses and has sufficient size.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

