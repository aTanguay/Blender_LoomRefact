# Phase 8: Testing Plan

**Status:** Ready to begin
**Goal:** Verify the refactored addon works correctly in Blender 5.0+

## Pre-Flight Validation (Without Blender)

Before loading in Blender, let's verify the code structure:

### ✅ Python Syntax Validation
```bash
# Validate all Python files compile
find loom -name "*.py" -exec python3 -m py_compile {} \;
```

### ✅ Import Structure Check
```bash
# Test that modules can be imported (without bpy)
python3 -c "import ast; import sys; [ast.parse(open(f).read()) for f in sys.argv[1:]]" loom/**/*.py
```

### ✅ Registration Order Verification
Check that classes are registered in correct order:
1. Properties (PG_*)
2. UI Lists (UL_*)
3. Operators (OT_*)
4. Menus (MT_*)
5. Panels (PT_*)
6. Handlers
7. Keymaps

## Blender Testing Phases

### Phase 8.1: Installation & Load Tests ⏳

**Objective:** Verify the addon loads without errors

**Steps:**
1. [ ] Open Blender 5.0 or newer
2. [ ] Open Preferences (Edit → Preferences)
3. [ ] Navigate to Add-ons tab
4. [ ] Click "Install..." button
5. [ ] Select `loom_addon.zip`
6. [ ] Click "Install Add-on"

**Expected Results:**
- ✅ No error messages appear
- ✅ Addon appears in add-ons list
- ✅ Can search for "Loom" and find it

**Verification:**
7. [ ] Enable the addon (check the checkbox)
8. [ ] Check System Console (Window → Toggle System Console)
9. [ ] Verify no Python errors or tracebacks

**Success Criteria:**
- [ ] Addon enables without errors
- [ ] No console warnings or errors
- [ ] Addon stays enabled after restart

---

### Phase 8.2: Preferences UI Tests ⏳

**Objective:** Verify preferences panel works correctly

**Steps:**
1. [ ] In Add-ons list, expand "Render: Loom"
2. [ ] Verify preferences panel appears

**Check Each Section:**

#### Global Variables
3. [ ] Global Variables list displays
4. [ ] Default variables present ($BLEND, $F4, $SCENE, etc.)
5. [ ] Can add new variable
6. [ ] Can edit variable expression
7. [ ] Can remove variable
8. [ ] List reorders correctly

#### Project Directories
9. [ ] Project directories list displays
10. [ ] Default directories present (assets, geometry, textures, render, comp)
11. [ ] Can add new directory
12. [ ] Can rename directory
13. [ ] Can remove directory
14. [ ] Creation flag toggles work

#### Other Settings
15. [ ] Terminal path setting visible
16. [ ] Dialog width setting adjustable
17. [ ] Playblast flag checkbox works
18. [ ] Reset preferences button works

**Success Criteria:**
- [ ] All preference sections accessible
- [ ] All UI elements interactive
- [ ] Settings persist after Blender restart

---

### Phase 8.3: UI Integration Tests ⏳

**Objective:** Verify UI panels and menus appear correctly

#### Render Menu
1. [ ] Open top menu bar
2. [ ] Click "Render" menu
3. [ ] Verify "Loom" submenu appears
4. [ ] Check submenu contains:
   - [ ] Loom (render dialog)
   - [ ] Batch Render and Encode
   - [ ] Render Flipbook
   - [ ] Playblast (if enabled in prefs)
   - [ ] Encode Image Sequence
   - [ ] Rename sequences
   - [ ] Open Output Folder

#### Output Properties Panel
5. [ ] Switch to Properties panel
6. [ ] Select Output Properties (printer icon)
7. [ ] Verify Loom sections appear:
   - [ ] Output path management (prepended)
   - [ ] Version numbering
   - [ ] Compositor paths

#### Render Stamp Note
8. [ ] In Output Properties, expand "Metadata"
9. [ ] Expand "Stamp Note" section
10. [ ] Verify Loom metadata section (prepended)

#### Render Presets Panel
11. [ ] Look for Loom Render Presets panel
12. [ ] Verify preset header displays
13. [ ] Verify preset flags section
14. [ ] Check Properties header for preset dropdown

#### Dopesheet Integration
15. [ ] Switch to Dopesheet editor
16. [ ] Check header for Loom integration
17. [ ] Verify marker menus updated (right-click timeline)

#### Timeline Markers (Blender 4.x compat)
18. [ ] If Blender < 5.0, check Timeline marker menu
19. [ ] Verify Loom marker options appear

**Success Criteria:**
- [ ] All UI panels visible
- [ ] No missing panels or menus
- [ ] UI elements properly styled
- [ ] No layout glitches

---

### Phase 8.4: Keyboard Shortcuts Tests ⏳

**Objective:** Verify all keyboard shortcuts work

**Test Each Shortcut:**

| Shortcut | Expected Action | Result |
|----------|----------------|--------|
| `Ctrl+Shift+F12` | Open Loom Render Dialog | ⏳ |
| `Ctrl+Shift+Alt+F12` | Open Batch Render Dialog | ⏳ |
| `Ctrl+Shift+F10` | Open Render Flipbook | ⏳ |
| `Ctrl+Shift+F11` | Open Playblast (if enabled) | ⏳ |
| `Ctrl+Shift+F9` | Open Encode Dialog | ⏳ |
| `Ctrl+Shift+F3` | Open Output Folder | ⏳ |
| `Ctrl+Shift+F2` | Open Rename Dialog | ⏳ |
| `Ctrl+Shift+F1` | Open Project Dialog | ⏳ |

**macOS Users (test with Cmd+Shift):**
- [ ] All shortcuts work with Cmd instead of Ctrl

**Success Criteria:**
- [ ] All shortcuts trigger correct dialogs
- [ ] No conflicts with other addons
- [ ] Shortcuts listed in Blender keymap preferences

---

### Phase 8.5: Render Dialog Tests ⏳

**Objective:** Test main render dialog functionality

**Open Render Dialog** (Ctrl+Shift+F12 or Render → Loom)

#### Frame Input
1. [ ] Frame range input field visible
2. [ ] Can enter frame range (e.g., "1-100")
3. [ ] Can enter frame list (e.g., "1,5,10,20")
4. [ ] Can enter frame range with step (e.g., "1-100x2")

#### Frame Validation
5. [ ] Click "Guess Frames" button
6. [ ] Verify frames detected from timeline
7. [ ] Click "Verify Frames" button
8. [ ] Check frame validation feedback

#### Render Settings
9. [ ] Render threads dropdown works
10. [ ] Full scale checkbox toggles
11. [ ] Output path displays correctly
12. [ ] Version numbering options work

#### Dialog Actions
13. [ ] "Render" button present
14. [ ] "Cancel" button closes dialog
15. [ ] Dialog remembers last settings

**Success Criteria:**
- [ ] Dialog opens without errors
- [ ] All controls functional
- [ ] Frame parsing works correctly
- [ ] Settings persist between opens

---

### Phase 8.6: Batch Rendering Tests ⏳

**Objective:** Test batch rendering functionality

**Open Batch Dialog** (Ctrl+Shift+Alt+F12 or Render → Loom → Batch)

#### File List Management
1. [ ] Batch list visible
2. [ ] Click "Scan Directory"
3. [ ] Select directory with .blend files
4. [ ] Verify .blend files added to list
5. [ ] Click "Add Files"
6. [ ] Select individual .blend files
7. [ ] Verify files added to list

#### List Operations
8. [ ] Select item in list
9. [ ] Test list actions:
   - [ ] Move up
   - [ ] Move down
   - [ ] Remove item
   - [ ] Clear all
10. [ ] Remove duplicates works

#### Batch Settings
11. [ ] Frame range per file editable
12. [ ] Default range button works
13. [ ] Codec selection dropdown
14. [ ] Colorspace selection dropdown
15. [ ] FPS setting adjustable
16. [ ] Terminal instance checkbox

#### Snapshot Feature
17. [ ] Click "Snapshot"
18. [ ] Verify current scene added to list
19. [ ] Snapshot includes current settings

**Success Criteria:**
- [ ] Can build batch list
- [ ] List operations work correctly
- [ ] Settings apply to all items
- [ ] No errors adding/removing files

---

### Phase 8.7: Encoding Tests ⏳

**Objective:** Test video encoding functionality

**Open Encode Dialog** (Ctrl+Shift+F9 or Render → Loom → Encode)

#### Image Sequence Selection
1. [ ] "Load Sequence" button visible
2. [ ] Click "Load Sequence"
3. [ ] Select image sequence
4. [ ] Verify sequence loaded
5. [ ] Frame range auto-detected

#### Path Verification
6. [ ] Click "Verify Sequence"
7. [ ] Check for missing frames
8. [ ] Gap detection works

#### Auto Paths
9. [ ] Click "Auto Paths"
10. [ ] Verify input/output paths set

#### Encoding Settings
11. [ ] Codec dropdown populated
12. [ ] Colorspace dropdown populated
13. [ ] FPS setting adjustable
14. [ ] Output format selection

#### Movie Selection
15. [ ] "Select Movie" button works
16. [ ] Can choose output location
17. [ ] Path displays correctly

**Success Criteria:**
- [ ] Can load image sequences
- [ ] Frame detection works
- [ ] Codec options available
- [ ] Output path configurable

---

### Phase 8.8: Preset System Tests ⏳

**Objective:** Test render preset save/load

**Access Presets** (Properties → Render Presets Panel)

#### Preset Creation
1. [ ] Configure render settings
2. [ ] Click "+" to add preset
3. [ ] Name preset
4. [ ] Verify preset saved

#### Preset Flags
5. [ ] Expand preset flags
6. [ ] Toggle each flag:
   - [ ] Include Resolution
   - [ ] Include Output Path
   - [ ] Include Scene Settings
   - [ ] Include Color Management
   - [ ] Include Metadata
   - [ ] Include Post Processing
   - [ ] Include Passes
   - [ ] Include File Format
   - [ ] Include Engine Settings

#### Preset Loading
7. [ ] Select different preset from dropdown
8. [ ] Verify settings change
9. [ ] Check that only flagged settings restored

#### Preset Management
10. [ ] Rename preset
11. [ ] Delete preset
12. [ ] Export preset

**Success Criteria:**
- [ ] Presets save correctly
- [ ] Presets load correctly
- [ ] Flags control what's saved
- [ ] Presets persist after restart

---

### Phase 8.9: Global Variables Tests ⏳

**Objective:** Test global variable expansion

**Setup:**
1. [ ] Open addon preferences
2. [ ] Verify global variables list
3. [ ] Check default variables present

**Test Variable Expansion:**

#### In Output Path
4. [ ] Set output path to: `/tmp/$BLEND/$SCENE/$F4`
5. [ ] Verify path expands correctly
6. [ ] Check $BLEND replaced with filename
7. [ ] Check $SCENE replaced with scene name
8. [ ] Check $F4 replaced with frame number

#### In Metadata
9. [ ] Enable metadata stamp note
10. [ ] Set note text including variables
11. [ ] Render single frame
12. [ ] Verify variables expanded in metadata

#### Custom Variables
13. [ ] Add custom variable
14. [ ] Set expression (e.g., `"test_value"`)
15. [ ] Use in output path
16. [ ] Verify expands correctly

**Test All Default Variables:**
- [ ] $BLEND - Blend filename
- [ ] $F4 - Frame (4 digits)
- [ ] $SCENE - Scene name
- [ ] $CAMERA - Camera name
- [ ] $LENS - Lens focal length
- [ ] $VIEWLAYER - View layer name
- [ ] $MARKER - Current marker name
- [ ] $COLL - Collection name
- [ ] $OB - Active object name
- [ ] $DAY - Current date
- [ ] $TIME - Current time
- [ ] $SUM - Example expression

**Success Criteria:**
- [ ] All variables expand correctly
- [ ] Custom variables work
- [ ] No errors with missing attributes
- [ ] Variables work in all contexts

---

### Phase 8.10: Project Setup Tests ⏳

**Objective:** Test project directory creation

**Open Project Dialog** (Ctrl+Shift+F1 or Render → Loom menu)

1. [ ] Dialog opens
2. [ ] Project directory list visible
3. [ ] Can select base directory
4. [ ] Check creation flags for directories
5. [ ] Click "Create Project"
6. [ ] Verify directories created:
   - [ ] assets/
   - [ ] geometry/
   - [ ] textures/
   - [ ] render/
   - [ ] comp/
7. [ ] Custom directories also created if added

**Success Criteria:**
- [ ] Project structure created correctly
- [ ] Only flagged directories created
- [ ] Paths resolve correctly
- [ ] No permission errors

---

### Phase 8.11: Utility Operators Tests ⏳

**Objective:** Test utility functions

#### Folder Operations
1. [ ] Click "Open Output Folder"
2. [ ] Verify folder opens in file manager
3. [ ] Test with non-existent path
4. [ ] Verify error handling

#### Marker Operations
5. [ ] Add timeline markers
6. [ ] Test "Generate Markers" operator
7. [ ] Test "Rename Markers" operator
8. [ ] Test "Unbind Markers" operator

#### Frame Range Operations
9. [ ] Test "Set Frame Range from Markers"
10. [ ] Verify frame range updates

#### Cleanup Operations
11. [ ] Test "Cleanup Compositor Nodes"
12. [ ] Test "Delete Bash Files"
13. [ ] Test "Delete File" operator

**Success Criteria:**
- [ ] All utilities execute without errors
- [ ] File operations work correctly
- [ ] Marker operations work
- [ ] Cleanup operations safe

---

### Phase 8.12: Render Execution Tests ⏳

**Objective:** Test actual rendering

#### Image Sequence Render
1. [ ] Set up simple scene
2. [ ] Open render dialog
3. [ ] Set frame range (e.g., 1-10)
4. [ ] Click "Render"
5. [ ] Verify render starts
6. [ ] Check output directory
7. [ ] Verify frames rendered

#### Batch Render
8. [ ] Set up batch list
9. [ ] Start batch render
10. [ ] Verify each file renders
11. [ ] Check terminal output
12. [ ] Verify encoded output (if selected)

#### Flipbook Render
13. [ ] Open flipbook dialog
14. [ ] Set parameters
15. [ ] Start render
16. [ ] Verify preview plays

**Success Criteria:**
- [ ] Renders complete successfully
- [ ] Output files created
- [ ] No crashes during render
- [ ] Render can be cancelled

---

### Phase 8.13: Error Handling Tests ⏳

**Objective:** Test graceful error handling

**Test Error Scenarios:**

1. [ ] Invalid frame range input
2. [ ] Missing output directory
3. [ ] Insufficient permissions
4. [ ] Missing .blend files in batch
5. [ ] Invalid global variable expression
6. [ ] Corrupted image sequence
7. [ ] Cancel during render
8. [ ] Cancel during encode

**Expected Behavior:**
- [ ] Clear error messages
- [ ] No crashes
- [ ] Can recover from errors
- [ ] Console shows helpful info

---

### Phase 8.14: Performance Tests ⏳

**Objective:** Verify performance is acceptable

1. [ ] Large batch list (100+ files)
2. [ ] Large frame range (1000+ frames)
3. [ ] Many global variables (20+)
4. [ ] Complex scene rendering

**Check:**
- [ ] No significant UI lag
- [ ] Memory usage reasonable
- [ ] No performance regressions vs original

---

### Phase 8.15: Integration Tests ⏳

**Objective:** Test with real-world workflows

**Workflow 1: Simple Render**
1. [ ] Create scene
2. [ ] Set output path with variables
3. [ ] Render with Loom
4. [ ] Verify output

**Workflow 2: Batch Production**
1. [ ] Prepare multiple .blend files
2. [ ] Set up batch render
3. [ ] Encode to video
4. [ ] Verify complete pipeline

**Workflow 3: Preset-Based Workflow**
1. [ ] Create render preset
2. [ ] Use preset on multiple scenes
3. [ ] Verify consistency

**Success Criteria:**
- [ ] Complete workflows work end-to-end
- [ ] No interruptions or errors
- [ ] Output quality as expected

---

## Final Validation Checklist

### Code Quality
- [ ] No Python errors in console
- [ ] No deprecation warnings
- [ ] Clean addon disable/enable
- [ ] Memory leaks checked

### Documentation
- [ ] All features documented
- [ ] Keyboard shortcuts listed
- [ ] Known issues noted

### Distribution
- [ ] loom_addon.zip installs correctly
- [ ] No extra files in package
- [ ] File permissions correct

---

## Bug Tracking Template

When issues are found, document them:

```markdown
### Bug #X: [Brief Description]

**Severity:** Critical / High / Medium / Low
**Phase:** [Which test phase]
**Steps to Reproduce:**
1.
2.
3.

**Expected Result:**

**Actual Result:**

**Console Output:**
```

**Workaround:**

**Fix Required:**
```

---

## Testing Sign-Off

When all tests pass:

- [ ] All 15 test phases completed
- [ ] All critical bugs fixed
- [ ] All high-priority bugs fixed
- [ ] Documentation updated
- [ ] Ready for production use

**Tested By:**
**Date:**
**Blender Version:**
**Platform:**

---

**Next Steps After Testing:**
1. Fix any critical bugs found
2. Update documentation with any quirks
3. Tag release version
4. Announce completion
5. Celebrate! 🎉
