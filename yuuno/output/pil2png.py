# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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

from io import BytesIO

from traitlets import Unicode, CInt, Any
from traitlets.config import Configurable
from PIL.Image import Image

from yuuno.clip import Frame
from yuuno.output.srgb_png import srgb


class YuunoImageOutput(Configurable):
    """
    Defines an output for PNG-files
    """

    ################
    # Settings
    yuuno = Any(help="Reference to the current Yuuno instance.")

    zlib_compression: int = CInt(6, help="0=No compression\n1=Fastest\n9=Slowest", config=True)
    icc_profile: str = Unicode("sRGB", help="Specify the path to an ICC-Profile (Defaults to sRGB).", allow_none=True, config=True)

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

        settings = {
            "compress_level": self.zlib_compression,
            "format": "png"
        }
        if self.icc_profile is not None:
            if self.icc_profile != "sRGB":
                with open(self.icc_profile, "rb") as f:
                    settings["icc_profile"] = f.read()
            else:
                settings.update(srgb())

        f = BytesIO()
        im.save(f, **settings)
        return f.getvalue()
