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
Preset system for Loom addon.

Provides render preset functionality to save and load render settings.
"""

import bpy
from bl_operators.presets import AddPresetBase


class LOOM_OT_render_preset(AddPresetBase, bpy.types.Operator):
    """Store or remove the current render settings as new preset"""
    bl_idname = 'loom.render_preset'
    bl_label = 'Add a new Render Preset'
    preset_menu = 'LOOM_MT_render_presets'

    preset_subdir = "loom/render_presets"
    preset_defines = [
                    'context = bpy.context',
                    'scene = context.scene',
                    'render = scene.render'
                     ]

    # References:
    # -> ./api/current/bpy.types.Menu.html#preset-menus
    # -> https://blender.stackexchange.com/a/211543
    # -> scripts/startup/preset.py

    @property
    def preset_values(self):
        context = bpy.context
        scene = context.scene
        preset_flags = scene.loom.render_preset_flags
        ignore_attribs = ('_', 'bl_', 'rna', 'reg', 'unreg', 'name')

        """ Defaults """
        preset_values = [
            "render.engine",
            'render.film_transparent',
            'render.fps',
            'render.fps_base',
            'render.frame_map_new',
            'render.frame_map_old',
            'render.threads',
            'render.use_high_quality_normals',
            'render.use_motion_blur',
            'render.use_persistent_data',
            #'render.use_simplify',
            'render.use_overwrite',
            'render.use_placeholder'
        ]

        """ User Flags """
        if preset_flags.include_resolution:
            preset_values += [
                            'render.resolution_x',
                            'render.resolution_y',
                            'render.resolution_percentage',
                            'render.filter_size',
                            'render.pixel_aspect_x',
                            'render.pixel_aspect_y',
                            'render.use_border',
                            'render.use_crop_to_border',
                            ]

        if preset_flags.include_output_path:
            preset_values.append('render.filepath')

        if preset_flags.include_scene_settings:
            preset_values += [
                            'scene.camera',
                            #'scene.background_set',
                            #'scene.active_clip'
                            ]

        if preset_flags.include_color_management:
            preset_values += [
                            'scene.display_settings.display_device',
                            'scene.view_settings.view_transform',
                            'scene.view_settings.look',
                            'scene.view_settings.exposure',
                            'scene.view_settings.gamma',
                            'scene.view_settings.use_curve_mapping',
                            ]

        if preset_flags.include_metadata:
            preset_values += [
                            'render.use_stamp',
                            'render.use_stamp_camera',
                            'render.use_stamp_date',
                            'render.use_stamp_filename',
                            'render.use_stamp_frame',
                            'render.use_stamp_frame_range',
                            'render.use_stamp_hostname',
                            'render.use_stamp_labels',
                            'render.use_stamp_lens',
                            'render.use_stamp_marker',
                            'render.use_stamp_memory',
                            'render.use_stamp_note',
                            'render.use_stamp_render_time',
                            'render.use_stamp_scene',
                            'render.use_stamp_sequencer_strip',
                            'render.use_stamp_time',
                            ]

        if preset_flags.include_post_processing:
            preset_values += [
                            'render.use_compositing',
                            'render.use_sequencer',
                            'render.dither_intensity',
                            ]

        if preset_flags.include_passes:
            for prop in dir(context.view_layer):
                if prop.startswith("use_"):
                    preset_values.append("context.view_layer.{}".format(prop))

            if bpy.context.scene.render.engine in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT') and \
                hasattr(context.view_layer, "eevee"):
                for prop in dir(context.view_layer.eevee):
                    if prop.startswith("use_"):
                        preset_values.append("context.view_layer.eevee.{}".format(prop))

        if preset_flags.include_file_format:
            preset_values += [
                            'render.image_settings.file_format',
                            'render.image_settings.color_mode',
                            'render.image_settings.color_depth',
                            ]
            image_settings = scene.render.image_settings
            if image_settings.file_format in ('OPEN_EXR', 'OPEN_EXR_MULTILAYER'):
                preset_values += [
                                'render.image_settings.exr_codec',
                                'render.image_settings.use_preview'
                                ]
                if bpy.app.version < (4, 0, 0):
                    preset_values.append('render.image_settings.use_zbuffer')

            if image_settings.file_format in ('TIFF'):
                preset_values += ['render.image_settings.tiff_codec']
            if image_settings.file_format in ('JPEG'):
                preset_values += ['render.image_settings.quality']

        """ Engine Settings """
        if preset_flags.include_engine_settings:
            if scene.render.engine == 'CYCLES':
                for prop in dir(scene.cycles):
                    if not prop.startswith(ignore_attribs):
                        preset_values.append("scene.cycles.{}".format(prop))

            elif bpy.context.scene.render.engine in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
                for prop in dir(scene.eevee):
                    if "options" in prop:
                        continue
                    if not prop.startswith(ignore_attribs + ("gi_cache_info",)):
                        preset_values.append("scene.eevee.{}".format(prop))

            elif scene.render.engine == 'HYDRA_STORM':
                for prop in dir(scene.hydra_storm):
                    if not prop.startswith(ignore_attribs + ("type",)):
                        preset_values.append("scene.hydra_storm.{}".format(prop))

            elif scene.render.engine == 'BLENDER_WORKBENCH':
                for prop in dir(scene.display.shading):
                    if not prop.startswith(ignore_attribs + ("selected_studio_light", "cycles", "wireframe_color_type")):
                        preset_values.append("scene.display.shading.{}".format(prop))
                for prop in dir(scene.display):
                    if not prop.startswith(ignore_attribs + ("shading",)):
                        preset_values.append("scene.display.{}".format(prop))

        return preset_values


class LOOM_MT_render_presets(bpy.types.Menu):
    bl_label = 'Loom Render Presets'
    preset_subdir = 'loom/render_presets'
    preset_operator = 'script.execute_preset'
    draw = bpy.types.Menu.draw_preset


# Classes for registration
classes = (
    LOOM_OT_render_preset,
    LOOM_MT_render_presets,
)
