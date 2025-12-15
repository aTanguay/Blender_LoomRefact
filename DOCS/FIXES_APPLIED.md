# Loom Addon Build Fixes - 2025-12-14

## Issues Found and Fixed

### 1. Invalid Escape Sequences in Regex Patterns ✅ FIXED

**Problem:** Python 3.x warns about invalid escape sequences in string literals when backslashes are used in regular expressions without raw strings.

**Files affected:**
- `loom/ui/draw_functions.py:84`
- `loom/operators/encode_operators.py:664`
- `loom/operators/playblast_operators.py:46`

**Fix:** Changed regex patterns to use raw strings (r"..."):
```python
# Before:
re.search("v\d+", ...)
re.sub('\d(?!\d)', ...)

# After:
re.search(r"v\d+", ...)
re.sub(r'\d(?!\d)', ...)
```

**Why this matters:** These warnings can cause issues in some Python environments and indicate potential runtime problems.

---

### 2. Duplicate Scene Property Registration ✅ FIXED

**Problem:** The `Scene.loom` property was being registered in **two** places, causing a registration conflict.

**Locations:**
1. `loom/properties/__init__.py:49` - Registered `bpy.types.Scene.loom`
2. `loom/__init__.py:92` - Also registered `bpy.types.Scene.loom`

**Fix:** Removed the registration from `loom/properties/__init__.py` and kept only the one in the main `__init__.py` to ensure proper module registration order.

**Why this matters:** Blender will throw an error when trying to register a property that's already registered.

---

### 3. Duplicate Draw Function Registration ✅ FIXED

**Problem:** UI draw functions were being appended to Blender panels in **two** places:

**Locations:**
1. `loom/ui/__init__.py:46-63` - Appended draw functions
2. `loom/__init__.py:170-185` - Also appended the same draw functions

**Fix:** Removed the draw function registration from `loom/ui/__init__.py` and kept only the registration in the main `__init__.py`.

**Why this matters:** Appending the same draw function twice will cause it to appear twice in the UI, and may cause errors during unregistration.

---

### 4. Missing Import: LOOM_PG_generic_arguments ✅ FIXED

**Problem:** `terminal_operators.py` was using `LOOM_PG_generic_arguments` as a property type but hadn't imported it.

**Location:** `loom/operators/terminal_operators.py:120`

**Error message:** `name 'LOOM_PG_generic_arguments' is not defined`

**Fix:** Added import statement:
```python
from ..properties.ui_props import LOOM_PG_generic_arguments
```

**Why this matters:** Without importing the property group class, Blender cannot resolve the type reference when defining the CollectionProperty.

---

### 5. Missing Import: LOOM_MT_render_presets ✅ FIXED

**Problem:** `render_operators.py` was using `LOOM_MT_render_presets.__name__` but hadn't imported it. Also incorrectly referenced as `LOOM_PT_render_presets` (Panel instead of Menu).

**Location:** `loom/operators/render_operators.py:621`

**Fix:** Added import and corrected class name:
```python
from ..presets.render_presets import LOOM_MT_render_presets
```
Changed `LOOM_PT_render_presets.__name__` to `LOOM_MT_render_presets.__name__`

**Why this matters:** The `menu_idname` parameter needs the Menu class, not the Panel class, and the class must be imported to be referenced.

---

### 6. Missing Import: ExportHelper ✅ FIXED

**Problem:** `utils_operators.py` was using `ExportHelper` in a class definition but only imported `ImportHelper`.

**Location:** `loom/operators/utils_operators.py:420`

**Error message:** `RuntimeError: Error: name 'ExportHelper' is not defined`

**Fix:** Updated import statement:
```python
from bpy_extras.io_utils import ImportHelper, ExportHelper
```

**Why this matters:** The `LOOM_OT_select_project_directory` operator inherits from `ExportHelper` to provide file selection functionality, so the class must be imported.

---

### 7. Incorrect EnumProperty Callback Signature ✅ FIXED

**Problem:** `render_preset_callback` had an incorrect function signature for a Blender EnumProperty callback. It was expecting 3 parameters `(scene, context, addon_name)` but Blender EnumProperty callbacks must use `(self, context)`.

**Location:** `loom/properties/render_props.py:30`

**Error message:** `RuntimeError: Error: bpy_struct "LOOM_PG_scene_settings" registration error: 'custom_render_presets' EnumProperty could not register`

**Fix:** Updated function signature and made it get addon_name internally:
```python
def render_preset_callback(self, context):
    # Get addon name from the package path
    addon_name = __package__.split('.')[0]
    preset_path = context.preferences.addons[addon_name].preferences.render_presets_path
    ...
```

**Why this matters:** Blender's EnumProperty `items` parameter expects a callback with exactly two parameters `(self, context)`. Using a different signature causes registration to fail.

---

## Registration Order

The correct registration order is now:

```
Main __init__.py:
1. properties.register()      # Register all property groups and preferences
2. ui.register()              # Register UI classes (lists, menus, panels)
3. operators.register()       # Register operators
4. presets.register()         # Register preset system
5. handlers.register()        # Register event handlers
6. Attach Scene.loom          # Attach main property to Scene
7. Register keymaps           # Set up keyboard shortcuts
8. Append draw functions      # Add UI elements to Blender panels
```

Unregistration happens in reverse order.

---

## Testing

### Quick Syntax Check (without Blender):
```bash
find loom -name "*.py" -type f -exec python3 -m py_compile {} \;
```
Should complete with no errors or warnings.

### Full Test in Blender:
```bash
blender --background --python test_addon_import.py
```

Or manually in Blender:
1. Edit > Preferences > Add-ons
2. Click "Install..."
3. Navigate to the `loom` folder
4. Select it and click "Install Add-on"
5. Enable the "Loom" addon

---

## Files Modified

1. ✅ `loom/ui/draw_functions.py` - Fixed regex escape sequence
2. ✅ `loom/operators/encode_operators.py` - Fixed regex escape sequence
3. ✅ `loom/operators/playblast_operators.py` - Fixed regex escape sequence
4. ✅ `loom/properties/__init__.py` - Removed duplicate Scene.loom registration
5. ✅ `loom/ui/__init__.py` - Removed duplicate draw function registration
6. ✅ `loom/operators/terminal_operators.py` - Added missing import for LOOM_PG_generic_arguments
7. ✅ `loom/operators/render_operators.py` - Added missing import for LOOM_MT_render_presets and fixed class reference
8. ✅ `loom/operators/utils_operators.py` - Added missing import for ExportHelper
9. ✅ `loom/properties/render_props.py` - Fixed render_preset_callback function signature
10. ✅ `loom/properties/scene_props.py` - Updated import comment for clarity

---

## Known Issues

None currently identified. All Python syntax checks pass cleanly.

---

## Next Steps for Testing

1. **Install in Blender:** Try installing the addon in Blender 5.0
2. **Check Console:** Look for any errors in the Blender system console
3. **Test Features:**
   - Open the Loom render dialog (Ctrl+Shift+F12)
   - Check preferences panel
   - Try rendering a simple scene
4. **Report Issues:** If any errors occur, check:
   - The exact error message in the console
   - Which operator/panel is causing the issue
   - Any missing dependencies or imports

---

## Verification Checklist

- ✅ All Python files have valid syntax
- ✅ No duplicate property registrations
- ✅ No duplicate draw function registrations
- ✅ All regex patterns use raw strings
- ✅ All `__init__.py` files present
- ✅ Registration order is correct
- ✅ Import dependencies are resolved
- ✅ Missing class imports fixed
- ✅ Addon loads in Blender 5.0 successfully
- ✅ Addon can be enabled without errors
- ✅ Loom menu appears in Render menu
- ⏳ Full feature testing (needs comprehensive testing)

---

**Last Updated:** 2025-12-14
**Status:** ✅ SUCCESSFULLY INSTALLED AND ENABLED IN BLENDER 5.0
