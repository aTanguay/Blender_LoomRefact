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
Draw functions for UI integration in Loom addon.

Contains functions that append Loom UI elements to existing Blender panels
and areas (Output, Metadata, Dopesheet, etc.).
"""

import bpy
import os
import re

# Import helpers
from ..helpers.globals_utils import replace_globals
from ..helpers.blender_compat import get_compositor_node_tree


def draw_loom_preset_flags(self, context):
    """Append preset flags to preset dialog."""
    preset_flags = context.scene.loom.render_preset_flags
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False
    layout.separator(factor=0.5)
    layout.emboss='NORMAL'
    col = layout.column(heading="Also include:")
    col.prop(preset_flags, "include_resolution")
    col.prop(preset_flags, "include_file_format")
    col.prop(preset_flags, "include_output_path")
    col.prop(preset_flags, "include_scene_settings", text="Scene Camera")
    col.prop(preset_flags, "include_passes")
    col.prop(preset_flags, "include_color_management")
    col.prop(preset_flags, "include_metadata")
    layout.separator(factor=0.3)


def draw_loom_preset_header(self, context):
    """Prepend header to preset dialog."""
    addon_name = __package__.split('.')[0]
    layout = self.layout
    preset_dir = context.preferences.addons[addon_name].preferences.render_presets_path
    row = layout.row(align=True)
    row.operator("loom.open_folder", icon="RENDER_STILL", text="", emboss=False).folder_path = preset_dir
    row.label(text=" Loom Render Presets")
    layout.separator(factor=0.3)


def draw_loom_render_menu(self, context):
    """Append Loom render menu to Topbar > Render menu."""
    layout = self.layout
    layout.separator()
    layout.menu("LOOM_MT_render_menu", icon='RENDER_STILL')


def draw_loom_marker_menu(self, context):
    """Append marker utilities to Marker menu."""
    layout = self.layout
    layout.separator()
    layout.operator("loom.utils_marker_generate", icon='CON_CAMERASOLVER', text="Markers from Cameras")
    layout.operator("loom.utils_marker_unbind", icon='UNLINKED', text="Unbind Selected Markers")
    layout.operator("loom.utils_marker_rename", icon='FONT_DATA', text="Batch Rename Markers")


def draw_loom_version_number(self, context):
    """Append Version Number Slider to the Output Area."""
    addon_name = __package__.split('.')[0]
    if re.search(r"v\d+", context.scene.render.filepath) is not None:
        glob_vars = context.preferences.addons[addon_name].preferences.global_variable_coll
        output_folder, file_name = os.path.split(bpy.path.abspath(context.scene.render.filepath))
        if any(ext in output_folder for ext in glob_vars.keys()):
            output_folder = replace_globals(output_folder, addon_name)
        else:
            output_folder = os.path.dirname(context.scene.render.frame_path())

        layout = self.layout
        row = layout.row(align=True)
        row.prop(context.scene.loom, "output_render_version")
        row.prop(context.scene.loom, "output_sync_comp", text="", toggle=True, icon="IMAGE_RGB_ALPHA")


def draw_loom_outputpath(self, context):
    """Append compiled file path using globals to the Output Area."""
    addon_name = __package__.split('.')[0]
    prefs = context.preferences.addons[addon_name].preferences
    glob_vars = prefs.global_variable_coll
    scn = context.scene

    if prefs.output_extensions or not scn.render.filepath:
        return

    output_folder, file_name = os.path.split(bpy.path.abspath(scn.render.filepath))
    output_folder = os.path.realpath(output_folder)

    if not file_name and bpy.data.is_saved:
        blend_name, ext = os.path.splitext(os.path.basename(bpy.data.filepath))
        file_name = blend_name + "_"

    if not file_name.count('#'):
        if not bool(re.search(r'\d+\.[a-zA-Z0-9]{3,4}\b', file_name)):
            file_name = "{}{}".format(file_name, "#"*4)
    else:
        file_name = re.sub(r"(?!#+$|#+\.[a-zA-Z0-9]{3,4}\b)#+", '', file_name)

    globals_flag = False
    if any(ext in file_name for ext in glob_vars.keys()):
        file_name = replace_globals(file_name, addon_name)
        globals_flag = True
    if any(ext in output_folder for ext in glob_vars.keys()):
        output_folder = replace_globals(output_folder, addon_name)
        globals_flag = True

    if file_name.endswith(tuple(scn.render.file_extension)):
        file_path = os.path.join(output_folder, file_name)
    else:
        file_path = os.path.join(output_folder, "{}{}".format(file_name, scn.render.file_extension))

    layout = self.layout
    box = layout.box()
    row = box.row()

    if not os.path.isdir(output_folder):
        row.operator("loom.utils_create_directory",
            icon='ERROR', text="", emboss=False).directory = os.path.dirname(file_path)
    else:
        row.operator("loom.open_output_folder", icon='DISK_DRIVE', text="", emboss=False)

    if scn.render.is_movie_format:
        row.label(text="Video file formats are not supported by Loom")
    else:
        row.label(text="{}".format(file_path if not scn.loom.is_rendering else scn.render.filepath))

    sub_row = row.row(align=True)

    original_paths = context.scene.loom.path_collection
    if globals_flag or context.scene.loom.path_collection:
        if len(original_paths) and not original_paths[0].orig == context.scene.render.filepath:
            sub_row.operator("loom.bake_globals", icon="RECOVER_LAST", text="").action='RESET'
        sub_row.operator("loom.bake_globals", icon="WORLD_DATA", text="").action='APPLY'

    sub_row.operator("loom.output_paths", icon="EXTERNAL_DRIVE", text="")
    layout.separator(factor=0.1)


def draw_loom_compositor_paths(self, context):
    """Display File Output paths to the Output Area."""
    addon_name = __package__.split('.')[0]
    if bpy.context.preferences.addons[addon_name].preferences.output_extensions:
        return
    scene = context.scene
    node_tree = get_compositor_node_tree(scene)
    if all([node_tree is not None and hasattr(node_tree, "nodes"), scene.render.use_compositing, scene.use_nodes]):
        output_nodes = [n for n in node_tree.nodes if n.type=='OUTPUT_FILE']
        if len(output_nodes) > 0:
            lum = scene.loom
            layout = self.layout
            layout.separator()
            box = layout.box()
            row = box.row()
            row.label(text="Compositor Output Nodes", icon='NODETREE')
            icon = 'MODIFIER' if lum.comp_image_settings else 'MODIFIER_DATA'
            row.prop(lum, "comp_image_settings", icon=icon, text="", emboss=False)

            for o in output_nodes:
                row = box.row()
                i = "IMAGE_PLANE" if o.format.file_format == 'OPEN_EXR_MULTILAYER' else "RENDERLAYERS"
                row.prop(o, "base_path", text="{}".format(o.name), icon=i)
                row.operator("loom.open_folder",
                    icon='DISK_DRIVE', text="", emboss=False).folder_path = o.base_path

                if lum.comp_image_settings:
                    col = box.column()
                    col.template_image_settings(o.format, color_management=False)
                    col.separator()

            box.separator()
            layout.separator()


def draw_loom_metadata(self, context):
    """Append compiled stamp string using globals to the Metadata area."""
    addon_name = __package__.split('.')[0]
    prefs = context.preferences.addons[addon_name].preferences
    glob_vars = prefs.global_variable_coll
    scn = context.scene

    if not scn.render.use_stamp_note:
        return

    globals_flag = False
    note_text = scn.render.stamp_note_text
    if any(ext in note_text for ext in glob_vars.keys()):
        note_text = replace_globals(note_text, addon_name)
        globals_flag = True

    if globals_flag or "\\n" in note_text:
        layout = self.layout
        box = layout.box()
        row = box.row()
        txt = " " + note_text.replace("\\n", " ¶ ")
        icn = 'MESH_UVSPHERE'
        if scn.render.is_movie_format:
            txt = " Video file formats are not supported by Loom"
            icn = 'ERROR'
        row.label(text=txt)
        row.label(text="", icon=icn)


def draw_loom_project(self, context):
    """Append project dialog to app settings."""
    layout = self.layout
    layout.separator()
    layout.operator("loom.project_dialog", icon="OUTLINER")


def draw_loom_dopesheet(self, context):
    """Append popover to the dopesheet."""
    addon_name = __package__.split('.')[0]
    if not context.preferences.addons[addon_name].preferences.timeline_extensions:
        layout = self.layout
        row = layout.row()
        if context.space_data.mode == 'TIMELINE':
            row.operator("loom.utils_framerange", text="", icon='TRACKING_FORWARDS_SINGLE')
        row.separator()
        row.popover(panel="LOOM_PT_dopesheet", text="", icon='SEQUENCE')


def draw_loom_render_presets(self, context):
    """Append render presets to the header of the Properties Area."""
    layout = self.layout
    layout.emboss = 'NONE'
    row = layout.row(align=True)
    row.popover(panel="LOOM_PT_render_presets", text="", icon='PRESET')
