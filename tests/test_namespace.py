#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yuuno
----------------------------------

Tests for `yuuno` module.
"""


import sys
import unittest

from yuuno import Yuuno
from yuuno.core.namespace import Namespace


class TestNamespace(unittest.TestCase):

    def setUp(self):
        self.namespace = Namespace()

    def tearDown(self):
        pass

    def test_001_simple_get_set(self):
        self.namespace['a'] = 1
        self.assertEqual(self.namespace['a'], 1)

    def test_002_watcher_registered(self):
        cb_values = None
        def _cb(k, v, o):
            nonlocal cb_values
            cb_values = k, v, o
        self.namespace.watch(_cb)
        self.namespace['a'] = 2
        self.assertEqual(cb_values, ('a', 2, Namespace.Undefined))
        del self.namespace['a']
        self.assertEqual(cb_values, ('a', Namespace.Undefined, 2))
        cb_values = None
        self.namespace.unwatch(_cb)
        self.namespace['a'] = 3
        self.assertIsNone(cb_values)
