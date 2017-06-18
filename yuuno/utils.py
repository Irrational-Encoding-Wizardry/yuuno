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
