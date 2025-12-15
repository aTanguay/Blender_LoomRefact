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
Encoding and sequence management operators for Loom addon.

Contains operators for encoding image sequences to video, renaming sequences,
and managing sequence files.
"""

import bpy
from bpy_extras.io_utils import ImportHelper
import os
import re
import subprocess
import errno
from itertools import count, groupby
from time import strftime

# Import helpers
from ..helpers.globals_utils import replace_globals


def codec_callback(self, context):
    codec = [
        ('PRORES422', "Apple ProRes 422", ""),
        ('PRORES422HQ', "Apple ProRes 422 HQ", ""),
        ('PRORES422LT', "Apple ProRes 422 LT", ""),
        ('PRORES422PR', "Apple ProRes 422 Proxy", ""),
        ('PRORES4444', "Apple ProRes 4444", ""),
        ('PRORES4444XQ', "Apple ProRes 4444 XQ", ""),
        ('DNXHD422-08-036', "Avid DNxHD 422 8-bit 36Mbit", ""),
        ('DNXHD422-08-145', "Avid DNxHD 422 8-bit 145Mbit", ""),
        ('DNXHD422-08-145', "Avid DNxHD 422 8-bit 220Mbit", ""),
        ('DNXHD422-10-185', "Avid DNxHD 422 10-bit 185Mbit", ""),
        #('DNXHD422-10-440', "Avid DNxHD 422 10-bit 440Mbit", ""),
        #('DNXHD444-10-350', "Avid DNxHD 422 10-bit 440Mbit", ""),
        ('DNXHR-444', "Avid DNxHR 444 10bit", ""),
        ('DNXHR-HQX', "Avid DNxHR HQX 10bit", ""),
        ('DNXHR-HQ', "Avid DNxHR HQ 8bit", ""),
        ('DNXHR-SQ', "Avid DNxHR SQ 8bit", "")
    ]
    return codec


def colorspace_callback(self, context):
    colorspace = [
        ('iec61966_2_1', "sRGB", ""),
        ('bt709', "rec709", ""),
        ('gamma22', "Gamma 2.2", ""),
        ('gamma28', "Gamma 2.8", ""),
        ('linear', "Linear", "")
    ]
    return colorspace


class LOOM_OT_encode_dialog(bpy.types.Operator):
    """Encode Image Sequence to ProRes or DNxHD"""
    bl_idname = "loom.encode_dialog"
    bl_label = "Encode Image Sequence"
    bl_options = {'REGISTER'}

    sequence: bpy.props.StringProperty(
        name="Path to sequence",
        description="Path to sequence",
        maxlen=1024,
        subtype='FILE_PATH')
    
    movie: bpy.props.StringProperty(
        name="Path to movie",
        description="Path to movie",
        maxlen=1024,
        subtype='FILE_PATH')

    fps: bpy.props.IntProperty(
        name="Frame Rate",
        description="Frame Rate",
        default=25, min=1)

    missing_frames_bool: bpy.props.BoolProperty(
        name="Missing Frames",
        description="Missing Frames")

    codec: bpy.props.EnumProperty(
        name="Codec",
        description="Codec",
        items=codec_callback)

    colorspace: bpy.props.EnumProperty(
        name="Colorspace",
        description="colorspace",
        items=colorspace_callback)
    
    terminal_instance: bpy.props.BoolProperty(
        name="New Terminal Instance",
        description="Opens Blender in a new Terminal Window",
        default=True)

    pause: bpy.props.BoolProperty(
        name="Confirm when done",
        description="Confirm when done",
        default=True)

    # https://avpres.net/FFmpeg/sq_ProRes.html, https://trac.ffmpeg.org/wiki/Encode/VFX
    encode_presets = {
        "PRORES422PR" : ["-c:v", "prores_ks", "-profile:v", 0],
        "PRORES422LT" : ["-c:v", "prores_ks", "-profile:v", 1],
        #"PRORES422" : ["-c:v", "prores", "-profile:v", 2, "-pix_fmt" "yuv422p10"], #["-c:v", "prores", "-profile:v", 2],
        "PRORES422" : ["-c:v", "prores_ks", "-profile:v", 2],
        "PRORES422HQ" : ["-c:v", "prores_ks", "-profile:v", 3],
        "PRORES4444" : ["-c:v", "prores_ks", "-profile:v", 4, "-quant_mat", "hq", "-pix_fmt", "yuva444p10le"],
        "PRORES4444XQ" : ["-c:v", "prores_ks", "-profile:v", 5, "-quant_mat", "hq", "-pix_fmt", "yuva444p10le"],
        "DNXHD422-08-036" : ["-c:v", "dnxhd", "-vf", "scale=1920x1080,fps=25/1,format=yuv422p", "-b:v", "36M"],
        "DNXHD422-08-145" : ["-c:v", "dnxhd", "-vf", "scale=1920x1080,fps=25/1,format=yuv422p", "-b:v", "145M"],
        "DNXHD422-08-145" : ["-c:v", "dnxhd", "-vf", "scale=1920x1080,fps=25/1,format=yuv422p", "-b:v", "220M"],
        "DNXHD422-10-185" : ["-c:v", "dnxhd", "-vf", "scale=1920x1080,fps=25/1,format=yuv422p10", "-b:v", "185M"],
        #"DNXHD422-10-440" : ["-c:v", "dnxhd", "-vf", "scale=1920x1080,fps=25/1,format=yuv422p10", "-b:v", "440M"],
        #"DNXHD444-10-350" : ["-c:v", "dnxhd", "-profile:v", "dnxhr_444", "-vf", "format=yuv444p10" "-b:v", "350M"],
        "DNXHR-444" : ["-c:v", "dnxhd", "-profile:v", "dnxhr_444", "-vf", "format=yuv444p10"],
        "DNXHR-HQX" : ["-c:v", "dnxhd", "-profile:v", "dnxhr_hqx", "-vf", "format=yuv422p10"],
        "DNXHR-HQ" : ["-c:v", "dnxhd", "-profile:v", "dnxhr_hq", "-vf", "format=yuv422p"],
        "DNXHR-SQ" : ["-c:v", "dnxhd", "-profile:v", "dnxhr_sq", "-vf", "format=yuv422p"],
        }
    
    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def rangify_frames(self, frames):
        """ Convert list of integers to Range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def verify_app(self, cmd):
        try:
            subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as e:

            if e.errno == errno.ENOENT:
                return False
        return True

    def determine_type(self, val): 
        #val = ast.literal_eval(s)
        if (isinstance(val, int)):
            return ("chi")
        elif (isinstance(val, float)):
            return ("chf")
        if val in ["true", "false"]:
            return ("chb")
        else:
            return ("chs")

    def number_suffix(self, filename):
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)

    def pack_arguments(self, lst):
        return [{"idc": 0, "name": self.determine_type(i), "value": str(i)} for i in lst]

    def check(self, context):
        return True        

    def execute(self, context):
        prefs = context.preferences.addons[addon_name].preferences
        prefs.default_codec = self.codec
        lum = context.scene.loom
        image_sequence = {}
        
        """ Verify ffmpeg """
        ffmpeg_error = False
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
        
        if ffmpeg_error:
            error_message = "Path to ffmpeg binary not set in addon preferences"
            if not self.options.is_invoke:
                print (error_message)
                return {"CANCELLED"}
            else:
                self.report({'ERROR'},error_message)
                bpy.ops.loom.encode_dialog('INVOKE_DEFAULT')
                return {"CANCELLED"}
            
        #if not self.properties.is_property_set("sequence"):
        seq_path = lum.sequence_encode if not self.sequence else self.sequence
        mov_path = lum.movie_path if not self.movie else self.movie

        """ Operator called via UI """
        path_error = False
        if not seq_path:
            self.report({'ERROR'}, "No image sequence specified")
            path_error = True

        if path_error and self.options.is_invoke:
            bpy.ops.loom.encode_dialog('INVOKE_DEFAULT')
            return {"CANCELLED"}

        basedir, filename = os.path.split(seq_path)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, extension = os.path.splitext(filename)

        if not os.path.isdir(basedir):
            self.report({'ERROR'},"The main directory '{}' does not exist".format(basedir))
            return {"CANCELLED"}

        """ Support for non-sequence paths when called via Command Line """
        if not self.options.is_invoke:
            filename_noext = replace_globals(filename_noext, addon_name)
            if '#' not in filename_noext:
                filename_noext += "####"
            if not extension:
                extension += context.scene.render.file_extension

        """ Verify image sequence """
        seq_error = False
        if '#' not in filename_noext:
            num_suff = self.number_suffix(filename_noext)
            if not num_suff:
                self.report({'ERROR'}, "No valid image sequence")
                seq_error = True
            else:
                filename_noext = filename_noext.replace(num_suff, "#"*len(num_suff))
        
        if not extension: # Sequence file format
            self.report({'ERROR'}, "File format not set (missing extension)")
            seq_error = True

        if seq_error and self.options.is_invoke:
            bpy.ops.loom.encode_dialog('INVOKE_DEFAULT')
            return {"CANCELLED"}

        hashes = filename_noext.count('#')
        name_real = filename_noext.replace("#", "")
        file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=name_real, ds=hashes, ex=extension)

        for f in os.scandir(basedir):
            if f.name.endswith(extension) and f.is_file():
                match = re.match(file_pattern, f.name, re.IGNORECASE)
                if match: image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

        if not len(image_sequence) > 1:
            self.report({'ERROR'},"'{}' cannot be found on disk".format(filename))
            if self.options.is_invoke:
                bpy.ops.loom.encode_dialog('INVOKE_DEFAULT')
            return {"CANCELLED"}

        if not mov_path:
            mov_path = next(iter(image_sequence.values()))

        """ Verify movie file name and extension """
        mov_basedir, mov_filename = os.path.split(mov_path)
        mov_filename_noext, mov_extension = os.path.splitext(mov_filename)
        mov_extension = ".mov"

        """ In case the sequence has no name """
        if mov_filename_noext.isdigit():
            mov_filename_noext = os.path.basename(basedir)
        
        """ If a file with the same name already exists, do not overwrite it """
        mov_path = os.path.join(mov_basedir, "{}{}".format(mov_filename_noext, mov_extension))
        if os.path.isfile(mov_path):
            time_stamp = strftime("%Y-%m-%d-%H-%M-%S")
            mov_filename_noext = "{}_{}".format(mov_filename_noext, time_stamp)
        
        mov_path = os.path.join(mov_basedir, "{}{}".format(mov_filename_noext, mov_extension))

        """ Detect missing frames """
        frame_numbers = sorted(list(image_sequence.keys())) #start_frame, end_frame = fn[0], fn[-1]
        missing_frame_list = self.missing_frames(frame_numbers)

        if missing_frame_list:
            lum.lost_frames = self.rangify_frames(missing_frame_list)
            error = "Missing frames detected: {}".format(lum.lost_frames)
            if not self.options.is_invoke:
                print ("ERROR: ", error)
                return {"CANCELLED"}
            else:
                self.report({'ERROR_INVALID_INPUT'}, error)
                self.report({'ERROR'},"Frame list copied to clipboard.")
                context.window_manager.clipboard = "{}".format(
                    ','.join(map(str, missing_frame_list)))
                bpy.ops.loom.encode_dialog('INVOKE_DEFAULT') # re-invoke the dialog
                return {"CANCELLED"}
        else:
            lum.lost_frames = ""
            
        """ Format image sequence for ffmpeg """
        fn_ffmpeg = filename_noext.replace("#"*hashes, "%0{}d{}".format(hashes, extension))
        fp_ffmpeg = os.path.join(basedir, fn_ffmpeg) # "{}%0{}d{}".format(filename_noext, 4, ext)
        cli_args = ["-start_number", frame_numbers[0], "-apply_trc", self.colorspace, "-i", fp_ffmpeg] 
        cli_args += self.encode_presets[self.codec]
        cli_args += [mov_path] if self.fps == 25 else ["-r", self.fps, mov_path]

        # TODO - PNG support
        if extension in (".png", ".PNG"):
            self.report({'WARNING'}, "Loom does not support png sequences, no guarantee that the output is correct.")
            #return {"FINISHED"}

        """ Run ffmpeg """
        bpy.ops.loom.run_terminal(
            #debug_arguments=True,
            binary=prefs.ffmpeg_path,
            terminal_instance=self.terminal_instance,
            argument_collection=self.pack_arguments(cli_args),
            bash_name="loom-ffmpeg-temp",
            force_bash=prefs.bash_flag,
            pause=self.pause)

        self.report({'INFO'}, "Encoding {}{} to {}".format(filename_noext, extension, mov_path))
        return {"FINISHED"}

    def invoke(self, context, event):
        lum = context.scene.loom
        prefs = context.preferences.addons[addon_name].preferences

        if not self.properties.is_property_set("codec"):
            if prefs.default_codec:
                try:
                    self.codec = prefs.default_codec
                except:
                    pass

        return context.window_manager.invoke_props_dialog(self, 
            width=(prefs.encode_dialog_width))

    def draw(self, context):
        lum = context.scene.loom
        prefs = context.preferences.addons[addon_name].preferences
        layout = self.layout

        split_width = .2
        split = layout.split(factor=split_width)
        col = split.column(align=True)
        col.label(text="Sequence:")
        col = split.column(align=True)
        sub = col.row(align=True)          
        sub.prop(lum, "sequence_encode", text="")
        if lum.sequence_encode:
            sub.operator("loom.image_sequence_verify", icon='GHOST_ENABLED', text="")
            sub.operator("loom.open_folder", 
                icon="DISK_DRIVE", text="").folder_path = os.path.dirname(lum.sequence_encode)
        else:
            sub.operator("loom.encode_auto_paths", text="", icon='AUTO') #GHOST_ENABLED, SEQUENCE
        sel_sequence = sub.operator("loom.load_sequence", text="", icon='FILE_TICK')
        #sel_sequence.verify_sequence = False

        split = layout.split(factor=split_width)
        col = split.column(align=True)
        col.label(text="Colorspace:")
        col = split.column(align=True)
        col.prop(self, "colorspace", text="")

        split = layout.split(factor=split_width)
        col = split.column(align=True)
        col.label(text="Frame Rate:")
        col = split.column(align=True)
        col.prop(self, "fps", text="")

        split = layout.split(factor=split_width)
        col = split.column(align=True)
        col.label(text="Codec:")
        col = split.column(align=True)
        col.prop(self, "codec", text="")

        split = layout.split(factor=split_width)
        col = split.column(align=True)
        col.label(text="Movie File:")
        col = split.column(align=True)
        sub = col.row(align=True)
        sub.prop(lum, "movie_path", text="")
        if lum.movie_path:
            sub.operator("loom.open_folder", 
                icon="DISK_DRIVE", text="").folder_path = os.path.dirname(lum.movie_path)
        sub.operator("loom.save_movie", text="", icon='FILE_TICK')
        
        if lum.lost_frames:
            layout.separator()
            spl = layout.split(factor=0.5)
            row = spl.row(align=True)
            row.prop(lum, "ignore_scene_range", text="", icon='RENDER_RESULT')
            fg = row.operator("loom.fill_image_sequence", text="Fill Gaps with Copies")
            fg.sequence_path = lum.sequence_encode
            fg.scene_range = not lum.ignore_scene_range
            txt = "Render Missing Frames"
            di = spl.operator("loom.render_input_dialog", icon='RENDER_STILL', text=txt)
            di.frame_input = lum.lost_frames
        layout.separator(factor=1.5)



class LOOM_OT_rename_dialog(bpy.types.Operator):
    """Rename Image or File Sequence"""
    bl_idname = "loom.rename_file_sequence"
    bl_label = "Rename File Sequence"
    bl_description = "Rename File or Image Sequence"
    bl_options = {'REGISTER'}
    bl_property = "new_name"

    sequence: bpy.props.StringProperty(
        name="Path to sequence",
        description="Path to sequence",
        maxlen=1024,
        subtype='FILE_PATH')
    
    new_name: bpy.props.StringProperty(
        name="Path to sequence",
        description="Path to sequence",
        maxlen=1024)
    
    keep_original_numbers: bpy.props.BoolProperty(
        name="Keep Original Numbers",
        description="Keep the Numbers of the Original File Sequence",
        default=False)

    start: bpy.props.IntProperty(
        name="Start at",
        description="Start at",
        default=1,
        min=0)
        
    open_file_browser: bpy.props.BoolProperty(
        name="Open File Browser",
        description="Open File Browser",
        default=True)
    
    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def rangify_frames(self, frames):
        """ Convert list of integers to Range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def determine_type(self, val): 
        #val = ast.literal_eval(s)
        if (isinstance(val, int)):
            return ("chi")
        elif (isinstance(val, float)):
            return ("chf")
        if val in ["true", "false"]:
            return ("chb")
        else:
            return ("chs")

    def number_suffix(self, filename):
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)

    def pack_arguments(self, lst):
        return [{"idc": 0, "name": self.determine_type(i), "value": str(i)} for i in lst]

    def check(self, context):
        return True        

    def execute(self, context):
        lum = context.scene.loom
        image_sequence = {}
        seq_path = lum.sequence_encode if not self.sequence else self.sequence
        
        path_error = False
        if not seq_path:
            self.report({'ERROR'}, "No image sequence specified")
            path_error = True

        if path_error:
            bpy.ops.loom.rename_file_sequence('INVOKE_DEFAULT')
            return {"CANCELLED"}

        """ Verify image sequence """
        basedir, filename = os.path.split(seq_path)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, extension = os.path.splitext(filename)

        seq_error = False
        if '#' not in filename_noext:
            num_suff = self.number_suffix(filename_noext)
            if not num_suff:
                self.report({'ERROR'}, "No valid image sequence")
                seq_error = True
            else:
                filename_noext = filename_noext.replace(num_suff, "#"*len(num_suff))
        
        if not extension: # Sequence file format
            self.report({'ERROR'}, "File format not set (missing extension)")
            seq_error = True

        if seq_error:
            bpy.ops.loom.rename_file_sequence('INVOKE_DEFAULT')
            return {"CANCELLED"}

        hashes = filename_noext.count('#')
        name_real = filename_noext.replace("#", "")
        file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=name_real, ds=hashes, ex=extension)

        for f in os.scandir(basedir):
            if f.name.endswith(extension) and f.is_file():
                match = re.match(file_pattern, f.name, re.IGNORECASE)
                if match: image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

        if not len(image_sequence) > 1:
            self.report({'WARNING'},"No valid image sequence")
            bpy.ops.loom.rename_file_sequence('INVOKE_DEFAULT')
            return {"CANCELLED"}

        """ Rename File Sequence """
        new_name = self.new_name
        if new_name.endswith(tuple(bpy.path.extensions_image)):
            new_name, file_extension = os.path.splitext(new_name)
        user_name = new_name.replace("#", "")
        user_hashes = new_name.count('#')
        if not user_hashes: user_hashes = hashes
        renamed = []

        # Rename the sequence temporary if already in place (windows issue)
        # -> os.rename fails in case the upcoming file has the same name
        if user_name == name_real and user_hashes == hashes:
            image_sequence_tmp = {}
            for c, (k, v) in enumerate(image_sequence.items(), start=1):
                num = "{n:0{dig}d}".format(n=c, dig=user_hashes)
                if self.keep_original_numbers:
                    d_tmp, fn_tmp = os.path.split(v)
                    num = "{n:0{dig}d}".format(n=int(self.number_suffix(fn_tmp)), dig=user_hashes)
                fp = os.path.join(basedir, "loom__tmp__{}{}".format(num, extension))
                os.rename(v, fp)
                image_sequence_tmp[int(num)] = fp
            image_sequence = image_sequence_tmp
        # -------------------------------------------------------------- */

        for c, (k, v) in enumerate(image_sequence.items(), start=self.start):
            num = "{n:0{dig}d}".format(n=c, dig=user_hashes)
            if self.keep_original_numbers:
                d_tmp, fn_tmp = os.path.split(v)
                num = "{n:0{dig}d}".format(n=int(self.number_suffix(fn_tmp)), dig=user_hashes)
            fp = os.path.join(basedir, "{}{}{}".format(user_name, num, extension))
            os.rename(v, fp)
            renamed.append(fp)
        
        if len(renamed) > 0:
            sn = "{}{}".format(user_name, '#'*user_hashes)
            lum.sequence_rename = "{}".format(sn)
            lum.sequence_encode = os.path.join(basedir, "{}{}".format(sn, extension))
            self.report({'INFO'}, "{} files renamed to {}".format(len(renamed), sn+extension))
            if self.open_file_browser:
                bpy.ops.loom.open_folder(folder_path=basedir)
        else:
            self.report({'ERROR'}, "Can not rename files")

        return {"FINISHED"}

    def invoke(self, context, event):
        prefs = context.preferences.addons[addon_name].preferences
        self.new_name = context.scene.loom.sequence_rename
        return context.window_manager.invoke_props_dialog(self, 
            width=(prefs.encode_dialog_width))

    def draw(self, context):
        lum = context.scene.loom
        prefs = context.preferences.addons[addon_name].preferences
        layout = self.layout

        split_width = .2
        split = layout.split(factor=split_width)
        col = split.column(align=True)
        col.label(text="Sequence:")
        col = split.column(align=True)
        sub = col.row(align=True)          
        sub.prop(lum, "sequence_encode", text="")
        if lum.sequence_encode:
            sub.operator("loom.image_sequence_verify", icon='GHOST_ENABLED', text="")
            sub.operator("loom.open_folder", 
                icon="DISK_DRIVE", text="").folder_path = os.path.dirname(lum.sequence_encode)
        else:
            sub.operator("loom.encode_auto_paths", text="", icon='AUTO') #GHOST_ENABLED, SEQUENCE
        sel_sequence = sub.operator("loom.load_sequence", text="", icon='FILE_TICK')
        sel_sequence.dialog = 'rename'
        sel_sequence.verify_sequence = False

        split = layout.split(factor=split_width)
        col = split.column(align=True)
        col.label(text="New Sequence Name:")
        col = split.column(align=True)
        split = col.split(factor=0.85)
        split.prop(self, "new_name", text="")
        row = split.row(align=True)
        row.prop(self, "keep_original_numbers", text="", icon='TEMP')
        col = row.column(align=True)
        col.enabled = not self.keep_original_numbers
        col.prop(self, "start", text="")
        layout.row()
        layout.row().prop(self, "open_file_browser")
        layout.separator()



class LOOM_OT_load_image_sequence(bpy.types.Operator, ImportHelper):
    """Select File of Image Sequence"""
    bl_idname = "loom.load_sequence"
    bl_label = "Select File of Image Sequence"
    bl_options = {'INTERNAL'}
    
    cursor_pos = [0,0]
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    dialog: bpy.props.EnumProperty(
        name="Dialog",
        options={'HIDDEN'},
        items=(
            ("encode", "Encode Dialog", "", 1),
            ("rename", "Rename Dialog", "", 2)))

    filter_glob: bpy.props.StringProperty(
        default="*.png;*.jpg;*.jpeg;*.jpg;*.exr;*dpx;*tga;*tif;*tiff;",
        #default="*" + ";*".join(bpy.path.extensions_image),
        options={'HIDDEN'})

    verify_sequence: bpy.props.BoolProperty(
            name="Verify Image Sequence",
            description="Detects missing frames",
            default=True,
            options={'SKIP_SAVE'})
    
    scene_range: bpy.props.BoolProperty(
            name="Scene Range",
            description="Consider the Frames of the Scene",
            default=False,
            #options={'SKIP_SAVE'}
            )

    def number_suffix(self, filename):
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)
    
    def bound_frame(self, frame_path, frame_iter):
        folder, filename = os.path.split(frame_path)
        digits = self.number_suffix(filename)
        frame = re.sub(r'\d(?!\d)', lambda x: str(int(x.group(0)) + frame_iter), digits)
        return os.path.exists(os.path.join(folder, frame.join(filename.rsplit(digits))))

    def is_sequence(self, filepath):
        folder, filename = os.path.split(filepath) # any(char.isdigit() for char in filename)
        filename_noext, ext = os.path.splitext(filename)
        if not filename_noext[-1].isdigit(): return False
        next_frame = self.bound_frame(filepath, 1)
        prev_frame = self.bound_frame(filepath, -1)
        return True if next_frame or prev_frame else False

    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))
    
    def rangify_frames(self, frames):
        """ Convert list of integers to Range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        #G=([list(x) for _,x in groupby(L, lambda x,c=count(): next(c)-x)])
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def display_popup(self, context):
        win = context.window #win.cursor_warp((win.width*.5)-100, (win.height*.5)+100)
        win.cursor_warp(x=self.cursor_pos[0], y=self.cursor_pos[1]+100) # x-100 y-+70
        if self.dialog == 'encode':
            bpy.ops.loom.encode_dialog('INVOKE_DEFAULT') # re-invoke the dialog
        if self.dialog == 'rename':
            bpy.ops.loom.rename_file_sequence('INVOKE_DEFAULT') # re-invoke the dialog

    @classmethod
    def poll(cls, context):
        return True #context.object is not None

    def execute(self, context):
        lum = context.scene.loom
        image_sequence = {}

        basedir, filename = os.path.split(self.filepath)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, ext = os.path.splitext(filename)
        frame_suff = self.number_suffix(filename)

        if not os.path.isfile(self.filepath):
            self.report({'WARNING'},"Please select one image of an image sequence")
            if bpy.app.version < (4, 1, 0): self.display_popup(context)
            return {"CANCELLED"}

        if not frame_suff:
            self.report({'WARNING'},"No valid image sequence")
            if bpy.app.version < (4, 1, 0): self.display_popup(context)
            return {"CANCELLED"}

        sequence_name = filename.replace(frame_suff,'#'*len(frame_suff))
        sequence_path = os.path.join(basedir, sequence_name)
        name_real = filename_noext.replace(frame_suff, "")

        """ Verify image sequence on disk (Scan directory) """
        if self.verify_sequence:
            hashes = sequence_name.count('#')
            file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=name_real, ds=hashes, ex=ext)
            for f in os.scandir(basedir):
                if f.name.endswith(ext) and f.is_file():
                    match = re.match(file_pattern, f.name, re.IGNORECASE)
                    if match: image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

            if not len(image_sequence) > 1:
                self.report({'WARNING'},"No valid image sequence")
                return {"CANCELLED"}

            """ Detect missing frames """  #start_frame, end_frame = fn[0], fn[-1]
            frame_numbers = sorted(list(image_sequence.keys()))
            missing_frame_list = self.missing_frames(frame_numbers)

            if frame_numbers and self.scene_range:
                scn = context.scene
                missing_frame_list += range(scn.frame_start, frame_numbers[0])
                missing_frame_list += range(frame_numbers[-1]+1, scn.frame_end+1)
                missing_frame_list = sorted(missing_frame_list)

            if missing_frame_list:
                lum.lost_frames = self.rangify_frames(missing_frame_list)
                context.window_manager.clipboard = "{}".format(
                    ','.join(map(str, missing_frame_list)))
                error_massage = "Missing frames detected: {}".format(self.rangify_frames(missing_frame_list))
                self.report({'ERROR_INVALID_INPUT'}, error_massage)
                self.report({'ERROR'},"Frame list copied to clipboard.")
            else:
                lum.lost_frames = ""
                self.report({'INFO'},"Valid image sequence, Frame range: {}".format(
                    self.rangify_frames(frame_numbers)))

        else:
            """ Quick test whether single image or not """
            if not self.is_sequence(self.filepath):
                self.report({'WARNING'},"No valid image sequence") #return {"CANCELLED"}
            else:
                lum.lost_frames = ""

        if self.dialog == 'encode':
            if not name_real: name_real = "untitled"
            name_real = name_real[:-1] if name_real.endswith(("-", "_")) else name_real
            lum.movie_path = os.path.join(basedir, name_real + ".mov")
        if self.dialog == 'rename':
            lum.sequence_rename = name_real
        lum.sequence_encode = sequence_path

        if bpy.app.version < (4, 1, 0): self.display_popup(context)
        return {'FINISHED'}
    
    def cancel(self, context):
        if bpy.app.version < (4, 1, 0): self.display_popup(context)

    def invoke(self, context, event):
        s = context.scene.loom.sequence_encode
        self.filepath = os.path.dirname(s) + "/" if s else bpy.path.abspath("//")
        self.cursor_pos = [event.mouse_x, event.mouse_y]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class LOOM_OT_encode_select_movie(bpy.types.Operator, ImportHelper):
    """Movie file path"""
    bl_idname = "loom.save_movie"
    bl_label = "Save Movie File"
    bl_options = {'INTERNAL'}
    
    cursor_pos = [0,0]
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")    
    filename: bpy.props.StringProperty()    
    
    filename_ext = ".mov"
    filter_glob: bpy.props.StringProperty(
            default="*.mov;",
            options={'HIDDEN'})
    
    def name_from_sequence(self, context):
        lum = context.scene.loom
        basedir, filename = os.path.split(lum.sequence_encode)
        filename_noext, ext = os.path.splitext(filename)
        name_real = filename_noext.replace('#', "")
        if name_real.endswith(("-", "_")):
            name_real = name_real[:-1]
        return "{}.mov".format(name_real)

    def display_popup(self, context):
        win = context.window #win.cursor_warp((win.width*.5)-100, (win.height*.5)+100)
        win.cursor_warp(x=self.cursor_pos[0], y=self.cursor_pos[1]+100)
        bpy.ops.loom.encode_dialog('INVOKE_DEFAULT') # re-invoke the dialog
        
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        lum = context.scene.loom
        folder, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)
        if os.path.isdir(self.filepath):
            filename = "untitled"
        if ext != ".mov":
            lum.movie_path = os.path.join(folder, "{}{}.mov".format(filename,ext))
        else:
            lum.movie_path = self.filepath #self.report({'WARNING'},"No valid file type")
        if bpy.app.version < (4, 1, 0): self.display_popup(context)
        return {'FINISHED'}
    
    def cancel(self, context):
        if bpy.app.version < (4, 1, 0): self.display_popup(context)

    def invoke(self, context, event):
        self.filename = self.name_from_sequence(context)
        self.cursor_pos = [event.mouse_x, event.mouse_y]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class LOOM_OT_encode_verify_image_sequence(bpy.types.Operator):
    """Verify & Refresh Image Sequence"""
    bl_idname = "loom.image_sequence_verify"
    bl_label = "Verify Image Sequence"
    bl_options = {'INTERNAL'}

    scene_range: bpy.props.BoolProperty(
        name="Scene Range",
        description="Consider the Frames of the Scene",
        default=True,
        options={'SKIP_SAVE'}
        )

    def rangify_frames(self, frames):
        """ Convert list of integers to Range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def number_suffix(self, filename):
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)

    def execute(self, context):
        lum = context.scene.loom
        image_sequence = {}

        if not lum.sequence_encode:
            self.report({'WARNING'},"No image sequence specified")
            return {"CANCELLED"}

        basedir, filename = os.path.split(lum.sequence_encode)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, ext = os.path.splitext(filename)
        
        seq_error = False
        if '#' not in filename_noext:
            num_suff = self.number_suffix(filename_noext)
            if num_suff:
                filename_noext = filename_noext.replace(num_suff, "#"*len(num_suff))
                sequence_name = "{}{}".format(filename_noext, ext)
                lum.sequence_encode = "{}".format(os.path.join(basedir, sequence_name))
            else:
                seq_error = True

        if seq_error:
            self.report({'ERROR'},"No valid image sequence")
            return {"CANCELLED"}
        if not ext:
            self.report({'ERROR'}, "File format not set (missing extension)")
            return {"CANCELLED"}

        hashes = filename_noext.count('#')
        name_real = filename_noext.replace("#", "")
        file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=name_real, ds=hashes, ex=ext)

        for f in os.scandir(basedir):
            if f.name.endswith(ext) and f.is_file():
                match = re.match(file_pattern, f.name, re.IGNORECASE)
                if match: image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

        if not len(image_sequence) > 1:
            self.report({'ERROR'},"Specified image sequence not found on disk")
            return {"CANCELLED"}

        """ Detect missing frames """
        frame_numbers = sorted(list(image_sequence.keys()))
        missing_frame_list = self.missing_frames(frame_numbers)
        msg = "(based on the image sequence found on disk)"

        if frame_numbers and self.scene_range:
            scn = context.scene
            missing_frame_list += range(scn.frame_start, frame_numbers[0])
            missing_frame_list += range(frame_numbers[-1]+1, scn.frame_end+1)
            missing_frame_list = sorted(missing_frame_list)
            msg = "(based on the frame range of the scene)"

        if missing_frame_list:
            lum.lost_frames = self.rangify_frames(missing_frame_list)
            context.window_manager.clipboard = "{}".format(
                ','.join(map(str, missing_frame_list)))
            error_massage = "Missing frames detected {}: {}".format(msg, self.rangify_frames(missing_frame_list))
            self.report({'ERROR'}, error_massage)
            self.report({'ERROR'},"Frame list copied to clipboard.")
        else:
            self.report({'INFO'},'Sequence: "{}{}" found on disk, Frame range: {}'.format(
                filename_noext, ext, self.rangify_frames(frame_numbers)))
            lum.lost_frames = ""
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if event.alt or event.ctrl:
            self.scene_range = False
        return self.execute(context)



class LOOM_OT_encode_auto_paths(bpy.types.Operator):
    """Auto Paths based on the latest Loom render (hold Ctrl to force the use of the default path)"""
    bl_idname = "loom.encode_auto_paths"
    bl_label = "Set sequence and movie path automatically"
    bl_options = {'INTERNAL'}

    default_path: bpy.props.BoolProperty(
        name="Default Output Path",
        description="Use the default Output Path",
        default=False,
        options={'SKIP_SAVE'})

    def number_suffix(self, filename):
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)

    @classmethod
    def poll(cls, context):
        return not context.scene.loom.sequence_encode

    def execute(self, context):
        lum = context.scene.loom
        basedir, filename = os.path.split(context.scene.render.frame_path(frame=0))
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, ext = os.path.splitext(filename)
        num_suff = self.number_suffix(filename_noext)
        report_msg = "Sequence path set based on default output path"

        if lum.render_collection and not self.default_path:
            latest_frame = lum.render_collection[-1]
            basedir = os.path.dirname(bpy.path.abspath(replace_globals(latest_frame.file_path, addon_name))) # Absolute or Relative?
            num_suff = "0".zfill(latest_frame.padded_zeros)
            filename_noext = replace_globals(latest_frame.name, addon_name) + num_suff
            ext = ".{}".format(latest_frame.image_format)
            report_msg = "Sequence path set based on latest Loom render"
        
        if not lum.movie_path:
            movie_noext = filename_noext.replace(num_suff, "")
            movie_noext = movie_noext[:-1] if movie_noext.endswith(("-", "_", ".")) else movie_noext
            lum.movie_path = "{}.mov".format(bpy.path.abspath(os.path.join(basedir, movie_noext)))

        filename_noext = filename_noext.replace(num_suff, "#"*len(num_suff))
        sequence_name = "{}{}".format(filename_noext, ext)
        lum.sequence_encode = "{}".format(os.path.join(basedir, sequence_name))
        self.report({'INFO'}, report_msg)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if event.alt or event.ctrl:
            self.default_path = True
        return self.execute(context)



class LOOM_OT_fill_sequence_gaps(bpy.types.Operator):
    """Fill gaps in image sequence with copies of existing frames"""
    bl_idname = "loom.fill_image_sequence"
    bl_label = "Fill gaps in image sequence with copies of previous frames?"
    bl_options = {'INTERNAL'}
    
    sequence_path: bpy.props.StringProperty()
    scene_range: bpy.props.BoolProperty(default=True, options={'SKIP_SAVE'})

    def re_path(self, basedir, name_real, frame, hashes, extension):
        return os.path.join(
            basedir, 
            "{n}{f:0{h}d}{e}".format(n=name_real, f=frame, h=hashes, e=extension)
            )

    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def execute(self, context):
        lum = context.scene.loom
        image_sequence = {}

        basedir, filename = os.path.split(self.sequence_path)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, ext = os.path.splitext(filename)

        if "#" not in filename_noext:
            self.report({'WARNING'},"No valid image sequence")
            return {"CANCELLED"}

        """ Scan directory """
        hashes = filename_noext.count('#')
        name_real = filename_noext.replace("#", "")
        file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=name_real, ds=hashes, ex=ext)
        for f in os.scandir(basedir):
            if f.name.endswith(ext) and f.is_file():
                match = re.match(file_pattern, f.name, re.IGNORECASE)
                if match: image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

        if not len(image_sequence) > 1:
            self.report({'WARNING'},"No valid image sequence")
            return {"CANCELLED"}

        """ Assemble missing frames """
        frame_numbers = sorted(list(image_sequence.keys())) 
        #start_frame, end_frame = fn[0], fn[-1]
        missing_frame_list = self.missing_frames(frame_numbers)
        frames_to_copy = {}

        if missing_frame_list:
            f_prev = frame_numbers[0]
            for frame in range(frame_numbers[0], frame_numbers[-1]+1):
                if frame not in image_sequence:
                    path_copy = self.re_path(basedir, name_real, frame, hashes, ext)
                    frames_to_copy.setdefault(image_sequence[f_prev], []).append(path_copy)
                else:
                    f_prev = frame

        """ Extend to frame range of the scene """
        if self.scene_range:
            for i in range(context.scene.frame_start, frame_numbers[0]):
                path_copy = self.re_path(basedir, name_real, i, hashes, ext)
                frames_to_copy.setdefault(image_sequence[frame_numbers[0]], []).append(path_copy)
            
            for o in range(frame_numbers[-1]+1, context.scene.frame_end+1):
                path_copy = self.re_path(basedir, name_real, o, hashes, ext)
                frames_to_copy.setdefault(image_sequence[frame_numbers[-1]], []).append(path_copy)
        
        """ Copy the Images """
        if frames_to_copy:
            try:
                from shutil import copyfile
                for src, dest in frames_to_copy.items():
                        for ff in dest:
                            copyfile(src, ff)
                self.report({'INFO'},"Successfully copied all missing frames")
                #if self.options.is_invoke:
                lum.lost_frames = ""
            except OSError:
                self.report({'ERROR'}, "Error while trying to copy frames")
        else:
            self.report({'INFO'},"No Gaps, nothing to do")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)




# Classes for registration
classes = (
    LOOM_OT_encode_dialog,
    LOOM_OT_rename_dialog,
    LOOM_OT_load_image_sequence,
    LOOM_OT_encode_select_movie,
    LOOM_OT_encode_verify_image_sequence,
    LOOM_OT_encode_auto_paths,
    LOOM_OT_fill_sequence_gaps,
)
