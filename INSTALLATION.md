# Loom Addon Installation Guide

## Quick Start

### Prerequisites
- Blender 5.0 or newer
- The `loom_addon.zip` file (81 KB)

### Installation Steps

1. **Open Blender 5.0+**

2. **Open Preferences**
   - Go to `Edit` → `Preferences`
   - Or press `F4` and search for "Preferences"

3. **Navigate to Add-ons**
   - Click on the `Add-ons` tab in the left sidebar

4. **Install the Addon**
   - Click the `Install...` button at the top right
   - Navigate to and select `loom_addon.zip`
   - Click `Install Add-on`

5. **Enable the Addon**
   - Search for "Loom" in the add-ons search box
   - Check the checkbox next to "Render: Loom"
   - The addon is now active!

6. **Verify Installation**
   - Check the console (Window → Toggle System Console on Windows, or check Terminal on macOS)
   - Look for the Loom menu under `Render` in the top menu bar
   - Press `Ctrl+Shift+F12` to test the render dialog

## Accessing Loom Features

### Main Menu
- **Render Menu** → `Loom`
  - Loom Render Dialog
  - Batch Render and Encode
  - Render Flipbook
  - Encode Image Sequence
  - Rename Sequences
  - Open Output Folder

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+F12` | Loom Render Dialog |
| `Ctrl+Shift+Alt+F12` | Batch Render Dialog |
| `Ctrl+Shift+F10` | Render Flipbook |
| `Ctrl+Shift+F11` | Playblast (if enabled) |
| `Ctrl+Shift+F9` | Encode Dialog |
| `Ctrl+Shift+F3` | Open Output Folder |
| `Ctrl+Shift+F2` | Rename Dialog |
| `Ctrl+Shift+F1` | Project Dialog |

**Note:** On macOS, you can also use `Cmd+Shift` instead of `Ctrl+Shift`

### Preferences

Access Loom preferences:
1. Open Blender Preferences (`Edit` → `Preferences`)
2. Go to `Add-ons` tab
3. Find and expand "Render: Loom"
4. Configure:
   - Global variables
   - Project directories
   - Terminal settings
   - Dialog width
   - Playblast option

### UI Integrations

Loom adds panels to several Blender areas:

1. **Output Properties**
   - Output path management
   - Version numbering
   - Compositor paths

2. **Render Presets Panel**
   - Save/load render settings
   - Customize preset flags

3. **Dopesheet Header**
   - Quick access to Loom features

4. **Marker Menus**
   - Timeline markers (Blender 4.x)
   - Dopesheet markers
   - NLA markers

## Troubleshooting

### Addon Won't Load
- **Check Blender version:** Loom requires Blender 5.0 or newer
- **Check console for errors:** Look for Python traceback messages
- **Verify zip integrity:** Re-download if necessary

### Missing Menu Items
- **Restart Blender:** Sometimes a restart is needed after installation
- **Check preferences:** Ensure the addon is enabled
- **Check console:** Look for registration errors

### Keyboard Shortcuts Don't Work
- **Check for conflicts:** Other addons might use the same shortcuts
- **Verify in preferences:** Check the keymap section in addon preferences
- **Try alternative shortcuts:** On macOS, try Cmd instead of Ctrl

### Features Not Working
- **Check dependencies:** Ensure FFmpeg is installed for video encoding
- **Verify paths:** Check output paths are valid
- **Console errors:** Check the system console for error messages

## Uninstallation

To remove Loom:

1. Open Blender Preferences (`Edit` → `Preferences`)
2. Go to `Add-ons` tab
3. Search for "Loom"
4. Click the `Remove` button
5. Restart Blender

## Getting Help

- **Documentation:** See [REFACTORING_PLAN.md](REFACTORING_PLAN.md) for architecture details
- **Status:** Check [STATUS.md](STATUS.md) for current features
- **Issues:** Report problems in the GitHub issue tracker

## Development

For developers wanting to modify or extend Loom:

- **Source structure:** See [README.md](README.md)
- **Architecture:** Read [REFACTORING_PLAN.md](REFACTORING_PLAN.md)
- **Task tracking:** Check [REFACTORING_TASKS.md](REFACTORING_TASKS.md)
- **Continuation guide:** See [CLAUDE.md](CLAUDE.md)

## License

Loom is licensed under **GNU General Public License v2.0**

See license headers in source files for details.

## Credits

- **Original Author:** Christian Brinkmann (p2or)
- **Original Repository:** [blender-loom](https://github.com/p2or/blender-loom)
- **Refactoring:** Modular architecture refactoring for Blender 5.0

---

**Version:** Refactored for Blender 5.0
**Status:** 87.5% complete (testing phase)
**Last Updated:** 2025-12-12
