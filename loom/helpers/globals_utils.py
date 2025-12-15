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
Global variable utilities.

Provides functions for managing and replacing user-defined global variables
in file output paths.
"""

import bpy

from .blender_compat import get_compositor_node_tree


def isevaluable(s):
    """Check if a string can be evaluated as Python code.

    Args:
        s: String to evaluate

    Returns:
        True if evaluable, False otherwise
    """
    try:
        eval(s)
        return True
    except:
        return False


def replace_globals(s, addon_name, debug=False):
    """Replace string by given global entries.

    Args:
        s: String to process for global variable replacement
        addon_name: Name of the addon (for accessing preferences)
        debug: If True, print debug info instead of replacing

    Returns:
        String with global variables replaced
    """
    vars = bpy.context.preferences.addons[addon_name].preferences.global_variable_coll
    for key, val in vars.items():
        if not debug:
            if key.startswith("$") and not key.isspace():
                if val.expr and not val.expr.isspace():
                    if isevaluable(val.expr):
                        s = s.replace(key, str(eval(val.expr)))
                    else:
                        s = s.replace(key, "NO-{}".format(key.replace("$", "")))
        else:
            print (key, val, val.expr)
    return s


def user_globals(context, addon_name):
    """Determine whether globals are used in the scene.

    Args:
        context: Blender context
        addon_name: Name of the addon (for accessing preferences)

    Returns:
        True if global variables are found in render paths, False otherwise
    """
    scn = context.scene
    vars = context.preferences.addons[addon_name].preferences.global_variable_coll
    if any(ext in scn.render.filepath for ext in vars.keys()):
        return True
    tree = get_compositor_node_tree(scn)
    if scn.use_nodes and tree and len(tree.nodes) > 0:
        nodes = (n for n in tree.nodes if n.type=='OUTPUT_FILE')
        for node in nodes:
            if any(ext in node.base_path for ext in vars.keys()):
                return True
            if "LAYER" in node.format.file_format:
                for slot in node.layer_slots:
                    if any(ext in slot.name for ext in vars.keys()):
                        return True
            else:
                for slot in node.file_slots:
                     if any(ext in slot.path for ext in vars.keys()):
                         return True
    return False
