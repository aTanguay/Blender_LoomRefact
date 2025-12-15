import sys
import os

# Add the local loom directory to Python path
repo_dir = "/Users/atanguay/Documents/GIThub/Blender_LoomRefact"
sys.path.insert(0, repo_dir)

import bpy

print("=" * 70)
print("LOOM ADDON LOCAL TEST (Using files from repo, not installed addon)")
print("=" * 70)

try:
    # Import loom from local directory
    print("\n1. Testing loom import from local directory...")
    print(f"   Sys.path[0]: {sys.path[0]}")
    import loom
    print(f"   ✓ loom module imported from: {loom.__file__}")

    # Register
    print("\n2. Testing loom registration...")
    loom.register()
    print("   ✓ loom registered successfully")

    # Check Scene.loom property
    print("\n3. Testing Scene.loom property...")
    if hasattr(bpy.types.Scene, 'loom'):
        print("   ✓ Scene.loom property exists")
    else:
        print("   ✗ Scene.loom property NOT FOUND")
        sys.exit(1)

    # Test accessing the property
    print("\n4. Testing property access...")
    scene = bpy.data.scenes.new("test_scene")
    loom_props = scene.loom
    print(f"   ✓ Scene.loom accessible: {type(loom_props)}")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)

except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
