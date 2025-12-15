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

"""Helper functions and utilities for Loom addon."""

# Import from submodules
from .blender_compat import (
    get_compositor_node_tree,
    get_action_fcurves,
    get_active_action,
)

from .frame_utils import (
    filter_frames,
)

from .version_utils import (
    version_number,
    render_version,
)

from .globals_utils import (
    isevaluable,
    replace_globals,
    user_globals,
)


__all__ = [
    # Blender compatibility
    "get_compositor_node_tree",
    "get_action_fcurves",
    "get_active_action",
    # Frame utilities
    "filter_frames",
    # Version utilities
    "version_number",
    "render_version",
    # Global variable utilities
    "isevaluable",
    "replace_globals",
    "user_globals",
]
