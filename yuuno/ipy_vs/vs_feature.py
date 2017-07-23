from traitlets import default, Any

from yuuno.ipython.feature import Feature


class VSFeature(Feature):
    """
    Base-Class for VS-Ipython-Features.
    """
    
    extension = Any()

    @default("environment")
    def _default_environment(self):
        return self.extension.yuuno.environment