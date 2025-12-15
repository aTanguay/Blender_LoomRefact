# Loom Blender Addon - Refactored Version

**Version:** 0.9.5  
**Status:** ✅ Successfully Installed & Tested on Blender 5.0  
**Build Date:** 2025-12-14

---

## 🎉 Refactoring Complete!

This is a fully refactored version of the **Loom** addon, restructured from a single 6,358-line file into a clean, modular architecture with 28 Python files organized across 7 modules.

### Installation Status: ✅ VERIFIED

- ✅ Installs without errors
- ✅ Enables successfully in Blender 5.0
- ✅ Loom menu appears in Render menu
- ✅ All imports resolved
- ✅ All registration issues fixed

---

## 📦 Quick Install

1. **Download** `loom-addon.zip` (80 KB)
2. Open **Blender 5.0** or later
3. Go to **Edit → Preferences → Add-ons**
4. Click **Install...** and select the ZIP file
5. Enable **"Render: Loom"**
6. Done! Access via **Render → Loom** menu

---

## 📚 Documentation

All documentation is organized in the **[DOCS/](DOCS/)** directory:

- **[QUICK_TEST.md](QUICK_TEST.md)** - Quick command-line testing guide ⚡
- **[DOCS/BLENDER_CLI_SETUP.md](DOCS/BLENDER_CLI_SETUP.md)** - Setup Blender CLI access
- **[DOCS/INSTALLATION_INSTRUCTIONS.md](DOCS/INSTALLATION_INSTRUCTIONS.md)** - Complete installation guide
- **[DOCS/FIXES_APPLIED.md](DOCS/FIXES_APPLIED.md)** - All 7 fixes documented in detail
- **[DOCS/BUILD_SUMMARY.md](DOCS/BUILD_SUMMARY.md)** - Build overview and testing checklist
- **[DOCS/TESTING_PROGRESS.md](DOCS/TESTING_PROGRESS.md)** - Current testing status

See **[DOCS/README.md](DOCS/README.md)** for complete documentation index.

---

## ✨ Features

- **Image Sequence Rendering** - Render and manage sequences
- **Batch Rendering** - Multiple scenes/view layers
- **Video Encoding** - Encode sequences to video
- **Playblast** - Quick viewport previews
- **Global Variables** - Dynamic path variables
- **Version Management** - Auto version numbering
- **Render Presets** - Save/load settings
- **Project Structure** - Auto directory creation

---

## 🏗️ Architecture

28 Python files organized into 7 modules:
- `helpers/` - Utilities (4 files)
- `properties/` - Property groups (4 files)
- `ui/` - UI components (5 files)
- `operators/` - 52 operators (7 files)
- `presets/` - Preset system (2 files)
- `handlers/` - Event handlers (2 files)

---

## 🔧 Fixed Issues (7 Total)

1. ✅ Invalid regex escape sequences
2. ✅ Duplicate Scene.loom registration
3. ✅ Duplicate draw function registration
4. ✅ Missing import: LOOM_PG_generic_arguments
5. ✅ Missing import: LOOM_MT_render_presets
6. ✅ Missing import: ExportHelper
7. ✅ Incorrect EnumProperty callback signature

See **[DOCS/FIXES_APPLIED.md](DOCS/FIXES_APPLIED.md)** for details.

---

## 🤝 Credits

- **Original Author:** Christian Brinkmann (p2or)
- **Original Repository:** https://github.com/p2or/blender-loom
- **Refactoring Date:** December 2025

---

## 📄 License

GPL v2 or later

---

**Status:** Ready for comprehensive feature testing! 🚀
