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
Playblast operators for Loom addon.

Contains experimental playblast functionality for quick preview rendering.
"""

import bpy
import os
from itertools import count, groupby

# Import helpers
from ..helpers.frame_utils import filter_frames


class LOOM_OT_playblast(bpy.types.Operator):
    """Playback rendered image sequence using the default or blender player"""
    bl_idname = "loom.playblast"
    bl_label = "Playblast Sequence"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    # Todo! Just a temporary solution.
    # Might be a better idea trying to implement properties
    # for bpy.ops.render.play_rendered_anim() operator,
    # /startup/bl_operators/screen_play_rendered.py
    _image_sequence = {}

    def is_sequence(self, filepath):
        next_frame = re.sub(r'\d(?!\d)', lambda x: str(int(x.group(0)) + 1), filepath)
        return True if os.path.exists(next_frame) else False

    def number_suffix(self, filename):
        # test whether last char is digit?
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)

    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def file_sequence(self, filepath, digits=None, extension=None):
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
                if match: self._image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

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

    def pack_arguments(self, lst):
        return [{"idc": 0, "name": self.determine_type(i), "value": str(i)} for i in lst]

    def execute(self, context):
        scn = context.scene
        lum = scn.loom
        addon_name = __package__.split('.')[0]

        prefs = context.preferences.addons[addon_name].preferences #prefs.user_player = True
        glob_vars = prefs.global_variable_coll
        preview_filetype = "jpg" if scn.render.image_settings.use_preview else None
        default_flag = False
        sequence_name = None

        if len(lum.render_collection) > 0 and prefs.log_render:
            seq = lum.render_collection[len(lum.render_collection)-1]
            file_path = seq.file_path
            seq_name = seq.name
            if any(ext in file_path for ext in glob_vars.keys()):
                file_path = replace_globals(file_path)
            if any(ext in seq_name for ext in glob_vars.keys()):
                seq_name = replace_globals(seq_name)

            seq_dir = os.path.realpath(bpy.path.abspath(os.path.split(file_path)[0]))
            seq_ext = seq.image_format if not preview_filetype else preview_filetype
            sequence_name = "{}.{}".format(file_path, seq_ext)

            self.file_sequence(
                filepath = os.path.join(seq_dir,"{}.{}".format(seq_name, seq.image_format)), 
                digits = seq.padded_zeros, 
                extension = preview_filetype)
            
        else:
            frame_path = bpy.path.abspath(scn.render.frame_path(frame=scn.frame_start, preview=False))
            default_flag = True
            """ Try default operator in the first place """ 
            if self.is_sequence(frame_path):
                bpy.ops.render.play_rendered_anim()
            else:
                self.file_sequence(filepath = frame_path, extension = preview_filetype)
                if self._image_sequence:
                    start = next(iter(self._image_sequence.keys()))
                    frame_path = next(iter(self._image_sequence.values()))
                    self.report({'WARNING'},"Sequence has offset and starts at {}".format(start))
                seq_dir, output_filename = os.path.split(frame_path)
                num_suffix = self.number_suffix(output_filename) #os.path.splitext(output_filename)[0]
                sequence_name = output_filename.replace(num_suffix,'#'*len(num_suffix))
        
        if not self._image_sequence:
            self.report({'WARNING'},"No sequence in loom cache")
            return {'CANCELLED'}
        else:
            if preview_filetype: 
                self.report({'WARNING'},"Preview Playback")
            if not default_flag:
                self.report({'INFO'},"Sequence from loom cache")
            else:
                self.report({'INFO'}, "Matching sequence ({}) found in {}".format(sequence_name, seq_dir))

        frames = sorted(list(self._image_sequence.keys()))
        start_frame = frames[0] 
        end_frame = frames[-1]

        """ Use preview range if enabled """
        if scn.use_preview_range:
            preview_start = scn.frame_preview_start
            preview_end = scn.frame_preview_end
            if all(x in frames for x in (preview_start, preview_end)):
                start_frame, end_frame = preview_start, preview_end
                frames = frames[frames.index(start_frame):frames.index(end_frame)]

        start_frame_path = self._image_sequence[frames[0]] # next(iter(self._image_sequence.values()))
        start_frame_suff = self.number_suffix(start_frame_path)
        start_frame_format = start_frame_path.replace(start_frame_suff,'#'*len(start_frame_suff))

        """ Detect missing frames """
        missing_frame_list = self.missing_frames(frames)
        if missing_frame_list:
            end_frame = missing_frame_list[0]-1
            self.report({'WARNING'}, "Missing Frames: {}".format(', '.join(map(str, missing_frame_list))))
            
        if not prefs.user_player:
            """ Assemble arguments and run the command """
            self.report({'INFO'}, "[Loom-OP Playback] {} {}-{}".format(sequence_name, start_frame, end_frame))
            self.report({'INFO'}, "Playblast Frame {}-{}".format(start_frame, end_frame))
            args = ["-a", "-f", str(scn.render.fps), str(scn.render.fps_base), "-s", str(start_frame), 
                    "-e", str(end_frame), "-j", str(scn.frame_step), start_frame_path]

            #bpy.ops.loom.run_terminal(arguments=" ".join(args), terminal_instance=False)
            bpy.ops.loom.run_terminal( 
                #debug_arguments=self.debug,
                terminal_instance=False,
                argument_collection=self.pack_arguments(args),
                force_bash=False)

        else: 
            """ Changes some scenes properties temporarily... Bullshit!
            However, the only way using the default operator at the moment """
            outfile = scn.render.filepath
            file_format = scn.render.image_settings.file_format
            scn.render.filepath = start_frame_format
            timeline = (scn.frame_start, scn.frame_end)
            
            scn.frame_start = start_frame
            scn.frame_end = end_frame
            if preview_filetype: scn.render.image_settings.file_format = 'JPEG'

            self.report({'INFO'}, "[Default-OP Playback] {}".format(sequence_name))
            self.report({'INFO'}, "Playblast {}-{}".format(start_frame, end_frame))

            bpy.ops.render.play_rendered_anim() # Try it again!

            scn.frame_start = timeline[0]
            scn.frame_end = timeline[1]
            scn.render.filepath = outfile
            scn.render.image_settings.file_format = file_format

        return {'FINISHED'}




# Classes for registration
classes = (
    LOOM_OT_playblast,
)
