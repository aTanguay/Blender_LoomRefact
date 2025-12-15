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
Blender 5.0 compatibility helper functions.

These functions provide compatibility wrappers for API changes between
Blender 4.x and Blender 5.0.
"""


def get_compositor_node_tree(scene):
    """Get the compositor node tree for a scene (Blender 5.0+ compatibility).

    In Blender 5.0, scene.node_tree was replaced with scene.compositing_node_group
    for compositor nodes.
    """
    # Blender 5.0+ uses compositing_node_group
    if hasattr(scene, 'compositing_node_group'):
        return scene.compositing_node_group
    # Older versions use node_tree
    elif hasattr(scene, 'node_tree'):
        return scene.node_tree
    return None


def get_action_fcurves(action):
    """Get all F-Curves from an action (Blender 5.0+ compatibility).

    In Blender 5.0, the legacy action.fcurves API was removed.
    F-Curves are now accessed through layers/strips/channelbags.

    Yields all FCurve objects from the action.
    """
    if action is None:
        return

    # Blender 5.0+ uses layered actions with channelbags
    if hasattr(action, 'layers') and len(action.layers) > 0:
        for layer in action.layers:
            if hasattr(layer, 'strips'):
                for strip in layer.strips:
                    # Get channelbags - they contain the fcurves
                    if hasattr(strip, 'channelbags'):
                        for channelbag in strip.channelbags:
                            if hasattr(channelbag, 'fcurves'):
                                for fcurve in channelbag.fcurves:
                                    yield fcurve
    # Legacy API (Blender 4.x and earlier)
    elif hasattr(action, 'fcurves'):
        for fcurve in action.fcurves:
            yield fcurve


def get_active_action(context):
    """Get the active action from context (Blender 5.0+ compatibility).

    In Blender 5.0, space_data.action was removed from Dope Sheet context.
    Use context.active_action instead.
    """
    # Blender 5.0+ uses context.active_action
    if hasattr(context, 'active_action'):
        return context.active_action
    # Legacy: try space_data.action
    if hasattr(context, 'space_data') and hasattr(context.space_data, 'action'):
        return context.space_data.action
    return None
