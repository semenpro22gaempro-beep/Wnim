-- Theme Changer Plugin for WNim
-- Allows switching between predefined color themes
-- Hotkeys: Ctrl+1 = Dark, Ctrl+2 = Light, Ctrl+3 = Midnight, Ctrl+4 = Monokai, Ctrl+5 = Show current

local plugin = {}

-- Predefined themes
local themes = {
    dark = {
        name = "Dark",
        status_bar = {1, 7},      -- Black on White
        line_numbers = {6, 0},     -- Cyan on Black
        keywords = {5, 0},         -- Magenta on Black
        builtins = {2, 0},         -- Green on Black
        strings = {2, 0},          -- Green on Black
        numbers = {6, 0},          -- Cyan on Black
        comments = {1, 0},         -- Red on Black
        operators = {7, 0},        -- White on Black
        brackets = {7, 0},         -- White on Black
        variables = {3, 0},        -- Yellow on Black
    },
    light = {
        name = "Light",
        status_bar = {0, 7},       -- Black on White
        line_numbers = {4, 0},     -- Blue on Black
        keywords = {5, 0},         -- Magenta on Black
        builtins = {2, 0},         -- Green on Black
        strings = {3, 0},          -- Yellow on Black
        numbers = {6, 0},          -- Cyan on Black
        comments = {8, 0},         -- Grey on Black
        operators = {0, 0},        -- Black on Black
        brackets = {0, 0},         -- Black on Black
        variables = {1, 0},        -- Red on Black
    },
    midnight = {
        name = "Midnight",
        status_bar = {1, 4},       -- Black on Blue
        line_numbers = {6, 0},     -- Cyan on Black
        keywords = {5, 0},         -- Magenta on Black
        builtins = {14, 0},        -- Blue on Black
        strings = {10, 0},         -- Green on Black
        numbers = {11, 0},         -- Magenta on Black
        comments = {8, 0},         -- Grey on Black
        operators = {7, 0},        -- White on Black
        brackets = {7, 0},         -- White on Black
        variables = {14, 0},       -- Blue on Black
    },
    monokai = {
        name = "Monokai",
        status_bar = {1, 3},       -- Black on Magenta
        line_numbers = {11, 0},    -- Magenta on Black
        keywords = {11, 0},        -- Magenta on Black
        builtins = {10, 0},        -- Green on Black
        strings = {3, 0},          -- Yellow on Black
        numbers = {9, 0},          -- Cyan on Black
        comments = {8, 0},         -- Grey on Black
        operators = {12, 0},       -- White on Black
        brackets = {7, 0},         -- White on Black
        variables = {3, 0},        -- Yellow on Black
    },
}

local current_theme = "dark"

function plugin.on_load(api)
    current_theme = "dark"
    api.editor.message("Theme Changer loaded. Ctrl+1=Dark, Ctrl+2=Light, Ctrl+3=Midnight, Ctrl+4=Monokai, Ctrl+5=Show")
end

function plugin.on_unload()
    -- Reset to default if needed
end

-- Apply theme colors to curses
function plugin.apply_theme(api, theme_name)
    if not themes[theme_name] then
        api.editor.message("Theme not found: " .. theme_name)
        return false
    end
    
    local theme = themes[theme_name]
    current_theme = theme_name
    
    -- Note: This is a placeholder for theme application
    -- In a real implementation, you would need to modify editor.py
    -- to support dynamic color changes via plugin API
    
    api.editor.message("Theme changed to: " .. theme.name .. " (requires editor update)")
    return true
end

-- Get current theme name
function plugin.get_current_theme()
    return current_theme
end

-- List available themes
function plugin.list_themes()
    local theme_list = ""
    for name, theme in pairs(themes) do
        if theme_list ~= "" then
            theme_list = theme_list .. ", "
        end
        theme_list = theme_list .. theme.name
    end
    return theme_list
end

-- Key handler
function plugin.on_key(code)
    -- Ctrl+1 = Dark theme
    if code == 49 then  -- '1'
        plugin.apply_theme(_G.plugin_api, "dark")
        return true
    end
    
    -- Ctrl+2 = Light theme
    if code == 50 then  -- '2'
        plugin.apply_theme(_G.plugin_api, "light")
        return true
    end
    
    -- Ctrl+3 = Midnight theme
    if code == 51 then  -- '3'
        plugin.apply_theme(_G.plugin_api, "midnight")
        return true
    end
    
    -- Ctrl+4 = Monokai theme
    if code == 52 then  -- '4'
        plugin.apply_theme(_G.plugin_api, "monokai")
        return true
    end
    
    -- Ctrl+5 = Show current theme (changed from Ctrl+T to avoid conflict with new tab)
    if code == 53 then  -- '5'
        _G.plugin_api.editor.message("Current theme: " .. plugin.get_current_theme() .. " | Available: " .. plugin.list_themes())
        return true
    end
    
    return false
end

-- Export functions for manual calling
plugin.set_theme = function(theme_name)
    plugin.apply_theme(_G.plugin_api, theme_name)
end

plugin.show_current = function()
    _G.plugin_api.editor.message("Current theme: " .. plugin.get_current_theme())
end

plugin.show_available = function()
    _G.plugin_api.editor.message("Available themes: " .. plugin.list_themes())
end

return plugin
