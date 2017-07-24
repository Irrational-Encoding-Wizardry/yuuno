# -*- encoding: utf-8 -*- 

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal
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


import os
from pathlib import Path

try:
    from pkg_resources import resource_filename
except ImportError:
    def resource_filename(_: str, name: str):
        this_dir, this_filename = os.path.split(__file__)
        path = os.path.join(this_dir, '..', name)
        return path


def get_data_file(name) -> Path:
    """
    Returns the path to a data file.
    :param name: Name of the file
    :return: A path object to the specified directory or file
    """
    filename = resource_filename('yuuno', 'data' + os.path.sep + name)
    return Path(filename)