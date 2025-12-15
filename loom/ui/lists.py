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
UIList classes for Loom addon.

Contains list display classes for global variables, project directories,
and batch render queue.
"""

import bpy
import os

# Import helpers
from ..helpers.globals_utils import isevaluable


class LOOM_UL_globals(bpy.types.UIList):
    """UIList for displaying global variable definitions."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.2)
        eval_icon = 'FILE_SCRIPT' if isevaluable(item.expr) else 'ERROR'
        var_icon = 'RADIOBUT_ON' if item.name.startswith("$") else 'RADIOBUT_OFF'
        split.prop(item, "name", text="", emboss=False, translate=False, icon=var_icon)
        split.prop(item, "expr", text="", emboss=True, translate=False, icon=eval_icon)

    def invoke(self, context, event):
        pass


class LOOM_UL_directories(bpy.types.UIList):
    """UIList for displaying project directory entries."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.05)
        split.label(text="{:02d}".format(index+1))
        row = split.row(align=True)
        row.prop(item, "name", text="", icon='FILE_FOLDER')
        row.prop(item, "creation_flag", text="", icon='RADIOBUT_ON' if item.creation_flag else 'RADIOBUT_OFF')

    def invoke(self, context, event):
        pass


class LOOM_UL_batch_list(bpy.types.UIList):
    """UIList for displaying batch render queue items."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences

        if prefs.batch_paths_flag:
            split = layout.split(factor=prefs.batch_path_col_width, align=True)
            split_left = split.split(factor=0.08)
            split_left.label(text="{:02d}".format(index+1))
            split_left.label(text=item.path, icon='FILE_BLEND')
        else:
            split = layout.split(factor=prefs.batch_name_col_width, align=True)
            split_left = split.split(factor=0.1)
            split_left.operator(
                "loom.batch_default_range",
                text="{:02d}".format(index+1),
                emboss=False).item_id = index
            split_left.label(text=item.name, icon='FILE_BLEND')

        split_right = split.split(factor=.99)
        row = split_right.row(align=True)
        row.operator(
            "loom.batch_default_range",
            icon="PREVIEW_RANGE",
            text="").item_id = index
        row.prop(item, "frames", text="")
        row.prop(item, "input_filter", text="", icon='FILTER')
        row.prop(item, "encode_flag", text="", icon='FILE_MOVIE')
        row.operator(
            "loom.batch_verify_input",
            text="",
            icon='GHOST_ENABLED').item_id = index
        row.separator()
        row.operator("loom.open_folder",
                icon="DISK_DRIVE", text="").folder_path = os.path.dirname(item.path)

    def invoke(self, context, event):
        pass


# Classes for registration
classes = (
    LOOM_UL_globals,
    LOOM_UL_directories,
    LOOM_UL_batch_list,
)
