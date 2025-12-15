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

"""Property groups and preferences for Loom addon."""

import bpy

# Import property modules
from . import ui_props
from . import render_props
from . import scene_props
from . import preferences

# Collect all classes for registration (order matters!)
classes = (
    # UI property groups (must come before preferences that reference them)
    *ui_props.classes,
    # Render property groups (LOOM_PG_slots must come before LOOM_PG_paths)
    *render_props.classes,
    # Scene settings (references render_props classes)
    *scene_props.classes,
    # Preferences (references ui_props classes)
    *preferences.classes,
)


def register():
    """Register all property groups and preferences."""
    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Attach scene properties to bpy.types.Scene
    bpy.types.Scene.loom = bpy.props.PointerProperty(type=scene_props.LOOM_PG_scene_settings)


def unregister():
    """Unregister all property groups and preferences."""
    # Remove scene properties
    del bpy.types.Scene.loom

    # Unregister all classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


__all__ = [
    "ui_props",
    "render_props",
    "scene_props",
    "preferences",
    "classes",
    "register",
    "unregister",
]
