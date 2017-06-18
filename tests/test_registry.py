import unittest

from yuuno.core.registry import Registry, Clip


class TestRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = Registry()

    def tearDown(self):
        del self.registry

    def test_001_register_raw(self):
        class TestClip(Clip): pass

        self.registry.register(TestClip, int)
        self.assertDictEqual(self.registry.clip_types, {int: TestClip})

    def test_002_register_decorator(self):
        @self.registry.register(int)
        class TestClip(Clip): pass

        self.assertDictEqual(self.registry.clip_types, {int: TestClip})

    def test_003_clip_type_correct_subclass(self):
        class A: pass
        class B(A): pass
        class C: pass

        @self.registry.register(A)
        class TestClip(Clip): pass

        self.assertEqual(self.registry.get_clip_type_for(A()), TestClip)
        self.assertEqual(self.registry.get_clip_type_for(B()), TestClip)
        self.assertEqual(self.registry.get_clip_type_for(C()), None)

    def test_004_clip_correct_wrapping(self):
        class TestClip(Clip):
            def __init__(self, item):
                self.base = item
        self.registry.register(TestClip, list)

        ref_value = []
        item = self.registry.wrap(ref_value)

        self.assertIs(item.base, ref_value)

        ref_invalid = {}
        with self.assertRaises(ValueError):
            self.registry.wrap(ref_invalid)

    def test_005_subregistry(self):
        class TestClip(Clip): pass

        subreg = Registry()
        subreg.register(TestClip, list)

        self.registry.add_subregistry(subreg)
        self.assertIs(self.registry.get_clip_type_for([]), TestClip)
        self.registry.remove_subregistry(subreg)
        self.assertIsNone(self.registry.get_clip_type_for([]))

    def test_006_all_types(self):
        class TestClip(Clip): pass

        class T1(object): pass
        class T2(object): pass
        class TS1(object): pass
        class TS2(object): pass

        sr = Registry()
        sr.register(TestClip, TS1)
        sr.register(TestClip, TS2)

        self.registry.register(TestClip, T1)
        self.registry.register(TestClip, T2)
        self.assertEqual(list(self.registry.all_types()), [T1, T2])

        self.registry.add_subregistry(sr)
        self.assertEqual(list(self.registry.all_types()), [T1, T2, TS1, TS2])

        self.registry.remove_subregistry(sr)
        self.assertEqual(list(self.registry.all_types()), [T1, T2])
