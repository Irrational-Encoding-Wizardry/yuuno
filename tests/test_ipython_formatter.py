#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yuuno
----------------------------------

Tests for `yuuno` module.
"""

import base64
import unittest

from IPython.testing import globalipapp

from yuuno import Yuuno
from yuuno.clip import Clip
from yuuno.utils import inline_resolved
from yuuno.core.extension import Extension
from yuuno.core.settings import Settings
from yuuno_ipython.ipython.environment import YuunoIPythonEnvironment
from yuuno_ipython.ipython.environment import load_ipython_extension, unload_ipython_extension

from yuuno_ipython.ipython.formatter import Formatter, InlineFormat

from tests.test_png_output import SinglePixelFrame, TestPNGOutput


class StaticObject(object):
    pass
STATIC_OBJECT = StaticObject()


class TestClip(Clip):

    def __len__(self):
        return 0

    @inline_resolved
    def __getitem__(self, item):
        return SinglePixelFrame(format="RGB")


class TestClipExtension(Extension):
    @classmethod
    def is_supported(cls):
        return True

    def initialize(self):
        self.parent.registry.register(TestClip, StaticObject)


class TestFormatter(unittest.TestCase):

    def setUp(self):
        Settings.DEFAULT_EXTENSION_TYPES.clear()
        Settings.DEFAULT_EXTENSION_TYPES.append("tests.test_ipython_formatter.TestClipExtension")
        YuunoIPythonEnvironment.feature_classes = [
            "yuuno_ipython.ipython.formatter.Formatter"
        ]

        self.shell = globalipapp.get_ipython()
        load_ipython_extension(self.shell)
        Yuuno.instance().output.icc_profile = None

        self.loaded = True

    def tearDown(self):
        if self.loaded:
            unload_ipython_extension(self.shell)

    def test_001_formatter_correct_image(self):
        tc = TestClip(None)

        inline = InlineFormat(environment=Yuuno.instance().environment, clip=tc)
        self.assertEqual(inline.ipy_image.data, TestPNGOutput.EXPECTED_RESULT_SIMPLE)

    def test_002_formatter_lookup_success(self):
        self.assertIsNotNone(self.shell.display_formatter.mimebundle_formatter.lookup(STATIC_OBJECT))

        raw, _ = self.shell.display_formatter.mimebundle_formatter.lookup(STATIC_OBJECT)(STATIC_OBJECT)

    def test_003_formatter_unload_success(self):
        self.loaded = False
        unload_ipython_extension(self.shell)

        with self.assertRaises(KeyError):
            self.shell.display_formatter.mimebundle_formatter.lookup(STATIC_OBJECT)
