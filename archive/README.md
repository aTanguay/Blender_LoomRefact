# Archive Directory

This directory contains original and reference files from the Loom addon refactoring project.

## 📁 Contents

### `original/`

**Original source files** - preserved for reference and comparison

- **loom_blender5_compatible_2.py** (249K)
  - The complete monolithic addon file (6,358 lines)
  - This is the source that was refactored into the modular structure
  - Original author: Christian Brinkmann (p2or)
  - Version: 0.9.5 for Blender 5.0+

- **compatibility.py** (3.0K)
  - Helper file from original development

- **utils.py** (10K)
  - Utility functions from original development

## 🔍 Purpose

These files are kept for:
1. **Reference** - Compare refactored code with original
2. **Verification** - Ensure no functionality was lost
3. **Documentation** - Understand original design decisions
4. **Backup** - Fallback if needed during development

## ⚠️ Important

**DO NOT USE THESE FILES IN PRODUCTION**

These are reference copies only. The active, refactored code is in the `loom/` directory.

## 📊 Refactoring Stats

Original monolithic structure:
- **Single file:** 6,358 lines
- **All components:** Mixed together in one file

Refactored modular structure:
- **28 files:** Organized by function
- **~5,100 lines:** Extracted and refactored
- **52 operators:** Across 7 organized modules
- **Zero circular imports:** Clean architecture

## 📅 Archive Created

**Date:** 2025-12-12
**Refactoring Phase:** Phase 5 complete (62.5%)
**Status:** Original files preserved for reference
