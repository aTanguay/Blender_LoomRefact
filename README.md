# Loom - Blender Image Sequence Renderer

[![Blender](https://img.shields.io/badge/Blender-5.0%2B-orange)](https://www.blender.org/)
[![GPL License](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](LICENSE)
[![Refactoring](https://img.shields.io/badge/Status-62.5%25%20Refactored-green)](STATUS.md)

Image sequence rendering, encoding and playback addon for Blender 5.0+

## 🚀 Project Status

This project is currently being **refactored from a monolithic single file** (6,358 lines) into a **maintainable multi-file structure**.

**Progress: 5/8 phases complete (62.5%)**

See [STATUS.md](STATUS.md) for detailed progress tracking.

## 📋 Features

- **Image Sequence Rendering** - Render frames individually or in batches
- **Batch Rendering** - Render multiple blend files in sequence
- **Video Encoding** - Encode sequences to ProRes or DNxHD
- **Frame Management** - Smart frame filtering and version numbering
- **Global Variables** - Dynamic path variables for flexible workflows
- **Playblast** - Quick preview rendering
- **Project Setup** - Automated directory structure creation

## 📁 Project Structure

```
loom/
├── __init__.py              # Main addon entry point
├── bl_info.py               # Addon metadata
├── helpers/                 # ✅ Utility functions (4 modules)
├── properties/              # ✅ Property groups (4 modules)
├── ui/                      # ✅ UI components (5 modules)
├── operators/               # ✅ Operators (8 modules, 52 operators)
├── presets/                 # 🔲 Preset system (Phase 6)
└── handlers/                # 🔲 Event handlers (Phase 6)
```

## 🔧 Installation

### For Development

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/loom.git
   cd loom
   ```

2. **Note:** The addon is currently being refactored and is not yet functional.
   See [REFACTORING_TASKS.md](REFACTORING_TASKS.md) for remaining work.

### For Users

⚠️ **Not ready for use yet** - The refactoring is in progress. Check back when Phase 8 (Testing) is complete.

## 🛠️ Development

### Current Refactoring Status

- ✅ **Phase 1:** Infrastructure (directories, init files)
- ✅ **Phase 2:** Helpers (compatibility, frame utils, version utils, globals)
- ✅ **Phase 3:** Properties (UI, render, scene, preferences)
- ✅ **Phase 4:** UI Components (lists, menus, panels, draw functions)
- ✅ **Phase 5:** Operators (52 operators across 8 modules)
- 🔲 **Phase 6:** Presets & Handlers
- 🔲 **Phase 7:** Registration
- 🔲 **Phase 8:** Testing

### Key Documents

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive development guide
- **[REFACTORING_PLAN.md](REFACTORING_PLAN.md)** - High-level architecture
- **[REFACTORING_TASKS.md](REFACTORING_TASKS.md)** - Detailed task breakdown
- **[STATUS.md](STATUS.md)** - Current progress snapshot

### Technical Patterns

This refactoring establishes several important patterns:

- **Addon Name Resolution:** `addon_name = __package__.split('.')[0]`
- **No Circular Imports:** String-based operator IDs
- **Helper Functions:** `addon_name` parameter where needed
- **Registration Order:** Properties → UILists → Operators → Menus → Panels
- **GPL Compliance:** All files include license headers

## 🧪 Testing

Testing will begin in Phase 8. The addon must pass:

- Basic load tests
- UI/UX validation
- All operator functionality
- Rendering workflows end-to-end
- Encoding and batch operations

## 📝 License

This project is licensed under the **GNU General Public License v2.0** - see the license headers in each file.

Original addon by **Christian Brinkmann (p2or)**

## 🙏 Credits

- **Original Author:** [Christian Brinkmann (p2or)](https://github.com/p2or)
- **Original Repository:** [blender-loom](https://github.com/p2or/blender-loom)
- **Refactoring:** Collaborative effort to improve maintainability

## 🔗 Links

- **Documentation:** [GitHub Wiki](https://github.com/p2or/blender-loom/wiki)
- **Issues:** [Issue Tracker](https://github.com/p2or/blender-loom/issues)
- **Blender:** [blender.org](https://www.blender.org/)

## 📊 Statistics

- **Original File:** 6,358 lines (monolithic)
- **Current Structure:** 28 files, ~5,100 lines extracted
- **Code Coverage:** ~80% of original code refactored
- **Operators:** 52 operators organized into 7 categories
- **Properties:** 10 property groups
- **UI Components:** 3 lists, 4 menus, 2 panels, 11 draw functions

## 🚦 Getting Started (After Refactoring)

Once the refactoring is complete (Phase 8), installation will be:

1. Download the addon
2. Open Blender → Edit → Preferences → Add-ons
3. Click "Install" and select the `loom` folder
4. Enable the "Loom" addon
5. Access from Render menu or Output Properties panel

---

**Note:** This addon is currently under heavy refactoring. Contributions are welcome, but please read [CLAUDE.md](CLAUDE.md) first to understand the project structure and patterns.
