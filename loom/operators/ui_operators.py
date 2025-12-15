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
UI-related operators for Loom addon.

Contains operators for preferences management, render dialogs, and keyframe/marker selection.
"""

import bpy
from itertools import count, groupby

# Import helpers
from ..helpers.blender_compat import get_compositor_node_tree, get_action_fcurves, get_active_action


# Default global variables and project directories
# These are used by LOOM_OT_preferences_reset
global_var_defaults = {
    "$BLEND": 'bpy.path.basename(bpy.data.filepath)[:-6]',
    "$F4": '"{:04d}".format(bpy.context.scene.frame_current)',
    "$SCENE": 'bpy.context.scene.name',
    "$CAMERA": 'bpy.context.scene.camera.name',
    "$LENS": '"{:0.0f}mm".format(bpy.context.scene.camera.data.lens)',
    "$VIEWLAYER": 'bpy.context.view_layer.name',
    "$MARKER": 'next((i.name for i in bpy.context.scene.timeline_markers if i.frame == bpy.context.scene.frame_current), "NO_NAME")',
    "$COLL": 'bpy.context.collection.name',
    "$OB": 'bpy.context.active_object.name',
    "$DAY": 'exec("import time") or time.strftime("%Y-%m-%d")',
    "$TIME": 'exec("import time") or time.strftime("%H-%M-%S")',
    "$SUM": 'str(sum([8, 16, 32]))'
}

project_directories = {
    1: "assets",
    2: "geometry",
    3: "textures",
    4: "render",
    5: "comp"
}

# User keymap IDs for preferences reset
user_keymap_ids = []


class LOOM_OT_preferences_reset(bpy.types.Operator):
    """Reset Add-on Preferences"""
    bl_idname = "loom.reset_preferences"
    bl_label = "Reset Loom Preferences"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
        props = prefs.__annotations__.keys()
        for p in props:
            prefs.property_unset(p)

        """ Restore Globals """
        for key, value in global_var_defaults.items():
            gvi = prefs.global_variable_coll.add()
            gvi.name = key
            gvi.expr = value

        """ Project Directories """
        for key, value in project_directories.items():
            di = prefs.project_directory_coll.add()
            di.name = value
            di.creation_flag = True

        """ Restore default keys by keymap ids """
        kc_usr = context.window_manager.keyconfigs.user
        km_usr = kc_usr.keymaps.get('Screen')
        for i in user_keymap_ids:
            kmi = km_usr.keymap_items.from_id(i)
            if kmi:
                km_usr.restore_item_to_default(kmi)

        return {'FINISHED'}


class LOOM_OT_globals_ui(bpy.types.Operator):
    """Move global variables up and down, add and remove"""
    bl_idname = "loom.globals_ui"
    bl_label = "Global Actions"
    bl_options = {'REGISTER', 'INTERNAL'}

    action: bpy.props.EnumProperty(
        items=(
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
        idx = prefs.global_variable_idx
        try:
            item = prefs.global_variable_coll[idx]
        except IndexError:
            pass
        else:
            if self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (prefs.global_variable_coll[idx].name)
                prefs.global_variable_idx -= 1
                prefs.global_variable_coll.remove(idx)
                if prefs.global_variable_idx < 0: prefs.global_variable_idx = 0
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            item = prefs.global_variable_coll.add()
            prefs.global_variable_idx = len(prefs.global_variable_coll)-1
            info = '"%s" added to list' % (item.name)
            self.report({'INFO'}, info)

        return {"FINISHED"}


class LOOM_OT_directories_ui(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "loom.directories_ui"
    bl_label = "Directory Actions"
    bl_options = {'REGISTER', 'INTERNAL'}

    action: bpy.props.EnumProperty(
        items=(
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
        idx = prefs.project_coll_idx
        try:
            item = prefs.project_directory_coll[idx]
        except IndexError:
            pass
        else:
            if self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (prefs.project_directory_coll[idx].name)
                prefs.project_coll_idx -= 1
                prefs.project_directory_coll.remove(idx)
                if prefs.project_coll_idx < 0: prefs.project_coll_idx = 0

        if self.action == 'ADD':
            item = prefs.project_directory_coll.add()
            item.creation_flag = True
            prefs.project_coll_idx = len(prefs.project_directory_coll)-1
        return {"FINISHED"}


class LOOM_OT_render_dialog(bpy.types.Operator):
    """Render Image Sequence Dialog"""
    bl_idname = "loom.render_dialog"
    bl_label = "Render Image Sequence"
    bl_options = {'REGISTER'}

    show_errors: bpy.props.BoolProperty(
        name="Show Errors",
        description="Displays Errors and Warnings",
        default=False,
        options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return not context.scene.render.is_movie_format

    def check(self, context):
        return True

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

    def write_permission(self, folder): # Hacky, but ok for now
        # https://stackoverflow.com/q/2113427/3091066
        try: # os.access(os.path.realpath(bpy.path.abspath(out_folder)), os.W_OK)
            import os
            pf = os.path.join(folder, "permission.txt")
            fh = open(pf, 'w')
            fh.close()
            os.remove(pf)
            return True
        except:
            return False

    def execute(self, context):
        addon_name = __package__.split('.')[0]
        prefs = context.preferences.addons[addon_name].preferences
        scn = context.scene
        lum = scn.loom
        filter_individual_numbers = lum.filter_input
        user_input = lum.frame_input

        """ Error handling """
        user_error = False
        if not self.options.is_invoke:
            user_error = True

        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Blend-file not saved.")
            bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT')
            user_error = True

        if not user_input and not any(char.isdigit() for char in user_input):
            self.report({'ERROR'}, "No frames to render.")
            user_error = True

        """ Scene validation """
        if scn.render.use_sequencer and hasattr(scn, "sequencer"):
            if len(scn.sequence_editor.sequences) and self.validate_sequencer(context):
                if not user_input.isdigit():
                    self.report(
                        {'INFO'},
                        "Scene Strip(s) in 'Sequencer' detected: "
                        "Switched to Command Line rendering...")
                    lum.command_line = True
        else:
            if scn.render.use_compositing and scn.use_nodes:
                rlyr = self.validate_comp(context)
                if rlyr is not None:
                    self.report(
                        {'WARNING'},
                        "No camera assigned in '{}' "
                        "scene (used in comp).".format(rlyr))
                    user_error = True
            else:
                if not scn.camera:
                    self.report({'WARNING'}, "No active camera.")
                    user_error = True

        if user_error: #bpy.ops.loom.render_dialog('INVOKE_DEFAULT')
            return {"CANCELLED"}

        """ Tests passed """
        if not lum.override_render_settings:
            lum.property_unset("custom_render_presets")

        """ Start rendering headless or within the UI as usual """
        if lum.command_line:
            bpy.ops.loom.render_terminal(
                #debug=True,
                frames = user_input,
                threads = lum.threads,
                isolate_numbers = filter_individual_numbers,
                render_preset = lum.custom_render_presets)
        else:
            bpy.ops.render.image_sequence(
                frames = user_input,
                isolate_numbers = filter_individual_numbers,
                render_silent = False,
                validate_scene = False)
        return {"FINISHED"}

    def invoke(self, context, event):
        addon_name = __package__.split('.')[0]
        scn = context.scene
        lum = scn.loom
        prefs = context.preferences.addons[addon_name].preferences

        if not lum.is_property_set("frame_input") or not lum.frame_input:
            bpy.ops.loom.guess_frames(detect_missing_frames=False)
        #lum.property_unset("custom_render_presets") # Reset Preset Property

        if not prefs.is_property_set("terminal") or not prefs.terminal:
            bpy.ops.loom.verify_terminal()
        if not lum.is_property_set("threads") or not lum.threads:
            lum.threads = scn.render.threads  # *.5

        return context.window_manager.invoke_props_dialog(self,
            width=(prefs.render_dialog_width))

    def draw(self, context):
        addon_name = __package__.split('.')[0]
        scn = context.scene
        lum = scn.loom
        prefs = context.preferences.addons[addon_name].preferences
        layout = self.layout  #layout.label(text="Render Image Sequence")
        split_factor = .17

        split = layout.split(factor=split_factor)
        col = split.column(align=True)
        col.label(text="Frames:")
        col = split.column(align=True)
        sub = col.row(align=True) #GHOST_ENABLED
        # guess_icon = 'AUTO' if len(lum.render_collection) else 'PREVIEW_RANGE'
        sub.operator("loom.guess_frames", icon='PREVIEW_RANGE', text="")
        sub.prop(lum, "frame_input", text="")
        sub.prop(lum, "filter_input", icon='FILTER', icon_only=True)
        #sub.prop(lum, "filter_keyframes", icon='SPACE2', icon_only=True)
        sub.operator("loom.verify_frames", icon='GHOST_ENABLED', text="")

        split = layout.split(factor=split_factor)
        col = split.column(align=True)
        col.active = not lum.command_line
        col.label(text="Display:")
        col = split.column(align=True)
        sub = col.row(align=True)
        sub.active = not lum.command_line
        sub.prop(prefs, "render_display_type", text="") #context.preferences.view
        sub.prop(scn.render, "use_lock_interface", icon_only=True)

        row = layout.row(align=True)
        row.prop(lum, "command_line", text="Render using Command Line")
        if scn.render.resolution_percentage < 100:
            row.prop(self, "show_errors", text="", icon='TEXT' if self.show_errors else "REC", emboss=False)
        else:
            hlp = row.operator("loom.openurl", icon='HELP', text="", emboss=False)
            hlp.description = "Open Loom Documentation on Github"
            hlp.url = "https://github.com/p2or/blender-loom"

        if lum.command_line:
            from ..properties.render_props import render_preset_callback
            row = layout.row(align=True)
            row.prop(lum, "override_render_settings",  icon='PARTICLE_DATA', icon_only=True)
            if len(render_preset_callback(scn, context, addon_name)) > 1:
                #split = row.split(factor=split_factor)
                #split.label(text="Preset:")
                #row = layout.row(align=True)
                preset = row.row(align=True)
                preset.prop(lum, "custom_render_presets", text="")
                preset.enabled = lum.override_render_settings
            else:
                thr_elem = row.row(align=True)
                thr_elem.active = bool(lum.command_line and lum.override_render_settings)
                thr_elem.prop(lum, "threads")
                thr_elem.operator("loom.render_threads", icon='LOOP_BACK', text="")
            layout.separator(factor=0.1)

        if self.show_errors:
            res_percentage = scn.render.resolution_percentage
            if res_percentage < 100:
                row = layout.row()
                row.label(text="Warning: Resolution Percentage Scale is set to {}%".format(res_percentage))
                row.operator("loom.render_full_scale", icon="INDIRECT_ONLY_OFF", text="", emboss=False)


class LOOM_OT_render_input_dialog(bpy.types.Operator):
    """Pass custom Frame Numbers and Ranges to the Render Dialog"""
    bl_idname = "loom.render_input_dialog"
    bl_label = "Render Frames"
    bl_options = {'INTERNAL'}

    frame_input: bpy.props.StringProperty()
    flipbook_dialog: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})
    operator_description: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        if properties.operator_description: #return self.__doc__
            return properties.operator_description

    def execute(self, context):
        if not self.frame_input:
            return {'CANCELLED'}

        context.scene.loom.frame_input = self.frame_input
        if self.flipbook_dialog:
            bpy.ops.loom.render_flipbook('INVOKE_DEFAULT')
        else:
            bpy.ops.loom.render_dialog('INVOKE_DEFAULT')
        return {'FINISHED'}


class LOOM_OT_selected_keys_dialog(bpy.types.Operator):
    """Render selected Keyframes in the Timeline, Graph Editor or Dopesheet"""
    bl_idname = "loom.selected_keys_dialog"
    bl_label = "Render Selected Keyframes"
    bl_options = {'REGISTER'}

    limit_to_object_selection: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})
    limit_to_scene_frames: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})
    all_keyframes: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})
    flipbook_dialog: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})

    def int_filter(self, flt):
        try:
            return int(flt)
        except ValueError:
            return None

    def rangify_frames(self, frames):
        """ Converts a list of integers to range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def keyframes_from_actions(self, context, object_selection=False, keyframe_selection=True):
        """ Returns either selected keys by object selection or all keys """
        actions = bpy.data.actions
        if object_selection:
            obj_actions = [i.animation_data.action for i in context.selected_objects if i.animation_data]
            if obj_actions:
                actions = obj_actions
        # There is a select flag for the handles:
        # key.select_left_handle & key.select_right_handle
        ctrl_points = set()
        for action in actions:
            for channel in get_action_fcurves(action): #if channel.select:
                for key in channel.keyframe_points:
                    if keyframe_selection:
                        if key.select_control_point:
                            ctrl_points.add(key.co.x)
                    else:
                        ctrl_points.add(key.co.x)
        return sorted(ctrl_points)

    def keyframes_from_channel(self, action):
        """ Returns selected keys based on the action in the action editor """
        ctrl_points = set()
        for channel in get_action_fcurves(action):
            for key in channel.keyframe_points:
                if key.select_control_point:
                    ctrl_points.add(key.co.x)
        return sorted(ctrl_points)

    def selected_ctrl_points(self, context):
        """ Returns selected keys in the dopesheet if a channel is selected """
        ctrl_points = set()
        for sel_keyframe in context.selected_editable_keyframes:
            if sel_keyframe.select_control_point:
                    ctrl_points.add(sel_keyframe.co.x)
        return sorted(ctrl_points)

    def channel_ctrl_points(self):
        """ Returns all keys of selected channels in dopesheet """
        ctrl_points = set()
        for action in bpy.data.actions:
            for channel in get_action_fcurves(action):
                if channel.select: #print(action, channel.group)
                    for key in channel.keyframe_points:
                        ctrl_points.add(key.co.x)
        return sorted(ctrl_points)

    def selected_gpencil_frames(self, context):
        """ Returns all selected grease pencil frames """
        ctrl_points = set()
        for o in context.selected_objects:
            if o.type in ('GPENCIL', 'GREASEPENCIL'):
                for l in o.data.layers:
                    for f in l.frames:
                        if f.select:
                            ctrl_points.add(f.frame_number)
        return sorted(ctrl_points)

    @classmethod
    def poll(cls, context):
        editors = ('DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'TIMELINE')
        '''
        areas = [a.type for a in context.screen.areas]
        return any((True for x in areas if x in editors))
        '''
        return context.space_data.type in editors and \
            not context.scene.render.is_movie_format

    def invoke(self, context, event):
        if event.ctrl:
            self.all_keyframes = True
        if event.alt:
            self.limit_to_scene_frames = True
        return self.execute(context)

    def execute(self, context):
        space = context.space_data

        selected_keys = None
        if space.type == 'DOPESHEET_EDITOR':
            mode = context.space_data.mode

            if mode == 'GPENCIL':
                selected_keys = self.selected_gpencil_frames(context)

            elif mode == 'ACTION':
                # Blender 5.0+: space_data.action removed, use get_active_action helper
                active_action = get_active_action(context)
                if active_action:
                    selected_keys = self.keyframes_from_channel(active_action)

            elif mode == 'MASK':
                self.report({'ERROR'}, "Not implemented.")
                return {"CANCELLED"}

            elif mode == 'CACHEFILE':
                self.report({'ERROR'}, "Not implemented.")
                return {"CANCELLED"}

            else: # Mode can be: DOPESHEET, 'SHAPEKEY'
                # if context.space_data.mode == 'DOPESHEET':
                if self.limit_to_object_selection and not context.selected_objects:
                    self.report({'ERROR'}, "No Object(s) selected")
                    return {"CANCELLED"}

                selected_keys = self.keyframes_from_actions(
                        context = context,
                        object_selection = self.limit_to_object_selection,
                        keyframe_selection = not self.all_keyframes)

        elif space.type == 'GRAPH_EDITOR':
            selected_keys = self.keyframes_from_actions(
                    context = context,
                    object_selection = self.limit_to_object_selection,
                    keyframe_selection = not self.all_keyframes)

        if not selected_keys:
            self.report({'ERROR'}, "No Keyframes selected")
            return {"CANCELLED"}

        """ Return integers whenever possible """
        int_frames = [self.int_filter(frame) for frame in selected_keys]
        frames = selected_keys if None in int_frames else int_frames

        if self.limit_to_scene_frames:
            scn = context.scene
            frames = set(frames).intersection(range(scn.frame_start, scn.frame_end+1))
            if not frames:
                self.report({'ERROR'}, "No frames keyframes in scene range")
                return {"CANCELLED"}

        bpy.ops.loom.render_input_dialog(
            frame_input=self.rangify_frames(frames),
            flipbook_dialog=self.flipbook_dialog
            )
        return {'FINISHED'}


class LOOM_OT_selected_makers_dialog(bpy.types.Operator):
    """Render selected Markers in the Timeline or Dopesheet"""
    bl_idname = "loom.selected_makers_dialog"
    bl_label = "Render Selected Markers"
    bl_options = {'REGISTER'}

    all_markers: bpy.props.BoolProperty(options={'SKIP_SAVE'})
    flipbook_dialog: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})

    def rangify_frames(self, frames):
        """ Converts a list of integers to range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    @classmethod
    def poll(cls, context):
        editors = ('DOPESHEET_EDITOR', 'TIMELINE')
        return context.space_data.type in editors and \
            not context.scene.render.is_movie_format

    def invoke(self, context, event):
        if event.alt:
            self.all_markers = True
        return self.execute(context)

    def execute(self, context):
        if not self.all_markers:
            markers = sorted(m.frame for m in context.scene.timeline_markers if m.select)
        else:
            markers = sorted(m.frame for m in context.scene.timeline_markers)

        if not markers:
            if not self.all_markers:
                self.report({'ERROR'}, "Select any Marker to render or enable 'All Markers'.")
            else:
                self.report({'ERROR'}, "No Markers to render.")
            return {"CANCELLED"}

        bpy.ops.loom.render_input_dialog(
            frame_input=self.rangify_frames(markers),
            flipbook_dialog=self.flipbook_dialog
            )

        return {'FINISHED'}


# Classes for registration
classes = (
    LOOM_OT_preferences_reset,
    LOOM_OT_globals_ui,
    LOOM_OT_directories_ui,
    LOOM_OT_render_dialog,
    LOOM_OT_render_input_dialog,
    LOOM_OT_selected_keys_dialog,
    LOOM_OT_selected_makers_dialog,
)
