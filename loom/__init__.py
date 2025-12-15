# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

"""
Loom - Image sequence rendering, encoding and playback addon for Blender.

This is the main initialization file for the refactored Loom addon.
"""

# Blender addon metadata
bl_info = {
    "name": "Loom",
    "description": "Image sequence rendering, encoding and playback",
    "author": "Christian Brinkmann (p2or)",
    "version": (0, 9, 5),
    "blender": (5, 0, 0),
    "location": "Render Menu > Loom, Output Properties",
    "doc_url": "https://github.com/p2or/blender-loom",
    "tracker_url": "https://github.com/p2or/blender-loom/issues",
    "support": "COMMUNITY",
    "category": "Render"
}

import sys

import bpy

# Module imports
from . import properties
from . import ui
from . import operators
from . import presets
from . import handlers

# Platform detection for keymaps
platform = sys.platform

# Keymap storage
addon_keymaps = []

# Default global variables for preferences
global_var_defaults = {
    "$BLEND": 'bpy.path.basename(bpy.data.filepath)[:-6]',
    "$F4": '"{:04d}".format(bpy.context.scene.frame_current)',
    "$SCENE": 'bpy.context.scene.name',
    "$CAMERA": 'bpy.context.scene.camera.name',
    "$LENS": '"{:0.0f}mm".format(bpy.context.scene.camera.data.lens)',
    "$VIEWLAYER": 'bpy.context.view_layer.name',
    "$MARKER": 'next((i.name for i in bpy.context.scene.timeline_markers if i.frame == bpy.context.scene.frame_current), "NO_NAME")',
    "$COLL": 'bpy.context.collection.name',
    "$OB": 'bpy.context.active_object.name',
    "$DAY": 'exec("import time") or time.strftime("%Y-%m-%d")',
    "$TIME": 'exec("import time") or time.strftime("%H-%M-%S")',
    "$SUM": 'str(sum([8, 16, 32]))'
}

# Default project directories
project_directories = {
    1: "assets",
    2: "geometry",
    3: "textures",
    4: "render",
    5: "comp"
}


def register():
    """Register all addon classes and handlers."""
    # Register modules in correct order
    properties.register()
    ui.register()
    operators.register()
    presets.register()
    handlers.register()

    # Attach scene property
    bpy.types.Scene.loom = bpy.props.PointerProperty(type=properties.scene_props.LOOM_PG_scene_settings)

    # Hotkey registration
    addon_name = __package__
    # Check if preferences are available (they might not be during initial registration)
    try:
        prefs = bpy.context.preferences.addons[addon_name].preferences
        playblast = prefs.playblast_flag
    except KeyError:
        # Preferences not yet available, use default
        playblast = False
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Screen", space_type='EMPTY')
        if playblast:
            kmi = km.keymap_items.new("loom.playblast", 'F11', 'PRESS', ctrl=True, shift=True)
            kmi.active = True
            addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("loom.project_dialog", 'F1', 'PRESS', ctrl=True, shift=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("loom.rename_dialog", 'F2', 'PRESS', ctrl=True, shift=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("loom.open_output_folder", 'F3', 'PRESS', ctrl=True, shift=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("loom.encode_dialog", 'F9', 'PRESS', ctrl=True, shift=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("loom.render_flipbook", 'F10', 'PRESS', ctrl=True, shift=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("loom.batch_render_dialog", 'F12', 'PRESS', ctrl=True, shift=True, alt=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("loom.render_dialog", 'F12', 'PRESS', ctrl=True, shift=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))

        if platform.startswith('darwin'):
            if playblast:
                kmi = km.keymap_items.new("loom.playblast", 'F11', 'PRESS', oskey=True, shift=True)
                kmi.active = True
                addon_keymaps.append((km, kmi))
            kmi = km.keymap_items.new("loom.project_dialog", 'F1', 'PRESS', oskey=True, shift=True)
            kmi.active = True
            addon_keymaps.append((km, kmi))
            kmi = km.keymap_items.new("loom.rename_dialog", 'F2', 'PRESS', oskey=True, shift=True)
            kmi.active = True
            addon_keymaps.append((km, kmi))
            kmi = km.keymap_items.new("loom.open_output_folder", 'F3', 'PRESS', oskey=True, shift=True)
            kmi.active = True
            addon_keymaps.append((km, kmi))
            kmi = km.keymap_items.new("loom.encode_dialog", 'F9', 'PRESS', oskey=True, shift=True)
            kmi.active = True
            addon_keymaps.append((km, kmi))
            kmi = km.keymap_items.new("loom.render_flipbook", 'F10', 'PRESS', oskey=True, shift=True)
            kmi.active = True
            addon_keymaps.append((km, kmi))
            kmi = km.keymap_items.new("loom.batch_render_dialog", 'F12', 'PRESS', oskey=True, shift=True, alt=True)
            kmi.active = True
            addon_keymaps.append((km, kmi))
            kmi = km.keymap_items.new("loom.render_dialog", 'F12', 'PRESS', oskey=True, shift=True)
            kmi.active = True
            addon_keymaps.append((km, kmi))

    # Initialize global variables
    glob = prefs.global_variable_coll
    if not glob:
        for key, value in global_var_defaults.items():
            gvi = glob.add()
            gvi.name = key
            gvi.expr = value

    # Initialize project directories
    dirs = prefs.project_directory_coll
    if not dirs:
        for key, value in project_directories.items():
            di = dirs.add()
            di.name = value
            di.creation_flag = True

    # Append UI draw functions to Blender panels
    bpy.types.TOPBAR_MT_render.append(ui.draw_functions.draw_loom_render_menu)
    # TIME_MT_marker was removed in Blender 5.0 (Timeline merged into Dope Sheet)
    if hasattr(bpy.types, 'TIME_MT_marker'):
        bpy.types.TIME_MT_marker.append(ui.draw_functions.draw_loom_marker_menu)
    bpy.types.DOPESHEET_MT_marker.append(ui.draw_functions.draw_loom_marker_menu)
    bpy.types.NLA_MT_marker.append(ui.draw_functions.draw_loom_marker_menu)
    bpy.types.RENDER_PT_output.prepend(ui.draw_functions.draw_loom_outputpath)
    bpy.types.RENDER_PT_output.append(ui.draw_functions.draw_loom_version_number)
    bpy.types.RENDER_PT_output.append(ui.draw_functions.draw_loom_compositor_paths)
    bpy.types.RENDER_PT_stamp_note.prepend(ui.draw_functions.draw_loom_metadata)
    bpy.types.DOPESHEET_HT_header.append(ui.draw_functions.draw_loom_dopesheet)
    bpy.types.PROPERTIES_HT_header.append(ui.draw_functions.draw_loom_render_presets)
    bpy.types.LOOM_PT_render_presets.append(ui.draw_functions.draw_loom_preset_flags)
    bpy.types.LOOM_PT_render_presets.prepend(ui.draw_functions.draw_loom_preset_header)
    bpy.types.TOPBAR_MT_blender.append(ui.draw_functions.draw_loom_project)


def unregister():
    """Unregister all addon classes and handlers."""
    # Remove UI draw functions
    bpy.types.DOPESHEET_HT_header.remove(ui.draw_functions.draw_loom_dopesheet)
    bpy.types.RENDER_PT_output.remove(ui.draw_functions.draw_loom_compositor_paths)
    bpy.types.RENDER_PT_stamp_note.remove(ui.draw_functions.draw_loom_metadata)
    bpy.types.RENDER_PT_output.remove(ui.draw_functions.draw_loom_outputpath)
    bpy.types.RENDER_PT_output.remove(ui.draw_functions.draw_loom_version_number)
    bpy.types.NLA_MT_marker.remove(ui.draw_functions.draw_loom_marker_menu)
    bpy.types.DOPESHEET_MT_marker.remove(ui.draw_functions.draw_loom_marker_menu)
    # TIME_MT_marker was removed in Blender 5.0 (Timeline merged into Dope Sheet)
    if hasattr(bpy.types, 'TIME_MT_marker'):
        bpy.types.TIME_MT_marker.remove(ui.draw_functions.draw_loom_marker_menu)
    bpy.types.TOPBAR_MT_render.remove(ui.draw_functions.draw_loom_render_menu)
    bpy.types.PROPERTIES_HT_header.remove(ui.draw_functions.draw_loom_render_presets)
    bpy.types.LOOM_PT_render_presets.remove(ui.draw_functions.draw_loom_preset_flags)
    bpy.types.LOOM_PT_render_presets.remove(ui.draw_functions.draw_loom_preset_header)
    bpy.types.TOPBAR_MT_blender.remove(ui.draw_functions.draw_loom_project)

    # Unregister modules in reverse order
    handlers.unregister()
    presets.unregister()
    operators.unregister()
    ui.unregister()
    properties.unregister()

    # Remove keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    # Remove scene property
    del bpy.types.Scene.loom


if __name__ == "__main__":
    register()
