from IPython import get_ipython

class InlineManager(object):
    """
    Manager for Inline-Reprs.
    """

    def __init__(self):
        self.inlines = []

    def register(self, type, format="text/plain"):
        def _wrapper(func):
            self.inlines.append((type, format, func))
            return func
        return _wrapper

    def install(self):
        formatters = get_ipython().display_formatter.formatters
        for type, format, func in self.inlines:
            formatters[format].for_type(type, func)


inlines = InlineManager()

