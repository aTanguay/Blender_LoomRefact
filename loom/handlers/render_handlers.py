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
Render handlers for Loom addon.

Provides persistent handlers for render events.
"""

import os
import bpy
from bpy.app.handlers import persistent

# Import helpers
from ..helpers.globals_utils import replace_globals


@persistent
def loom_meta_note(scene):
    """Handle metadata note with global variable replacement before render."""
    if scene.render.use_stamp_note and not scene.render.is_movie_format:
        addon_name = __package__.split('.')[0]
        prefs = bpy.context.preferences.addons[addon_name].preferences
        glob_vars = prefs.global_variable_coll

        scene.loom.meta_note = scene.render.stamp_note_text
        if any(ext in scene.render.stamp_note_text for ext in glob_vars.keys()):
            scene.render.stamp_note_text = replace_globals(scene.render.stamp_note_text, addon_name)

        lines = scene.render.stamp_note_text.split("\\n")
        scene.render.stamp_note_text = lines[0]
        if len(lines) > 1:
            scene.render.stamp_note_text += os.linesep
            for i in lines[1:]:
                scene.render.stamp_note_text += i + os.linesep


@persistent
def loom_meta_note_reset(scene):
    """Reset metadata note to original value after render."""
    if scene.render.use_stamp_note and not scene.render.is_movie_format:
        scene.render.stamp_note_text = scene.loom.meta_note


# Handler functions for registration
handlers = [
    (bpy.app.handlers.render_pre, loom_meta_note),
    (bpy.app.handlers.render_post, loom_meta_note_reset),
    (bpy.app.handlers.render_cancel, loom_meta_note_reset),
]
