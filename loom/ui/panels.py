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
Panel classes for Loom addon.

Contains panel definitions for render presets and dopesheet integration.
"""

import bpy
from bl_ui.utils import PresetPanel


class LOOM_PT_render_presets(PresetPanel, bpy.types.Panel):
    """Panel for render presets."""

    bl_label = 'Loom Render Presets'
    preset_subdir = 'loom/render_presets'
    preset_operator = 'script.execute_preset'
    preset_add_operator = 'loom.render_preset'


class LOOM_PT_dopesheet(bpy.types.Panel):
    """Dopesheet Render Options panel."""

    bl_label = "Loom"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'HEADER'
    bl_ui_units_x = 11

    def draw(self, context):
        scn = context.scene
        lum = scn.loom
        layout = self.layout
        row = layout.row()
        row.label(text="Loom", icon="RENDER_STILL")
        vp_icon = 'RESTRICT_VIEW_OFF' if lum.flipbook_flag else 'RESTRICT_VIEW_ON'
        row.prop(lum, "flipbook_flag", icon=vp_icon, text="", emboss=False)
        row = layout.row()

        col = layout.column()
        row = col.row(align=True)
        row.prop(lum, "scene_selection", icon="SCENE_DATA", text="")
        ka_op = row.operator("loom.selected_keys_dialog", text="Render Selected Keyframes")
        ka_op.limit_to_object_selection = lum.scene_selection
        ka_op.flipbook_dialog = lum.flipbook_flag
        col.separator(factor=0.05)
        row = col.row(align=True)
        row.prop(lum, "all_markers_flag", icon="TEMP", text="")
        ma_txt = "Render All Markers" if lum.all_markers_flag else "Render Active Markers"
        ma_op = row.operator("loom.selected_makers_dialog", text=ma_txt)
        ma_op.all_markers = lum.all_markers_flag
        ma_op.flipbook_dialog = lum.flipbook_flag

        col.separator(factor=1.5)
        txt = "Render Flipbook Animation" if lum.flipbook_flag else "Render Image Sequence"
        icon = 'RENDER_RESULT' if lum.flipbook_flag else 'SEQUENCE'
        di = col.operator("loom.render_input_dialog", icon=icon, text=txt)
        di.flipbook_dialog = lum.flipbook_flag
        di.frame_input = "{}-{}".format(scn.frame_start, scn.frame_end)
        di.operator_description = txt
        col.separator(factor=0.5)


# Classes for registration
classes = (
    LOOM_PT_render_presets,
    LOOM_PT_dopesheet,
)
