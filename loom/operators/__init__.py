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
Operator modules for Loom addon.

This package contains all operator classes organized by functionality.
"""

import bpy

# Import all operator modules
from . import (
    ui_operators,
    batch_operators,
    encode_operators,
    render_operators,
    playblast_operators,
    terminal_operators,
    utils_operators,
)

# Collect all classes for registration
classes = (
    *ui_operators.classes,
    *batch_operators.classes,
    *encode_operators.classes,
    *render_operators.classes,
    *playblast_operators.classes,
    *terminal_operators.classes,
    *utils_operators.classes,
)


def register():
    """Register all operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister all operator classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
