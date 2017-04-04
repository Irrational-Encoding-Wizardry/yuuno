from IPython.core.magic import register_line_cell_magic, register_line_magic, register_cell_magic


_deferred = []
def _make_deferred(decorator):
    def _decorator(func):
        def _registrar():
            decorator(func)
        _deferred.append(_registrar)
        return func
    return _decorator


def install():
    for installer in _deferred:
        installer()


cell_magic = _make_deferred(register_cell_magic)
line_magic = _make_deferred(register_line_magic)
line_cell_magic = _make_deferred(register_line_cell_magic)