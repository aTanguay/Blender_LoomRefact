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
Scene-level property group for Loom addon.

Contains the main property group that is attached to bpy.types.Scene,
holding all scene-specific Loom settings.
"""

import bpy

# Import helpers for callbacks
from ..helpers.version_utils import render_version

# Import other property groups that this references
from .render_props import (
    LOOM_PG_render,
    LOOM_PG_batch_render,
    LOOM_PG_preset_flags,
    LOOM_PG_paths,
    render_preset_callback,  # Callback function for custom_render_presets enum
)


class LOOM_PG_scene_settings(bpy.types.PropertyGroup):
    """Main property group for Loom scene settings."""

    frame_input: bpy.props.StringProperty(
        name="Frames to render",
        description="Specify a range or single frames to render")

    filter_input: bpy.props.BoolProperty(
        name="Filter individual elements",
        description="Isolate numbers after exclude chars (^, !)",
        default=False)

    command_line: bpy.props.BoolProperty(
        name="Render using Command Line",
        description="Send frames to command line (background process)",
        default=False)

    is_rendering: bpy.props.BoolProperty(
        name="Render Flag",
        description="Determine whether Loom is rendering",
        default=False)

    override_render_settings: bpy.props.BoolProperty(
        name="Override render settings",
        description="Force to render with specified settings",
        default=False)

    threads: bpy.props.IntProperty(
        name="CPU Threads",
        description="Number of CPU threads to use simultaneously while rendering",
        min=1)

    sequence_encode: bpy.props.StringProperty(
        name="Image Sequence",
        description="Image sequence to encode",
        maxlen=1024)

    movie_path: bpy.props.StringProperty(
        name="Movie",
        description="Movie file output path",
        maxlen=1024)

    sequence_rename: bpy.props.StringProperty(
        name="Sequence Name",
        description="New sequence name for renaming",
        maxlen=1024)

    lost_frames: bpy.props.StringProperty(
        name="Missing Frames",
        description="Missing Frames of the given sequence",
        default="",
        options={'SKIP_SAVE'})

    render_collection: bpy.props.CollectionProperty(
        name="Render Collection",
        type=LOOM_PG_render)

    batch_scan_folder: bpy.props.StringProperty(
        name="Folder",
        description="Folder to search for .blend files",
        maxlen=1024)

    batch_render_idx: bpy.props.IntProperty(
        name="Collection Index",
        description="Collection Index")

    batch_render_coll: bpy.props.CollectionProperty(
        name="Batch Render Collection",
        type=LOOM_PG_batch_render)

    output_render_version: bpy.props.IntProperty(
        name = "Render Version",
        description="Change the given version number within the output path",
        default=1,
        min=1,
        update=render_version)

    output_sync_comp: bpy.props.BoolProperty(
        name="Sync Compositor",
        description="Keep version number of all file output nodes in sync",
        default=True)

    comp_image_settings: bpy.props.BoolProperty(
        name="Display Image Settings",
        description="Display image settings of each file output node",
        default=False)

    project_directory: bpy.props.StringProperty(
        name="Project Directory",
        description="Stores the path to the project directory",
        maxlen=1024)

    path_collection: bpy.props.CollectionProperty(
        name="Globals Path Collection",
        type=LOOM_PG_paths)

    scene_selection: bpy.props.BoolProperty(
        name="Limit by Object Selection",
        description="Only add keyframes assigned to the object(s) in selection",
        default=False)

    ignore_scene_range: bpy.props.BoolProperty(
        name="Ignore Scene Range",
        description="Do not consider the frame range of the scene",
        default=False)

    all_markers_flag: bpy.props.BoolProperty(
        name="All Markers",
        description="Add all markers to the list",
        default=False)

    render_preset_flags: bpy.props.PointerProperty(
        type=LOOM_PG_preset_flags)

    custom_render_presets: bpy.props.EnumProperty(
        name="Render Preset",
        description="Select a custom render preset",
        items=render_preset_callback,
        options={'SKIP_SAVE'})

    meta_note: bpy.props.StringProperty(
        name="Note",
        description="Stores the value of the stamp note")

    flipbook_flag: bpy.props.BoolProperty(
        name="Render Flipbook",
        description="Render the contents of the viewport",
        default=False,
        options={'SKIP_SAVE'})


# Classes for registration
classes = (
    LOOM_PG_scene_settings,
)
