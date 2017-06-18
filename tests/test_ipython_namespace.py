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
from yuuno.core.settings import Settings
from yuuno.core.extension import Extension

from yuuno.ipython.environment import YuunoIPythonEnvironment
from yuuno.ipython.environment import load_ipython_extension, unload_ipython_extension

from yuuno.ipython.namespace import Namespace


class TestExtension(Extension):

    @classmethod
    def is_supported(cls):
        return True

    def initialize(self):
        self.parent.namespace['testificate'] = "Hello"

    def deinitialize(self):
        del self.parent.namespace['testificate']


class TestIPythonNamespace(unittest.TestCase):

    def setUp(self):
        Settings.DEFAULT_EXTENSION_TYPES.clear()
        Settings.DEFAULT_EXTENSION_TYPES.append('test_ipython_namespace.TestExtension')
        YuunoIPythonEnvironment.feature_classes = [
            "yuuno.ipython.namespace.Namespace"
        ]

        self.shell = globalipapp.get_ipython()
        load_ipython_extension(self.shell)

        self.loaded = True

        self.yuuno = Yuuno.instance()

    def tearDown(self):
        if self.loaded:
            unload_ipython_extension(self.shell)

    def test_001_test_push(self):
        obj = object()
        self.yuuno.namespace['var'] = obj

        self.assertEqual(self.shell.user_ns['testificate'], "Hello")
        self.assertIs(self.shell.user_ns['var'], obj)

    def test_002_test_pop(self):
        obj = object()
        self.yuuno.namespace['var'] = obj
        del self.yuuno.namespace['var']

        self.assertNotIn('var', self.shell.user_ns)

    def test_003_test_deinitialize(self):
        self.loaded = False
        unload_ipython_extension(self.shell)
        self.assertNotIn('testificate', self.shell.user_ns)
