#!/usr/bin/env python3
"""
Comprehensive module-by-module test for Loom addon.
Run with: blender --background --python DOCS/test_addon_modules.py
"""

import sys
import bpy

# Test results tracking
tests_passed = 0
tests_failed = 0
test_details = []

def test_result(test_name, passed, details=""):
    """Track test results."""
    global tests_passed, tests_failed, test_details
    if passed:
        tests_passed += 1
        status = "✓ PASS"
    else:
        tests_failed += 1
        status = "✗ FAIL"

    message = f"{status}: {test_name}"
    if details:
        message += f" - {details}"

    print(message)
    test_details.append((test_name, passed, details))

print("=" * 80)
print("LOOM ADDON - COMPREHENSIVE MODULE TESTING")
print("=" * 80)

# ==============================================================================
# TEST 1: Module Import
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 1: MODULE IMPORT")
print("=" * 80)

try:
    import loom
    test_result("Import loom module", True, f"from {loom.__file__}")
except Exception as e:
    test_result("Import loom module", False, str(e))
    sys.exit(1)

# ==============================================================================
# TEST 2: Submodule Imports
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 2: SUBMODULE IMPORTS")
print("=" * 80)

submodules = [
    ('loom.helpers', ['blender_compat', 'frame_utils', 'version_utils', 'globals_utils']),
    ('loom.properties', ['ui_props', 'render_props', 'scene_props', 'preferences']),
    ('loom.ui', ['lists', 'menus', 'panels', 'draw_functions']),
    ('loom.operators', ['ui_operators', 'batch_operators', 'encode_operators',
                        'render_operators', 'playblast_operators', 'terminal_operators', 'utils_operators']),
    ('loom.presets', ['render_presets']),
    ('loom.handlers', ['render_handlers']),
]

for parent_module, submodule_list in submodules:
    for submodule_name in submodule_list:
        try:
            full_name = f"{parent_module}.{submodule_name}"
            exec(f"from {parent_module} import {submodule_name}")
            test_result(f"Import {full_name}", True)
        except Exception as e:
            test_result(f"Import {full_name}", False, str(e))

# ==============================================================================
# TEST 3: Helper Functions
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 3: HELPER FUNCTIONS")
print("=" * 80)

# Test frame_utils.filter_frames
try:
    from loom.helpers.frame_utils import filter_frames
    # Test various frame range formats
    test_cases = [
        ("1-10", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ("1,3,5", [1, 3, 5]),
        ("1-5,10", [1, 2, 3, 4, 5, 10]),
    ]

    all_passed = True
    for input_str, expected in test_cases:
        result = filter_frames(input_str)
        if result != expected:
            all_passed = False
            test_result(f"filter_frames('{input_str}')", False,
                       f"Expected {expected}, got {result}")
        else:
            test_result(f"filter_frames('{input_str}')", True)
except Exception as e:
    test_result("filter_frames tests", False, str(e))

# Test globals_utils
try:
    from loom.helpers.globals_utils import isevaluable

    test_cases = [
        ("$project", True),
        ("$scene", True),
        ("regular_string", False),
    ]

    for input_str, expected in test_cases:
        result = isevaluable(input_str)
        if result != expected:
            test_result(f"isevaluable('{input_str}')", False,
                       f"Expected {expected}, got {result}")
        else:
            test_result(f"isevaluable('{input_str}')", True)
except Exception as e:
    test_result("isevaluable tests", False, str(e))

# ==============================================================================
# TEST 4: Addon Registration
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 4: ADDON REGISTRATION")
print("=" * 80)

try:
    loom.register()
    test_result("loom.register()", True)
except Exception as e:
    test_result("loom.register()", False, str(e))
    print("\nREGISTRATION FAILED - Cannot continue with further tests")
    sys.exit(1)

# ==============================================================================
# TEST 5: Property Groups Registration
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 5: PROPERTY GROUPS REGISTRATION")
print("=" * 80)

# Check Scene.loom property
try:
    if hasattr(bpy.types.Scene, 'loom'):
        test_result("Scene.loom property exists", True)
    else:
        test_result("Scene.loom property exists", False, "Property not attached")
except Exception as e:
    test_result("Scene.loom property check", False, str(e))

# Test accessing the property
try:
    scene = bpy.data.scenes.new("test_scene")
    loom_props = scene.loom
    test_result("Access Scene.loom", True, f"Type: {type(loom_props).__name__}")

    # Check for key properties
    key_attrs = ['frame_input', 'custom_render_presets', 'render', 'batch_render']
    for attr in key_attrs:
        if hasattr(loom_props, attr):
            test_result(f"Scene.loom.{attr} exists", True)
        else:
            test_result(f"Scene.loom.{attr} exists", False)

except Exception as e:
    test_result("Access Scene.loom", False, str(e))

# ==============================================================================
# TEST 6: Operator Registration
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 6: OPERATOR REGISTRATION")
print("=" * 80)

# List of expected operators
expected_operators = [
    'loom.render_dialog',
    'loom.batch_render_dialog',
    'loom.encode_dialog',
    'loom.playblast',
    'loom.project_dialog',
    'loom.rename_dialog',
    'loom.open_output_folder',
]

for op_name in expected_operators:
    try:
        # Check if operator exists
        op_module, op_func = op_name.split('.')
        if hasattr(bpy.ops, op_module) and hasattr(getattr(bpy.ops, op_module), op_func):
            test_result(f"Operator '{op_name}' registered", True)
        else:
            test_result(f"Operator '{op_name}' registered", False, "Not found in bpy.ops")
    except Exception as e:
        test_result(f"Check operator '{op_name}'", False, str(e))

# ==============================================================================
# TEST 7: UI Elements
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 7: UI ELEMENTS REGISTRATION")
print("=" * 80)

# Check for UI lists
ui_lists = [
    'LOOM_UL_batch_list',
    'LOOM_UL_arguments_list',
]

for ui_list in ui_lists:
    try:
        if hasattr(bpy.types, ui_list):
            test_result(f"UIList '{ui_list}' registered", True)
        else:
            test_result(f"UIList '{ui_list}' registered", False, "Not found in bpy.types")
    except Exception as e:
        test_result(f"Check UIList '{ui_list}'", False, str(e))

# Check for menus
menus = [
    'LOOM_MT_main_menu',
    'LOOM_MT_render_presets',
]

for menu in menus:
    try:
        if hasattr(bpy.types, menu):
            test_result(f"Menu '{menu}' registered", True)
        else:
            test_result(f"Menu '{menu}' registered", False, "Not found in bpy.types")
    except Exception as e:
        test_result(f"Check Menu '{menu}'", False, str(e))

# ==============================================================================
# TEST 8: Preferences
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 8: ADDON PREFERENCES")
print("=" * 80)

try:
    # Access addon preferences
    addon_name = 'loom'
    if addon_name in bpy.context.preferences.addons:
        prefs = bpy.context.preferences.addons[addon_name].preferences
        test_result("Access addon preferences", True, f"Type: {type(prefs).__name__}")

        # Check for key preference properties
        pref_attrs = ['render_presets_path', 'playblast_flag', 'ffmpeg_path']
        for attr in pref_attrs:
            if hasattr(prefs, attr):
                test_result(f"Preference '{attr}' exists", True)
            else:
                test_result(f"Preference '{attr}' exists", False)
    else:
        test_result("Access addon preferences", False, "Addon not in preferences collection")
except Exception as e:
    test_result("Access addon preferences", False, str(e))

# ==============================================================================
# TEST 9: EnumProperty Callbacks
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 9: ENUMPROPERTY CALLBACKS")
print("=" * 80)

try:
    from loom.operators.encode_operators import codec_callback, colorspace_callback

    # Test that callbacks can be called
    # Create a mock object with context
    class MockSelf:
        pass

    mock_self = MockSelf()

    # Test codec_callback
    try:
        result = codec_callback(mock_self, bpy.context)
        if isinstance(result, list) and len(result) > 0:
            test_result("codec_callback() returns valid data", True, f"{len(result)} codecs")
        else:
            test_result("codec_callback() returns valid data", False, "Empty or invalid result")
    except Exception as e:
        test_result("codec_callback() execution", False, str(e))

    # Test colorspace_callback
    try:
        result = colorspace_callback(mock_self, bpy.context)
        if isinstance(result, list) and len(result) > 0:
            test_result("colorspace_callback() returns valid data", True, f"{len(result)} colorspaces")
        else:
            test_result("colorspace_callback() returns valid data", False, "Empty or invalid result")
    except Exception as e:
        test_result("colorspace_callback() execution", False, str(e))

except Exception as e:
    test_result("EnumProperty callbacks import", False, str(e))

# ==============================================================================
# TEST 10: Render Preset Callback
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 10: RENDER PRESET CALLBACK")
print("=" * 80)

try:
    from loom.properties.render_props import render_preset_callback

    class MockSelf:
        pass

    mock_self = MockSelf()

    try:
        result = render_preset_callback(mock_self, bpy.context)
        if isinstance(result, list):
            test_result("render_preset_callback() returns valid data", True, f"{len(result)} presets")
        else:
            test_result("render_preset_callback() returns valid data", False, "Invalid result type")
    except Exception as e:
        test_result("render_preset_callback() execution", False, str(e))

except Exception as e:
    test_result("render_preset_callback import", False, str(e))

# ==============================================================================
# TEST 11: Cleanup and Unregistration
# ==============================================================================
print("\n" + "=" * 80)
print("TEST 11: CLEANUP AND UNREGISTRATION")
print("=" * 80)

try:
    loom.unregister()
    test_result("loom.unregister()", True)

    # Verify Scene.loom property removed
    if not hasattr(bpy.types.Scene, 'loom'):
        test_result("Scene.loom property removed", True)
    else:
        test_result("Scene.loom property removed", False, "Property still exists")

except Exception as e:
    test_result("loom.unregister()", False, str(e))

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

total_tests = tests_passed + tests_failed
pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"\nTotal Tests Run: {total_tests}")
print(f"Passed: {tests_passed} ({pass_rate:.1f}%)")
print(f"Failed: {tests_failed}")

if tests_failed > 0:
    print("\n" + "=" * 80)
    print("FAILED TESTS:")
    print("=" * 80)
    for name, passed, details in test_details:
        if not passed:
            print(f"✗ {name}")
            if details:
                print(f"  → {details}")

print("\n" + "=" * 80)

# Exit with appropriate code
sys.exit(0 if tests_failed == 0 else 1)
