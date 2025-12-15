# Loom Addon - Installation Instructions

## Package Information

**File:** `loom-addon.zip` (80 KB)
**Version:** 0.9.5
**Blender Compatibility:** 5.0.0+
**Build Date:** 2025-12-14

## Quick Install

### Method 1: Install via Blender Preferences (Recommended)

1. **Open Blender 5.0** or later

2. **Open Preferences:**
   - Go to: `Edit` > `Preferences` (or `Blender` > `Preferences` on macOS)

3. **Go to Add-ons section:**
   - Click the `Add-ons` tab on the left

4. **Install the ZIP file:**
   - Click the `Install...` button at the top right
   - Navigate to and select `loom-addon.zip`
   - Click `Install Add-on`

5. **Enable the addon:**
   - Search for "Loom" in the add-ons list
   - Check the checkbox next to "Render: Loom"
   - The addon is now active!

### Method 2: Manual Installation

1. **Extract the ZIP file:**
   ```bash
   unzip loom-addon.zip
   ```

2. **Locate your Blender scripts folder:**
   - **Windows:** `%APPDATA%\Blender Foundation\Blender\5.0\scripts\addons\`
   - **macOS:** `~/Library/Application Support/Blender/5.0/scripts/addons/`
   - **Linux:** `~/.config/blender/5.0/scripts/addons/`

3. **Copy the `loom` folder:**
   - Copy the entire `loom` folder into the `addons` directory

4. **Restart Blender** and enable the addon in Preferences

## Verification

After installation, verify the addon is working:

1. **Check the Render Menu:**
   - Go to: `Render` menu in the top menu bar
   - You should see a "Loom" submenu

2. **Test the Render Dialog:**
   - Press `Ctrl+Shift+F12` (or `Cmd+Shift+F12` on macOS)
   - The Loom render dialog should open

3. **Check Preferences:**
   - Open: `Edit` > `Preferences` > `Add-ons`
   - Find "Loom" and expand it
   - You should see the addon preferences panel

## Keyboard Shortcuts

Once installed, these shortcuts are available:

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+F12` | Open Render Dialog |
| `Ctrl+Shift+F11` | Playblast |
| `Ctrl+Shift+F10` | Render Flipbook |
| `Ctrl+Shift+F9` | Encode Dialog |
| `Ctrl+Shift+F3` | Open Output Folder |
| `Ctrl+Shift+F2` | Rename Dialog |
| `Ctrl+Shift+F1` | Project Dialog |

*On macOS, use `Cmd` instead of `Ctrl`*

## Features

- **Image Sequence Rendering:** Render and manage image sequences
- **Batch Rendering:** Render multiple scenes or view layers
- **Encoding:** Encode image sequences to video formats
- **Playblast:** Quick preview rendering
- **Global Variables:** Use dynamic variables in file paths
- **Version Management:** Automatic version numbering
- **Preset System:** Save and load render settings

## Troubleshooting

### Addon Won't Enable

1. **Check Blender Version:**
   - This addon requires Blender 5.0 or later
   - Check: `Help` > `About Blender`

2. **Check the Console:**
   - Windows: `Window` > `Toggle System Console`
   - macOS/Linux: Run Blender from terminal to see output
   - Look for error messages when enabling the addon

3. **Common Errors:**
   - If you see import errors, make sure the entire `loom` folder was installed
   - Check that all files are present (28 Python files)

### Addon Loads but Features Don't Work

1. **Check Preferences:**
   - Some features require configuration in addon preferences
   - Set up terminal path for external commands

2. **File Permissions:**
   - Make sure Blender has write permissions to output directories

3. **Report Issues:**
   - If problems persist, check: https://github.com/p2or/blender-loom/issues

## Uninstallation

1. **Disable the addon:**
   - `Edit` > `Preferences` > `Add-ons`
   - Find "Loom" and uncheck it

2. **Remove the addon:**
   - Click the `Remove` button next to the addon
   - Or manually delete the `loom` folder from the addons directory

## What's New in This Build

This refactored version includes:

- ✅ Improved code organization (modular structure)
- ✅ Better compatibility with Blender 5.0
- ✅ Fixed regex pattern warnings
- ✅ Resolved registration conflicts
- ✅ All import dependencies properly resolved

## Support

- **Documentation:** https://github.com/p2or/blender-loom
- **Issues:** https://github.com/p2or/blender-loom/issues
- **Original Author:** Christian Brinkmann (p2or)

---

**Build Info:**
- Date: 2025-12-14
- Python Files: 28
- Modules: 7 (helpers, properties, ui, operators, presets, handlers)
- Operators: 52
- Total Lines: ~6,300
