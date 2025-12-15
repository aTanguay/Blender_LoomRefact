# Quick Start: Phase 8 Testing

## ✅ Pre-Flight Validation Complete!

The addon structure has been validated and is ready for Blender testing.

**Validation Results:**
- ✅ 29 Python files - all syntax valid
- ✅ 73 Blender classes registered
- ✅ All modules properly structured
- ✅ bl_info complete with all required keys
- ✅ Zero errors, zero warnings

---

## 🚀 Getting Started

### Step 1: Install in Blender

1. **Open Blender 5.0+**

2. **Open Preferences**
   - Menu: `Edit` → `Preferences`
   - Or: Press `F4` and type "Preferences"

3. **Navigate to Add-ons**
   - Click `Add-ons` tab (left sidebar)

4. **Install the Addon**
   - Click `Install...` button (top right)
   - Navigate to: `/Users/andytanguay/Downloads/loom/`
   - Select: `loom_addon.zip`
   - Click `Install Add-on`

5. **Enable the Addon**
   - Search for "Loom" in the add-ons search box
   - Check the checkbox next to "Render: Loom"

6. **Verify Installation**
   - Look for "Render: Loom" in the addons list
   - Check the checkbox is enabled
   - No errors in console

---

### Step 2: First Checks

#### Check Console
1. **Windows:** `Window` → `Toggle System Console`
2. **macOS/Linux:** Check Terminal where Blender was launched
3. **Look for:** No Python errors or tracebacks

#### Check Menu
1. Click top menu: `Render`
2. Look for: `Loom` submenu
3. Should contain:
   - Loom (render dialog)
   - Batch Render and Encode
   - Render Flipbook
   - Encode Image Sequence
   - Rename sequences
   - Open Output Folder

#### Check Preferences
1. In Add-ons list, expand "Render: Loom"
2. Should see:
   - Global Variables section
   - Project Directories section
   - Terminal settings
   - Dialog width
   - Playblast flag

---

### Step 3: Quick Functional Test

#### Test 1: Render Dialog
1. Press `Ctrl+Shift+F12` (or `Render` → `Loom`)
2. Dialog should open without errors
3. Should see:
   - Frame input field
   - Guess Frames button
   - Verify Frames button
   - Render settings

#### Test 2: Global Variables
1. Open addon preferences
2. Check Global Variables list
3. Should see 11 default variables:
   - $BLEND, $F4, $SCENE, $CAMERA, $LENS
   - $VIEWLAYER, $MARKER, $COLL, $OB
   - $DAY, $TIME, $SUM

#### Test 3: Output Panel
1. Switch to Properties panel (right side)
2. Click Output Properties (printer icon)
3. Look for Loom sections:
   - Output path management (at top)
   - Version numbering
   - Compositor paths

---

## 📋 Comprehensive Testing

For full testing, see: **[TESTING_PLAN.md](TESTING_PLAN.md)**

The testing plan covers 15 test phases:
1. Installation & Load Tests
2. Preferences UI Tests
3. UI Integration Tests
4. Keyboard Shortcuts Tests
5. Render Dialog Tests
6. Batch Rendering Tests
7. Encoding Tests
8. Preset System Tests
9. Global Variables Tests
10. Project Setup Tests
11. Utility Operators Tests
12. Render Execution Tests
13. Error Handling Tests
14. Performance Tests
15. Integration Tests

---

## 🐛 If You Find Issues

### Common Issues

**Issue: Addon won't enable**
- Check Blender version (need 5.0+)
- Look in console for errors
- Try restarting Blender

**Issue: Menu items missing**
- Restart Blender
- Check addon is enabled
- Look for console errors

**Issue: Keyboard shortcuts don't work**
- Check for conflicts with other addons
- On macOS, try Cmd instead of Ctrl
- Check keymap in Blender preferences

### Reporting Bugs

When you find a bug, note:
1. **What you did** (steps to reproduce)
2. **What happened** (actual result)
3. **What you expected** (expected result)
4. **Console output** (any error messages)
5. **Blender version** and **platform** (Windows/macOS/Linux)

---

## ✨ What to Test First

### Priority 1: Critical Functions
- [ ] Addon loads without errors
- [ ] Render dialog opens
- [ ] Preferences accessible
- [ ] No console errors

### Priority 2: Core Features
- [ ] Global variables work
- [ ] Keyboard shortcuts work
- [ ] UI panels appear
- [ ] Presets save/load

### Priority 3: Advanced Features
- [ ] Batch rendering
- [ ] Video encoding
- [ ] Project setup
- [ ] Marker operations

---

## 📊 Testing Progress

You can track testing progress in: **[REFACTORING_TASKS.md](REFACTORING_TASKS.md)**

Phase 8 section has 15 test categories with detailed checklist items.

---

## 🎉 Success Criteria

The addon is ready for production when:
- ✅ Loads without errors in Blender 5.0+
- ✅ All UI panels and menus visible
- ✅ Keyboard shortcuts working
- ✅ Basic render workflow works
- ✅ No crashes or major bugs
- ✅ Documentation matches functionality

---

## 📁 Important Files

**For Testing:**
- `loom_addon.zip` - The addon to install
- `TESTING_PLAN.md` - Comprehensive test plan
- `INSTALLATION.md` - Installation guide

**For Reference:**
- `STATUS.md` - Current progress
- `README.md` - Project overview
- `PHASE_6_7_SUMMARY.md` - Recent work summary

**For Troubleshooting:**
- `CLAUDE.md` - Development guide
- `REFACTORING_PLAN.md` - Architecture
- `loom/` - Source code

---

## 🔧 Development Environment

If you want to test with source code directly (instead of zip):

1. Create symlink in Blender addons directory:
   ```bash
   # macOS/Linux
   ln -s /Users/andytanguay/Downloads/loom/loom ~/Library/Application\ Support/Blender/5.0/scripts/addons/loom

   # Windows
   mklink /D "%APPDATA%\Blender Foundation\Blender\5.0\scripts\addons\loom" "C:\path\to\loom\loom"
   ```

2. In Blender:
   - Preferences → Add-ons
   - Click "Refresh" button
   - Enable "Render: Loom"

This allows you to edit source and reload addon without reinstalling.

---

## ⚡ Quick Reload (During Development)

To reload addon after code changes:

1. **In Blender Text Editor:**
   ```python
   import bpy
   import importlib
   import sys

   # Unregister
   bpy.ops.preferences.addon_disable(module="loom")

   # Remove from cache
   modules = [m for m in sys.modules if m.startswith('loom')]
   for m in modules:
       del sys.modules[m]

   # Re-enable
   bpy.ops.preferences.addon_enable(module="loom")
   ```

2. **Or simpler:**
   - F3 → "Reload Scripts"
   - Disable and re-enable addon

---

## 🎯 Next Steps

1. **Install addon in Blender** (Step 1 above)
2. **Run quick functional test** (Step 3 above)
3. **If all good:** Start comprehensive testing (see TESTING_PLAN.md)
4. **Document any issues** found
5. **Celebrate progress!** 🎉

---

**Good luck with testing!** The hard work of refactoring is done - now it's time to see it in action! 🚀
