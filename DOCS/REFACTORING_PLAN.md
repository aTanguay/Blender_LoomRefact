# Loom Blender Addon Refactoring Plan

## Overview
This document outlines the plan to refactor the monolithic `loom_blender5_compatible_2.py` file (6358 lines) into a maintainable multi-file structure while preserving all functionality.

## Current Structure Analysis

The current file contains the following sections (line numbers):
1. **Lines 1-51**: GPL License, imports, bl_info
2. **Lines 52-337**: Helper functions (10 functions)
3. **Lines 338-1046**: Preferences & Scene Properties (17 classes)
4. **Lines 1047-3716**: UI Operators (37 classes)
5. **Lines 3717-4494**: Rendering Operators (8 classes)
6. **Lines 4495-4669**: Playblast (Experimental) (1 class)
7. **Lines 4670-5583**: Utilities (13 classes)
8. **Lines 5584-5796**: Presets (3 classes)
9. **Lines 5797-6113**: Handler & Panels/Menus (9 functions/classes)
10. **Lines 6114-6358**: Registration & Shortcuts

### Key Statistics
- **Total lines**: 6,358
- **Total classes**: ~78
- **Total functions**: ~20
- **Dependencies**: bpy, numpy, blend_render_info, rna_keymap_ui, etc.

## Proposed File Structure

```
loom/
├── __init__.py                 # Main registration, imports all modules
├── bl_info.py                  # Addon metadata (bl_info dict)
├── helpers/
│   ├── __init__.py
│   ├── blender_compat.py       # Blender 5.0 compatibility helpers
│   ├── frame_utils.py          # Frame filtering and processing
│   ├── version_utils.py        # Version numbering utilities
│   └── globals_utils.py        # Global variable replacement
├── properties/
│   ├── __init__.py
│   ├── preferences.py          # LOOM_AP_preferences
│   ├── scene_props.py          # LOOM_PG_scene_settings
│   ├── render_props.py         # Render-related property groups
│   └── ui_props.py             # UI-related property groups (globals, dirs)
├── operators/
│   ├── __init__.py
│   ├── ui_operators.py         # Dialog and UI-related operators
│   ├── render_operators.py    # Core rendering operators
│   ├── batch_operators.py      # Batch rendering operators
│   ├── encode_operators.py     # Encoding and renaming operators
│   ├── utils_operators.py      # Utility operators (markers, directories, etc.)
│   ├── playblast_operators.py  # Playblast operators (experimental)
│   └── terminal_operators.py   # Terminal and shell execution operators
├── presets/
│   ├── __init__.py
│   └── render_presets.py       # Preset system (AddPresetBase)
├── ui/
│   ├── __init__.py
│   ├── panels.py               # All PT_ panels
│   ├── menus.py                # All MT_ menus
│   ├── lists.py                # All UL_ UIList classes
│   └── draw_functions.py       # Draw helper functions
└── handlers/
    ├── __init__.py
    └── render_handlers.py      # Persistent handlers
```

## Migration Strategy

### Phase 1: Create Infrastructure
1. Create directory structure
2. Create all `__init__.py` files
3. Move `bl_info` to `bl_info.py`
4. Set up main `__init__.py` with basic imports

### Phase 2: Extract Helpers (Low Risk)
1. Move Blender 5.0 compatibility functions to `helpers/blender_compat.py`
2. Move frame filtering to `helpers/frame_utils.py`
3. Move version numbering to `helpers/version_utils.py`
4. Move global variable functions to `helpers/globals_utils.py`
5. Test imports work correctly

### Phase 3: Extract Properties (Medium Risk)
1. Move property groups to appropriate files in `properties/`
2. Ensure all property callbacks are accessible
3. Update registration in `__init__.py`

### Phase 4: Extract UI Components (Low Risk)
1. Move UIList classes to `ui/lists.py`
2. Move Panel classes to `ui/panels.py`
3. Move Menu classes to `ui/menus.py`
4. Move draw functions to `ui/draw_functions.py`

### Phase 5: Extract Operators (High Risk - Most Complex)
1. Group operators by functionality
2. Move to appropriate operator files
3. Ensure all operator dependencies are imported
4. Handle circular dependencies if any

### Phase 6: Extract Presets & Handlers (Medium Risk)
1. Move preset classes to `presets/render_presets.py`
2. Move handlers to `handlers/render_handlers.py`

### Phase 7: Update Registration (Critical)
1. Update `__init__.py` register() function
2. Update `__init__.py` unregister() function
3. Ensure proper registration order (properties before operators)

### Phase 8: Testing & Validation
1. Test addon loads without errors
2. Test all UI panels display correctly
3. Test all operators function
4. Test rendering workflow
5. Test batch rendering
6. Test encoding/playback

## Critical Considerations

### Import Dependencies
- All operators depend on property groups
- Many operators depend on helper functions
- UI elements depend on operators
- Handlers depend on properties

### Registration Order
Must register in this order:
1. Property Groups (PG_)
2. UI Lists (UL_)
3. Operators (OT_)
4. Menus (MT_)
5. Panels (PT_)
6. Handlers
7. Keymaps

### Circular Dependencies
Watch for:
- Operators importing from other operators
- Properties with callbacks referencing operators
- Handlers referencing operators

### Blender Addon Requirements
- `bl_info` must be importable from main `__init__.py`
- Registration must happen in `__init__.py`
- All classes must have proper `bl_idname`
- Addon name (`__name__`) is used in preferences

## Testing Checklist

- [ ] Addon appears in Blender preferences
- [ ] All preferences panels load
- [ ] Timeline menu items appear
- [ ] Output panel extensions work
- [ ] Render dialog opens and functions
- [ ] Batch render dialog works
- [ ] Encode dialog works
- [ ] Frame filtering works
- [ ] Version numbering works
- [ ] Global variables work
- [ ] Project directories work
- [ ] Presets load and save
- [ ] Keyboard shortcuts work
- [ ] Rendering executes successfully
- [ ] Playblast functions (if enabled)

## Risks & Mitigation

### High Risk Areas
1. **Operator dependencies**: Operators frequently call each other
   - Mitigation: Careful dependency analysis before moving

2. **Property callbacks**: Some properties have update callbacks
   - Mitigation: Ensure callback functions are imported

3. **Registration order**: Incorrect order causes failures
   - Mitigation: Follow strict registration order

4. **Addon name references**: `__name__` used in preferences
   - Mitigation: Pass addon name explicitly or use `__package__`

### Low Risk Areas
1. Helper functions (pure functions, no side effects)
2. UI Lists (self-contained display logic)
3. Panels (declarative UI)

## Success Criteria

1. ✅ All original functionality preserved
2. ✅ No errors on addon load
3. ✅ All UI elements display correctly
4. ✅ All operators execute successfully
5. ✅ Code is organized logically
6. ✅ Each file is < 500 lines (ideal) or < 1000 lines (acceptable)
7. ✅ Clear separation of concerns
8. ✅ Easy to locate specific functionality

## Timeline Notes

This is a complex refactoring that requires careful, methodical work. Breaking it into phases allows for incremental testing and reduces risk of breaking functionality. Each phase should be completed and tested before moving to the next.

## Next Steps

See `REFACTORING_TASKS.md` for detailed task breakdown and progress tracking.
