"""WNim Plugin Manager - loads Lua plugins via lupa"""

import os
import sys
from pathlib import Path

try:
    from lupa import LuaRuntime
    HAS_LUPA = True
except Exception:
    HAS_LUPA = False


class PluginManager:
    def __init__(self, editor):
        self.editor = editor
        self.plugins = {}
        self.lua = None
        self.plugin_dir = Path(__file__).parent
        self._add_plugin_dir_to_path()
        if HAS_LUPA:
            self.lua = LuaRuntime(unpack_returned_tuples=True)

    def _add_plugin_dir_to_path(self):
        if str(self.plugin_dir) not in sys.path:
            sys.path.insert(0, str(self.plugin_dir))

    def load_plugin(self, name):
        if name in self.plugins:
            return f"Plugin {name} already loaded"

        lua_file = self.plugin_dir / f"{name}.lua"
        if not lua_file.exists():
            return f"Plugin file not found: {lua_file}"

        if not HAS_LUPA:
            return "lupa not installed. Run: pip install lupa"

        try:
            with open(lua_file, "r", encoding="utf-8") as f:
                lua_code = f.read()

            lua_globals = self.lua.globals()
            lua_globals.plugin_api = self._create_api()

            lua_module = self.lua.execute(lua_code)

            plugin = {
                "name": name,
                "lua_module": lua_module,
                "file": lua_file,
            }

            if hasattr(lua_module, "on_load"):
                lua_module.on_load(lua_globals.plugin_api)

            self.plugins[name] = plugin
            return f"Plugin {name} loaded"
        except Exception as e:
            return f"Error loading plugin {name}: {e}"

    def unload_plugin(self, name):
        if name not in self.plugins:
            return f"Plugin {name} not found"

        plugin = self.plugins[name]
        if hasattr(plugin["lua_module"], "on_unload"):
            try:
                plugin["lua_module"].on_unload()
            except Exception:
                pass

        del self.plugins[name]
        return f"Plugin {name} unloaded"

    def reload_plugin(self, name):
        self.unload_plugin(name)
        return self.load_plugin(name)

    def _create_api(self):
        ed = self.editor
        return self.lua.table_from({
            "editor": self.lua.table_from({
                "insert_text": ed.insert_text,
                "get_line": ed.get_line,
                "set_line": ed.set_line,
                "get_cursor": ed.get_cursor,
                "set_cursor": ed.set_cursor,
                "get_text": ed.get_text,
                "set_text": ed.set_text,
                "message": lambda msg: setattr(ed, "message", msg),
            }),
            "utils": self.lua.table_from({
                "upper": str.upper,
                "lower": str.lower,
                "reverse": lambda s: s[::-1],
                "trim": str.strip,
            })
        })

    def trigger_hook(self, hook_name, *args):
        results = []
        for name, plugin in self.plugins.items():
            mod = plugin["lua_module"]
            if hasattr(mod, hook_name):
                try:
                    result = getattr(mod, hook_name)(*args)
                    results.append((name, result))
                except Exception as e:
                    results.append((name, f"Error: {e}"))
        return results

    def list_plugins(self):
        return [f.stem for f in self.plugin_dir.glob("*.lua")]

    def list_loaded(self):
        return list(self.plugins.keys())