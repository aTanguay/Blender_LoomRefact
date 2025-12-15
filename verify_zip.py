#!/usr/bin/env python3
"""
Verify loom.zip is correctly structured for Blender installation.
"""

import zipfile
import sys
from pathlib import Path

def verify_addon_zip(zip_path):
    """Verify the addon zip structure."""
    print("🔍 Verifying Blender Addon Zip Structure\n")
    print(f"File: {zip_path}")
    print(f"Size: {Path(zip_path).stat().st_size / 1024:.1f} KB\n")

    errors = []
    warnings = []

    with zipfile.ZipFile(zip_path, 'r') as zf:
        files = zf.namelist()

        # Check for addon directory
        has_loom_dir = any(f.startswith('loom/') for f in files)
        if not has_loom_dir:
            print("✗ ERROR: No 'loom/' directory found")
            errors.append("Missing loom/ directory")
        else:
            print("✓ Addon directory: loom/")

        print()

        # Check required files in loom directory
        required_files = ['loom/__init__.py', 'loom/bl_info.py']
        for req_file in required_files:
            if req_file in files:
                print(f"✓ Required file: {req_file}")
            else:
                print(f"✗ Missing: {req_file}")
                errors.append(f"Missing required file: {req_file}")

        print()

        # Check directory structure
        expected_dirs = ['loom/helpers/', 'loom/properties/', 'loom/ui/', 'loom/operators/', 'loom/presets/', 'loom/handlers/']
        found_dirs = set()
        for f in files:
            if f.count('/') >= 2:  # loom/subdir/file
                parts = f.split('/')
                found_dirs.add(f"{parts[0]}/{parts[1]}/")

        for exp_dir in expected_dirs:
            if exp_dir in found_dirs:
                print(f"✓ Directory: {exp_dir}")
            else:
                print(f"⚠ Missing directory: {exp_dir}")
                warnings.append(f"Missing directory: {exp_dir}")

        print()

        # Check for unwanted files
        unwanted_patterns = ['.pyc', '__pycache__', '.DS_Store', '.md', '.git']
        unwanted_found = []
        for pattern in unwanted_patterns:
            matching = [f for f in files if pattern in f]
            if matching:
                unwanted_found.extend(matching)

        if unwanted_found:
            print("⚠ Unwanted files found:")
            for f in unwanted_found[:5]:
                print(f"  - {f}")
            if len(unwanted_found) > 5:
                print(f"  ... and {len(unwanted_found) - 5} more")
            warnings.append(f"{len(unwanted_found)} unwanted files")
        else:
            print("✓ No unwanted files (.pyc, __pycache__, .DS_Store, .md)")

        print()

        # Try to read bl_info
        try:
            bl_info_content = zf.read('loom/bl_info.py').decode('utf-8')
            if 'bl_info' in bl_info_content:
                print("✓ bl_info.py is readable")
                if '"blender": (5, 0, 0)' in bl_info_content:
                    print("✓ Blender version: 5.0.0")
                else:
                    print("⚠ Blender version may not be 5.0.0")
                    warnings.append("Blender version not 5.0.0")
            else:
                print("✗ bl_info dict not found")
                errors.append("bl_info dict missing")
        except Exception as e:
            print(f"✗ Error reading bl_info.py: {e}")
            errors.append(f"Cannot read bl_info.py: {e}")

        print()
        print("=" * 60)
        print()

        # Summary
        if errors:
            print(f"❌ VALIDATION FAILED - {len(errors)} error(s)")
            for err in errors:
                print(f"  • {err}")
            return False
        elif warnings:
            print(f"⚠️  VALIDATION PASSED WITH WARNINGS - {len(warnings)} warning(s)")
            for warn in warnings:
                print(f"  • {warn}")
            return True
        else:
            print("✅ VALIDATION PASSED - Addon zip is correctly structured!")
            print()
            print("📦 Ready to install in Blender:")
            print("   1. Open Blender 5.0+")
            print("   2. Edit → Preferences → Add-ons")
            print("   3. Install → Select loom.zip")
            print("   4. Enable 'Render: Loom'")
            return True

if __name__ == '__main__':
    zip_path = Path(__file__).parent / 'loom.zip'

    if not zip_path.exists():
        print(f"❌ Error: {zip_path} not found")
        sys.exit(1)

    success = verify_addon_zip(zip_path)
    sys.exit(0 if success else 1)
