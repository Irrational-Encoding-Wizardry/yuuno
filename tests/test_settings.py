#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yuuno
----------------------------------

Tests for `yuuno` module.
"""


import unittest

from yuuno.core.settings import Settings
from yuuno.core.registry import Registry


class FakeRegistry(object):
    pass


class TestSettings(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()

    def tearDown(self):
        pass

    def test_001_registry_default(self):
        self.assertIsInstance(self.settings.registry, Registry)

    def test_002_update_registry_type(self):
        self.settings.registry_type = "tests.test_settings.FakeRegistry"
        self.assertIsInstance(self.settings.registry, FakeRegistry)
