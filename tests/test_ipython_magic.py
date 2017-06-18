#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yuuno
----------------------------------

Tests for `yuuno` module.
"""


import unittest

from IPython.testing import globalipapp

from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_magic, cell_magic

from yuuno import Yuuno
from yuuno.core.settings import Settings
from yuuno.ipython.magic import MagicFeature
from yuuno.ipython.environment import YuunoIPythonEnvironment
from yuuno.ipython.environment import load_ipython_extension, unload_ipython_extension


class TestMagicFeature(MagicFeature):

    @classmethod
    def feature_name(cls):
        return "formatter"

    @magics_class
    class TestMagics(Magics):

        @line_magic
        def test_line_magic(self, line):
            return line

        @cell_magic
        def test_cell_magic(self, line, cell):
            return line, cell

    def initialize(self):
        self.register_magics(TestMagicFeature.TestMagics)


class TestIPythonMagic(unittest.TestCase):

    def setUp(self):
        Settings.DEFAULT_EXTENSION_TYPES.clear()
        Settings.DEFAULT_EXTENSION_TYPES.append("test_ipython_formatter.TestClipExtension")
        YuunoIPythonEnvironment.feature_classes = [
            "test_ipython_magic.TestMagicFeature"
        ]

        self.shell = globalipapp.get_ipython()
        load_ipython_extension(self.shell)

        self.loaded = True

    def tearDown(self):
        if self.loaded:
            unload_ipython_extension(self.shell)

    def _execute(self, code):
        exec_result = self.shell.run_cell(code, silent=True)
        if not exec_result.success:
            exec_result.raise_error()
        return exec_result.result

    def test_001_test_magic_register(self):
        self.assertEqual(self.shell.run_line_magic("test_line_magic", "testificate"), "testificate")
        self.assertEqual(self.shell.run_cell_magic("test_cell_magic", "testificate", "1 2 3"), ("testificate", "1 2 3"))

    def test_002_test_magic_unregister(self):
        Yuuno.instance().environment.features[0].unregister_magics(TestMagicFeature.TestMagics)
        self.assertIsNone(self.shell.run_line_magic("test_line_magic", "testificate"))
        self.assertIsNone(self.shell.run_cell_magic("test_cell_magic", "testificate", "1 2 3"))

    def test_003_test_magic_autounregister(self):
        self.loaded = False
        unload_ipython_extension(self.shell)
        self.assertIsNone(self.shell.run_line_magic("test_line_magic", "testificate"))
        self.assertIsNone(self.shell.run_cell_magic("test_cell_magic", "testificate", "1 2 3"))
