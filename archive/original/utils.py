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
Utility functions for the Loom addon.
"""

import bpy
import os
import re
from numpy import arange, around, isclose

from .compatibility import get_compositor_node_tree


def filter_frames(frame_input, increment=1, filter_individual=False):
    """ Filter frame input & convert it to a set of frames """
    def float_filter(st):
        try:
            return float(st)
        except ValueError:
            return None

    def int_filter(flt):
        try:
            return int(flt) if flt.is_integer() else None
        except ValueError:
            return None

    numeric_pattern = r"""
        [\^\!]? \s*? # Exclude option
        [-+]?        # Negative or positive number
        (?:
            # Range & increment 1-2x2, 0.0-0.1x.02
            (?: \d* \.? \d+ \s? \- \s? \d* \.? \d+ \s? [x%] \s? [-+]? \d* \.? \d+ )
            |
            # Range 1-2, 0.0-0.1 etc
            (?: \d* \.? \d+ \s? \- \s? [-+]? \d* \.? \d+ )
            |
            # .1 .12 .123 etc 9.1 etc 98.1 etc
            (?: \d* \. \d+ )
            |
            # 1. 12. 123. etc 1 12 123 etc
            (?: \d+ \.? )
        )
        """
    range_pattern = r"""
        ([-+]? \d*? \.? [0-9]+ \b) # Start frame
        (\s*? \- \s*?)             # Minus
        ([-+]? \d* \.? [0-9]+)     # End frame
        ( (\s*? [x%] \s*? )( [-+]? \d* \.? [0-9]+ \b ) )? # Increment
        """
    exclude_pattern = r"""
        [\^\!] \s*?             # Exclude option
        ([-+]? \d* \.? \d+)$    # Int or Float
        """

    rx_filter = re.compile(numeric_pattern, re.VERBOSE)
    rx_group = re.compile(range_pattern, re.VERBOSE)
    rx_exclude = re.compile(exclude_pattern, re.VERBOSE)

    input_filtered = rx_filter.findall(frame_input)
    if not input_filtered: return None

    """ Option to add a ^ or ! at the beginning to exclude frames """
    if not filter_individual:
        first_exclude_item = next((i for i, v in enumerate(input_filtered) if "^" in v or "!" in v), None)
        if first_exclude_item:
            input_filtered = input_filtered[:first_exclude_item] + \
                             [elem if elem.startswith(("^", "!")) else "^" + elem.lstrip(' ') \
                              for elem in input_filtered[first_exclude_item:]]

    """ Find single values as well as all ranges & compile frame list """
    frame_list, exclude_list, conform_list  = [], [], []

    conform_flag = False
    for item in input_filtered:
        frame = float_filter(item)

        if frame is not None: # Single floats
            frame_list.append(frame)
            if conform_flag: conform_list.append(frame)

        else:  # Ranges & items to exclude
            exclude_item = rx_exclude.search(item)
            range_item = rx_group.search(item)

            if exclude_item:  # Single exclude items like ^-3 or ^10
                exclude_list.append(float_filter(exclude_item.group(1)))
                if filter_individual: conform_flag = True

            elif range_item:  # Ranges like 1-10, 20-10, 1-3x0.1, ^2-7 or ^-3--1
                start = min(float_filter(range_item.group(1)), float_filter(range_item.group(3)))
                end = max(float_filter(range_item.group(1)), float_filter(range_item.group(3)))
                step = increment if not range_item.group(4) else float_filter(range_item.group(6))

                if start < end:  # Build the range & add all items to list
                    frame_range = around(arange(start, end, step), decimals=5).tolist()
                    if item.startswith(("^", "!")):
                        if filter_individual: conform_flag = True
                        exclude_list.extend(frame_range)
                        if isclose(step, (end - frame_range[-1])):
                            exclude_list.append(end)
                    else:
                        frame_list.extend(frame_range)
                        if isclose(step, (end - frame_range[-1])):
                            frame_list.append(end)

                        if conform_flag:
                            conform_list.extend(frame_range)
                            if isclose(step, (end - frame_range[-1])):
                                conform_list.append(end)

                elif start == end:  # Not a range, add start frame
                    if not item.startswith(("^", "!")):
                        frame_list.append(start)
                    else:
                        exclude_list.append(start)

    if filter_individual:
        exclude_list = sorted(set(exclude_list).difference(conform_list))
    float_frames = sorted(set(frame_list).difference(exclude_list))

    """ Return integers whenever possible """
    int_frames = [int_filter(frame) for frame in float_frames]
    return float_frames if None in int_frames else int_frames


def version_number(file_path, number, delimiter="_", min_lead=2):
    """Replace or add a version string by given number"""
    match = re.search(r'v(\d+)', file_path)
    if match:
        g = match.group(1)
        n = str(int(number)).zfill(len(g))
        return file_path.replace(match.group(0), "v{v}".format(v=n))

    else:
        lead_zeros = str(int(number)).zfill(min_lead)
        version = "{dl}v{lz}{dl}".format(dl=delimiter, lz=lead_zeros)
        ext = (".png",".jpg",".jpeg","jpg",".exr",".dpx",".tga",".tif",".tiff",".cin")

        if "#" in file_path:
            dash = file_path.find("#")
            head, tail = file_path[:dash], file_path[dash:]
            if head.endswith(delimiter):
                head = head.rstrip(delimiter)
            return "{h}{v}{t}".format(h=head, v=version, t=tail)

        elif file_path.endswith(ext):
            head, extension = os.path.splitext(file_path)
            if head.endswith(delimiter):
                head = head.rstrip(delimiter)
            return "{fp}{v}{ex}".format(fp=head, v=version[:-1], ex=extension)

        else:
            if file_path.endswith(delimiter):
                file_path = file_path.rstrip(delimiter)
            return "{fp}{v}".format(fp=file_path, v=version)


def render_version(self, context):
    context.area.tag_redraw()
    scene = context.scene
    render = scene.render

    """ Replace the render path """
    render.filepath = version_number(
            render.filepath,
            scene.loom.output_render_version)

    """ Replace file output """
    node_tree = get_compositor_node_tree(scene)
    if not scene.render.use_compositing or \
        not scene.loom.output_sync_comp or \
        not node_tree:
        return

    output_nodes = [n for n in node_tree.nodes if n.type=='OUTPUT_FILE']
    for out_node in output_nodes:
        """ Set base path only """
        if "LAYER" in out_node.format.file_format:
            out_node.base_path = version_number(
                out_node.base_path,
                scene.loom.output_render_version)
        else:
            """ Set the base path """
            out_node.base_path = version_number(
                out_node.base_path,
                scene.loom.output_render_version)
            """ Set all slots """
            for out_file in out_node.file_slots:
                out_file.path = version_number(
                    out_file.path,
                    scene.loom.output_render_version)
    return None


def isevaluable(s):
    try:
        eval(s)
        return True
    except:
        return False


def replace_globals(s, debug=False):
    """Replace string by given global entries"""
    from . import bl_info
    addon_name = bl_info['name']

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


def user_globals(context):
    """Determine whether globals used in the scene"""
    from . import bl_info
    addon_name = bl_info['name']

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


def render_preset_callback(scene, context):
    """Callback for render preset enum"""
    from .presets import LOOM_MT_render_presets
    preset_items = [
        ('0', "No Render Preset", "", 0),
    ]
    if hasattr(bpy.types, LOOM_MT_render_presets.__name__):
        presets = LOOM_MT_render_presets.preset_subdir
        preset_items.extend([
            (str(i+1), label, "")
            for i, label in enumerate(
                sorted(p for p in bpy.utils.preset_find(presets))
            )
        ])
    return preset_items
