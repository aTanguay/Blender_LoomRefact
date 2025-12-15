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
Version numbering utilities.

Provides functions for adding and updating version numbers in file paths.
"""

import re
import os

from .blender_compat import get_compositor_node_tree


def version_number(file_path, number, delimiter="_", min_lead=2):
    """Replace or add a version string by given number.

    Args:
        file_path: The file path to add/update version number
        number: The version number to use
        delimiter: Delimiter character(s) for version string
        min_lead: Minimum number of leading zeros

    Returns:
        Updated file path with version number
    """
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
    """Update render output path version number.

    This is a property callback that updates both the main render path
    and compositor file output node paths when the version number changes.

    Args:
        self: The property owner (scene.loom)
        context: Blender context
    """
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
