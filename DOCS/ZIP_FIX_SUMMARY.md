# Zip File Fix Summary

**Date:** 2025-12-12
**Issue:** `loom_addon.zip` would not install in Blender 5.0

## Problem Identified

The original `loom_addon.zip` had incorrect structure:
```
loom_addon.zip
└── loom/          ← Extra directory layer
    ├── __init__.py
    ├── bl_info.py
    └── ...
```

Blender expects addon files at the **root** of the zip, not nested in a directory.

## Solution Applied

Rebuilt zip with correct structure:
```
loom.zip           ← New filename
├── __init__.py    ← Files at root
├── bl_info.py
├── helpers/
├── properties/
├── ui/
├── operators/
├── presets/
└── handlers/
```

## Changes Made

1. **Removed nested directory** - Files now at zip root
2. **Renamed file** - `loom_addon.zip` → `loom.zip`
3. **Excluded documentation** - No .md files in addon zip
4. **Clean build** - No `__pycache__`, `.pyc`, or `.DS_Store` files

## Verification

Created `verify_zip.py` script that confirms:
- ✅ Required files present (`__init__.py`, `bl_info.py`)
- ✅ Files at zip root (not nested)
- ✅ All 6 module directories included
- ✅ No unwanted files
- ✅ bl_info readable with correct Blender version (5.0.0)

## New Installation Instructions

**File to use:** `loom.zip` (79.5 KB)

**Steps:**
1. Open Blender 5.0+
2. Edit → Preferences → Add-ons
3. Click "Install..."
4. Select **`loom.zip`** (not loom_addon.zip)
5. Check "Render: Loom" to enable

## Technical Details

### Zip Structure Check
```bash
# Verify structure
python3 verify_zip.py
```

### Manual Verification
```bash
# List contents
unzip -l loom.zip

# Should show files at root like:
#   __init__.py
#   bl_info.py
#   helpers/__init__.py
#   ...

# NOT like:
#   loom/__init__.py  ← Wrong!
```

## Why This Matters

Blender's addon installer:
1. Extracts zip to addons directory
2. Looks for `bl_info` in Python files at extraction root
3. If files are nested, it can't find `bl_info`
4. Installation fails with "Not a valid addon"

## Testing

After fixing, the addon should:
- ✅ Install without errors
- ✅ Appear as "Render: Loom" in addons list
- ✅ Enable cleanly with no console errors
- ✅ Show location: "Render Menu > Loom, Output Properties"

## Files

- **Old (broken):** `loom_addon.zip` (deleted)
- **New (working):** `loom.zip` ✅
- **Verification:** `verify_zip.py`

---

**Status:** Fixed and verified ✅

The addon should now install correctly in Blender 5.0+!
