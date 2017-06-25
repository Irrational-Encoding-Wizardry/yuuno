#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yuuno
----------------------------------

Tests for `yuuno` module.
"""


import unittest

from IPython.testing import globalipapp

from traitlets import Bool

from yuuno import Yuuno
from yuuno.core.settings import Settings
from yuuno.ipython.feature import Feature
from yuuno.ipython.environment import YuunoIPythonEnvironment
from yuuno.ipython.environment import load_ipython_extension, unload_ipython_extension

from tests.helpers import AdditionalAsserts
from tests.test_yuuno import SupportedTestExtension


class TestFeature(Feature):

    init_called: bool = Bool(False)
    deinit_called: bool = Bool(False)

    @classmethod
    def feature_name(cls):
        return "formatter"

    def initialize(self):
        self.init_called = True

    def deinitialize(self):
        self.deinit_called = True


class TestIPythonEnvironment(AdditionalAsserts, unittest.TestCase):

    def setUp(self):
        Settings.DEFAULT_EXTENSION_TYPES.clear()
        Settings.DEFAULT_EXTENSION_TYPES.append("tests.test_yuuno.SupportedTestExtension")
        YuunoIPythonEnvironment.feature_classes = ["test_ipython_environment.TestFeature"]

        self.shell = globalipapp.get_ipython()

    def tearDown(self):
        Yuuno.clear_instance()

    def test_001_ipython_enable(self):
        load_ipython_extension(self.shell)
        yuuno = Yuuno.instance()
        self.assertIsInstance(yuuno.environment, YuunoIPythonEnvironment)
        self.assertIn(yuuno.environment, self.shell.configurables)
        self.assertInstanceIn(self.shell.configurables, SupportedTestExtension)
        self.assertIn(yuuno, self.shell.configurables)

    def test_002_ipython_disable(self):
        load_ipython_extension(self.shell)
        yuuno = Yuuno.instance()
        ext = yuuno.extensions[0]
        unload_ipython_extension(self.shell)

        self.assertIsNot(yuuno, Yuuno.instance())
        self.assertNotIn(yuuno, self.shell.configurables)
        self.assertNotIn(yuuno.environment, self.shell.configurables)
        self.assertNotIn(ext, self.shell.configurables)

    def test_003_feature_initialization(self):
        load_ipython_extension(self.shell)
        yuuno = Yuuno.instance()

        self.assertInstanceIn(yuuno.environment.features, TestFeature)
        self.assertTrue(yuuno.environment.features[0].init_called)
        self.assertFalse(yuuno.environment.features[0].deinit_called)

    def test_004_feature_deinitialization(self):
        load_ipython_extension(self.shell)
        yuuno = Yuuno.instance()
        unload_ipython_extension(self.shell)

        self.assertTrue(yuuno.environment.features[0].init_called)
        self.assertTrue(yuuno.environment.features[0].deinit_called)
