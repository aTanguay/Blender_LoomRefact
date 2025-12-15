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
Render-related property groups for Loom addon.

Contains property groups for render logging, batch rendering,
preset flags, and file output paths.
"""

import bpy
import os


def render_preset_callback(scene, context, addon_name):
    """Callback to populate render preset enum items.

    Args:
        scene: Current scene
        context: Blender context
        addon_name: Name of the addon for accessing preferences

    Returns:
        List of tuples for enum items
    """
    items = [('EMPTY', "Current Render Settings", "")]
    preset_path = context.preferences.addons[addon_name].preferences.render_presets_path
    if os.path.exists(preset_path):
        for f in os.listdir(preset_path):
            if not f.startswith(".") and f.endswith(".py"):
                fn, ext = os.path.splitext(f)
                #d = bpy.path.display_name(os.path.join(rndr_presets_path, f))
                items.append((f, "'{}' Render Preset".format(fn), ""))
    return items


class LOOM_PG_render(bpy.types.PropertyGroup):
    """Property group for render logging information."""
    # name: bpy.props.StringProperty()
    render_id: bpy.props.IntProperty()
    start_time: bpy.props.StringProperty()
    start_frame: bpy.props.StringProperty()
    end_frame: bpy.props.StringProperty()
    file_path: bpy.props.StringProperty()
    padded_zeros: bpy.props.IntProperty()
    image_format: bpy.props.StringProperty()


class LOOM_PG_batch_render(bpy.types.PropertyGroup):
    """Property group for batch render queue items."""
    # name: bpy.props.StringProperty()
    rid: bpy.props.IntProperty()
    path: bpy.props.StringProperty()
    frame_start: bpy.props.IntProperty()
    frame_end: bpy.props.IntProperty()
    scene: bpy.props.StringProperty()
    frames: bpy.props.StringProperty(name="Frames")
    encode_flag: bpy.props.BoolProperty(default=False)
    input_filter: bpy.props.BoolProperty(default=False)


class LOOM_PG_preset_flags(bpy.types.PropertyGroup):
    """Property group for render preset save/load flags."""

    include_engine_settings: bpy.props.BoolProperty(
        name="Engine Settings", # Currently not exposed to the user
        description="Store 'Render Engine' settings",
        default=True)

    include_resolution: bpy.props.BoolProperty(
        name="Resolution",
        description="Store current 'Format' settings")

    include_output_path: bpy.props.BoolProperty(
        name="Output Path",
        description="Store current 'Output Path'")

    include_file_format: bpy.props.BoolProperty(
        name="File Format",
        description="Store current 'File Format' settings")

    include_scene_settings: bpy.props.BoolProperty(
        name="Scene Settings",
        description="Store current 'Scene' settings")

    include_passes: bpy.props.BoolProperty(
        name="Passes",
        description="Store current 'Passes' settings")

    include_color_management: bpy.props.BoolProperty(
        name="Color Management",
        description="Store current 'Color Management' settings")

    include_metadata: bpy.props.BoolProperty(
        name="Metadata",
        description="Store current 'Metadata' settings")

    include_post_processing: bpy.props.BoolProperty(
        name="Post Processing", # Currently not exposed to the user
        description="Store current 'Post Processing' settings",
        default=True)


class LOOM_PG_slots(bpy.types.PropertyGroup):
    """Property group for file output node slots."""
    # name: bpy.props.StringPropery()
    orig: bpy.props.StringProperty()
    repl: bpy.props.StringProperty()


class LOOM_PG_paths(bpy.types.PropertyGroup):
    """Property group for file output paths and their slots."""
    # name: bpy.props.StringPropery()
    id: bpy.props.IntProperty()
    orig: bpy.props.StringProperty()
    repl: bpy.props.StringProperty()
    slts: bpy.props.CollectionProperty(name="Slot Collection", type=LOOM_PG_slots)


# Classes for registration (order matters - LOOM_PG_slots before LOOM_PG_paths)
classes = (
    LOOM_PG_render,
    LOOM_PG_batch_render,
    LOOM_PG_preset_flags,
    LOOM_PG_slots,
    LOOM_PG_paths,
)
