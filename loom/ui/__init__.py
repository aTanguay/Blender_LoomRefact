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
    """Register all UI classes."""
    # Register all classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Note: Draw functions are appended to Blender UI in the main __init__.py
    # after all modules are registered to ensure proper registration order


def unregister():
    """Unregister all UI classes."""
    # Note: Draw functions are removed from Blender UI in the main __init__.py

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
