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
Core rendering operators for Loom addon.

Contains operators for image sequence rendering, flipbook rendering,
and render configuration.
"""

import bpy
import os
import re
import subprocess
from sys import platform
from itertools import count, groupby

# Import helpers
from ..helpers.blender_compat import get_compositor_node_tree
from ..helpers.frame_utils import filter_frames
from ..helpers.version_utils import version_number

# Import presets
from ..presets.render_presets import LOOM_MT_render_presets


class LOOM_OT_render_threads(bpy.types.Operator):
    """Set all available threads"""
    bl_idname = "loom.available_threads"
    bl_label = "Reset Threads"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        from multiprocessing import cpu_count
        context.scene.loom.threads = cpu_count()
        self.report({'INFO'}, "Set to core maximum")
        return {'FINISHED'}



class LOOM_OT_render_full_scale(bpy.types.Operator):
    """Set Resolution Percentage Scale to 100%"""
    bl_idname = "loom.full_scale"
    bl_label = "Full Scale Image"
    bl_options = {'INTERNAL'}

    def execute(self, context): #context.area.tag_redraw()
        context.scene.render.resolution_percentage = 100
        return {'FINISHED'}



class LOOM_OT_guess_frames(bpy.types.Operator):
    """Either set the Range of the Timeline or find all missing Frames"""
    bl_idname = "loom.guess_frames"
    bl_label = "Set Timeline Range or detect missing Frames"
    bl_options = {'INTERNAL'}

    detect_missing_frames: bpy.props.BoolProperty(
            name="Missing Frames",
            description="Detect all missing Frames based based on the Output Path",
            default=True,
            options={'SKIP_SAVE'})

    def missing_frames(self, timeline_frames, rendered_frames):
        return sorted(set(timeline_frames).difference(rendered_frames))

    def rangify_frames(self, frames):
        """ Convert list of integers to Range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def execute(self, context):
        glob_vars = context.preferences.addons[__name__].preferences.global_variable_coll
        scn = context.scene
        lum = scn.loom

        timeline_range = "{start}-{end}".format(start=scn.frame_start, end=scn.frame_end)
        timeline_inc = "{range}x{inc}".format(range=timeline_range, inc=scn.frame_step)
        lum.frame_input = timeline_inc if scn.frame_step != 1 else timeline_range
        
        """ Detect missing frames """
        if self.detect_missing_frames:
            image_sequence = {}
            given_filename = True

            fp = bpy.path.abspath(scn.render.filepath)
            output_folder, file_name = os.path.split(fp)
            output_folder = os.path.realpath(output_folder)

            if any(ext in file_name for ext in glob_vars.keys()):
                    file_name = replace_globals(file_name)
            if any(ext in output_folder for ext in glob_vars.keys()):
                output_folder = replace_globals(output_folder)

            if not file_name:
                given_filename = False
                blend_name, ext = os.path.splitext(os.path.basename(bpy.data.filepath))
                file_name = blend_name + "_"

            hashes = file_name.count('#')
            if not hashes:
                file_name = "{}{}".format(file_name, "#"*4)

            if file_name.endswith(tuple(scn.render.file_extension)):
                file_path = os.path.join(output_folder, file_name)
            else:
                file_path = os.path.join(output_folder, "{}{}".format(file_name, scn.render.file_extension))

            basedir, filename = os.path.split(file_path)
            basedir = os.path.realpath(bpy.path.abspath(basedir))
            filename_noext, extension = os.path.splitext(filename)
            hashes = filename_noext.count('#')
            name_real = filename_noext.replace("#", "")
            file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=name_real, ds=hashes, ex=extension)
            seq_name = "{}{}{}".format(name_real, hashes*"#", extension)

            if not os.path.exists(basedir):
                self.report({'INFO'}, 'Set to default range, "{}" does not exist on disk'.format(basedir))
                return {"CANCELLED"}

            for f in os.scandir(basedir):
                if f.name.endswith(extension) and f.is_file():
                    match = re.match(file_pattern, f.name, re.IGNORECASE)
                    if match: image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

            if not len(image_sequence) > 1:
                if not given_filename:
                    return {"CANCELLED"}
                else:
                    # -> String needs to be split up, multiline "\" is not supported for INFO reports 
                    err_seq_name = 'No matching sequence with the name "{}" found in'.format(seq_name)
                    err_dir_name = 'directory "{}", set to default timeline range'.format(basedir)
                    self.report({'INFO'},"{} {}".format(err_seq_name, err_dir_name))
                return {"CANCELLED"}

            missing_frames = self.missing_frames(
                        [*range(scn.frame_start, scn.frame_end+1)],
                        sorted(list(image_sequence.keys())))

            if missing_frames:
                frames_to_render = self.rangify_frames(missing_frames)
                frame_count = len(missing_frames)
                lum.frame_input = frames_to_render
                self.report({'INFO'}, "{} missing Frame{} to render based on the output path: {} [{}]".format(
                    frame_count, 's'[:frame_count^1], seq_name, frames_to_render))
            else:
                self.report({'INFO'}, 'All given Frames are rendered, see "{}" folder'.format(basedir))
        return {'FINISHED'}

    def invoke(self, context, event):
        if event.ctrl or event.oskey:
            self.detect_missing_frames = False
        return self.execute(context)



class LOOM_OT_verify_frames(bpy.types.Operator):
    """Report all Frames to render & the current Render Location"""
    bl_idname = "loom.verify_frames"
    bl_label = "Verify Input Frames"
    bl_options = {'INTERNAL'}

    frame_input = None

    individual_frames: bpy.props.BoolProperty(
            name="Individual Frames",
            description="List all Frames individually",
            default=False,
            options={'SKIP_SAVE'})

    def rangify_frames(self, frames):
        """ Convert list of integers to Range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def execute(self, context):
        scn = context.scene
        if self.frame_input:
            frame_count = len(self.frame_input)
            msg =  "{} Frame{} will be rendered".format(
                frame_count, 's'[:frame_count^1])
            if frame_count > 1:
                if not self.individual_frames:
                    msg += ": [{}]".format(self.rangify_frames(self.frame_input))
                else:
                    msg += ": [{}]".format(', '.join('{}'.format(i) for i in self.frame_input))
            self.report({'INFO'}, msg)
        else:
            self.report({'INFO'}, "No frames specified")
        return {'FINISHED'}

    def invoke(self, context, event):
        lum = context.scene.loom
        self.frame_input = filter_frames(
            lum.frame_input, context.scene.frame_step, lum.filter_input)
        if event.ctrl or event.oskey:
            self.individual_frames = True
        return self.execute(context)



class LOOM_OT_render_terminal(bpy.types.Operator):
    """Render image sequence in terminal instance"""
    bl_idname = "loom.render_terminal"
    bl_label = "Render Image Sequence in Terminal Instance"
    bl_options = {'REGISTER', 'INTERNAL'}

    frames: bpy.props.StringProperty(
        name="Frames",
        description="Specify a range or frames to render")

    threads: bpy.props.IntProperty(
        name="CPU Threads",
        description="Number of CPU threads to use simultaneously while rendering",
        min = 1)

    digits: bpy.props.IntProperty(
        name="Digits",
        description="Specify digits in filename",
        default=4)

    isolate_numbers: bpy.props.BoolProperty(
        name="Filter Raw Items",
        description="Filter raw elements in frame input",
        default=False)

    render_preset: bpy.props.StringProperty(
        name="Render Preset",
        description="Pass a custom Preset.py")

    debug: bpy.props.BoolProperty(
        name="Debug Arguments",
        description="Print full argument list",
        default=False)

    def determine_type(self, val):
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

    @classmethod
    def poll(cls, context):
        return not context.scene.render.is_movie_format

    def execute(self, context):
        addon_name = __package__.split('.')[0]

        prefs = context.preferences.addons[addon_name].preferences

        if bpy.data.is_dirty: 
            # Save latest changes and suppress visual errors
            with suppress(RuntimeError):
                bpy.ops.wm.save_as_mainfile(
                    filepath=bpy.data.filepath)

        python_expr = ("import bpy;" +\
                "bpy.ops.render.image_sequence(" +\
                "frames='{fns}', isolate_numbers={iel}," +\
                "render_silent={cli}, digits={lzs}, render_preset='{pst}')").format(
                    fns=self.frames,
                    iel=self.isolate_numbers, 
                    cli=True, 
                    lzs=self.digits,
                    pst=self.render_preset)

        cli_args = ["-b", bpy.data.filepath, "--python-expr", python_expr]
        
        if self.properties.is_property_set("threads"):
            cli_args = cli_args + ["-t", "{}".format(self.threads)]

        bpy.ops.loom.run_terminal( 
            debug_arguments=self.debug,
            terminal_instance=True,
            argument_collection=self.pack_arguments(cli_args), 
            bash_name="loom-render-temp",
            force_bash = prefs.bash_flag)

        return {"FINISHED"}



class LOOM_OT_render_image_sequence(bpy.types.Operator):
    """Render image sequence either in background or within the UI"""
    bl_idname = "render.image_sequence"
    bl_label = "Render Image Sequence"
    bl_options = {'REGISTER', 'INTERNAL'}

    frames: bpy.props.StringProperty(
        name="Frames",
        description="Specify a range or single frames to render")

    isolate_numbers: bpy.props.BoolProperty(
        name="Filter Raw Items",
        description="Filter raw elements in frame input",
        default=False)

    render_silent: bpy.props.BoolProperty(
        name="Render silent",
        description="Render without displaying the progress within the UI",
        default=False)

    digits: bpy.props.IntProperty(
        name="Digits",
        description="Specify digits in filename",
        default=4)
    
    render_preset: bpy.props.StringProperty(
        name="Render Preset",
        description="Pass a custom Preset.py")

    validate_scene: bpy.props.BoolProperty(
        name="Scene Validation",
        description="Sequencer Strips, Active Camera etc.",
        default=True)

    _image_formats = {'BMP': 'bmp', 'IRIS': 'iris', 'PNG': 'png', 'JPEG': 'jpg', 
        'JPEG2000': 'jp2', 'TARGA': 'tga', 'TARGA_RAW': 'tga', 'CINEON': 'cin', 
        'DPX': 'dpx', 'OPEN_EXR_MULTILAYER': 'exr', 'OPEN_EXR': 'exr', 'HDR': 'hdr', 
        'TIFF': 'tif', 'WEBP': 'webp', 'SUPPLEMENT1': 'tiff', 'SUPPLEMENT2': 'jpeg'}

    _rendered_frames, _skipped_frames = [], []
    _timer = _frames = _stop = _rendering = _dec = _log = None
    _output_path = _folder = _filename = _extension = None
    _subframe_flag = _temp_display_type = False
    _output_nodes = {}
    
    @classmethod
    def poll(cls, context):
        if context.scene.render.is_movie_format:
            cls.poll_message_set("Video file formats are not supported by Loom")
            return False
        return True

    def pre_render(self, scene, depsgraph):
        self._rendering = True
        scene.loom.is_rendering = True

    def cancel_render(self, scene, depsgraph):
        self._stop = True
        self.reset_output_paths(scene)
        self._rendered_frames.pop()

    def post_render(self, scene, depsgraph):
        self._frames.pop(0)
        self._rendering = False
        scene.loom.is_rendering = False

    def file_extension(self, file_format):
        return self._image_formats[file_format]
    
    def subframes(self, sub_frames):
        subs = []
        for frame in sub_frames:
            main_frame, sub_frame = repr(frame).split('.')
            subs.append((int(main_frame), float('.' + sub_frame)))
        return subs

    def format_frame(self, file_name, frame, extension=None):
        file_name = replace_globals(file_name)
        if extension:
            return "{f}{fn:0{lz}d}.{ext}".format(
                f=file_name, fn=frame, lz=self.digits, ext=extension)
        else:
            return "{f}{fn:0{lz}d}_".format(
                f=file_name, fn=frame, lz=self.digits)

    def format_subframe(self, file_name, frame, extension=None):
        file_name = replace_globals(file_name)
        sub_frame = "{sf:.{dec}f}".format(sf = frame[1], dec=self._dec).split('.')[1]
        if extension:
            return "{f}{mf:0{lz}d}{sf}.{ext}".format(
                f=file_name, mf=frame[0], lz=self.digits, 
                sf=sub_frame, ext=extension)
        else:
            return "{f}{mf:0{lz}d}{sf}_".format(
                f=file_name, mf=frame[0], lz=self.digits, sf=sub_frame)

    def safe_filename(self, file_name):
        if file_name:
            if file_name.lower().endswith(tuple(self._image_formats.values())):
                name_real, ext = os.path.splitext(file_name)
            else:
                name_real = file_name
            if "#" in name_real:
                hashes = re.findall("#+$", name_real)
                name_real = re.sub("#", '', name_real)
                self.digits = len(hashes[0]) if hashes else 4
            return name_real + "_" if name_real and name_real[-1].isdigit() else name_real
        
        else: # If filename not specified, use blend-file name instead
            blend_name, ext = os.path.splitext(os.path.basename(bpy.data.filepath))
            return blend_name + "_"

    def out_nodes(self, scene):
        tree = get_compositor_node_tree(scene)
        return [n for n in tree.nodes if n.type=='OUTPUT_FILE'] if tree else []

    def reset_output_paths(self, scene):
        scene.render.filepath = self._output_path
        for k, v in self._output_nodes.items():
            k.base_path = v["Base Path"]
            if "File Slots" in v: # Reset Slots
                for c, fs in enumerate(k.file_slots):
                    fs.path = v["File Slots"][c]

    def frame_repath(self, scene, frame_number):
        ''' Set the frame, assamble main file and output node paths '''
        if self._subframe_flag:
            scene.frame_set(frame_number[0], subframe=frame_number[1])
            ff = self.format_subframe(self._filename, frame_number, self._extension)
        else:
            scene.frame_set(frame_number)
            ff = self.format_frame(self._filename, frame_number, self._extension)
        
        """ Final main path assembly """
        scene.render.filepath = os.path.join(self._folder, ff)
                
        for k, v in self._output_nodes.items():
            if "File Slots" in v:
                k.base_path = replace_globals(k.base_path)
                for c, f in enumerate(k.file_slots):
                    if self._subframe_flag:
                        f.path = self.format_subframe(v["File Slots"][c], frame_number)
                    else:
                        #f.path = self.format_frame(v["File Slots"][c], frame_number)
                        f.path = replace_globals(v["File Slots"][c])
            else:
                if self._subframe_flag:
                    of = self.format_subframe(v["Filename"], frame_number)
                else:
                    #of = self.format_frame(v["Filename"], frame_number)
                    of = replace_globals(v["Filename"])
                """ Final output node path assembly """
                k.base_path = os.path.join(replace_globals(v["Folder"]), of)

    def start_render(self, scene, frame, silent=False):
        rndr = scene.render
        if not rndr.use_overwrite and os.path.isfile(rndr.filepath):
            self._skipped_frames.append(frame)
            if not silent:
                self.post_render(scene, None)
            else:
                print("Skipped frame: {} (already exists)".format(frame))
        else:
            if rndr.use_placeholder and not os.path.isfile(rndr.filepath):
                os.makedirs(os.path.dirname(rndr.filepath), exist_ok=True)
                open(rndr.filepath, 'a').close()
            
            if silent:
                bpy.ops.render.render(write_still=True)
            else:
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)
            if frame not in self._rendered_frames:
                self._rendered_frames.append(frame)

    def validate_comp(self, context):
        node_tree = get_compositor_node_tree(context.scene)
        if context.scene.use_nodes and node_tree:
            for n in node_tree.nodes:
                if n.type == 'R_LAYERS' and not n.scene.camera:
                    if not n.mute:
                        return n.scene.name
        return None

    def validate_sequencer(self, context):
        seq = context.scene.sequence_editor
        for i in seq.sequences_all:
            if i.type == 'SCENE' and not i.mute:
                if not seq.channels[i.channel].mute:
                    return True
        return False

    def log_sequence(self, scene, limit):
        from time import ctime #lum.render_collection.clear()
        lum = scene.loom
        if len(lum.render_collection) == limit:
            lum.render_collection.remove(0)
        render = lum.render_collection.add()
        render.render_id = len(lum.render_collection)
        render.start_time = ctime()
        render.start_frame = str(self._frames[0])
        render.end_frame = str(self._frames[-1])
        render.name = self._filename
        render.file_path = self._output_path
        render.padded_zeros = self.digits if not self._dec else self.digits + self._dec
        render.image_format = self._extension

    def final_report(self):
        if self._rendered_frames:
            frame_count = len(self._rendered_frames)
            if isinstance(self._rendered_frames[0], tuple):
                rendered = ', '.join("{mf}.{sf}".format(
                    mf=i[0], sf=str(i[1]).split(".")[1]) for i in self._rendered_frames)
            else:
                rendered = ','.join(map(str, self._rendered_frames))
            self.report({'INFO'}, "{} {} rendered.".format(
                "Frames" if frame_count > 1 else "Frame", rendered))
            self.report({'INFO'}, "{} saved to {}".format(
                "Images" if frame_count > 1 else "Image", self._folder))
                
        if self._skipped_frames:
            if isinstance(self._skipped_frames[0], tuple):
                skipped = ', '.join("{mf}.{sf}".format(
                    mf=i[0], sf=str(i[1]).split(".")[1]) for i in self._skipped_frames)
            else:
                skipped = ','.join(map(str, self._skipped_frames))
            
            self.report(
                {'WARNING'}, 
                "Frame(s): {} skipped (would overwrite existing file(s))".format(skipped))

    def execute(self, context):
        scn = context.scene
        prefs = context.preferences
        loom_prefs = prefs.addons[__name__].preferences
        glob_vars = loom_prefs.global_variable_coll

        """ Filter user input """
        self._frames = filter_frames(self.frames, scn.frame_step, self.isolate_numbers)
        if not self._frames:
            self.report({'INFO'}, "No frames to render")
            return {"CANCELLED"}

        """ Scene validation in case the operator is called via console """
        if self.validate_scene:
            if scn.render.use_sequencer and len(scn.sequence_editor.sequences):
                if self.validate_sequencer(context):
                    if len(self._frames) > 1 and not self.render_silent:
                        self.report(
                            {'INFO'}, 
                            "Scene Strip(s) in 'Sequencer' detected: " 
                            "Automatically switched to 'silent' rendering...")
                        self.render_silent = True
            else:
                if scn.render.use_compositing and scn.use_nodes:
                    rlyr = self.validate_comp(context)
                    if rlyr is not None:
                        self.report(
                            {'WARNING'}, 
                            "No camera assigned in '{}' "
                            "scene (used in comp).".format(rlyr))
                        return {"CANCELLED"}
                else:
                    if not scn.camera:
                        self.report({'WARNING'}, "No camera in scene.")
                        return {"CANCELLED"}

        if not self.render_silent:
            self.report({'INFO'}, "Rendering Image Sequence...\n")

        """ Main output path """        
        self._output_path = scn.render.filepath
        output_folder, self._filename = os.path.split(bpy.path.abspath(self._output_path))
        self._folder = os.path.realpath(output_folder)        
        self._extension = self.file_extension(scn.render.image_settings.file_format)
        self._filename = self.safe_filename(self._filename)
        #self._output_path = os.path.join(self._folder, self._filename)

        """ Replace globals in main output path """
        if any(ext in self._folder for ext in glob_vars.keys()):
            self._folder = replace_globals(self._folder)
            bpy.ops.loom.create_directory(directory=self._folder)
            if not os.path.isdir(self._folder):
                self.report({'INFO'}, "Specified folder can not be created")
                return {"CANCELLED"}

        """ Output node paths """
        for out_node in self.out_nodes(scn):
            fd, fn = os.path.split(bpy.path.abspath(out_node.base_path))
            self._output_nodes[out_node] = {
                "Type": out_node.format.file_format,
                "Extension": self.file_extension(out_node.format.file_format),
                "Base Path": out_node.base_path,
                "Folder": os.path.realpath(fd),
                "Filename": fn}

            """ Single file slots in case """
            if not "LAYER" in out_node.format.file_format:
                self._output_nodes[out_node].update({"File Slots": [s.path for s in out_node.file_slots]})
                #"File Slots": {s.path : self.safe_filename(s.path) for s in out_node.file_slots}
        
        """ Clear assigned frame numbers """
        self._skipped_frames.clear(), self._rendered_frames.clear()

        """ Determine whether given frames are subframes """
        if isinstance(self._frames[0], float):
            self._frames = self.subframes(self._frames)
            self._dec = max(map(lambda x: len(str(x[1]).split('.')[1]), self._frames))
            self._subframe_flag = True

        """ Logging """
        if loom_prefs.log_render: self.log_sequence(scn, loom_prefs.log_render_limit)
        
        """ Render silent """
        if self.render_silent:
            """ Apply custom Render Preset """
            if self.render_preset and self.render_preset != "EMPTY":
                bpy.ops.script.execute_preset(
                    filepath=os.path.join(loom_prefs.render_presets_path,self.render_preset),
                    menu_idname=LOOM_MT_render_presets.__name__)
            
            for frame_number in self._frames:
                self.frame_repath(scn, frame_number)
                self.start_render(scn, frame_number, silent=True)

            """ Reset output path & display results """
            self.final_report()
            self.reset_output_paths(scn)
            return {"FINISHED"}

        """ Add timer & handlers for modal """
        if not self.render_silent:
            self._stop = False
            self._rendering = False
            bpy.app.handlers.render_pre.append(self.pre_render)
            bpy.app.handlers.render_post.append(self.post_render)
            bpy.app.handlers.render_cancel.append(self.cancel_render)
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.3, window=context.window)
            wm.modal_handler_add(self)

            """ Set render display type, see: #78 """
            #if prefs.view.render_display_type == 'SCREEN': #'WINDOW'
            self._temp_display_type = prefs.view.render_display_type
            prefs.view.render_display_type = loom_prefs.render_display_type

            return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == 'TIMER':
            scn = context.scene

            """ Determine whether frame list is empty or process is interrupted by the user """
            if not self._frames or self._stop: #if True in (not self._frames, self._stop is True):
                context.window_manager.event_timer_remove(self._timer)
                bpy.app.handlers.render_pre.remove(self.pre_render)
                bpy.app.handlers.render_post.remove(self.post_render)
                bpy.app.handlers.render_cancel.remove(self.cancel_render)

                """ Reset output path & display type"""
                self.reset_output_paths(scn)
                context.preferences.view.render_display_type = self._temp_display_type
                
                """ Display results """
                self.final_report()

                return {"FINISHED"}

            elif self._rendering is False:
                """ Render within UI & show the progress as usual """
                if self._frames:
                    frame_number = self._frames[0]
                    self.frame_repath(scn, frame_number)
                    self.start_render(scn, frame_number, silent=False)

        return {"PASS_THROUGH"}



class LOOM_OT_render_flipbook(bpy.types.Operator):
    """Render the Contents of the Viewport"""
    bl_idname = "loom.render_flipbook"
    bl_label = "Render Flipbook Animation"
    bl_options = {'REGISTER'}

    frames: bpy.props.StringProperty(
        name="Frames",
        description="Specify a range or frames to render")
    
    digits: bpy.props.IntProperty(
        name="Digits",
        description="Specify digits in filename",
        default=4)

    isolate_numbers: bpy.props.BoolProperty(
        name="Filter Raw Items",
        description="Filter raw elements in frame input",
        default=False)
    
    keep_overlays: bpy.props.BoolProperty(
        name="Keep Overlays",
        description="Do not turn off overlays while rendering",
        default=False,
        options={'SKIP_SAVE'})

    open_render_folder: bpy.props.BoolProperty(
        name="Open Render Folder",
        description="Open up the system folder when done",
        default=False,
        options={'SKIP_SAVE'})

    _image_formats = {'BMP': 'bmp', 'IRIS': 'iris', 'PNG': 'png', 'JPEG': 'jpg', 
        'JPEG2000': 'jp2', 'TARGA': 'tga', 'TARGA_RAW': 'tga', 'CINEON': 'cin', 
        'DPX': 'dpx', 'OPEN_EXR_MULTILAYER': 'exr', 'OPEN_EXR': 'exr', 'HDR': 'hdr', 
        'TIFF': 'tif', 'WEBP': 'webp', 'SUPPLEMENT1': 'tiff', 'SUPPLEMENT2': 'jpeg'}
    
    _rendered_frames, _skipped_frames = [], []
    _frames = _dec = _log = _output_path = _folder = _filename = _extension = None
    _subframe_flag = _overlays_state = _gizmos_state = False

    @classmethod
    def poll(cls, context):
        return not context.scene.render.is_movie_format
    
    def shading_type_order(self):
        d = {}
        for c, i in enumerate(bpy.types.View3DShading.bl_rna.properties['type'].enum_items):
            d[i.identifier] = c #print(i.identifier, i.name, i.description, i.icon)
        return d
    
    def predict_viewport(self, context):
        area = context.area
        if area.type != 'VIEW_3D':
            viewport_areas = []            
            for a in context.screen.areas:
                if a.type=='VIEW_3D':
                    viewport_areas.append(a)
            if not viewport_areas:
                return None
            highest_shading_type = 0
            sto = self.shading_type_order()
            for v in viewport_areas:
                sh = sto[v.spaces.active.shading.type]
                if sh > highest_shading_type:
                    highest_shading_type = sh
                    area = v
        return area

    def gizmos(self, area, state):
        if area.type == 'VIEW_3D':
            area.spaces[0].show_gizmo = state

    def overlays(self, area, state):
        if area.type == 'VIEW_3D':
            area.spaces[0].overlay.show_overlays = state

    def in_camera(self, area):
        return area.spaces[0].region_3d.view_perspective == 'CAMERA'

    def file_extension(self, file_format):
        return self._image_formats[file_format]

    def subframes(self, sub_frames):
        subs = []
        for frame in sub_frames:
            main_frame, sub_frame = repr(frame).split('.')
            subs.append((int(main_frame), float('.' + sub_frame)))
        return subs

    def format_frame(self, file_name, frame, extension=None):
        file_name = replace_globals(file_name)
        if extension:
            return "{f}{fn:0{lz}d}.{ext}".format(
                f=file_name, fn=frame, lz=self.digits, ext=extension)
        else:
            return "{f}{fn:0{lz}d}_".format(
                f=file_name, fn=frame, lz=self.digits)
    
    def format_subframe(self, file_name, frame, extension=None):
        file_name = replace_globals(file_name)
        sub_frame = "{sf:.{dec}f}".format(sf = frame[1], dec=self._dec).split('.')[1]
        if extension:
            return "{f}{mf:0{lz}d}{sf}.{ext}".format(
                f=file_name, mf=frame[0], lz=self.digits, 
                sf=sub_frame, ext=extension)
        else:
            return "{f}{mf:0{lz}d}{sf}_".format(
                f=file_name, mf=frame[0], lz=self.digits, sf=sub_frame)

    def safe_filename(self, file_name):
        if file_name:
            if file_name.lower().endswith(tuple(self._image_formats.values())):
                name_real, ext = os.path.splitext(file_name)
            else:
                name_real = file_name
            if "#" in name_real:
                hashes = re.findall("#+$", name_real)
                name_real = re.sub("#", '', name_real)
                self.digits = len(hashes[0]) if hashes else 4
            return name_real + "_" if name_real and name_real[-1].isdigit() else name_real
        
        else: # If filename not specified, use blend-file name instead
            blend_name, ext = os.path.splitext(os.path.basename(bpy.data.filepath))
            return blend_name + "_"

    def frame_repath(self, scene, frame_number):
        ''' Set the frame, assamble main file and output node paths '''
        if self._subframe_flag:
            scene.frame_set(frame_number[0], subframe=frame_number[1])
            ff = self.format_subframe(self._filename, frame_number, self._extension)
        else:
            scene.frame_set(frame_number)
            ff = self.format_frame(self._filename, frame_number, self._extension)
        
        scene.render.filepath = os.path.join(self._folder, ff)

    def log_sequence(self, scene, limit):
        from time import ctime #lum.render_collection.clear()
        lum = scene.loom
        if len(lum.render_collection) == limit:
            lum.render_collection.remove(0)
        render = lum.render_collection.add()
        render.render_id = len(lum.render_collection)
        render.start_time = ctime()
        render.start_frame = str(self._frames[0])
        render.end_frame = str(self._frames[-1])
        render.name = self._filename
        render.file_path = self._output_path
        render.padded_zeros = self.digits if not self._dec else self.digits + self._dec
        render.image_format = self._extension

    def reset_output_path(self, scene):
        scene.render.filepath = self._output_path

    def final_report(self):
        if self._rendered_frames:
            frame_count = len(self._rendered_frames)
            if isinstance(self._rendered_frames[0], tuple):
                rendered = ', '.join("{mf}.{sf}".format(
                    mf=i[0], sf=str(i[1]).split(".")[1]) for i in self._rendered_frames)
            else:
                rendered = ','.join(map(str, self._rendered_frames))
            
            self.report({'INFO'}, "{} {} rendered.".format(
                "Frames" if frame_count > 1 else "Frame", rendered))
            self.report({'INFO'}, "{} saved to {}".format(
                "Images" if frame_count > 1 else "Image", self._folder))
                
        if self._skipped_frames:
            if isinstance(self._skipped_frames[0], tuple):
                skipped = ', '.join("{mf}.{sf}".format(
                    mf=i[0], sf=str(i[1]).split(".")[1]) for i in self._skipped_frames)
            else:
                skipped = ','.join(map(str, self._skipped_frames))
            self.report({'ERROR'}, "Frame(s) {} skipped (would overwrite existing file(s))".format(skipped))

    def execute(self, context):
        scn = context.scene
        addon_name = __package__.split('.')[0]

        prefs = context.preferences.addons[addon_name].preferences
        glob_vars = prefs.global_variable_coll

        """ Filter user input """
        if self.options.is_invoke:
            self._frames = filter_frames(scn.loom.frame_input, scn.frame_step, self.isolate_numbers)
        else:
            self._frames = filter_frames(self.frames, scn.frame_step, self.isolate_numbers)

        if not self._frames:
            self.report({'ERROR'}, "No frames to render")
            return {"CANCELLED"}
        
        """ Viewport reference """
        area = self.predict_viewport(context)
        if not area:
            self.report({'ERROR'}, "No viewport to render")
            return {'CANCELLED'}

        """ Handle overlay states """
        self._overlays_state = area.spaces[0].overlay.show_overlays
        #self._gizmos_state = area.spaces[0].overlay.show_overlays
        if scn.render.engine != 'CYCLES':
            self.overlays(area, self.keep_overlays)

        """ Main output path """        
        self._output_path = scn.render.filepath
        output_folder, self._filename = os.path.split(bpy.path.abspath(self._output_path))
        self._folder = os.path.realpath(output_folder)        
        self._extension = self.file_extension(scn.render.image_settings.file_format)
        self._filename = self.safe_filename(self._filename)

        if any(ext in self._folder for ext in glob_vars.keys()):
            self._folder = replace_globals(self._folder)
            bpy.ops.loom.create_directory(directory=self._folder)
            if not os.path.isdir(self._folder):
                self.report({'INFO'}, "Specified folder can not be created")
                return {"CANCELLED"}
        
        """ Determine whether given frames are subframes """
        if isinstance(self._frames[0], float):
            self._frames = self.subframes(self._frames)
            self._dec = max(map(lambda x: len(str(x[1]).split('.')[1]), self._frames))
            self._subframe_flag = True

        """ Logging """
        self._skipped_frames.clear(), self._rendered_frames.clear()
        if prefs.log_render: self.log_sequence(scn, prefs.log_render_limit)

        """ Display the rendering progress """
        wm = context.window_manager
        wm.progress_begin(0, len(self._frames))

        """ Start the rendering """
        for c, f in enumerate(self._frames):
            self.frame_repath(scn, f)
            wm.progress_update(c)
            if not scn.render.use_overwrite and os.path.isfile(scn.render.filepath):
                self._skipped_frames.append(f)
                continue

            with context.temp_override(area=area):
                bpy.ops.render.opengl(write_still=True)

            if f not in self._rendered_frames:
                self._rendered_frames.append(f)

        """ Reset output path and overlay states """
        wm.progress_end()
        self.overlays(area, self._overlays_state)
        self.final_report()
        self.reset_output_path(scn)

        """ Open up the folder """
        if self.open_render_folder:
            addon_name = __package__.split('.')[0]

            prefs = context.preferences.addons[addon_name].preferences
            glob_vars = prefs.global_variable_coll

            output_folder, filename = os.path.split(bpy.path.abspath(scn.render.filepath))
            rndr_folder = os.path.realpath(output_folder)
            if any(ext in rndr_folder for ext in glob_vars.keys()):
                rndr_folder = replace_globals(rndr_folder)

            bpy.ops.loom.open_folder(
                folder_path=rndr_folder)
        
        return {"FINISHED"}

    def draw(self, context):
        lum = context.scene.loom
        layout = self.layout
        split_factor = .17

        split = layout.split(factor=split_factor)
        col = split.column(align=True)
        col.label(text="Frames:")
        col = split.column(align=True)
        sub = col.row(align=True)
        sub.operator(LOOM_OT_guess_frames.bl_idname, icon='PREVIEW_RANGE', text="")
        sub.prop(lum, "frame_input", text="")
        sub.prop(lum, "filter_input", icon='FILTER', icon_only=True)
        sub.operator(LOOM_OT_verify_frames.bl_idname, icon='GHOST_ENABLED', text="")       

        # current/bpy.types.PreferencesSystem.html#bpy.types.PreferencesSystem.viewport_aa
        split = layout.split(factor=split_factor) # prop(pref_system, "viewport_aa")
        split.label(text="Settings:")#Anti-Aliasing:
        row = split.row(align=True)
        row.prop(self, "keep_overlays", toggle=True, icon='OVERLAY', text="")
        row.prop(context.preferences.system, "viewport_aa", text="")
        #row.prop(context.preferences.system, "anisotropic_filter", text="")
        #row = layout.row(align=True)

        row = layout.row(align=True)    
        row.prop(self, "open_render_folder", text="Open render folder when done")

        hlp = row.operator("loom.openurl", icon='HELP', text="", emboss=False)
        hlp.description = "Open Loom Documentation on Github"
        hlp.url = "https://github.com/p2or/blender-loom"

    def invoke(self, context, event):
        lum = context.scene.loom
        addon_name = __package__.split('.')[0]

        prefs = context.preferences.addons[addon_name].preferences
        
        # Set invoke properties
        #self.frames = lum.frame_input
        self.open_render_folder = True
        if not lum.is_property_set("frame_input") or not lum.frame_input:
            bpy.ops.loom.guess_frames(detect_missing_frames=False)
        
        return context.window_manager.invoke_props_dialog(self, 
            width=(prefs.render_dialog_width))




# Classes for registration
classes = (
    LOOM_OT_render_threads,
    LOOM_OT_render_full_scale,
    LOOM_OT_guess_frames,
    LOOM_OT_verify_frames,
    LOOM_OT_render_terminal,
    LOOM_OT_render_image_sequence,
    LOOM_OT_render_flipbook,
)
