# Addon Installation Fix - bl_info Location

**Issue:** Addon did not appear in Blender's addon list after installation

**Root Cause:** 
Blender requires `bl_info` to be defined **directly** in the `__init__.py` file, not imported from another module.

## What Was Wrong

Previous structure:
```python
# __init__.py
from .bl_info import bl_info  # ❌ Blender can't find this
```

## What Was Fixed

Current structure:
```python
# __init__.py
bl_info = {
    "name": "Loom",
    "description": "...",
    # ...
}  # ✅ Blender finds this immediately
```

## Changes Made

1. **Moved `bl_info` dict** from `bl_info.py` into `__init__.py`
2. **Removed `bl_info.py`** from the addon (no longer needed)
3. **Rebuilt zip** with corrected structure

## Why This Matters

Blender's addon scanner:
1. Looks for `__init__.py` in addon directories
2. Reads the file and looks for `bl_info` at module level
3. Uses `bl_info` to populate addon metadata in the UI
4. **Does NOT execute imports** during this scan

So importing `bl_info` from another file meant Blender couldn't see it during the initial scan.

## Testing

After this fix, the addon should:
- ✅ Appear in the addon list when installed
- ✅ Show correct name: "Loom"
- ✅ Show correct category: "Render"
- ✅ Show correct description and metadata
- ✅ Be searchable by name

## New Installation Steps

1. Open Blender 5.0+
2. Edit → Preferences → Add-ons
3. Click "Install..."
4. Select **`loom.zip`** (79 KB)
5. **Search for "Loom"** - should now appear!
6. Enable "Render: Loom"

---

**Status:** Fixed ✅  
**New Zip:** loom.zip (79 KB)  
**Date:** 2025-12-13
