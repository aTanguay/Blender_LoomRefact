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

"""UI components (panels, menus, lists) for Loom addon."""

import bpy

# Import UI modules
from . import lists
from . import menus
from . import panels
from . import draw_functions

# Collect all classes for registration (order matters!)
classes = (
    # UIList classes
    *lists.classes,
    # Menu classes
    *menus.classes,
    # Panel classes
    *panels.classes,
)


def register():
    """Register all UI classes and append draw functions."""
    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Append draw functions to Blender UI
    # These functions add Loom UI elements to existing Blender panels
    bpy.types.TOPBAR_MT_render.append(draw_functions.draw_loom_render_menu)
    bpy.types.DOPESHEET_HT_header.append(draw_functions.draw_loom_dopesheet)
    bpy.types.DOPESHEET_MT_marker.append(draw_functions.draw_loom_marker_menu)
    bpy.types.PROPERTIES_HT_header.append(draw_functions.draw_loom_render_presets)

    # Output panel extensions
    bpy.types.RENDER_PT_output.append(draw_functions.draw_loom_version_number)
    bpy.types.RENDER_PT_output.append(draw_functions.draw_loom_outputpath)
    bpy.types.RENDER_PT_output.append(draw_functions.draw_loom_compositor_paths)

    # Metadata panel extension
    bpy.types.RENDER_PT_stamp.append(draw_functions.draw_loom_metadata)

    # Preset dialog hooks
    bpy.types.RENDER_PT_context.prepend(draw_functions.draw_loom_preset_header)
    bpy.types.RENDER_PT_context.append(draw_functions.draw_loom_preset_flags)


def unregister():
    """Unregister all UI classes and remove draw functions."""
    # Remove draw functions from Blender UI
    bpy.types.RENDER_PT_context.remove(draw_functions.draw_loom_preset_flags)
    bpy.types.RENDER_PT_context.remove(draw_functions.draw_loom_preset_header)
    bpy.types.RENDER_PT_stamp.remove(draw_functions.draw_loom_metadata)
    bpy.types.RENDER_PT_output.remove(draw_functions.draw_loom_compositor_paths)
    bpy.types.RENDER_PT_output.remove(draw_functions.draw_loom_outputpath)
    bpy.types.RENDER_PT_output.remove(draw_functions.draw_loom_version_number)
    bpy.types.PROPERTIES_HT_header.remove(draw_functions.draw_loom_render_presets)
    bpy.types.DOPESHEET_MT_marker.remove(draw_functions.draw_loom_marker_menu)
    bpy.types.DOPESHEET_HT_header.remove(draw_functions.draw_loom_dopesheet)
    bpy.types.TOPBAR_MT_render.remove(draw_functions.draw_loom_render_menu)

    # Unregister all classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


__all__ = [
    "lists",
    "menus",
    "panels",
    "draw_functions",
    "classes",
    "register",
    "unregister",
]
