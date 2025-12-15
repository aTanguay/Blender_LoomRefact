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
Addon preferences for Loom.

Contains the main preferences panel with all addon-level settings.
"""

import bpy
import os
import rna_keymap_ui
from sys import platform

# Import helpers
from ..helpers.globals_utils import isevaluable

# Import property groups that preferences references
from .ui_props import LOOM_PG_globals, LOOM_PG_project_directories

# Forward declarations for operators (will be resolved at runtime)
# These are referenced in the draw method but not imported to avoid circular deps
# LOOM_OT_globals_ui
# LOOM_OT_directories_ui
# LOOM_OT_delete_bash_files
# LOOM_OT_open_folder
# LOOM_OT_openURL
# LOOM_OT_preferences_reset

# Global for tracking user keymap IDs
user_keymap_ids = []
addon_keymaps = []


class LOOM_AP_preferences(bpy.types.AddonPreferences):
    """Addon preferences for Loom."""

    bl_idname = __package__.split('.')[0]  # Gets 'loom' from 'loom.properties.preferences'

    terminal: bpy.props.EnumProperty(
        name="Terminal",
        items=(
            ("win-default", "Windows Default Terminal", "", 1),
            ("osx-default", "OSX Default Terminal", "", 2),
            ("x-terminal-emulator", "X Terminal Emulator", "", 3),
            ("xfce4-terminal", "Xfce4 Terminal", "", 4),
            ("xterm", "xterm", "", 5)))

    xterm_flag: bpy.props.BoolProperty(
        name="Use Xterm (Terminal Fallback)",
        description="Serves as fallback for OSX and others",
        default=False)

    bash_file: bpy.props.StringProperty(
        name="Bash file",
        description = "Filepath to temporary bash or bat file")

    bash_flag: bpy.props.BoolProperty(
        name="Force Bash File",
        description="Force using bash file instead of individual arguments",
        default=False)

    render_dialog_width: bpy.props.IntProperty(
        name="Render Dialog Width",
        description = "Width of Image Sequence Render Dialog",
        subtype='PIXEL',
        default=450, min=400)

    encode_dialog_width: bpy.props.IntProperty(
        name="Encoding/Rename Dialog Width",
        description = "Width of Encoding and Rename Dialog",
        subtype='PIXEL',
        default=650, min=400)

    project_dialog_width: bpy.props.IntProperty(
        name="Project Dialog Width",
        description = "Width of Project Dialog",
        subtype='PIXEL',
        default=650, min=400)

    timeline_extensions: bpy.props.BoolProperty(
        name="Timeline Extensions",
        description="Do not display Loom operators in the Timeline",
        default=False)

    output_extensions: bpy.props.BoolProperty(
        name="Output Panel Extensions",
        description="Do not display all File Output nodes and the final Output Path in the Output Panel",
        default=False)

    log_render: bpy.props.BoolProperty(
        name="Logging (Required for Playback)",
        description="If enabled render output properties will be saved",
        default=True)

    log_render_limit: bpy.props.IntProperty(
        name="Log Limit",
        default=3)

    playblast_flag: bpy.props.BoolProperty(
        name="Playblast (Experimental)",
        description="Playback rendered sequences",
        default=False)

    user_player: bpy.props.BoolProperty(
        name="Default Animation Player",
        description="Use default player (User Preferences > File Paths)",
        default=False)

    ffmpeg_path: bpy.props.StringProperty(
        name="FFmpeg Binary",
        description="Path to ffmpeg",
        maxlen=1024,
        subtype='FILE_PATH')

    snapshot_directory: bpy.props.StringProperty(
        name="Snapshot Directory",
        description="Path of the Snapshot directory",
        maxlen=1024,
        default="//temp",
        subtype='DIR_PATH')

    default_codec: bpy.props.StringProperty(
        name="User Codec",
        description = "Default user codec")

    batch_dialog_width: bpy.props.IntProperty(
        name="Batch Dialog Width",
        description="Width of Batch Render Dialog",
        subtype='PIXEL',
        default=750, min=600, max=1800)

    batch_dialog_rows: bpy.props.IntProperty(
        name="Number of Rows",
        description="Number of Rows",
        min=7, max=40,
        default=9)

    batch_paths_flag: bpy.props.BoolProperty(
        name="Display File Paths",
        description="Display File paths")

    batch_path_col_width: bpy.props.FloatProperty(
        name="Path Column Width",
        description="Width of path column in list",
        default=0.6, min=0.3, max=0.8)

    batch_name_col_width: bpy.props.FloatProperty(
        name="Name Column Width",
        description="Width of name column in list",
        default=0.45, min=0.3, max=0.8)

    render_background: bpy.props.BoolProperty(
        name="Render in Background",
        description="Do not activate the Console",
        default=False)

    global_variable_coll: bpy.props.CollectionProperty(
        name="Global Variables",
        type=LOOM_PG_globals)

    global_variable_idx: bpy.props.IntProperty(
        name="Index",
        default=0)

    expression: bpy.props.StringProperty(
        name="Expression",
        description = "Test Expression",
        options={'SKIP_SAVE'})

    project_directory_coll: bpy.props.CollectionProperty(
        name="Project Folders",
        type=LOOM_PG_project_directories)

    project_coll_idx: bpy.props.IntProperty(
        name="Index",
        default=0)

    render_presets_path: bpy.props.StringProperty(
        subtype = "FILE_PATH",
        default = bpy.utils.user_resource(
            'SCRIPTS',
            path=os.path.join("presets", "loom", "render_presets")))

    render_display_type: bpy.props.EnumProperty(
        name="Render Display Type",
        description="Location where rendered images will be displayed to",
        items=[ ('NONE', "Keep User Interface", ""),
                ('AREA', "Image Editor", ""),
                ('WINDOW', "New Window", "")
              ],
        default='WINDOW'
        )

    display_general: bpy.props.BoolProperty(
        default=True)

    display_globals: bpy.props.BoolProperty(
        default=False)

    display_directories: bpy.props.BoolProperty(
        default=False)

    display_presets: bpy.props.BoolProperty(
        default=False)

    display_advanced: bpy.props.BoolProperty(
        default=False)

    display_hotkeys: bpy.props.BoolProperty(
        default=True)

    def draw_state(self, prop):
        return 'RADIOBUT_OFF' if not prop else 'RADIOBUT_ON'

    def draw(self, context):
        split_width = 0.5
        layout = self.layout

        """ General """
        box_general = layout.box()
        row = box_general.row()
        row.prop(self, "display_general",
            icon="TRIA_DOWN" if self.display_general else "TRIA_RIGHT",
            icon_only=True, emboss=False)
        row.label(text="General")

        if self.display_general:
            split = box_general.split(factor=split_width)
            col = split.column()
            col.prop(self, "render_dialog_width")
            col.prop(self, "batch_dialog_width")
            col = split.column()
            col.prop(self, "project_dialog_width")
            col.prop(self, "encode_dialog_width")

            split = box_general.split(factor=split_width)
            col = split.column()
            col.prop(self, "timeline_extensions", toggle=True, icon=self.draw_state(not self.timeline_extensions))
            col.prop(self, "output_extensions", toggle=True, icon=self.draw_state(not self.output_extensions))
            col = split.column()
            col.prop(self, "playblast_flag", toggle=True, icon=self.draw_state(self.playblast_flag))
            upl = col.column()
            upl.prop(self, "user_player", toggle=True, icon=self.draw_state(self.user_player))
            upl.enabled = self.playblast_flag

            box_general.row().prop(self, "ffmpeg_path")
            box_general.row()

        """ Globals """
        box_globals = layout.box()
        row = box_globals.row()
        row.prop(self, "display_globals",
            icon="TRIA_DOWN" if self.display_globals else "TRIA_RIGHT",
            icon_only=True, emboss=False)
        row.label(text="Globals (File Output)")

        if self.display_globals:
            row = box_globals.row()
            row.template_list(
                listtype_name = "LOOM_UL_globals",
                list_id = "",
                dataptr = self,
                propname = "global_variable_coll",
                active_dataptr = self,
                active_propname = "global_variable_idx",
                rows=6)
            col = row.column(align=True)
            col.operator("loom.globals_ui", icon='ADD', text="").action = 'ADD'
            col.operator("loom.globals_ui", icon='REMOVE', text="").action = 'REMOVE'
            col.separator()
            col.operator("wm.save_userpref", text="", icon="CHECKMARK")
            col.separator()
            exp_box = box_globals.box()
            row = exp_box.row()
            row.label(text='Expression Tester')
            row = exp_box.row()
            split = row.split(factor=0.2)
            split.label(text="Expression:", icon='FILE_SCRIPT')
            split.prop(self, "expression", text="")
            if not self.expression or self.expression.isspace():
                eval_info = "Nothing to evaluate"
            else:
                eval_info = eval(self.expression) if isevaluable(self.expression) else "0"
            row = exp_box.row()
            split = row.split(factor=0.2)
            split.label(text="Result:", icon='FILE_VOLUME')
            split.label(text="{}".format(eval_info))
            box_globals.row()

        """ Project Directories """
        box_dirs = layout.box()
        row = box_dirs.row()
        row.prop(self, "display_directories",
            icon="TRIA_DOWN" if self.display_directories else "TRIA_RIGHT",
            icon_only=True, emboss=False)
        row.label(text="Project Directories")

        if self.display_directories:
            row = box_dirs.row()
            row.template_list(
                listtype_name = "LOOM_UL_directories",
                list_id = "",
                dataptr = self,
                propname = "project_directory_coll",
                active_dataptr = self,
                active_propname = "project_coll_idx",
                rows=6)
            col = row.column(align=True)
            col.operator("loom.directories_ui", icon='ADD', text="").action = 'ADD'
            col.operator("loom.directories_ui", icon='REMOVE', text="").action = 'REMOVE'
            box_dirs.row()

        """ Advanced """
        box_advanced = layout.box()
        row = box_advanced.row()
        row.prop(self, "display_advanced",
            icon="TRIA_DOWN" if self.display_advanced else "TRIA_RIGHT",
            icon_only=True, emboss=False)
        row.label(text="Advanced Settings")

        if self.display_advanced:
            split = box_advanced.split(factor=split_width)

            lft = split.column() # Left
            fsh = lft.column(align=True)
            txt = "Force generating .bat file" if platform.startswith('win32') else "Force generating .sh file"
            lft.prop(self, "bash_flag", text=txt, toggle=True, icon=self.draw_state(self.bash_flag))

            rsh = lft.row(align=True)
            txt = "Delete temporary .bat Files" if platform.startswith('win32') else "Delete temporary .sh files"
            rsh.operator("loom.delete_bash_files", text=txt, icon="FILE_SCRIPT")
            script_folder = bpy.utils.script_path_user()
            rsh.operator("loom.open_folder", icon="DISK_DRIVE", text="").folder_path = script_folder

            rgt = split.column() # Right
            rbg = rgt.column(align=True)
            rbg.prop(self, "render_background", toggle=True, icon=self.draw_state(self.render_background))

            rgt.column(align=True)
            xtm = rgt.row(align=True)
            xtm.prop(self, "xterm_flag", toggle=True, icon=self.draw_state(self.xterm_flag))
            wp = xtm.operator("loom.open_url", icon='HELP', text="")
            wp.description = "Open the Wikipedia page about Xterm"
            wp.url = "https://en.wikipedia.org/wiki/Xterm"

            """ OSX specific properties """
            if platform.startswith('darwin'):
                fsh.enabled = False
                rbg.enabled = True

            box_advanced.row()
            box_advanced.row().prop(self, "snapshot_directory")
            box_advanced.row()

        """ Hotkeys """
        box_hotkeys = layout.box()
        row = box_hotkeys.row()
        row.prop(self, "display_hotkeys",
            icon="TRIA_DOWN" if self.display_hotkeys else "TRIA_RIGHT",
            icon_only=True, emboss=False)
        row.label(text="Hotkeys")

        if self.display_hotkeys:
            split = box_hotkeys.split()
            col = split.column()
            kc_usr = bpy.context.window_manager.keyconfigs.user
            km_usr = kc_usr.keymaps.get('Screen')

            if not user_keymap_ids: # Ouch, Todo!
                for kmi_usr in km_usr.keymap_items:
                    for km_addon, kmi_addon in addon_keymaps:
                        if kmi_addon.compare(kmi_usr):
                            user_keymap_ids.append(kmi_usr.id)
            for kmi_usr in km_usr.keymap_items: # user hotkeys by namespace
                if kmi_usr.idname.startswith("loom."):
                    col.context_pointer_set("keymap", km_usr)
                    rna_keymap_ui.draw_kmi([], kc_usr, km_usr, kmi_usr, col, 0)
            box_hotkeys.row()

        """ Reset Prefs """
        layout.operator("loom.preferences_reset", icon='RECOVER_LAST')


# Classes for registration
classes = (
    LOOM_AP_preferences,
)
