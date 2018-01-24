#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yuuno
----------------------------------

Tests for `yuuno` module.
"""


import unittest

from traitlets import default, HasTraits, Unicode

from PIL import Image

from yuuno.output import YuunoImageOutput
from yuuno.clip import Frame


class SinglePixelFrame(Frame, HasTraits):

    format = Unicode()

    @default("subsampling")
    def _get_subsampling(self):
        """Faking coverage"""

    @default("planes")
    def _get_planes(self):
        """Faking coverage"""

    def to_pil(self):
        return Image.new(self.format, (1,1))


class TestPNGOutput(unittest.TestCase):

    EXPECTED_RESULT_SIMPLE = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00'
        b'\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    EXPECTED_RESULT_CMYK_TO_RGB = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08'
        b'\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00'
        b'\x05\xfe\x02\xfe\r\xefF\xb8\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    def setUp(self):
        self.output = YuunoImageOutput()
        self.output.icc_profile = None
        self.frame = SinglePixelFrame()

    def tearDown(self):
        pass

    def test_001_test_dump(self):
        self.assertEqual(self.output.bytes_of(SinglePixelFrame(format="RGB")), self.EXPECTED_RESULT_SIMPLE)

    def test_002_test_dump_nonsupported(self):
        self.assertEqual(self.output.bytes_of(SinglePixelFrame(format="CMYK")), self.EXPECTED_RESULT_CMYK_TO_RGB)
