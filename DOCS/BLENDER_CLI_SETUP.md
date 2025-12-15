# Blender Command-Line Setup Guide

This guide will help you set up Blender so it can be called from the command line for testing and automation.

---

## 🍎 macOS Setup

### Option 1: Create an Alias (Recommended for Testing)

Add this to your shell configuration file (`~/.zshrc` or `~/.bash_profile`):

```bash
# Blender 5.0 alias
alias blender="/Applications/Blender50.app/Contents/MacOS/Blender"
```

**Apply changes:**
```bash
source ~/.zshrc
# or
source ~/.bash_profile
```

**Test it:**
```bash
blender --version
```

### Option 2: Create a Symbolic Link (System-wide)

```bash
sudo ln -s /Applications/Blender50.app/Contents/MacOS/Blender /usr/local/bin/blender
```

**Test it:**
```bash
blender --version
```

### Option 3: Add to PATH

Add this to your `~/.zshrc` or `~/.bash_profile`:

```bash
export PATH="/Applications/Blender50.app/Contents/MacOS:$PATH"
```

**Apply and test:**
```bash
source ~/.zshrc
blender --version
```

---

## 🪟 Windows Setup

### Option 1: Add to System PATH

1. **Find Blender installation path:**
   - Default: `C:\Program Files\Blender Foundation\Blender 5.0\`

2. **Add to PATH:**
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\Program Files\Blender Foundation\Blender 5.0\`
   - Click "OK" on all dialogs

3. **Test in new terminal:**
   ```cmd
   blender --version
   ```

### Option 2: Create a Batch File

Create `blender.bat` in a directory that's in your PATH (e.g., `C:\Windows\`):

```batch
@echo off
"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" %*
```

---

## 🐧 Linux Setup

### Blender is usually in PATH by default

If not, add to `~/.bashrc`:

```bash
export PATH="/usr/bin:$PATH"
# or wherever Blender is installed
```

---

## 🧪 Testing the Loom Addon from Command Line

### Basic Addon Test

Test if the addon can be imported without starting the UI:

```bash
blender --background --python DOCS/test_addon_import.py
```

### Run Blender with Addon Enabled

```bash
# Start Blender with Python console
blender --python-console

# In the console, test:
import bpy
bpy.ops.preferences.addon_enable(module='loom')
```

### Test Addon Registration

Create a test script `test_loom.py`:

```python
import bpy

# Enable the addon
bpy.ops.preferences.addon_enable(module='loom')

# Check if it's enabled
if 'loom' in bpy.context.preferences.addons:
    print("✅ Loom addon enabled successfully!")

    # Test Scene.loom property exists
    if hasattr(bpy.context.scene, 'loom'):
        print("✅ Scene.loom property is accessible")
    else:
        print("❌ Scene.loom property not found")
else:
    print("❌ Failed to enable Loom addon")
```

**Run it:**
```bash
blender --background --python test_loom.py
```

---

## 🎯 Useful Blender CLI Commands

### Get Version
```bash
blender --version
```

### Run in Background (No UI)
```bash
blender --background
```

### Run Python Script
```bash
blender --background --python script.py
```

### Run Python Command
```bash
blender --background --python-expr "import bpy; print(bpy.app.version_string)"
```

### Render a File
```bash
blender --background file.blend --render-frame 1
```

### Enable Addon and Render
```bash
blender --background file.blend \
  --python-expr "import bpy; bpy.ops.preferences.addon_enable(module='loom')" \
  --render-anim
```

### Get Help
```bash
blender --help
```

---

## 📋 Common Testing Commands for Loom

### 1. Quick Addon Validation
```bash
# Navigate to the repo
cd /Users/atanguay/Documents/GIThub/Blender_LoomRefact

# Run the test script
blender --background --python DOCS/test_addon_import.py
```

### 2. Interactive Testing
```bash
# Start Blender with Python console
blender --python-console

# Then in the console:
>>> import bpy
>>> bpy.ops.preferences.addon_enable(module='loom')
>>> bpy.context.scene.loom
```

### 3. Check for Errors
```bash
# This will show any Python errors during startup
blender --background --python-expr "import bpy; bpy.ops.preferences.addon_enable(module='loom'); print('Success!')" 2>&1
```

### 4. Test Specific Operator
```bash
blender --background --python-expr "
import bpy
bpy.ops.preferences.addon_enable(module='loom')
# Test an operator exists
if hasattr(bpy.ops.loom, 'render_dialog'):
    print('✅ Render dialog operator found')
else:
    print('❌ Render dialog operator not found')
"
```

---

## 🔍 Troubleshooting

### "command not found: blender"

**macOS:**
- Check the path: `ls /Applications/Blender50.app/Contents/MacOS/Blender`
- If it exists, the alias/symlink wasn't set up correctly
- Try the full path: `/Applications/Blender50.app/Contents/MacOS/Blender --version`

**Windows:**
- Check the installation path exists
- Make sure PATH was updated (close and reopen terminal)
- Try full path: `"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --version`

### "Module 'loom' not found"

The addon needs to be installed first:

1. Open Blender normally
2. Install the addon via Preferences
3. Then CLI commands will work

Or install from command line:
```bash
blender --background --python-expr "
import bpy
import os
addon_path = '/Users/atanguay/Documents/GIThub/Blender_LoomRefact/loom-addon.zip'
bpy.ops.preferences.addon_install(filepath=addon_path)
bpy.ops.preferences.addon_enable(module='loom')
bpy.ops.wm.save_userpref()
"
```

---

## 📝 Testing Workflow Example

Here's a complete testing workflow:

```bash
# 1. Set up the alias (first time only)
echo 'alias blender="/Applications/Blender50.app/Contents/MacOS/Blender"' >> ~/.zshrc
source ~/.zshrc

# 2. Verify Blender is accessible
blender --version

# 3. Navigate to the addon repository
cd /Users/atanguay/Documents/GIThub/Blender_LoomRefact

# 4. Run the addon test
blender --background --python DOCS/test_addon_import.py

# 5. If successful, test in GUI mode
blender
```

---

## 🎓 Advanced: Automated Testing Script

Create `run_tests.sh`:

```bash
#!/bin/bash

echo "=== Loom Addon Automated Tests ==="
echo ""

# Set Blender path (adjust as needed)
BLENDER="/Applications/Blender50.app/Contents/MacOS/Blender"

# Test 1: Version check
echo "Test 1: Blender version check"
$BLENDER --version
echo ""

# Test 2: Syntax validation
echo "Test 2: Python syntax validation"
find loom -name "*.py" -exec python3 -m py_compile {} \; 2>&1
if [ $? -eq 0 ]; then
    echo "✅ All Python files valid"
else
    echo "❌ Syntax errors found"
fi
echo ""

# Test 3: Addon import test
echo "Test 3: Addon import test"
$BLENDER --background --python DOCS/test_addon_import.py 2>&1 | grep -E "(✓|✗|Error)"
echo ""

echo "=== Tests Complete ==="
```

**Make it executable and run:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

---

## 📚 Reference

- **Blender CLI Documentation:** https://docs.blender.org/manual/en/latest/advanced/command_line/index.html
- **Blender Python API:** https://docs.blender.org/api/current/
- **Addon Development:** https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html

---

**Last Updated:** 2025-12-14
**Blender Version:** 5.0
**Platform:** macOS (with Windows/Linux notes)
