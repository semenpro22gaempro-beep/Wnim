# Creating Plugins for WNim

## Overview

WNim supports plugins written in the Lua language. Plugins extend the editor's functionality, allowing you to add custom commands and event handlers.

## Requirements

The `lupa` library is required for plugin support:

```powershell
pip install lupa
```

## Plugin Structure

Plugins are stored in the `plugins/` folder and must have the `.lua` extension.

Example plugin file structure:

```lua
local plugin = {}

function plugin.on_load(api)
    -- Called when the plugin is loaded
end

function plugin.on_unload()
    -- Called when the plugin is unloaded
end

function plugin.on_key(code)
    -- Called on every key press
    -- Returns true if the key is handled
end

return plugin
```

## Editor API

The plugin accesses the editor through the `api` object.

### Editor Methods

#### Insert Text
```lua
api.editor.insert_text(text)
```
Inserts text at the current cursor position.

#### Get Line
```lua
local line = api.editor.get_line(y)
```
Returns the content of line with index y. If y is not specified, returns the current line.

#### Set Line
```lua
api.editor.set_line(y, text)
```
Sets the content of line with index y.

#### Get Cursor Position
```lua
local y, x = api.editor.get_cursor()
```
Returns cursor coordinates (y, x).

#### Set Cursor Position
```lua
api.editor.set_cursor(y, x)
```
Sets cursor to position (y, x).

#### Get All Text
```lua
local text = api.editor.get_text()
```
Returns all text from the file.

#### Set All Text
```lua
api.editor.set_text(text)
```
Replaces all text in the file.

#### Display Message
```lua
api.editor.message("Message")
```
Displays a message in the status bar.

### Utilities

#### Case Conversion
```lua
local upper = api.utils.upper("text")
local lower = api.utils.lower("TEXT")
```

#### Reverse String
```lua
local reversed = api.utils.reverse("text")
```

#### Trim Whitespace
```lua
local trimmed = api.utils.trim("  text  ")
```

## Plugin Events

### on_load(api)
Called when the plugin is loaded. Use this to initialize variables or register handlers.

```lua
function plugin.on_load(api)
    api.editor.message("Plugin loaded")
end
```

### on_unload()
Called when the plugin is unloaded. Use this to clean up resources.

```lua
function plugin.on_unload()
    -- Cleanup
end
```

### on_key(code)
Called on every key press. The code parameter is the key code. Return true if the key should be handled and not passed further.

```lua
function plugin.on_key(code)
    if code == 65 then  -- Ctrl+A
        api.editor.message("Ctrl+A pressed")
        return true
    end
    return false
end
```

## Plugin Examples

### Example 1: Greeting

```lua
local plugin = {}

function plugin.on_load(api)
    api.editor.message("Greeting plugin loaded")
end

function plugin.greet()
    local api = _G.plugin_api
    api.editor.insert_text("Hello, World!")
end

return plugin
```

### Example 2: Case Conversion

```lua
local plugin = {}

function plugin.on_load(api)
    api.editor.message("Case conversion plugin loaded")
end

function plugin.to_upper()
    local api = _G.plugin_api
    local text = api.editor.get_text()
    api.editor.set_text(api.utils.upper(text))
end

function plugin.to_lower()
    local api = _G.plugin_api
    local text = api.editor.get_text()
    api.editor.set_text(api.utils.lower(text))
end

return plugin
```

### Example 3: Key Handling

```lua
local plugin = {}

function plugin.on_load(api)
    api.editor.message("Key handling plugin loaded")
end

function plugin.on_key(code)
    -- Enter key
    if code == 10 then
        local api = _G.plugin_api
        api.editor.message("Enter pressed")
        return false
    end
    return false
end

return plugin
```

## Plugin Management

### In the Editor

- `Ctrl+L` - load plugin (enter name without .lua extension)
- `Ctrl+U` - unload plugin (enter name)
- `Ctrl+P` - show list of available and loaded plugins

### Auto-load

To automatically load plugins on editor startup, add their names to the configuration file:

```json
{
    "plugins_auto_load": ["plugin1", "plugin2"]
}
```

## Accessing API from Plugin

The global variable `_G.plugin_api` contains the current editor API. It is set automatically when the plugin is loaded.

```lua
function plugin.some_function()
    local api = _G.plugin_api
    -- Use api here
end
```

## Debugging Plugins

Use the `print()` function for debugging:

```lua
function plugin.on_load(api)
    print("Plugin loaded")
    api.editor.message("See output in console")
end
```

## Limitations

- Plugins run in an isolated Lua environment
- File system access is limited
- Blocking operations are not recommended

## Extending Functionality

To add new functions to the editor API, modify `editor.py` and add corresponding methods to the plugin API object.
