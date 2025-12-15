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
Event handler modules for Loom addon.

This package contains persistent handlers for render events.
"""

# Import handler modules
from . import render_handlers


def register():
    """Register all handlers."""
    for handler_list, handler_func in render_handlers.handlers:
        if handler_func not in handler_list:
            handler_list.append(handler_func)


def unregister():
    """Unregister all handlers."""
    for handler_list, handler_func in render_handlers.handlers:
        if handler_func in handler_list:
            handler_list.remove(handler_func)
