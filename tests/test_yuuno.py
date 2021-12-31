#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yuuno
----------------------------------

Tests for `yuuno` module.
"""

import unittest

from yuuno.core.extension import Extension
from yuuno.core.settings import Settings

from yuuno import Yuuno
from yuuno.core.environment import Environment

from tests.helpers import AdditionalAsserts


class TestEnvironment(Environment):

    def __init__(self, *args, **kwargs):
        super(TestEnvironment, self).__init__(*args, **kwargs)
        self.initialize_called = False
        self.deinitialize_called = False

    def initialize(self):
        super(TestEnvironment, self).initialize()
        self.initialize_called = True

    def deinitialize(self):
        super(TestEnvironment, self).deinitialize()
        self.deinitialize_called = True


class BaseTestExtension(Extension):

    def __init__(self, *args, **kwargs):
        super(BaseTestExtension, self).__init__(*args, **kwargs)
        self.initialized = False
        self.deinitialized = False

    def initialize(self):
        super(BaseTestExtension, self).initialize()
        self.initialized = True

    def deinitialize(self):
        super(BaseTestExtension, self).initialize()
        self.deinitialized = True


class SupportedTestExtension(BaseTestExtension):

    @classmethod
    def is_supported(cls):
        return True


class UnsupportedTestExtension(BaseTestExtension):
    @classmethod
    def is_supported(cls):
        return False


class TestYuuno(AdditionalAsserts, unittest.TestCase):

    def setUp(self):
        # To be test-friendly, disable all extensions
        Settings.DEFAULT_EXTENSION_TYPES.clear()
        Settings.DEFAULT_EXTENSION_TYPES.extend([
            "tests.test_yuuno.SupportedTestExtension",
            "tests.test_yuuno.UnsupportedTestExtension"
        ])

        self.environment = TestEnvironment()
        self.yuuno = Yuuno.instance(environment=self.environment)

    def tearDown(self):
        Yuuno.clear_instance()


    def test_001_test_start_initialization(self):
        self.yuuno.start()
        self.assertTrue(self.environment.initialize_called)
        self.assertFalse(self.environment.deinitialize_called)

    def test_002_test_stop_deinitialization(self):
        self.yuuno.stop()
        self.assertFalse(self.environment.initialize_called)
        self.assertTrue(self.environment.deinitialize_called)

    def test_003_test_extension_initialization(self):
        self.yuuno.start()
        self.assertInstanceIn(self.yuuno.extensions, SupportedTestExtension)
        self.assertInstanceNotIn(self.yuuno.extensions, UnsupportedTestExtension)

        ext = self.yuuno.extensions[0]
        self.assertTrue(ext.initialized)
        self.assertFalse(ext.deinitialized)

    def test_004_test_extension_deinitialization(self):
        self.yuuno.extensions = self.yuuno._load_extensions()
        self.yuuno.stop()

        ext = self.yuuno.extensions[0]
        self.assertFalse(ext.initialized)
        self.assertTrue(ext.deinitialized)

    def test_005_test_get_extension(self):
        self.yuuno.start()

        self.assertIsInstance(self.yuuno.get_extension(SupportedTestExtension), SupportedTestExtension)
        self.assertIsNone(self.yuuno.get_extension(UnsupportedTestExtension))
