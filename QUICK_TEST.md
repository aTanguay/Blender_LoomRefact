# Quick Test Guide - Loom Addon

**Quick command-line tests for the Loom addon**

---

## ✅ Setup Complete!

Blender is now accessible from the command line:
- ✅ Alias added to `~/.zshrc`
- ✅ Blender 5.0.0 detected
- ✅ Ready for testing

---

## 🚀 Quick Test Commands

### 1. Verify Blender CLI Access
```bash
blender --version
```

**Expected output:** `Blender 5.0.0`

---

### 2. Test Addon Import
```bash
cd /Users/atanguay/Documents/GIThub/Blender_LoomRefact
blender --background --python DOCS/test_addon_import.py
```

**Expected output:**
```
✓ bpy module imported successfully
✓ loom module imported successfully
✓ Addon registered successfully
...
```

---

### 3. Quick Syntax Check
```bash
cd /Users/atanguay/Documents/GIThub/Blender_LoomRefact
find loom -name "*.py" -exec python3 -m py_compile {} \; 2>&1
echo "✅ Syntax check complete"
```

---

### 4. Interactive Testing
```bash
blender --python-console
```

**Then in the console:**
```python
import bpy
bpy.ops.preferences.addon_enable(module='loom')
print("✅ Addon enabled!")
bpy.context.scene.loom
```

---

### 5. Test Specific Operator
```bash
blender --background --python-expr "
import bpy
bpy.ops.preferences.addon_enable(module='loom')
print('Available operators:')
print([op for op in dir(bpy.ops.loom) if not op.startswith('_')])
"
```

---

## 📝 One-Line Test

For quick validation, run this single command:

```bash
blender --background --python DOCS/test_addon_import.py 2>&1 | grep -E "(✓|✗|Error|Success)"
```

---

## 🔧 Troubleshooting

### If `blender: command not found`

**Temporary fix (current session only):**
```bash
alias blender="/Applications/Blender50.app/Contents/MacOS/Blender"
```

**Permanent fix:**
```bash
echo 'alias blender="/Applications/Blender50.app/Contents/MacOS/Blender"' >> ~/.zshrc
source ~/.zshrc
```

### If alias doesn't work after terminal restart

Reload your shell config:
```bash
source ~/.zshrc
```

Or use the full path:
```bash
/Applications/Blender50.app/Contents/MacOS/Blender --version
```

---

## 📚 More Information

- Full setup guide: [DOCS/BLENDER_CLI_SETUP.md](DOCS/BLENDER_CLI_SETUP.md)
- Testing plan: [DOCS/TESTING_PROGRESS.md](DOCS/TESTING_PROGRESS.md)
- Installation: [README.md](README.md)

---

**Last Updated:** 2025-12-14
