#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yuuno
----------------------------------

Tests for `yuuno` module.
"""


import sys
import unittest

from traitlets.utils.importstring import import_item

from yuuno import Yuuno
from yuuno.core.settings import Settings
from yuuno.vs.extension import VapourSynth

from tests.helpers import TestEnvironment


def filter1(clip, *args, **kwargs):
    return clip


@unittest.skipUnless(VapourSynth.is_supported(), "vapoursynth support not found")
class TestVapourSynth(unittest.TestCase):

    def setUp(self):
        Settings.DEFAULT_EXTENSION_TYPES.clear()
        Settings.DEFAULT_EXTENSION_TYPES.append(
            'yuuno.vs.extension.VapourSynth'
        )
        Yuuno.instance(environment=TestEnvironment()).start()

        self.vs = import_item("vapoursynth")

        # We will work with a dedicated VapourSynth-core.
        self.core = self.vs.core.core

        self.black_clip_grey = self.core.std.BlankClip(width=10, height=10, format=self.vs.GRAY8)
        self.black_clip_yuv444 = self.core.std.BlankClip(width=10, height=10, format=self.vs.YUV444P8)
        self.black_clip_yuv422 = self.core.std.BlankClip(width=10, height=10, format=self.vs.YUV422P8)
        self.black_clip_yuv420 = self.core.std.BlankClip(width=10, height=10, format=self.vs.YUV420P8)
        self.black_clip = self.core.std.BlankClip(width=10, height=10, format=self.vs.RGB24)
        self.black_compat = self.black_clip.resize.Spline36(format=self.vs.COMPATBGR32)

    def tearDown(self):
        Yuuno.instance().stop()

    def test_001_vapoursynth_frame_plane_size(self):
        from yuuno.vs.clip import calculate_size

        print("A")
        self.assertEqual(calculate_size(self.black_clip_grey.get_frame(0), 0), (10, 10))
        print("B")

        self.assertEqual(calculate_size(self.black_clip.get_frame(0), 0), (10, 10))
        print("C")
        self.assertEqual(calculate_size(self.black_clip.get_frame(0), 1), (10, 10))
        print("D")
        self.assertEqual(calculate_size(self.black_clip.get_frame(0), 2), (10, 10))

        print("E")
        self.assertEqual(calculate_size(self.black_clip_yuv444.get_frame(0), 0), (10, 10))
        print("F")
        self.assertEqual(calculate_size(self.black_clip_yuv444.get_frame(0), 1), (10, 10))
        print("G")
        self.assertEqual(calculate_size(self.black_clip_yuv444.get_frame(0), 2), (10, 10))

        print("H")
        self.assertEqual(calculate_size(self.black_clip_yuv422.get_frame(0), 0), (10, 10))
        print("I")
        self.assertEqual(calculate_size(self.black_clip_yuv422.get_frame(0), 1), ( 5, 10))
        print("K")
        self.assertEqual(calculate_size(self.black_clip_yuv422.get_frame(0), 2), ( 5, 10))

        print("L")
        self.assertEqual(calculate_size(self.black_clip_yuv420.get_frame(0), 0), (10, 10))
        print("M")
        self.assertEqual(calculate_size(self.black_clip_yuv420.get_frame(0), 1), ( 5,  5))
        print("O")
        self.assertEqual(calculate_size(self.black_clip_yuv420.get_frame(0), 2), ( 5,  5))

    def test_002_vapoursynth_plane_extract(self):
        from yuuno.vs.clip import extract_plane

        self.assertEqual(extract_plane(self.black_clip_grey.get_frame(0), 0).mode, "L")

        self.assertEqual(extract_plane(self.black_clip.get_frame(0), 0).mode, "L")
        self.assertEqual(extract_plane(self.black_clip.get_frame(0), 1).mode, "L")
        self.assertEqual(extract_plane(self.black_clip.get_frame(0), 2).mode, "L")

        self.assertEqual(extract_plane(self.black_clip_yuv444.get_frame(0), 0).mode, "L")
        self.assertEqual(extract_plane(self.black_clip_yuv444.get_frame(0), 1).mode, "L")
        self.assertEqual(extract_plane(self.black_clip_yuv444.get_frame(0), 2).mode, "L")

        self.assertEqual(extract_plane(self.black_clip_yuv422.get_frame(0), 0).mode, "L")
        self.assertEqual(extract_plane(self.black_clip_yuv422.get_frame(0), 0).mode, "L")
        self.assertEqual(extract_plane(self.black_clip_yuv422.get_frame(0), 0).mode, "L")

        self.assertEqual(extract_plane(self.black_clip_yuv420.get_frame(0), 0).mode, "L")
        self.assertEqual(extract_plane(self.black_clip_yuv420.get_frame(0), 0).mode, "L")
        self.assertEqual(extract_plane(self.black_clip_yuv420.get_frame(0), 0).mode, "L")

        self.assertEqual(extract_plane(self.black_clip_grey.get_frame(0), 0).size, (10, 10))

        self.assertEqual(extract_plane(self.black_clip.get_frame(0), 0).size, (10, 10))
        self.assertEqual(extract_plane(self.black_clip.get_frame(0), 1).size, (10, 10))
        self.assertEqual(extract_plane(self.black_clip.get_frame(0), 2).size, (10, 10))

        self.assertEqual(extract_plane(self.black_clip_yuv444.get_frame(0), 0).size, (10, 10))
        self.assertEqual(extract_plane(self.black_clip_yuv444.get_frame(0), 1).size, (10, 10))
        self.assertEqual(extract_plane(self.black_clip_yuv444.get_frame(0), 2).size, (10, 10))

        self.assertEqual(extract_plane(self.black_clip_yuv422.get_frame(0), 0).size, (10, 10))
        self.assertEqual(extract_plane(self.black_clip_yuv422.get_frame(0), 1).size, ( 5, 10))
        self.assertEqual(extract_plane(self.black_clip_yuv422.get_frame(0), 2).size, ( 5, 10))

        self.assertEqual(extract_plane(self.black_clip_yuv420.get_frame(0), 0).size, (10, 10))
        self.assertEqual(extract_plane(self.black_clip_yuv420.get_frame(0), 1).size, ( 5,  5))
        self.assertEqual(extract_plane(self.black_clip_yuv420.get_frame(0), 2).size, ( 5,  5))

    def test_003_vapoursynth_frame_extract(self):
        from yuuno.vs.clip import VapourSynthFrameWrapper
        fw = VapourSynthFrameWrapper(
            frame=self.black_clip.get_frame(0),
            rgb_frame=self.black_clip.get_frame(0),
            compat_frame=self.black_compat.get_frame(0)
        )
        im = fw.to_pil()

        self.assertEqual(im.width, self.black_clip.width)
        self.assertEqual(im.height, self.black_clip.height)

        #                                        R       G       B
        self.assertEqual(im.getextrema()[:3], ((0, 0), (0, 0), (0, 0)))

    def test_004_vapoursynth_resizer(self):
        vse = VapourSynth()
        vse.resizer = "test_vapoursynth_support.filter1"
        self.assertIs(vse.resize_filter, filter1)

        def _fk(*args, **kwargs):
            pass
        vse.resizer = _fk
        self.assertIs(vse.resize_filter, _fk)

    def test_005_vapoursynth_wrap_clip(self):
        from yuuno.vs.clip import VapourSynthClip

        self.assertEqual(len(VapourSynthClip(self.black_clip)), len(self.black_clip))

        cpf = VapourSynthClip(self.black_clip_yuv444)[0].result().compat_frame
        self.assertEqual(cpf.format.id, self.vs.COMPATBGR32)
        self.assertEqual(cpf.width, self.black_clip_yuv444.width)
        self.assertEqual(cpf.height, self.black_clip_yuv444.height)

    def test_006_vapoursynth_wrap_frame(self):
        from yuuno.vs.clip import VapourSynthFrame

        self.assertEqual(len(VapourSynthFrame(self.black_clip.get_frame(0))), 1)

        cpf = VapourSynthFrame(self.black_clip_yuv444.get_frame(0))[0].result().compat_frame
        self.assertEqual(cpf.format.id, self.vs.COMPATBGR32)
        self.assertEqual(cpf.width, self.black_clip_yuv444.width)
        self.assertEqual(cpf.height, self.black_clip_yuv444.height)

    def test_007_vapoursynth_variable_push(self):
        ns = Yuuno.instance().namespace.as_dict()
        import vapoursynth
        self.assertEqual(ns['vs'], vapoursynth)
        self.assertIn('core', ns)
