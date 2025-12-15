# Loom Addon - Repository Structure

**Last Updated:** 2025-12-14

---

## 📁 Repository Organization

```
Blender_LoomRefact/
├── README.md                          # Main project documentation
├── loom-addon.zip                     # Ready-to-install addon package (80 KB)
├── .gitignore                         # Git ignore file
│
├── loom/                              # Main addon source code
│   ├── __init__.py                    # Main registration & entry point
│   ├── bl_info.py                     # Addon metadata
│   │
│   ├── helpers/                       # Utility functions (4 files)
│   │   ├── __init__.py
│   │   ├── blender_compat.py          # Blender 5.0 compatibility
│   │   ├── frame_utils.py             # Frame range filtering
│   │   ├── version_utils.py           # Version numbering
│   │   └── globals_utils.py           # Global variable expansion
│   │
│   ├── properties/                    # Property groups (4 files)
│   │   ├── __init__.py
│   │   ├── ui_props.py                # UI property groups
│   │   ├── render_props.py            # Render properties
│   │   ├── scene_props.py             # Main scene settings
│   │   └── preferences.py             # Addon preferences
│   │
│   ├── ui/                            # UI components (5 files)
│   │   ├── __init__.py
│   │   ├── lists.py                   # UIList classes
│   │   ├── menus.py                   # Menu classes
│   │   ├── panels.py                  # Panel classes
│   │   └── draw_functions.py          # UI draw helpers
│   │
│   ├── operators/                     # Operators (7 files, 52 total)
│   │   ├── __init__.py
│   │   ├── ui_operators.py            # Dialog operators (7)
│   │   ├── batch_operators.py         # Batch rendering (11)
│   │   ├── encode_operators.py        # Encoding/renaming (7)
│   │   ├── render_operators.py        # Rendering (7)
│   │   ├── playblast_operators.py     # Playblast (1)
│   │   ├── terminal_operators.py      # Terminal execution (3)
│   │   └── utils_operators.py         # Utilities (16)
│   │
│   ├── presets/                       # Preset system (2 files)
│   │   ├── __init__.py
│   │   └── render_presets.py          # Render presets
│   │
│   └── handlers/                      # Event handlers (2 files)
│       ├── __init__.py
│       └── render_handlers.py         # Render event handlers
│
└── DOCS/                              # Documentation & utilities (22 files)
    ├── README.md                      # Documentation index
    │
    ├── Installation & Setup
    │   ├── INSTALLATION_INSTRUCTIONS.md
    │   └── INSTALLATION.md
    │
    ├── Build & Fixes
    │   ├── FIXES_APPLIED.md           # All 7 fixes documented
    │   ├── BUILD_SUMMARY.md           # Build overview
    │   ├── ADDON_INSTALL_FIX.md
    │   ├── FINAL_FIX_SUMMARY.md
    │   ├── ZIP_FIX_SUMMARY.md
    │   └── ZIP_STRUCTURE_CONFIRMED.md
    │
    ├── Testing
    │   ├── TESTING_PROGRESS.md        # Current testing status
    │   ├── TESTING_PLAN.md
    │   ├── QUICK_START_TESTING.md
    │   └── test_addon_import.py       # Python test script
    │
    ├── Refactoring Process
    │   ├── CLAUDE.md                  # Session guide
    │   ├── REFACTORING_PLAN.md        # Original strategy
    │   └── REFACTORING_TASKS.md       # Task breakdown
    │
    ├── Progress & Status
    │   ├── SESSION_SUMMARY.md
    │   ├── STATUS.md
    │   ├── PROGRESS_CELEBRATION.md
    │   ├── PHASE_6_7_SUMMARY.md
    │   └── PHASE_8_READY.md
    │
    └── Utilities
        ├── validate_structure.py      # Validate addon structure
        ├── verify_zip.py              # Verify ZIP contents
        └── loom-original.zip          # Original ZIP before fixes
```

---

## 📊 Statistics

### Source Code
- **Total Python Files:** 28
- **Total Lines:** ~6,300
- **Modules:** 7 (helpers, properties, ui, operators, presets, handlers)
- **Operators:** 52
- **Property Groups:** 10
- **UI Classes:** 8 (lists, menus, panels)

### Documentation
- **Total Documentation Files:** 22
- **Installation Guides:** 2
- **Fix Documentation:** 6
- **Testing Documentation:** 4
- **Process Documentation:** 6
- **Utilities:** 4

---

## 🎯 Quick Access

### For Users
1. **Installation:** Read [README.md](README.md)
2. **Install Addon:** Use [loom-addon.zip](loom-addon.zip)
3. **Troubleshooting:** See [DOCS/FIXES_APPLIED.md](DOCS/FIXES_APPLIED.md)

### For Developers
1. **Refactoring Guide:** [DOCS/CLAUDE.md](DOCS/CLAUDE.md)
2. **Build Process:** [DOCS/BUILD_SUMMARY.md](DOCS/BUILD_SUMMARY.md)
3. **Testing:** [DOCS/TESTING_PROGRESS.md](DOCS/TESTING_PROGRESS.md)

### For Testing
1. **Testing Plan:** [DOCS/TESTING_PLAN.md](DOCS/TESTING_PLAN.md)
2. **Quick Tests:** [DOCS/QUICK_START_TESTING.md](DOCS/QUICK_START_TESTING.md)
3. **Test Script:** [DOCS/test_addon_import.py](DOCS/test_addon_import.py)

---

## ✅ Repository Status

**Organization:** Clean and organized ✅
**Documentation:** Complete and indexed ✅
**Build:** Ready for distribution ✅
**Testing:** Installation verified ✅

All development files organized in DOCS directory for easy reference.

---

**Note:** This structure keeps the root directory clean with only essential files, while all documentation and development files are organized in the DOCS directory.
