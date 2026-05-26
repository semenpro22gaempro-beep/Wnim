# WNim Plugins

This folder contains plugins for the WNim editor.

## Requirements

- **lupa** library: `pip install lupa`
- **Plugin files** must have `.lua` extension
- **Plugins** are loaded on demand or auto-loaded via config

## Cross-Platform Support

Plugins work on both Windows and Linux. The plugin API is identical across platforms.

## Available Plugins

### smart_indent.lua

Productivity plugin with text editing shortcuts:

- **Ctrl+M** - Indent current line (add 4 spaces)
- **Ctrl+U** - Unindent current line (remove 4 spaces)
- **Ctrl+D** - Duplicate current line

### theme_changer.lua

Theme switching plugin:

- **Ctrl+1** - Dark theme
- **Ctrl+2** - Light theme
- **Ctrl+3** - Midnight theme
- **Ctrl+4** - Monokai theme
- **Ctrl+T** - Show current theme

Note: Full theme support requires editor.py updates to expose color pair modification API.

See `plugins/README.md` for details.

## Creating Your Own Plugin

See `docs/plugins.md` for detailed documentation on creating custom plugins.

Basic structure:

```lua
local plugin = {}

function plugin.on_load(api)
    api.editor.message("Plugin loaded")
end

function plugin.on_unload()
    -- Cleanup
end

function plugin.on_key(code)
    -- Handle key presses
    return false  -- Return true to consume the key
end

return plugin
```

## Managing Plugins

In the editor:
- **Ctrl+L** - Load plugin
- **Ctrl+U** - Unload plugin
- **Ctrl+P** - List plugins

## Notes

- Plugins run in an isolated Lua environment
- Global variable `_G.plugin_api` provides access to editor functions
- Use `print()` for debugging
- Avoid blocking operations
