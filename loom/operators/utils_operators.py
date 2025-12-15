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
Utility operators for Loom addon.

Contains misc utility operators for file management, markers, globals,
and project setup.
"""

import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
import os
import subprocess
import webbrowser
from sys import platform

# Import helpers
from ..helpers.blender_compat import get_compositor_node_tree
from ..helpers.globals_utils import replace_globals, user_globals, isevaluable
from ..helpers.version_utils import render_version


class LOOM_OT_open_folder(bpy.types.Operator):
    """Opens a certain Folder in the File Browser"""
    bl_idname = "loom.open_folder"
    bl_label = "Open Folder"
    bl_options = {'INTERNAL'}
    
    folder_path: bpy.props.StringProperty()
    
    def execute(self, context):
        fp = self.folder_path
        glob_vars = context.preferences.addons[__name__].preferences.global_variable_coll
        if any(ext in fp for ext in glob_vars.keys()):
            fp = replace_globals(fp, addon_name)
        
        fp = os.path.realpath(bpy.path.abspath(fp))
        if os.path.isfile(fp) or not os.path.exists(fp):
            fp = os.path.dirname(fp)
        if not os.path.isdir(fp):
            self.report({'INFO'}, "'{}' no folder".format(fp))
            return {"CANCELLED"}
        try:
            if platform.startswith('darwin'):
                webbrowser.open("file://{}".format(fp))
            elif platform.startswith('linux'):
                try:
                    #os.system('xdg-open "{}"'.format(fp))
                    subprocess.call(["xdg-open", fp])
                except:
                    webbrowser.open(fp)
            else:
                webbrowser.open(fp)
        except OSError:
            self.report({'INFO'}, "'{}' does not exist".format(fp))
        return {'FINISHED'}



class LOOM_OT_open_output_folder(bpy.types.Operator):
    """Open up the Output Directory in the File Browser"""
    bl_idname = "loom.open_ouput_dir"
    bl_label = "Open Output Directory"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        fp = context.scene.render.filepath
        glob_vars = context.preferences.addons[__name__].preferences.global_variable_coll
        if any(ext in fp for ext in glob_vars.keys()):
            fp = replace_globals(fp, addon_name)

        fp = os.path.realpath(bpy.path.abspath(fp))
        if not os.path.isdir(fp):
            fp = os.path.dirname(fp)
        if os.path.isdir(fp):
            bpy.ops.loom.open_folder(folder_path=fp)
        else:
            bpy.ops.loom.open_folder(folder_path=bpy.path.abspath("//"))
            self.report({'INFO'}, "Folder does not exist")
        return {'FINISHED'}



class LOOM_OT_utils_node_cleanup(bpy.types.Operator):
    """Remove version strings from File Output Nodes"""
    bl_idname = "loom.remove_version_strings"
    bl_label = "Remove Version Strings from File Output Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # space = context.space_data return space.type == 'NODE_EDITOR'
        # Blender 5.0+ uses compositing_node_group instead of node_tree
        node_tree = get_compositor_node_tree(context.scene)
        return node_tree is not None and hasattr(node_tree, "nodes")
        
    def remove_version(self, fpath):
        match = re.search(r'(v\d+)', fpath)
        delimiters = ("-", "_", ".")
        if match:
            head, tail = fpath.split(match.group(0))
            if tail.startswith(delimiters):
                tail = tail[1:]
            fpath = head + tail
            return fpath[:-1] if fpath.endswith(delimiters) else fpath
        else:
            return fpath
    
    def execute(self, context):
        scene = context.scene    
        node_tree = get_compositor_node_tree(scene)
        nodes = node_tree.nodes
        output_nodes = [n for n in nodes if n.type=='OUTPUT_FILE']
        
        if not output_nodes:
            self.report({'INFO'}, "Nothing to operate on")
            return {'CANCELLED'}
            
        for out_node in output_nodes:
            if "LAYER" in out_node.format.file_format:
                out_node.base_path = self.remove_version(out_node.base_path)
                for layer in out_node.layer_slots:
                    layer.name = self.remove_version(layer.name)
            else:
                out_node.base_path = self.remove_version(out_node.base_path)
                for out_file in out_node.file_slots:
                    out_file.path = self.remove_version(out_file.path)
            
            scene.loom.output_sync_comp=False
        return {'FINISHED'}



class LOOM_OT_open_preferences(bpy.types.Operator):
    """Preferences Window"""
    bl_idname = "loom.open_preferences"
    bl_label = "Loom Preferences"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        bpy.ops.preferences.addon_show(module="loom")
        return {'FINISHED'}
        
        

class LOOM_OT_openURL(bpy.types.Operator):
    """Open URL in default Browser"""
    bl_idname = "loom.open_url"
    bl_label = "Documentation"
    bl_options = {'INTERNAL'}
    
    url: bpy.props.StringProperty(name="URL")
    description: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        return properties.description

    def execute(self, context):
        webbrowser.open_new(self.url)
        return {'FINISHED'}



class LOOM_OT_delete_bash_files(bpy.types.Operator):
    """Delete temporary bash file"""
    bl_idname = "loom.delete_bashfiles"
    bl_label = "Delete temporary Bash File"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        addon_name = __package__.split('.')[0]

        prefs = context.preferences.addons[addon_name].preferences

        rem_lst = []
        for f in os.scandir(bpy.utils.script_path_user()):
            if f.name.endswith((".sh", ".bat")) and \
                f.name.startswith("loom-") and f.is_file():
                    try:
                        os.remove(f.path)
                        rem_lst.append(f.name)
                    except:
                        pass
        if rem_lst:
            self.report({'INFO'}, "{} removed.".format(", ".join(rem_lst)))
            prefs.bash_file = ""
        else:
            self.report({'INFO'}, "Nothing to remove")
        return {'FINISHED'}



class LOOM_OT_delete_file(bpy.types.Operator):
    """Deletes a file by given path"""
    bl_idname = "loom.delete_file"
    bl_label = "Remove a File"
    bl_options = {'INTERNAL'}
    
    file_path: bpy.props.StringProperty()
    message_success: bpy.props.StringProperty(default="File removed")
    message_error: bpy.props.StringProperty(default="No file")
    
    def execute(self, context):
        try:
            os.remove(self.file_path)
            self.report({'INFO'}, self.message_success)
            return {'FINISHED'}
        except:
            self.report({'WARNING'}, self.message_error)
            return {'CANCELLED'}



class LOOM_OT_utils_create_directory(bpy.types.Operator):
    """Create a directory based on a given path"""
    bl_idname = "loom.create_directory"
    bl_label = "Create given directory"
    bl_options = {'INTERNAL'}
    
    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        if not self.directory:
            self.report({'WARNING'},"No directory specified")
            return {'CANCELLED'}
        
        abs_path = bpy.path.abspath(self.directory)

        '''
        head, tail = os.path.split(abs_path)
        if not os.path.isdir(head):
            self.report({'WARNING'},"Access denied: '{}' does not exists".format(head))
            return {'CANCELLED'}
        else:
        '''
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
            self.report({'INFO'},"'{}' created".format(abs_path))
        else:
            self.report({'INFO'},"'{}' already in place".format(abs_path))
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)



class LOOM_OT_utils_marker_unbind(bpy.types.Operator):
    """Unbind Markers in Selection"""
    bl_idname = "loom.unbind_markers"
    bl_label = "Unbind Markers from Cameras in Selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return any(m for m in context.scene.timeline_markers if m.select)
    
    def execute(self, context):
        marker_candidates = [m for m in context.scene.timeline_markers if m.select]
        for m in marker_candidates:
            m.camera = None
        self.report({'INFO'}, "Detached {} Marker(s)".format(len(marker_candidates))) 
        
        return {'FINISHED'}
        


class LOOM_OT_utils_marker_rename(bpy.types.Operator):
    """Rename Markers in Selection"""
    bl_idname = "loom.rename_markers"
    bl_label = "Rename Markers in Selection"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "new_name"
    
    new_name: bpy.props.StringProperty(
        name="New Name",
        default="$SCENE_$LENS_$F4_###")
    
    @classmethod
    def poll(cls, context):
        return any(m for m in context.scene.timeline_markers if m.select)
    
    def execute(self, context):
        frame_curr = context.scene.frame_current
        markers = [m for m in context.scene.timeline_markers if m.select]
        markers = sorted(markers, key=lambda m: m.frame)
        for c, m in enumerate(markers):
            frame_flag = False
            marker_name = self.new_name
            if "$" in marker_name:
                context.scene.frame_set(m.frame)
                marker_name = replace_globals(marker_name, addon_name)
                frame_flag = True
            if "#" in marker_name:
                hashes = self.new_name.count("#")
                number = "{n:0{digits}d}".format(n=c, digits=hashes)
                marker_name = marker_name.replace("#"*hashes, number)
            m.name = marker_name
        
        if frame_flag:   
            context.scene.frame_set(frame_curr)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, "new_name")
        layout.row()
        


class LOOM_OT_utils_marker_generate(bpy.types.Operator):
    """Add Markers from Cameras in Selection"""
    bl_idname = "loom.generate_markers"
    bl_label = "Add Markers based on Selected Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    def set_playhead(self, context):
        if self.playhead:
            self.frame = context.scene.frame_current
        else:
            self.frame = max(
                context.scene.frame_start, 
                max([m.frame for m in context.scene.timeline_markers], default=1))
                
    offset: bpy.props.IntProperty(
        name="Frame Offset",
        description="Offset Markers by Frame",
        default=1, min=1)
        
    frame: bpy.props.IntProperty(
        name="Insert on Frame",
        default=1)
    
    sort_reverse: bpy.props.BoolProperty(
        name = "Add Camera Markers in reverse Order",
        default = False)

    playhead: bpy.props.BoolProperty(
        name = "Insert Markers at Playhead Position",
        default = False,
        update=set_playhead)

    @classmethod
    def poll(cls, context):
        return any(c for c in context.selected_objects if c.type == 'CAMERA')
        
    def execute(self, context):
        cam_candidates = [c for c in context.selected_objects if c.type == 'CAMERA']
        if not cam_candidates:
            self.report({'INFO'}, "No Cameras in Selection")
            return {"CANCELLED"}
        
        cam_candidates = sorted(
            cam_candidates, 
            key=lambda o: o.name, 
            reverse=self.sort_reverse)
        
        if self.playhead:
            self.frame = context.scene.frame_current
            
        markers = context.scene.timeline_markers
        marker_frames = sorted(m.frame for m in markers)
        
        for cam in cam_candidates:
            if self.frame in marker_frames:
                m = [m for m in markers if m.frame==self.frame][0]
                m.name = cam.name
            else:            
                m = markers.new(cam.name, frame=self.frame)
            m.camera = cam
            self.frame += self.offset
            
        self.report({'INFO'}, "Added {} Markers".format(len(cam_candidates)))
        return {'FINISHED'}
        
    def invoke(self, context, event):
        if self.playhead:
            self.frame = context.scene.frame_current
        return context.window_manager.invoke_props_dialog(self, width=500)
    
    def draw(self, context):
        scn = context.scene        
        layout = self.layout
        layout.separator()
        row = layout.row()
        split = row.split(factor=0.9, align=True)
        c = split.column(align=True)
        c.prop(self, "frame")
        c.enabled = not self.playhead
        col = split.column(align=True)
        col.prop(self, "playhead", icon='NLA_PUSHDOWN', text="")
        row = layout.row()
        row.prop(self, "sort_reverse", icon='SORTALPHA')
        row = layout.row()
        row.prop(self, "offset")        
        layout.separator()



class LOOM_OT_select_project_directory(bpy.types.Operator, ExportHelper):
    """Select Project Directory using the File Browser"""
    bl_idname = "loom.select_project_directory"
    bl_label = "Project Directory"
    bl_options = {'INTERNAL'}

    filename_ext = ""
    use_filter_folder = True
    cursor_pos = [0,0]
    
    def display_popup(self, context):
        win = context.window #win.cursor_warp((win.width*.5)-100, (win.height*.5)+100)
        win.cursor_warp(x=self.cursor_pos[0], y=self.cursor_pos[1]+100) # re-invoke the dialog
        bpy.ops.loom.set_project_dialog('INVOKE_DEFAULT')

    def cancel(self, context):
        if bpy.app.version < (4, 1, 0): self.display_popup(context)

    def invoke(self, context, event):
        self.cursor_pos = [event.mouse_x, event.mouse_y]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        scn = context.scene
        lum = scn.loom
        lum.project_directory = os.path.dirname(self.filepath)
        if bpy.app.version < (4, 1, 0): self.display_popup(context)
        return {'FINISHED'}



class LOOM_OT_project_dialog(bpy.types.Operator):
    """Loom — Set Project Dialog"""
    bl_idname = "loom.set_project_dialog"
    bl_label = "Setup Project Directory"
    bl_options = {'REGISTER'}
    
    directory: bpy.props.StringProperty(name="Project Directory")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scn = context.scene
        lum = scn.loom

        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Blend-file not saved.")
            bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT')
            return {'CANCELLED'}

        project_dir = lum.project_directory
        if not self.options.is_invoke:
            project_dir = self.directory
        
        if not project_dir or not os.path.isdir(project_dir):
            self.report({'ERROR'}, "Please specify a valid Project Directory")
            bpy.ops.loom.set_project_dialog('INVOKE_DEFAULT')
            return {'CANCELLED'}

        errors = []
        addon_name = __package__.split('.')[0]

        prefs = context.preferences.addons[addon_name].preferences
        for d in prefs.project_directory_coll:
            if d.creation_flag and d.name:
                pdir = os.path.join(project_dir, d.name)
                bpy.ops.loom.create_directory(directory=pdir)
                if not os.path.isdir(bpy.path.abspath(pdir)):
                    errors.append(d.name)
                if any(x in d.name.lower() for x in ["rndr", "render"]):
                    if os.path.isdir(bpy.path.abspath(pdir)) and \
                        scn.render.filepath.startswith(("/tmp", "/temp")) or \
                        scn.render.filepath == "//":
                        scn.render.filepath = bpy.path.relpath(pdir) + "/"

        if not errors:
            self.report({'INFO'}, "All directories successfully created")
        else:
            self.report({'WARNING'}, 
                "Something went wrong while creating [{0}]".format(
                    ', '.join(map(str, errors))))
        
        return {'FINISHED'}

    def invoke(self, context, event):
        addon_name = __package__.split('.')[0]

        prefs = context.preferences.addons[addon_name].preferences
        lum = context.scene.loom
        if not context.scene.loom.project_directory:
            lum.project_directory = bpy.path.abspath('//')
        return context.window_manager.invoke_props_dialog(self, width=prefs.project_dialog_width)

    def check(self, context):
        return True

    def draw(self, context):
        addon_name = __package__.split('.')[0]

        prefs = context.preferences.addons[addon_name].preferences
        scn = context.scene
        lum = scn.loom
        
        layout = self.layout
        row = layout.row()
        row.template_list(
            listtype_name = "LOOM_UL_directories", 
            list_id = "", 
            dataptr = prefs,
            propname = "project_directory_coll", 
            active_dataptr = prefs,
            active_propname = "project_coll_idx", 
            rows=6)
        
        col = row.column(align=True)
        col.operator(LOOM_OT_directories_ui.bl_idname, icon='ADD', text="").action = 'ADD'
        col.operator(LOOM_OT_directories_ui.bl_idname, icon='REMOVE', text="").action = 'REMOVE'
        layout.separator()
        row = layout.row(align=True)
        row.prop(lum, "project_directory")
        row.operator(LOOM_OT_select_project_directory.bl_idname, icon='FILE_FOLDER', text="")
        layout.separator()



class LOOM_OT_bake_globals(bpy.types.Operator):
    """Apply Globals or Restore Filepaths"""
    bl_idname = "loom.globals_bake"
    bl_label = "Bake Globals"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    action: bpy.props.EnumProperty(
        name="Action",
        description="Apply or Restore Paths",
        default = 'APPLY',
        items=(
            ('RESET', "Restore User Paths", "", "RECOVER_LAST", 1),
            ('APPLY', "Apply Globals", "", "WORLD_DATA", 2)))

    def out_nodes(self, scene):
        tree = get_compositor_node_tree(scene)
        return [n for n in tree.nodes if n.type=='OUTPUT_FILE'] if tree else []

    def execute(self, context):
        scn = context.scene    
        addon_name = __package__.split('.')[0]
    
        prefs = context.preferences.addons[addon_name].preferences
        glob_vars = prefs.global_variable_coll
        lum = scn.loom

        '''
        if any(ext in scn.render.filepath for ext in glob_vars.keys()):
            scn.render.filepath = replace_globals(scn.render.filepath, addon_name)
        for node in self.out_nodes(scn):
            node.base_path = replace_globals(node.base_path, addon_name)
            if "LAYER" in node.format.file_format:
                for slot in node.layer_slots:
                    slot.name = replace_globals(slot.name, addon_name)
            else:
                for slot in node.file_slots:
                    slot.path = replace_globals(slot.path, addon_name)
        # DEBUG
        for i in lum.path_collection:
            print (30*"-")
            print (i.name)
            print (i.orig, i.repl)
            for s in i.slts:
                print (s.orig, s.repl)
        '''

        if self.action == 'APPLY':
            """ Main output path """
            if any(ext in scn.render.filepath for ext in glob_vars.keys()):
                item = lum.path_collection.get("Output Path")
                if not item:
                    item = lum.path_collection.add()
                item.name = "Output Path" #item.id = 
                item.orig = scn.render.filepath
                compiled_path = replace_globals(scn.render.filepath, addon_name)
                item.repl = compiled_path
                # Set the regular file path 
                scn.render.filepath = compiled_path

            """ Output nodes """
            for node in self.out_nodes(scn):
                item = lum.path_collection.get(node.name)
                if not item:
                    item = lum.path_collection.add()
                item.name = node.name
                item.orig = node.base_path
                item.repl = replace_globals(node.base_path, addon_name)
                # Set the base path
                if item.repl: node.base_path = item.repl

                if "LAYER" in node.format.file_format:
                    for slot in node.layer_slots:
                        slt = item.slts.get(slot.name)
                        if not slt:
                            slt = item.slts.add()
                        slt.name = slot.name
                        slt.orig = slot.name
                        slt.repl = replace_globals(slot.name, addon_name)
                        # Set the slot name
                        if slt.repl: slot.name = slt.repl
                else:
                    for slot in node.file_slots:
                        slt = item.slts.get(slot.path)
                        if not slt:
                            slt = item.slts.add()
                        slt.name = slot.path
                        slt.orig = slot.path
                        slt.repl = replace_globals(slot.path, addon_name)
                        if slt.repl: slot.path = slt.repl
            self.report({'INFO'}, "Replaced all Globals")
        
        if self.action == 'RESET':
            node_tree = get_compositor_node_tree(scn)
            for i in lum.path_collection:
                if i.name == "Output Path":
                    scn.render.filepath = i.orig
                else:
                    node = node_tree.nodes.get(i.name) if node_tree else None
                    if node:
                        node.base_path = i.orig
                        if "LAYER" in node.format.file_format:
                            for slot in node.layer_slots:
                                for o in i.slts:
                                    if o.repl == slot.name:
                                        slot.name = o.orig
                        else:
                            for slot in node.file_slots:
                                for o in i.slts:
                                    if o.repl == slot.path:
                                        slot.path = o.orig
            self.report({'INFO'}, "Reset all Paths")
        return {'FINISHED'}



class LOOM_OT_output_paths(bpy.types.Operator):
    """Convert all output paths either into relative or absolute paths"""
    bl_idname = "loom.output_paths"
    bl_label = "Convert Output File Paths"
    bl_options = {'REGISTER', 'UNDO'}
    
    action: bpy.props.EnumProperty(
        name="Convert Paths to",
        description="Absolute or relative Paths",
        default = 'RELATIVE',
        items=(
            ('ABSOLUTE', "Absolute Paths", "", "CURVE_PATH", 1),
            ('RELATIVE', "Relative Paths", "", "CON_FOLLOWPATH", 2)),
        options={'SKIP_SAVE'})
    
    out_path: bpy.props.BoolProperty(
        name="Convert output path",
        description="Convert the regular output path",
        default=True)
        
    comp_paths: bpy.props.BoolProperty(
        name="Convert paths used in Comp",
        description="Convert the paths of all file output nodes used in comp",
        default=True)
    
    def convert_path(self, filepath, relative=True):
        basedir, filename = os.path.split(filepath)
        if relative:
            basedir = bpy.path.relpath(basedir)
        else:
            basedir = os.path.realpath(bpy.path.abspath(basedir))
        return os.path.join(basedir, filename)

    def out_nodes(self, scene):
        tree = get_compositor_node_tree(scene)
        return [n for n in tree.nodes if n.type=='OUTPUT_FILE'] if tree else []
    
    def execute(self, context):
        scn = context.scene
        
        if self.action == 'ABSOLUTE':
            if self.out_path:
                scn.render.filepath = self.convert_path(scn.render.filepath, relative=False)
            if self.comp_paths:
                for node in self.out_nodes(scn):
                    node.base_path = self.convert_path(node.base_path, relative=False)
        else:
            if self.out_path:
                scn.render.filepath = self.convert_path(scn.render.filepath)
            if self.comp_paths:
                for node in self.out_nodes(scn):
                    node.base_path = self.convert_path(node.base_path)

        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)
        #else: return self.execute(context)
        
    def draw(self, context):
        layout = self.layout
        #layout.separator()
        row = layout.row()
        row = row.prop(self, "action") # , expand=True
        row = layout.row(align=True)
        row.prop(self, "out_path", toggle=True)
        row.prop(self, "comp_paths", toggle=True)
        row = layout.row()



class LOOM_OT_utils_framerange(bpy.types.Operator):
    bl_idname = "loom.shot_range"
    bl_label = "Shot Range"
    bl_description = "Set Frame Range to 1001-1241"
    bl_options = {'REGISTER', 'UNDO'}
    
    start: bpy.props.IntProperty(
        name="Start Frame",
        description="Custom start frame",
        default=1001)
    
    end: bpy.props.IntProperty(
        name="End Frame",
        description="Custom end frame",
        default=1241)

    @classmethod
    def poll(cls, context):
        return context.area.type == 'DOPESHEET_EDITOR'

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def execute(self, context):
        bpy.ops.action.view_all()
        context.scene.frame_start = self.start
        context.scene.frame_end = self.end
        context.scene.frame_current = self.start
        bpy.ops.action.view_all()
        return{'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "start")
        row.prop(self, "end")
        layout.separator(factor=0.5)




# Classes for registration
classes = (
    LOOM_OT_open_folder,
    LOOM_OT_open_output_folder,
    LOOM_OT_utils_node_cleanup,
    LOOM_OT_open_preferences,
    LOOM_OT_openURL,
    LOOM_OT_delete_bash_files,
    LOOM_OT_delete_file,
    LOOM_OT_utils_create_directory,
    LOOM_OT_utils_marker_unbind,
    LOOM_OT_utils_marker_rename,
    LOOM_OT_utils_marker_generate,
    LOOM_OT_select_project_directory,
    LOOM_OT_project_dialog,
    LOOM_OT_bake_globals,
    LOOM_OT_output_paths,
    LOOM_OT_utils_framerange,
)
