#!/usr/bin/env python3
"""
Test script to check Loom addon structure and imports.
Run this with Blender's Python: blender --background --python test_addon_import.py
"""

import sys
import os

def test_addon_structure():
    """Test the addon can be imported and registered."""
    print("=" * 60)
    print("Testing Loom Addon Structure")
    print("=" * 60)

    try:
        import bpy
        print("✓ bpy module imported successfully")
    except ImportError as e:
        print("✗ Failed to import bpy - are you running this in Blender?")
        print(f"  Error: {e}")
        return False

    # Test importing the addon
    try:
        import loom
        print("✓ loom module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import loom module: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test that all submodules can be imported
    submodules = ['helpers', 'properties', 'ui', 'operators', 'presets', 'handlers']
    for submodule in submodules:
        try:
            mod = getattr(loom, submodule)
            print(f"✓ loom.{submodule} imported successfully")
        except Exception as e:
            print(f"✗ Failed to import loom.{submodule}: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Test registration
    try:
        loom.register()
        print("✓ Addon registered successfully")
    except Exception as e:
        print(f"✗ Failed to register addon: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Check that Scene.loom property exists
    try:
        scene = bpy.context.scene
        loom_props = scene.loom
        print("✓ Scene.loom property is accessible")
    except Exception as e:
        print(f"✗ Failed to access Scene.loom: {e}")
        return False

    # Test unregistration
    try:
        loom.unregister()
        print("✓ Addon unregistered successfully")
    except Exception as e:
        print(f"✗ Failed to unregister addon: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    # Add the parent directory to path so we can import loom
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    if addon_dir not in sys.path:
        sys.path.insert(0, addon_dir)

    success = test_addon_structure()
    sys.exit(0 if success else 1)
