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
Batch rendering operators for Loom addon.

Contains operators for managing batch rendering of multiple blend files.
"""

import bpy
from bpy_extras.io_utils import ImportHelper
import os
import re
import subprocess
import errno
from sys import platform
from time import strftime

# Import blend_render_info from Blender's modules
from blend_render_info import read_blend_rend_chunk

# Import helpers
from ..helpers.frame_utils import filter_frames
from ..helpers.globals_utils import user_globals

# Import from other operators for callbacks
from . import encode_operators


class LOOM_OT_batch_dialog(bpy.types.Operator):
    """Loom Batch Render Dialog"""
    bl_idname = "loom.batch_render_dialog"
    bl_label = "Loom Batch"
    bl_options = {'REGISTER'}

    colorspace: bpy.props.EnumProperty(
        name="Colorspace",
        description="colorspace",
        items='encode_operators.colorspace_callback')

    codec: bpy.props.EnumProperty(
        name="Codec",
        description="Codec",
        items='encode_operators.codec_callback')

    fps: bpy.props.IntProperty(
        name="Frame Rate",
        description="Frame Rate",
        default=25, min=1)

    terminal: bpy.props.BoolProperty(
        name="Terminal Instance",
        description="Render in new Terminal Instance",
        default=True)

    override_render_settings: bpy.props.BoolProperty(
        name="Override Render Settings",
        default=False)

    render_preset: bpy.props.StringProperty(
        name="Render Preset",
        description="Pass a custom Preset.py")

    shutdown: bpy.props.BoolProperty(
        name="Shutdown",
        description="Shutdown when done",
        default=False)

    def determine_type(self, val): #val = ast.literal_eval(s)
        if (isinstance(val, int)):
            return ("chi")
        elif (isinstance(val, float)):
            return ("chf")
        if val in ["true", "false"]:
            return ("chb")
        else:
            return ("chs")

    def pack_multiple_cmds(self, dct):
        rna_lst = []
        for key, args in dct.items():
            for i in args:
                rna_lst.append({"idc": key, "name": self.determine_type(i), "value": str(i)})
        return rna_lst

    def pack_arguments(self, lst):
        return [{"idc": 0, "name": self.determine_type(i), "value": str(i)} for i in lst]

    def write_permission(self, folder): # Hacky, but ok for now
        # https://stackoverflow.com/q/2113427/3091066
        try: # os.access(os.path.realpath(bpy.path.abspath(out_folder)), os.W_OK)
            pf = os.path.join(folder, "permission.txt")
            fh = open(pf, 'w')
            fh.close()
            os.remove(pf)
            return True
        except:
            return False

    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def verify_app(self, cmd):
        try:
            subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as e:
            if e.errno == errno.ENOENT:
                return False
        return True

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
        lum = context.scene.loom
        black_list = []

        """ Error handling """
        user_error = False
        ffmpeg_error = False

        if not bool(lum.batch_render_coll):
            self.report({'ERROR'}, "No files to render.")
            user_error = True

        for item in lum.batch_render_coll:
            if not item.frames and not any(char.isdigit() for char in item.frames):
                self.report({'ERROR'}, "{} [wrong frame input]".format(item.name))
                user_error = True

            if not os.path.isfile(item.path):
                self.report({'ERROR'}, "{} does not exist anymore".format(item.name))
                user_error = True

            """ encode errors """
            if item.encode_flag:

                """ Verify ffmpeg """
                if not prefs.ffmpeg_path:
                    if self.verify_app(["ffmpeg", "-h"]):
                        prefs.ffmpeg_path = "ffmpeg"
                    else:
                        ffmpeg_error = True

                elif prefs.ffmpeg_path and prefs.ffmpeg_path != "ffmpeg":
                    if not os.path.isabs(prefs.ffmpeg_path) or prefs.ffmpeg_path.startswith('//'):
                        ffmpeg_bin = os.path.realpath(bpy.path.abspath(prefs.ffmpeg_path))
                        if os.path.isfile(ffmpeg_bin):
                            prefs.ffmpeg_path = ffmpeg_bin
                    if not self.verify_app([prefs.ffmpeg_path, "-h"]):
                        ffmpeg_error = True

                """ verify frames """
                frames_user = filter_frames(frame_input=item.frames, filter_individual=item.input_filter)
                if self.missing_frames(frames_user):
                    black_list.append(item.name)
                    info = "Encoding {} will be skipped [Missing Frames]".format(item.name)
                    self.report({'INFO'}, info)

            """
            out_folder, out_filename = os.path.split(bpy.path.abspath(context.scene.render.filepath))
            if not self.write_permission(os.path.realpath(out_folder)):
                self.report({'ERROR'}, "Specified output folder does not exist (permission denied)")
                user_error = True
            """

        if len(black_list) > 1:
            self.report({'ERROR'}, "Can not encode: {} (missing frames)".format(", ".join(black_list)))
            user_error = True

        if user_error or ffmpeg_error:
            if ffmpeg_error:
                self.report({'ERROR'}, "Path to ffmpeg binary not set in Addon preferences")
            bpy.ops.loom.batch_render_dialog('INVOKE_DEFAULT')
            return {"CANCELLED"}

        if not self.properties.is_property_set("render_preset"):
            self.render_preset = lum.custom_render_presets
        else:
            preset_path = os.path.join(prefs.render_presets_path, self.render_preset)
            if not os.path.exists(preset_path):
                self.report({'ERROR'}, "Given preset file does not exist {}".format(preset_path))
                bpy.ops.loom.batch_render_dialog('INVOKE_DEFAULT')
                return {"CANCELLED"}

        # Wrap blender binary path in quotations
        bl_bin = '"{}"'.format(bpy.app.binary_path) if not platform.startswith('win32') else bpy.app.binary_path

        cli_arg_dict = {}
        for c, item in enumerate(lum.batch_render_coll):
            python_expr = ("import bpy;" +\
                    "bpy.ops.render.image_sequence(" +\
                    "frames='{fns}', isolate_numbers={iel}," +\
                    "render_silent={cli}").format(
                        fns=item.frames,
                        iel=item.input_filter,
                        cli=True)

            if self.override_render_settings and self.render_preset != 'EMPTY':
                python_expr += ", render_preset='{pst}'".format(pst=self.render_preset)

            python_expr += ");"
            python_expr += "bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)"
            #print(type(python_expr), python_expr, self.render_preset)

            cli_args = [bl_bin, "-b", item.path, "--python-expr", python_expr]
            cli_arg_dict[c] = cli_args

        coll_len = len(cli_arg_dict)
        for c, item in enumerate(lum.batch_render_coll):
            if item.encode_flag and item.name not in black_list:
                # bpy.context.scene.loom.render_collection[-1]['file_path'];
                # seq_path=bpy.context.scene.render.frame_path(frame=1);
                python_expr = ("import bpy;" +\
                            "ext=bpy.context.scene.render.file_extension;" +\
                            "seq_path=bpy.context.scene.render.filepath+ext;" +\
                            "bpy.ops.loom.encode_dialog(" +\
                            "sequence=seq_path," +\
                            "fps={fps}," +\
                            "codec='{cdc}'," +\
                            "colorspace='{cls}'," +\
                            "terminal_instance=False," +\
                            "pause=False)").format(
                                fps = self.fps,
                                cdc = self.codec,
                                cls = self.colorspace)

                cli_args = [bl_bin, "-b", item.path, "--python-expr", python_expr]
                cli_arg_dict[c+coll_len] = cli_args

        """ Start headless batch """
        bpy.ops.loom.run_terminal(
            #debug_arguments=True,
            binary="",
            terminal_instance=self.terminal,
            argument_collection=self.pack_multiple_cmds(cli_arg_dict),
            bash_name="loom-batch-temp",
            force_bash=True,
            shutdown=self.shutdown)

        return {'FINISHED'}

    def invoke(self, context, event):
        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
        context.scene.loom.property_unset("custom_render_presets")
        return context.window_manager.invoke_props_dialog(self,
            width=(prefs.batch_dialog_width))

    def check(self, context):
        return True

    def draw(self, context):
        from ..properties.render_props import render_preset_callback

        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
        scn = context.scene
        lum = scn.loom

        layout = self.layout
        row = layout.row()

        row.template_list(
            listtype_name = "LOOM_UL_batch_list",
            list_id = "",
            dataptr = lum,
            propname = "batch_render_coll",
            active_dataptr = lum,
            active_propname = "batch_render_idx",
            rows=prefs.batch_dialog_rows)

        col = row.column(align=True)
        col.operator("loom.batch_select_blends", icon='ADD', text="")
        col.operator("loom.batch_dialog_action", icon='REMOVE', text="").action = 'REMOVE'
        col.menu("LOOM_MT_display_settings", icon='DOWNARROW_HLT', text="")
        col.separator()
        col.separator()
        col.operator("loom.batch_dialog_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("loom.batch_dialog_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        layout.row() # Separator
        row = layout.row(align=True)
        col = row.column(align=True)
        col.operator("loom.batch_select_blends", icon="DOCUMENTS")
        row = col.row(align=True)
        row.operator("loom.batch_scandir_blends", icon='ZOOM_SELECTED') #VIEWZOOM
        if bpy.data.is_saved: # icon="WORKSPACE"
            row.operator("loom.batch_snapshot", icon="IMAGE_BACKGROUND", text="Add Snapshot")

        layout.row() # Separator
        row = layout.row(align=True)
        sub_row = row.row(align=True)
        sub_row.operator("loom.batch_remove_doubles", text="Remove Duplicates", icon="SEQ_SPLITVIEW")
        sub_row.operator("loom.batch_clear_list", text="Clear List", icon="PANEL_CLOSE")

        if any(i.encode_flag for i in lum.batch_render_coll):
            row = layout.row()
            row.separator()
            split_perc = 0.3
            row = layout.row()
            split = row.split(factor=split_perc)
            split.label(text="Colorspace")
            split.prop(self, "colorspace", text="")
            row = layout.row()
            split = row.split(factor=split_perc)
            split.label(text="Frame Rate")
            split.prop(self, "fps", text="")
            row = layout.row()
            split = row.split(factor=split_perc)
            split.label(text="Codec")
            split.prop(self, "codec", text="")
            row = layout.row()
            row.separator()

        layout.separator(factor=0.5)
        row = layout.row() #if platform.startswith('win32'):
        row.prop(self, "shutdown", text="Shutdown when done")
        if len(render_preset_callback(scn, context, addon_name)) > 1:
            settings_icon = 'MODIFIER_ON' if self.override_render_settings else 'MODIFIER_OFF'
            row.prop(self, "override_render_settings", icon=settings_icon, text="", emboss=False)
            if self.override_render_settings:
                layout.separator()
                layout.prop(lum, "custom_render_presets", text="Render Settings Override")
                layout.separator()
        row = layout.row()


class LOOM_OT_batch_snapshot(bpy.types.Operator):
    """Create a Snapshot from the current Blend File"""
    bl_idname = "loom.batch_snapshot"
    bl_label = "Snapshot"
    bl_options = {'INTERNAL'}
    bl_property = "file_name"

    snapshot_folder: bpy.props.StringProperty(
        name="Snapshot Folder",
        description="Folder to copy the snapshot to",
        default="//tmp",
        subtype='DIR_PATH')

    file_name: bpy.props.StringProperty(
        name="Filename",
        description="The filename used for the copy",
        default="",
        options={'SKIP_SAVE'})

    suffix: bpy.props.EnumProperty(
        name="Filename",
        description="Apply or Restore Paths",
        default = 'DATE',
        items=(
            ('DATE', "Date (no Suffix)", ""),
            ('NUMBSUFF', "Number Suffix", ""),
            ('DATESUFF', "Date Suffix", "")))

    overwrite: bpy.props.BoolProperty(
        name="Overwrite File",
        description="Overwrite existing files",
        default=False)

    convert_paths: bpy.props.BoolProperty(
        name="Convert Output Paths",
        description="Convert all output paths to absolute paths",
        default=True)

    apply_globals: bpy.props.BoolProperty(
        name="Apply Globals",
        default=False)

    globals_flag: bpy.props.BoolProperty(
        name="Globals Flag",
        options={'HIDDEN'},
        default=False)

    def number_suffix(self, filename_no_extension):
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename_no_extension)])
        return next(reversed(digits), None)

    def file_sequence(self, filepath, digits=None, extension=None):
        file_sequence = {}
        basedir, filename = os.path.split(filepath)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, ext = os.path.splitext(filename)
        num_suffix = self.number_suffix(filename_noext)
        filename = filename_noext.replace(num_suffix,'') if num_suffix else filename_noext
        if extension: ext = extension
        if digits:
            file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=filename, ds=digits, ex=ext)
        else:
            file_pattern = r"{fn}(\d+)\.?{ex}".format(fn=filename, ex=ext)

        for f in os.scandir(basedir):
            if f.name.endswith(ext) and f.is_file():
                match = re.match(file_pattern, f.name, re.IGNORECASE)
                if match: file_sequence[int(match.group(1))] = os.path.join(basedir, f.name)
        return file_sequence

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved

    def execute(self, context):
        addon_name = __package__.split('.')[0]
        snap_dir = self.snapshot_folder
        if not self.properties.is_property_set("snapshot_folder"):
            snap_dir = context.preferences.addons[addon_name].preferences.snapshot_directory

        basedir = os.path.realpath(bpy.path.abspath(snap_dir))
        fn_noext, ext = os.path.splitext(self.file_name)
        fn_noext = fn_noext if self.file_name else "00"
        ext = ext if ext else ".blend"

        ''' Create the folder if not present '''
        if not os.path.exists(basedir):
            bpy.ops.loom.create_directory(directory=basedir)

        ''' Format the filename '''
        fcopy = None
        if self.suffix == 'NUMBSUFF':
            leading_zeros = 2 # Expose?
            suff = "{:0{}d}".format(1, leading_zeros)
            bound_filename = suff if not self.file_name else "{}_{}".format(fn_noext, suff)
            fcopy = os.path.join(basedir, "{}{}".format(bound_filename, ext))

            if os.path.isfile(fcopy) and not self.overwrite:
                fs = self.file_sequence(fcopy, digits=leading_zeros)
                if fs:
                    suff = "{:0{}d}".format(max(fs.keys())+1, leading_zeros)
                    nextf = suff if not self.file_name else "{}_{}".format(fn_noext, suff)
                    #last_number, last_path = list(fs.items())[-1] # Python 3.8+
                    fcopy = os.path.join(basedir, "{}{}".format(nextf, ext))
        else:
            ft = strftime("%Y-%m-%d-%H-%M-%S")
            if self.suffix == 'DATE' and self.options.is_invoke:
                fcopy = os.path.join(basedir, "{}{}".format(ft, ext))
            else:
                date_fn = ft if not self.file_name else "{}_{}".format(fn_noext, ft)
                fcopy = os.path.join(basedir, "{}{}".format(date_fn, ext))

        ''' Save a copy and add it to Loom Batch '''
        if os.path.exists(basedir) and fcopy is not None:

            #relative_output_filepath = context.scene.render.filepath.startswith('//')
            if self.apply_globals: bpy.ops.loom.globals_bake(action='APPLY')
            if self.convert_paths: bpy.ops.loom.output_paths(action='ABSOLUTE')

            bpy.ops.wm.save_as_mainfile(filepath=fcopy, copy=True)

            if self.apply_globals: bpy.ops.loom.globals_bake(action='RESET')
            if not self.apply_globals and self.convert_paths:
                bpy.ops.loom.output_paths(action='RELATIVE')

            if not os.path.isfile(fcopy):
                self.report({'WARNING'},"Can not save a copy of the current file")
                return {"CANCELLED"}
            else:
                self.report({'INFO'},"Snapshot created: {}".format(fcopy))

            ''' Add the snapshot to the list '''
            if self.options.is_invoke:
                fd, fn = os.path.split(fcopy)
                scn = context.scene
                lum = scn.loom

                data = read_blend_rend_chunk(fcopy)
                if not data:
                    self.report({'WARNING'}, "Skipped {}, invalid .blend file".format(fcopy))
                    return {'CANCELLED'}
                else:
                    start, end, sc = data[0]
                    item = lum.batch_render_coll.add()
                    item.rid = len(lum.batch_render_coll)
                    item.name = fn
                    item.path = fcopy
                    item.frame_start = start
                    item.frame_end = end
                    item.scene = sc
                    item.frames = "{}-{}".format(item.frame_start, item.frame_end)
                    lum.batch_render_idx = len(lum.batch_render_coll)-1

        return {'FINISHED'}

    def invoke(self, context, event):
        addon_name = __package__.split('.')[0]
        if user_globals(context, addon_name):
            self.globals_flag = True
        if bpy.data.filepath:
            self.file_name = bpy.path.basename(bpy.data.filepath)[:-6]
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row = row.prop(self, "suffix", expand=True)
        if self.suffix != 'DATE':
            row = layout.row(align=True)
            row.prop(self, "file_name")

        row = layout.row(align=True)
        if self.globals_flag:
            row.prop(self, "apply_globals", toggle=True)
        row.prop(self, "convert_paths", toggle=True)
        '''
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "suffix", expand=True)
        if self.globals_flag:
            row = col.row(align=True)
            row.prop(self, "apply_globals", toggle=True)
        '''
        layout.row()


class LOOM_OT_batch_selected_blends(bpy.types.Operator, ImportHelper):
    """Select Blend Files via File Browser"""
    bl_idname = "loom.batch_select_blends"
    bl_label = "Select Blend Files"
    bl_options = {'INTERNAL'}

    filename_ext = ".blend"
    filter_glob: bpy.props.StringProperty(
            default="*.blend",
            options={'HIDDEN'},
            maxlen=255)

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    cursor_pos = [0,0]

    def display_popup(self, context):
        win = context.window #win.cursor_warp((win.width*.5)-100, (win.height*.5)+100)
        win.cursor_warp(x=self.cursor_pos[0], y=self.cursor_pos[1]+100) # re-invoke the dialog
        bpy.ops.loom.batch_render_dialog('INVOKE_DEFAULT')

    def cancel(self, context):
        if bpy.app.version < (4, 1, 0): self.display_popup(context)

    def invoke(self, context, event):
        self.cursor_pos = [event.mouse_x, event.mouse_y]
        self.filename = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        scn = context.scene
        lum = scn.loom

        valid_files, invalid_files = [], []
        start, end, sc = [1, 250, "Scene"]
        for i in self.files:
            path_to_file = os.path.join(os.path.dirname(self.filepath), i.name)
            if os.path.isfile(path_to_file):

                # /Blender <version>/<version>/scripts/modules/blender_render_info.py
                # https://blender.stackexchange.com/a/55503/3710
                data = read_blend_rend_chunk(path_to_file)
                if not data:
                    invalid_files.append(i.name)
                    self.report({'INFO'}, "Can not read frame range from {}, invalid .blend".format(i.name))
                else:
                    valid_files.append(i.name)
                    start, end, sc = data[0]

                item = lum.batch_render_coll.add()
                item.rid = len(lum.batch_render_coll)
                item.name = i.name
                item.path = path_to_file
                item.frame_start = start
                item.frame_end = end
                item.scene = sc
                item.frames = "{}-{}".format(item.frame_start, item.frame_end)

        #self.report({'INFO'}, "Skipped {}, no valid .blend".format(", ".join(valid_files)))
        if invalid_files:
            self.report({'WARNING'}, "Can not read frame range from {}, invalid .blend file(s)".format(", ".join(invalid_files)))
        elif valid_files:
            self.report({'INFO'}, "Added {} to the list".format(", ".join(valid_files)))
        else:
            self.report({'INFO'}, "Nothing selected")

        lum.batch_render_idx = len(lum.batch_render_coll)-1
        if bpy.app.version < (4, 1, 0): self.display_popup(context)
        return {'FINISHED'}


class LOOM_OT_scan_blends(bpy.types.Operator, ImportHelper):
    """Scan directory for blend files and add to list"""
    bl_idname = "loom.batch_scandir_blends"
    bl_label = "Scan Directory for Blend Files"
    bl_options = {'INTERNAL'}

    # ImportHelper mixin class uses this
    filename_ext = ".blend"

    filter_glob: bpy.props.StringProperty(
            default="*.blend",
            options={'HIDDEN'},
            maxlen=255)

    directory: bpy.props.StringProperty(subtype='DIR_PATH')
    sub_folders: bpy.props.BoolProperty(default=True, name="Scan Subfolders")
    cursor_pos = [0,0]

    def blend_files(self, base_dir, recursive):
        # Limitation: https://bugs.python.org/issue26111
        # https://stackoverflow.com/q/14710708/3091066
        for entry in os.scandir(base_dir):
            try:
                if entry.is_file() and entry.name.endswith(".blend"):
                    yield entry
                elif entry.is_dir() and recursive:
                    yield from self.blend_files(entry.path, recursive)
            except WindowsError:
                self.report({'WARNING'},"Access denied: {} (not a real directory)".format(entry.name))

    def display_popup(self, context):
        win = context.window #win.cursor_warp((win.width*.5)-100, (win.height*.5)+100)
        win.cursor_warp(x=self.cursor_pos[0], y=self.cursor_pos[1]+100) # re-invoke the dialog
        bpy.ops.loom.batch_render_dialog('INVOKE_DEFAULT')
        #bpy.context.window.screen = bpy.context.window.screen

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scn = context.scene
        lum = scn.loom
        lum.batch_scan_folder = self.directory

        if not self.directory:
            return {'CANCELLED'}

        blend_files = self.blend_files(self.directory, self.sub_folders)
        if next(blend_files, None) is None:
            if bpy.app.version < (4, 1, 0): self.display_popup(context)
            self.report({'WARNING'},"No blend files found in {}".format(self.directory))
            return {'CANCELLED'}

        valid_files, invalid_files = [], []
        for i in blend_files:
            path_to_file = (i.path)
            data = read_blend_rend_chunk(path_to_file)
            if not data:
                invalid_files.append(i.name)
            else:
                valid_files.append(i.name)
                start, end, sc = data[0]
                start, end, sc = data[0]
                item = lum.batch_render_coll.add()
                item.rid = len(lum.batch_render_coll)
                item.name = i.name
                item.path = path_to_file
                item.frame_start = start
                item.frame_end = end
                item.scene = sc
                item.frames = "{}-{}".format(item.frame_start, item.frame_end)

        if valid_files:
             self.report({'INFO'}, "Added {} to the list".format(", ".join(valid_files)))
        if invalid_files:
            self.report({'WARNING'}, "Skipped {}, invalid .blend file(s)".format(", ".join(invalid_files)))

        lum.batch_render_idx = len(lum.batch_render_coll)-1
        if bpy.app.version < (4, 1, 0): self.display_popup(context)
        return {'FINISHED'}

    def cancel(self, context):
        if bpy.app.version < (4, 1, 0): self.display_popup(context)

    def invoke(self, context, event):
        self.cursor_pos = [event.mouse_x, event.mouse_y]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class LOOM_OT_batch_list_actions(bpy.types.Operator):
    """Loom Batch Dialog Actions"""
    bl_idname = "loom.batch_dialog_action"
    bl_label = "Loom Batch Dialog Action"
    bl_options = {'INTERNAL'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        scn = context.scene
        lum = scn.loom
        idx = lum.batch_render_idx
        try:
            item = lum.batch_render_coll[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(lum.batch_render_coll) - 1:
                item_next = lum.batch_render_coll[idx+1].name
                lum.batch_render_coll.move(idx, idx + 1)
                lum.batch_render_idx += 1

            elif self.action == 'UP' and idx >= 1:
                item_prev = lum.batch_render_coll[idx-1].name
                lum.batch_render_coll.move(idx, idx-1)
                lum.batch_render_idx -= 1

            elif self.action == 'REMOVE':
                info = '"{}" removed from list'.format(lum.batch_render_coll[lum.batch_render_idx].name)
                lum.batch_render_idx -= 1
                if lum.batch_render_idx < 0: lum.batch_render_idx = 0
                self.report({'INFO'}, info)
                lum.batch_render_coll.remove(idx)

        if self.action == 'ADD':
            bpy.ops.loom.batch_select_blends('INVOKE_DEFAULT')
            lum.batch_render_idx = len(lum.batch_render_coll)

        return {"FINISHED"}


class LOOM_OT_batch_clear_list(bpy.types.Operator):
    """Clear all items of the Render Collection"""
    bl_idname = "loom.batch_clear_list"
    bl_label = "Delete all items of the list?"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.loom.batch_render_coll)

    def execute(self, context):
        context.scene.loom.batch_render_coll.clear()
        self.report({'INFO'}, "All items removed")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class LOOM_OT_batch_dialog_reset(bpy.types.Operator):
    """Reset Batch Dialog Display Settings"""
    bl_idname = "loom.batch_dialog_reset_display"
    bl_label = "Reset Display Settings"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
        prefs.property_unset("batch_dialog_rows")
        prefs.property_unset("batch_paths_flag")
        prefs.property_unset("batch_path_col_width")
        prefs.property_unset("batch_name_col_width")
        return {'FINISHED'}


class LOOM_OT_batch_remove_doubles(bpy.types.Operator):
    """Remove Duplicates in List based on the filename"""
    bl_idname = "loom.batch_remove_doubles"
    bl_label = "Remove All Duplicates?"
    bl_options = {'INTERNAL'}

    doubles = []

    def find_duplicates(self, context):
        path_lookup = {}
        for c, i in enumerate(context.scene.loom.batch_render_coll):
            path_lookup.setdefault(i.path, []).append(i.name)

        for path, names in path_lookup.items():
            for i in names[1:]:
                self.doubles.append(i)
        return len(self.doubles)

    @classmethod
    def poll(cls, context):
        return bool(context.scene.loom.batch_render_coll)

    def execute(self, context):
        lum = context.scene.loom
        removed_items = []
        for i in self.doubles:
            item_id = lum.batch_render_coll.find(i)
            lum.batch_render_coll.remove(item_id)
            removed_items.append(i)

        lum.batch_render_idx = (len(lum.batch_render_coll)-1)
        self.report({'INFO'}, "{} {} removed: {}".format(
                    len(removed_items),
                    "items" if len(removed_items) > 1 else "item",
                    ', '.join(set(removed_items))))
        return {'FINISHED'}

    def invoke(self, context, event):
        self.doubles.clear()
        if self.find_duplicates(context):
            return context.window_manager.invoke_confirm(self, event)
        else:
            self.report({'INFO'}, "No doubles in list, nothing to do.")
            return {'FINISHED'}


class LOOM_OT_batch_active_item(bpy.types.Operator):
    """Print active Item"""
    bl_idname = "loom.batch_active_item"
    bl_label = "Print Active Item to Console"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        lum = context.scene.loom
        try:
            print (lum.batch_render_coll[lum.batch_render_idx].name)
        except IndexError:
            print ("No active item")
        return{'FINISHED'}


class LOOM_OT_batch_default_range(bpy.types.Operator):
    """Revert to default frame range"""
    bl_idname = "loom.batch_default_frames"
    bl_label = "Revert to default frame range"
    bl_options = {'INTERNAL'}

    item_id: bpy.props.IntProperty()

    def execute(self, context):
        try:
            item = context.scene.loom.batch_render_coll[self.item_id]
            default_range = "{}-{}".format(item.frame_start, item.frame_end)
            item.frames = default_range
        except IndexError:
            self.report({'INFO'}, "No active item")
        return{'FINISHED'}


class LOOM_OT_batch_verify_input(bpy.types.Operator):
    """Verify Input Frame Range"""
    bl_idname = "loom.batch_verify_input"
    bl_label = "Verify Input Frame Range"
    bl_options = {'INTERNAL'}

    item_id: bpy.props.IntProperty()

    def execute(self, context):
        try:
            item = context.scene.loom.batch_render_coll[self.item_id]
        except IndexError:
            self.report({'INFO'}, "No active item") # redundant?
            return{'CANCELLED'}

        folder = os.path.realpath(bpy.path.abspath(item.path))
        frame_input = filter_frames(
            frame_input = item.frames,
            filter_individual = item.input_filter)

        if frame_input:
            self.report({'INFO'}, ("{} {} [{}] will be rendered to {}".format(
                len(frame_input),
                "Frame" if len(frame_input) == 1 else "Frames",
                ', '.join('{}'.format(i) for i in frame_input),
                folder)))
        else:
            self.report({'INFO'}, "No frames specified")
        return {'FINISHED'}


# Classes for registration
classes = (
    LOOM_OT_batch_dialog,
    LOOM_OT_batch_snapshot,
    LOOM_OT_batch_selected_blends,
    LOOM_OT_scan_blends,
    LOOM_OT_batch_list_actions,
    LOOM_OT_batch_clear_list,
    LOOM_OT_batch_dialog_reset,
    LOOM_OT_batch_remove_doubles,
    LOOM_OT_batch_active_item,
    LOOM_OT_batch_default_range,
    LOOM_OT_batch_verify_input,
)
