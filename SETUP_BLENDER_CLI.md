# Setup Blender CLI - Action Required

The Blender CLI alias has been added to your `~/.zshrc` file, but you need to reload your shell to use it.

---

## ⚡ Quick Fix (Choose One)

### Option 1: Reload Your Terminal (Recommended)

**Close and reopen your terminal**, then test:
```bash
blender --version
```

### Option 2: Reload Shell Config (Current Terminal)

Run this command in your terminal:
```bash
source ~/.zshrc
blender --version
```

### Option 3: Use Full Path (Temporary)

If you don't want to reload, use the full path:
```bash
/Applications/Blender50.app/Contents/MacOS/Blender --version
```

---

## ✅ Verify It's Working

After reloading, you should see:
```
Blender 5.0.0
	build date: 2025-11-18
	...
```

---

## 🧪 Quick Test After Setup

Once the `blender` command works, run:

```bash
cd /Users/atanguay/Documents/GIThub/Blender_LoomRefact
blender --background --python DOCS/test_addon_import.py
```

---

## 📝 What Was Added

The following was added to your `~/.zshrc`:

```bash
# Blender 5.0 CLI alias
alias blender="/Applications/Blender50.app/Contents/MacOS/Blender"
```

---

## 🔧 If Still Not Working

1. **Check the file exists:**
   ```bash
   ls -la /Applications/Blender50.app/Contents/MacOS/Blender
   ```

2. **Manually add the alias:**
   ```bash
   echo 'alias blender="/Applications/Blender50.app/Contents/MacOS/Blender"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Use full path for now:**
   - See [DOCS/BLENDER_CLI_SETUP.md](DOCS/BLENDER_CLI_SETUP.md) for alternative setup methods

---

**After setup, see [QUICK_TEST.md](QUICK_TEST.md) for testing commands!**
