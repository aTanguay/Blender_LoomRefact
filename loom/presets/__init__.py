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
Preset modules for Loom addon.

This package contains preset system for saving and loading render settings.
"""

import bpy

# Import preset modules
from . import render_presets

# Collect all classes for registration
classes = (
    *render_presets.classes,
)


def register():
    """Register all preset classes."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister all preset classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
