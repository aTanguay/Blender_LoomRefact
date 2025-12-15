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
Menu classes for Loom addon.

Contains menu definitions for batch display settings, render presets,
main render menu, and marker utilities.
"""

import bpy


class LOOM_MT_display_settings(bpy.types.Menu):
    """Menu for batch render display settings."""

    bl_label = "Loom Batch Display Settings"
    bl_idname = "LOOM_MT_display_settings"

    def draw(self, context):
        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
        layout = self.layout
        layout.label(text="Display Settings", icon="COLOR")
        layout.separator()
        layout.prop(prefs, "batch_paths_flag")
        layout.prop(prefs, "batch_dialog_rows")
        if prefs.batch_paths_flag:
            layout.prop(prefs, "batch_path_col_width")
        else:
            layout.prop(prefs, "batch_name_col_width")
        layout.operator("loom.batch_dialog_reset", icon="ANIM")


class LOOM_MT_render_presets(bpy.types.Menu):
    """Menu for render preset selection."""

    bl_label = 'Loom Render Presets'
    preset_subdir = 'loom/render_presets'
    preset_operator = 'script.execute_preset'
    draw = bpy.types.Menu.draw_preset


class LOOM_MT_render_menu(bpy.types.Menu):
    """Main Loom render menu."""

    bl_label = "Loom"
    bl_idname = "LOOM_MT_render_menu"

    def draw(self, context):
        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
        layout = self.layout
        layout.operator("loom.render_dialog", icon='SEQUENCE')
        layout.operator("loom.batch_dialog", icon='FILE_MOVIE', text="Batch Render and Encode")
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("loom.render_flipbook", icon='RENDER_RESULT')
        if prefs.playblast_flag:
            layout.operator("loom.playblast", icon='PLAY', text="Loom Playblast")
        layout.separator()
        layout.operator("loom.encode_dialog", icon='RENDER_ANIMATION', text="Encode Image Sequence")
        layout.operator("loom.rename_dialog", icon="SORTALPHA")
        layout.separator()
        layout.operator("loom.open_output_folder", icon='FOLDER_REDIRECT')
        layout.operator("loom.open_preferences", icon='PREFERENCES', text="Loom Preferences")


class LOOM_MT_marker_menu(bpy.types.Menu):
    """Menu for marker utilities."""

    bl_label = "Loom"
    bl_idname = "LOOM_MT_marker_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("loom.utils_marker_generate", icon='CON_CAMERASOLVER', text="Markers from Cameras")
        layout.operator("loom.utils_marker_unbind", icon='UNLINKED', text="Unbind Selected Markers")
        layout.operator("loom.utils_marker_rename", icon='FONT_DATA', text="Batch Rename Markers")


# Classes for registration
classes = (
    LOOM_MT_display_settings,
    LOOM_MT_render_presets,
    LOOM_MT_render_menu,
    LOOM_MT_marker_menu,
)
