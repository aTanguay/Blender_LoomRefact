#!/usr/bin/env python3
"""
Quick modular test for Loom addon - tests individual components.
Run with: blender --background --python DOCS/test_quick.py
"""

import sys
import os

# Add local path to test from repo, not installed version
repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_dir)

import bpy

print("=" * 70)
print("LOOM ADDON - QUICK MODULAR TEST")
print(f"Testing from: {repo_dir}")
print("=" * 70)

# Test 1: Helper functions
print("\n[TEST 1] Helper Functions")
try:
    from loom.helpers.frame_utils import filter_frames
    result = filter_frames("1-5")
    assert result == [1, 2, 3, 4, 5], f"Expected [1,2,3,4,5], got {result}"
    print("  ✓ filter_frames() works")
except Exception as e:
    print(f"  ✗ filter_frames() failed: {e}")

try:
    from loom.helpers.globals_utils import isevaluable
    assert isevaluable("$project") == True
    assert isevaluable("regular") == False
    print("  ✓ isevaluable() works")
except Exception as e:
    print(f"  ✗ isevaluable() failed: {e}")

# Test 2: Property groups import
print("\n[TEST 2] Property Groups")
try:
    from loom.properties import scene_props, render_props, ui_props
    print("  ✓ All property modules import successfully")
except Exception as e:
    print(f"  ✗ Property import failed: {e}")

# Test 3: Operator imports
print("\n[TEST 3] Operators")
try:
    from loom.operators import ui_operators, batch_operators, encode_operators
    print("  ✓ All operator modules import successfully")
except Exception as e:
    print(f"  ✗ Operator import failed: {e}")

# Test 4: UI imports
print("\n[TEST 4] UI Components")
try:
    from loom.ui import lists, menus, panels, draw_functions
    print("  ✓ All UI modules import successfully")
except Exception as e:
    print(f"  ✗ UI import failed: {e}")

# Test 5: Registration
print("\n[TEST 5] Addon Registration")
try:
    import loom
    print(f"  Loading loom from: {loom.__file__}")
    loom.register()
    print("  ✓ Addon registered successfully")

    # Test Scene.loom
    if hasattr(bpy.types.Scene, 'loom'):
        print("  ✓ Scene.loom property attached")
    else:
        print("  ✗ Scene.loom property NOT found")

    # Test operator existence
    if hasattr(bpy.ops.loom, 'render_dialog'):
        print("  ✓ loom.render_dialog operator registered")
    else:
        print("  ✗ loom.render_dialog operator NOT found")

    # Test callbacks
    from loom.operators.encode_operators import codec_callback, colorspace_callback

    class Mock:
        pass

    codecs = codec_callback(Mock(), bpy.context)
    print(f"  ✓ codec_callback() returns {len(codecs)} codecs")

    colors = colorspace_callback(Mock(), bpy.context)
    print(f"  ✓ colorspace_callback() returns {len(colors)} colorspaces")

    # Unregister
    loom.unregister()
    print("  ✓ Addon unregistered successfully")

except Exception as e:
    print(f"  ✗ Registration failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TESTS COMPLETE")
print("=" * 70)
