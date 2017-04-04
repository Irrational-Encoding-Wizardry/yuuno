import os

try:
    from pkg_resources import resource_filename
except ImportError:
    def resource_filename(module, name):
        this_dir, this_filename = os.path.split(__file__)
        path = os.path.join(this_dir, '..', name)
        return path


def get_data_file(name):
    return resource_filename('yuuno', 'data' + os.path.sep + name)