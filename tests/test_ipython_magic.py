#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yuuno
----------------------------------

Tests for `yuuno` module.
"""


import unittest

from IPython import __version__ as ipy_version
from IPython.testing import globalipapp

from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_magic, cell_magic

from yuuno import Yuuno
from yuuno.core.settings import Settings
from yuuno_ipython.ipython.magic import MagicFeature
from yuuno_ipython.ipython.environment import YuunoIPythonEnvironment
from yuuno_ipython.ipython.environment import load_ipython_extension, unload_ipython_extension


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
        Settings.DEFAULT_EXTENSION_TYPES.append("tests.test_ipython_formatter.TestClipExtension")
        YuunoIPythonEnvironment.feature_classes = [
            "tests.test_ipython_magic.TestMagicFeature"
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

    def _exec_magic(self, type, *args, **kwargs):
        return getattr(self.shell, f'run_{type}_magic')(*args, **kwargs)

    def _run_magic(self, type, *args, **kwargs):
        if ipy_version < '6':
            return self._exec_magic(type, *args, **kwargs)
        else:
            from IPython.core.error import UsageError

            try:
                return self._exec_magic(type, *args, **kwargs)
            except UsageError:
                return None

    def test_001_test_magic_register(self):
        self.assertEqual(self._run_magic("line", "test_line_magic", "testificate"), "testificate")
        self.assertEqual(self._run_magic("cell", "test_cell_magic", "testificate", "1 2 3"), ("testificate", "1 2 3"))

    def test_002_test_magic_unregister(self):
        Yuuno.instance().environment.features[0].unregister_magics(TestMagicFeature.TestMagics)
        self.assertIsNone(self._run_magic("line", "test_line_magic", "testificate"))
        self.assertIsNone(self._run_magic("cell", "test_cell_magic", "testificate", "1 2 3"))

    def test_003_test_magic_autounregister(self):
        self.loaded = False
        unload_ipython_extension(self.shell)
        self.assertIsNone(self._run_magic("line", "test_line_magic", "testificate"))
        self.assertIsNone(self._run_magic("cell", "test_cell_magic", "testificate", "1 2 3"))
