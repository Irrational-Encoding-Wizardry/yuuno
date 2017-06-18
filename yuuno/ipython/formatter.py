from traitlets import observe
from traitlets import HasTraits, Instance, Any

from IPython.display import Image as IPyImage

from yuuno.clip import Frame, Clip
from yuuno.ipython.feature import Feature
from yuuno.ipython.environment import Environment


class InlineFormat(HasTraits):
    """
    Represents an inline formatted object.
    """

    clip: Clip = Any()
    first_frame: Frame = Any(read_only=True, allow_none=True)
    environment: Environment = Instance(Environment)

    @observe("clip")
    def _update_initial_frame(self, value):
        value = value['new']
        self.set_trait('first_frame', value[0].to_pil())

    def ipy_image(self) -> IPyImage:
        """
        Converts a clip to an image.
        """
        raw = self.environment.parent.output.bytes_of(self.first_frame)
        return IPyImage(
            data=raw,
            format="png",
            embed=True,
            unconfined=True,
            width=self.first_frame.width,
            height=self.first_frame.height
        )

    def _repr_pretty_(self, pp, cycle):
        pp.text(f"<{self.clip.clip!r} {self.first_frame.width}x{self.first_frame.height}, {len(self.clip)} frames>")

    def _repr_html_(self, *args, **kwargs):
        return self.ipy_image()._repr_html_(*args, **kwargs)

    def _repr_png_(self, *args, **kwargs):
        return self.ipy_image()._repr_png_(*args, **kwargs)


class Formatter(Feature):

    type_to_repr = {
        'image/png': '_repr_png_',
        'text/html': '_repr_html_',
        'text/plain': '_repr_pretty_'
    }

    @property
    def display_formatters(self):
        return self.environment.ipython.display_formatter.formatters

    def display(self, format):
        formatter_type = self.type_to_repr.get(format)

        def _callback(obj, *args, **kwargs):
            clip = self.environment.parent.registry.wrap(obj)
            wrapper = InlineFormat(environment=self.environment, clip=clip)
            return getattr(wrapper, formatter_type)(*args, **kwargs)
        return _callback

    def initialize(self):
        for type in self.environment.parent.registry.all_types():
            self.environment.parent.log.debug(f"Registering {type!r} to IPython")
            for format in self.type_to_repr:
                cb = self.display(format)
                self.display_formatters[format].for_type(type, cb)

    def deinitialize(self):
        for type in self.environment.parent.registry.all_types():
            self.environment.parent.log.debug(f"Unregistering {type!r} from IPython")
            for format in self.type_to_repr:
                self.display_formatters[format].pop(type)
