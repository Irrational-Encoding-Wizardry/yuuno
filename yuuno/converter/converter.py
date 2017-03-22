from PIL import Image

class _ConverterManager(object):
    """
    Manages converters for different frame-servers.
    """

    def __init__(self):
        self.types = {}

    def _get_converter(self, obj):
        for cls in type(obj).mro():
            if cls in self.types:
                return self.types[cls](obj)

    def convert(self, obj, **kwargs) -> Image.Image:
        return self._get_converter(obj).extract(**kwargs)

    def register(self, type, converter=None):
        if converter is None:
            def _decorator(cls):
                self.register(type, cls)
                return cls
            return _decorator
        
        self.types[type] = converter
        return converter


converters = _ConverterManager()
