from io import BytesIO

from traitlets import HasTraits, Any
from PIL.Image import Image

from yuuno.clip import Frame


class PNGOutput(HasTraits):
    """
    Defines an output for PNG-files
    """
    yuuno = Any(help="Reference to the current Yuuno instance.")

    def bytes_of(self, im: Frame) -> bytes:
        """
        Converts the frame into a bytes-object containing
        the frame as a PNG-file.

        :param im: the frame to convert.
        :return: A bytes-object containing the image.
        """
        if not isinstance(im, Image):
            im = im.to_pil()
        if im.mode not in ("RGBA", "RGB", "1", "L", "P"):
            im = im.convert("RGB")

        f = BytesIO()
        im.save(f, format="png")
        return f.getvalue()
