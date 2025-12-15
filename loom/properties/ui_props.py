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
UI-related property groups for Loom addon.

Contains property groups for global variables, project directories,
and generic arguments.
"""

import bpy


class LOOM_PG_globals(bpy.types.PropertyGroup):
    """Property group for global variable definitions."""
    # name: bpy.props.StringProperty()
    expr: bpy.props.StringProperty(name="Python Expression")


class LOOM_PG_project_directories(bpy.types.PropertyGroup):
    """Property group for project directory entries."""
    # name: bpy.props.StringProperty()
    creation_flag: bpy.props.BoolProperty()


class LOOM_PG_generic_arguments(bpy.types.PropertyGroup):
    """Property group for generic terminal arguments."""
    # name: bpy.props.StringProperty()
    value: bpy.props.StringProperty()
    idc: bpy.props.IntProperty()


# Classes for registration
classes = (
    LOOM_PG_globals,
    LOOM_PG_project_directories,
    LOOM_PG_generic_arguments,
)
