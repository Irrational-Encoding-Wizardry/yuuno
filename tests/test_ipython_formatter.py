#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yuuno
----------------------------------

Tests for `yuuno` module.
"""


import sys
import unittest

from IPython.testing import globalipapp

from yuuno import Yuuno
from yuuno.clip import Clip
from yuuno.core.extension import Extension
from yuuno.core.settings import Settings
from yuuno.ipython.environment import YuunoIPythonEnvironment
from yuuno.ipython.environment import load_ipython_extension, unload_ipython_extension

from yuuno.ipython.formatter import Formatter, InlineFormat

from test_png_output import SinglePixelFrame, TestPNGOutput


class TestClip(Clip):

    def __len__(self):
        pass

    def __getitem__(self, item):
        return SinglePixelFrame(format="RGB")


class TestClipExtension(Extension):
    @classmethod
    def is_supported(cls):
        return True

    def initialize(self):
        self.parent.registry.register(TestClip, int)


class TestFormatter(unittest.TestCase):

    def setUp(self):
        Settings.DEFAULT_EXTENSION_TYPES.clear()
        Settings.DEFAULT_EXTENSION_TYPES.append("test_ipython_formatter.TestClipExtension")
        YuunoIPythonEnvironment.feature_classes = [
            "yuuno.ipython.formatter.Formatter"
        ]

        self.shell = globalipapp.get_ipython()
        load_ipython_extension(self.shell)

        self.loaded = True

    def tearDown(self):
        if self.loaded:
            unload_ipython_extension(self.shell)

    def test_001_formatter_correct_image(self):
        tc = TestClip(None)

        inline = InlineFormat(environment=Yuuno.instance().environment, clip=tc)
        self.assertEqual(inline.ipy_image().data, TestPNGOutput.EXPECTED_RESULT_SIMPLE)

    def test_002_formatter_lookup_success(self):
        self.assertIsNotNone(self.shell.display_formatter.formatters['image/png'].lookup(1))
        self.assertIsNotNone(self.shell.display_formatter.formatters['text/html'].lookup(1))
        self.assertIsNotNone(self.shell.display_formatter.formatters['text/plain'].lookup(1))

        raw, _ = self.shell.display_formatter.formatters['image/png'].lookup(1)(1)
        self.assertEqual(raw, TestPNGOutput.EXPECTED_RESULT_SIMPLE)

    def test_003_formatter_unload_success(self):
        self.loaded = False
        unload_ipython_extension(self.shell)

        with self.assertRaises(KeyError):
            self.shell.display_formatter.formatters['image/png'].lookup(1)

        with self.assertRaises(KeyError):
            self.shell.display_formatter.formatters['text/html'].lookup(1)

        with self.assertRaises(KeyError):
            self.shell.display_formatter.formatters['text/plain'].lookup(1)
