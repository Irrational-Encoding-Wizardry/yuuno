# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2018 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import pkg_resources


def discover_environments(module_dict):
    all_exts = []
    for ep in pkg_resources.iter_entry_points('yuuno.environments'):
        module_dict[ep.name] = ep.load()
        all_exts.append(ep.name)

    # This makes yuuno_ipython work easier in development environments.
    if "load_ipython_extension" not in module_dict:
        import yuuno_ipython.ipython.environment as ipy_env
        module_dict["load_ipython_extension"] = ipy_env.load_ipython_extension
        module_dict["unload_ipython_extension"] = ipy_env.unload_ipython_extension
        all_exts.append("load_ipython_extension")
        all_exts.append("unload_ipython_extension")

    return all_exts


def discover_extensions():
    for ep in pkg_resources.iter_entry_points('yuuno.extensions'):
        extension = ep.load()
        if not hasattr(extension, '_name'):
            extension._name = ep.name
        yield extension


def discover_commands():
    commands = {}
    for ep in pkg_resources.iter_entry_points('yuuno.commands'):
        command = ep.load()
        commands[ep.name] = command
    return commands
