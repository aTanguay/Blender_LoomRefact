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
Terminal execution operators for Loom addon.

Contains operators for running external commands and terminal instances.
"""

import bpy
import os
import subprocess
import tempfile
from sys import platform

# Import property groups
from ..properties.ui_props import LOOM_PG_generic_arguments


class LOOM_OT_clear_dialog(bpy.types.Operator):
    """Clear Log Collection"""
    bl_idname = "loom.clear_log"
    bl_label = "Clear Log"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.loom.render_collection.clear()
        return {'FINISHED'}



class LOOM_OT_verify_terminal(bpy.types.Operator):
    """Search and verify system terminal"""
    bl_idname = "loom.verify_terminal"
    bl_label = "Verify Terminal"
    bl_options = {'INTERNAL'}

    def verify_app(self, cmd):
        try:
            subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as e:
            if e.errno == errno.ENOENT:
                return False
        return True

    def execute(self, context):
        addon_name = __package__.split('.')[0]

        prefs = context.preferences.addons[addon_name].preferences

        if platform.startswith('win32'):
            prefs.terminal = 'win-default'

        elif platform.startswith('darwin'):
            prefs.terminal = 'osx-default'
            prefs.bash_flag = True

        elif platform.startswith('linux'):

            if self.verify_app(["x-terminal-emulator", "--help"]):
                prefs.terminal = 'x-terminal-emulator'
            elif self.verify_app(["xfce4-terminal", "--help"]):
                prefs.terminal = 'xfce4-terminal'
            elif self.verify_app(["xterm", "--help"]):
                prefs.terminal = 'xterm'
            else:
                self.report({'INFO'}, "Terminal not supported.")

        elif platform.startswith('freebsd'):
            if self.verify_app(["xterm", "--help"]):
                prefs.terminal = 'xterm'

        else:
            if self.verify_app(["xterm", "--help"]):
                prefs.terminal = 'xterm'
            else:
                self.report({'INFO'}, "Terminal not supported.")
        
        if prefs.terminal:
            bpy.ops.wm.save_userpref()

        self.report({'INFO'}, "Terminal is '{}'".format(prefs.terminal))

        return {'FINISHED'}



class LOOM_OT_run_terminal(bpy.types.Operator):
    """Run instance of an application in a new terminal"""
    bl_idname = "loom.run_terminal"
    bl_label = "Run Application in Terminal"
    bl_options = {'INTERNAL'}

    binary: bpy.props.StringProperty(
        name="Binary Path",
        description="Binary Path",
        maxlen=1024,
        subtype='FILE_PATH',
        default=bpy.app.binary_path)

    arguments: bpy.props.StringProperty(
        name="Command Line Arguments",
        description='[args …] "[file]" [args …]')

    argument_collection: bpy.props.CollectionProperty(
        name="Command Line Arguments",
        description="Allows passing a dictionary",
        type=LOOM_PG_generic_arguments)

    debug_arguments: bpy.props.BoolProperty(
        name="Debug Arguments",
        description="Print full argument list",
        default=False)

    terminal_instance: bpy.props.BoolProperty(
        name="New Terminal Instance",
        description="Opens Blender in a new Terminal Window",
        default=True)

    force_bash: bpy.props.BoolProperty(
        name="Force Bash File",
        description="Use bash file instead of passing the arguments",
        default=False)

    bash_name: bpy.props.StringProperty(
        name="Name of bash file",
        description="Name of bash file")

    communicate: bpy.props.BoolProperty(
        name="Batch process",
        description="Wait for other process",
        default=False)
    
    shutdown: bpy.props.BoolProperty(
        name="Hibernate when done",
        description="Hibernate when done",
        default=False)

    pause: bpy.props.BoolProperty(
        name="Confirm when done",
        description="Confirm when done",
        default=True)

    def single_bash_cmd(self, arg_list):
        #l = [i for s in arg_list for i in s]
        return ["{b}{e}{b}".format(b='\"', e=x) \
            if x.startswith("import") else x for x in arg_list]

    def write_bat(self, bat_path, bat_args):
        try:
            fp = open(bat_path, "w")
            fp.write("@ECHO OFF\n") #fp.write('COLOR 7F\n')
            if isinstance(bat_args[0], list):
                bat_args = [[self.binary] + i if self.binary else i for i in bat_args]
                # Double quotes and double percentage %%
                bat_args = [["{b}{e}{b}".format(b='\"', e=x) \
                    if x.startswith("import") or '\\' in x else x for x in args] \
                    for args in bat_args] #  or os.path.isfile(x)
                bat_args = [[x.replace("%", "%%") for x in args] for args in bat_args]
                for i in bat_args:
                    fp.write(" ".join(i) + "\n")
            else:
                bat_args = [self.binary] + bat_args if self.binary else bat_args
                bat_args = ["{b}{e}{b}".format(b='\"', e=x) \
                    if '\\' in x or x.startswith("import") else x for x in bat_args] # or os.path.isfile(x)
                bat_args = [x.replace("%", "%%") for x in bat_args]
                fp.write(" ".join(bat_args) + "\n")

            if self.shutdown:
                fp.write('shutdown -s\n')
            if self.pause:
                fp.write('pause\n')
            fp.write('echo Loom Rendering and Encoding done.\n')
            fp.close()
        except:
            self.report({'INFO'}, "Something went wrong while writing the bat file")
            return {'CANCELLED'}

    def write_bash(self, bash_path, bash_args):
        try:
            fp = open(bash_path, 'w')
            fp.write('#! /bin/sh\n')
            bl_bin = '"{}"'.format(self.binary) # if platform.startswith('darwin') else self.binary
            
            if isinstance(bash_args[0], list):
                bash_args = [[bl_bin] + i if self.binary else i for i in bash_args]

                """ Add quotes to python command """
                bash_args = [["{b}{e}{b}".format(b='\"', e=x) \
                    if x.startswith("import") else x for x in args] for args in bash_args]
                """ Add quotes to blend file path """
                bash_args = [["{b}{e}{b}".format(b='\"', e=x) \
                    if x.endswith(".blend") else x for x in args] for args in bash_args]
                """ Write the the file """
                for i in bash_args:
                    fp.write(" ".join(i) + "\n")
            else:
                bash_args = [bl_bin] + bash_args if self.binary else bash_args
                """ Add quotes to python command """
                bash_args = ["{b}{e}{b}".format(b='\"', e=x) \
                    if x.startswith("import") else x for x in bash_args]
                """ Add quotes to blend file path """
                bash_args = ["{b}{e}{b}".format(b='\"', e=x) \
                    if x.endswith(".blend") else x for x in bash_args]
                """ Write the the file """
                fp.write(" ".join(bash_args) + "\n")
            
            if self.pause: # https://stackoverflow.com/a/17778773
                fp.write('read -n1 -r -p "Press any key to continue..." key\n')
            if self.shutdown:
                fp.write('shutdown\n')
            fp.write('exit')
            fp.close()
            os.chmod(bash_path, 0o777)
        except:
            self.report({'WARNING'}, "Something went wrong while writing the bash file")
            return {'CANCELLED'}

    def execute(self, context):
        addon_name = __package__.split('.')[0]

        prefs = context.preferences.addons[addon_name].preferences
        args_user = []

        if not prefs.is_property_set("terminal") or not prefs.terminal:
            bpy.ops.loom.verify_terminal()

        if not prefs.terminal:
            self.report({'INFO'}, "Terminal not supported")
            return {'CANCELLED'}

        if self.arguments:
            '''
            Limitation: Splits the string by any whitespace, single or double quotes
            Could be improved with a regex to find the 'actual paths'
            '''
            pattern = r"""('[^']+'|"[^"]+"|[^\s']+)"""
            args_filter = re.compile(pattern, re.VERBOSE)
            lines = self.arguments.splitlines()
            for c, line in enumerate(lines):
                args_user.append(args_filter.findall(" ".join(lines)))
            
            ''' If no bash file name is provided and bash is the only option '''
            if prefs.terminal == 'osx-default' and not self.bash_name:
                self.bash_name = "loom"
        
        elif len(self.argument_collection) > 0:
            #idcs = set([item.idc for item in self.argument_collection]) 
            arg_dict = {}
            for item in self.argument_collection:
                arg_dict.setdefault(item.idc, []).append(item.value)
            for key, args in arg_dict.items():
                args_user.append(args)

        if not args_user:
            self.report({'INFO'}, "No Arguments")
            return {'CANCELLED'}

        if self.bash_name:
            addon_folder = bpy.utils.script_path_user() # tempfile module?
            ext = ".bat" if prefs.terminal == 'win-default' else ".sh"
            prefs.bash_file = os.path.join(addon_folder, "{}{}".format(self.bash_name, ext))
        
        """ Allow command stacking """
        if len(args_user) > 1 and not self.communicate:
            self.force_bash = True

        """ Compile arguments for each terminal """
        if prefs.terminal == 'win-default':
            # ['start', 'cmd /k', self.binary, '-h', '&& TIMEOUT 1']
            args = [self.binary] + args_user[0] if self.binary else args_user[0]
            if self.force_bash:
                args = prefs.bash_file 

        elif prefs.xterm_flag:
            """ Xterm Fallback """ # https://bugs.python.org/issue12247
            xterm = ['xterm'] if not platform.startswith('darwin') else ['/usr/X11/bin/xterm']
            args = xterm + ["-e", self.binary] if self.binary else xterm + ["-e"]
            if self.force_bash:
                args = xterm + ["-e", prefs.bash_file]
            else:
                args += args_user[0] # Single command

        elif prefs.terminal == 'osx-default':
            """ OSX """
            #args = ["open", "-n", "-a", "Terminal", "--args", prefs.bash_file]
            #args = ["osascript", "-e", 'Tell application "Terminal" to do script "{} ;exit"'.format(quote(prefs.bash_file))]
            from shlex import quote
            activate = ["-e", 'Tell application "Terminal" to activate'] if not prefs.render_background else []
            run_bash = ["-e", 'Tell application "Terminal" to do script "{} ;exit"'.format(quote(prefs.bash_file))]
            args = ["osascript"] + activate + run_bash
            self.force_bash = True
            
        elif prefs.terminal in ['x-terminal-emulator', 'xterm']:
            """ Debian & FreeBSD """
            args = [prefs.terminal, "-e", self.binary] if self.binary else [prefs.terminal, "-e"]
            if self.force_bash:
                args = [prefs.terminal, "-e", prefs.bash_file]
            else:
                args += args_user[0] # Single command

        elif prefs.terminal in ['xfce4-terminal']: 
            """ Arch """
            args = [prefs.terminal, "-e"]
            if self.force_bash:
                args += [prefs.bash_file]
            else:
                args_xfce = self.single_bash_cmd(args_user[0])
                args_xfce = [self.binary] + args_xfce if self.binary else args_xfce
                args.append(" ".join(str(i) for i in args_xfce)) # Needs to be a string!               

        """ Print all compiled arguments """
        if self.debug_arguments:
            
            debug_list = args_user if not isinstance(args_user[0], list) \
                else [" ".join(i) for i in args_user] #else [i for sl in args_user for i in sl]
            '''
            if not any(os.path.isfile(x) and (x.endswith(".blend")) for x in debug_list):
                self.report({'INFO'}, "No blend-file provided")
            '''
            self.report({'INFO'}, "User Arguments: {}\n".format(
                ' '.join('\n{}: {}'.format(*k) for k in enumerate(debug_list))))
            if self.force_bash:
                self.report({'INFO'}, "Commands will be written to Bash: {}".format(args))
            else:
                self.report({'INFO'}, "Command: {}".format(args))
            return {'CANCELLED'}

        """ Write the file """ 
        if self.force_bash:
            if not platform.startswith('win32'):
                self.write_bash(prefs.bash_file, args_user)
            else:
                self.write_bat(prefs.bash_file, args_user)
        
        """ Open Terminal & pass all arguments """
        try:
            if not self.terminal_instance:
                env_copy = os.environ.copy()
                subprocess.Popen(args, env=env_copy)
            
            elif platform.startswith('win32'):
                p = subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
                if self.communicate: p.communicate()

            else:
                # subprocess.call(args), same as Popen().wait(), print ("PID", p.pid)
                p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if self.communicate: p.communicate()

            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, "Couldn't run command {} \nError: {}".format(
                        ' '.join('\n{}: {}'.format(*k) for k in enumerate(args)), str(e)))
            return {'CANCELLED'}




# Classes for registration
classes = (
    LOOM_OT_clear_dialog,
    LOOM_OT_verify_terminal,
    LOOM_OT_run_terminal,
)
