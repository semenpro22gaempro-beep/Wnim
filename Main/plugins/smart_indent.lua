-- Smart Indent Plugin for WNim
-- Adds multi-line indent/unindent with Ctrl+M / Alt+U
-- Also adds duplicate line with Ctrl+D

local plugin = {}

function plugin.on_load(api)
    api.editor.message("Smart Indent loaded. Ctrl+M=indent, Alt+U=unindent, Ctrl+D=duplicate")
end

function plugin.on_unload()
    -- Cleanup if needed
end

-- Indent current line or selection
function plugin.indent_line(api)
    local y, x = api.editor.get_cursor()
    local line = api.editor.get_line(y)
    
    -- Add 4 spaces at current position
    local new_line = string.sub(line, 1, x) .. "    " .. string.sub(line, x + 1)
    api.editor.set_line(y, new_line)
    
    -- Move cursor
    api.editor.set_cursor(y, x + 4)
end

-- Unindent current line or selection
function plugin.unindent_line(api)
    local y, x = api.editor.get_cursor()
    local line = api.editor.get_line(y)
    
    -- Remove up to 4 spaces before cursor
    local spaces_to_remove = 0
    for i = x, math.max(1, x - 4), -1 do
        if string.sub(line, i, i) == " " then
            spaces_to_remove = spaces_to_remove + 1
        else
            break
        end
    end
    
    if spaces_to_remove > 0 then
        local new_line = string.sub(line, 1, x - spaces_to_remove) .. string.sub(line, x + 1)
        api.editor.set_line(y, new_line)
        api.editor.set_cursor(y, x - spaces_to_remove)
    end
end

-- Duplicate current line
function plugin.duplicate_line(api)
    local y, x = api.editor.get_cursor()
    local line = api.editor.get_line(y)
    
    -- Insert copied line below
    api.editor.set_cursor(y + 1, 0)
    api.editor.insert_text(line .. "\n")
    
    -- Return to original position
    api.editor.set_cursor(y, x)
end

-- Key handler
function plugin.on_key(code)
    -- Ctrl+M = indent
    if code == 13 then
        plugin.indent_line(_G.plugin_api)
        return true
    end
    
    -- Ctrl+] = unindent (code 29) - changed from Ctrl+U to avoid conflict with unload plugin
    if code == 29 then
        local y, x = _G.plugin_api.editor.get_cursor()
        local line = _G.plugin_api.editor.get_line(y)
        -- Check if there are spaces to remove
        local has_spaces = false
        for i = x, math.max(1, x - 4), -1 do
            if i >= 1 and string.sub(line, i, i) == " " then
                has_spaces = true
                break
            end
        end
        if has_spaces then
            plugin.unindent_line(_G.plugin_api)
            return true
        end
    end
    
    -- Ctrl+D = duplicate line
    if code == 4 then
        plugin.duplicate_line(_G.plugin_api)
        return true
    end
    
    return false
end

-- Export functions for manual calling
plugin.indent = function()
    plugin.indent_line(_G.plugin_api)
end

plugin.unindent = function()
    plugin.unindent_line(_G.plugin_api)
end

plugin.duplicate = function()
    plugin.duplicate_line(_G.plugin_api)
end

return plugin
