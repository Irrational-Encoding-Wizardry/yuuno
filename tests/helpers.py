from yuuno import Yuuno
from yuuno.core.environment import Environment


class AdditionalAsserts(object):
    def assertInstanceIn(self, lst, cls):
        for item in lst:
            if isinstance(item, cls): return
        raise AssertionError(f"{cls} not in list")

    def assertInstanceNotIn(self, lst, cls):
        with self.assertRaises(AssertionError):
            self.assertInstanceIn(lst, cls)


class TestEnvironment(Environment):

    @classmethod
    def create(cls):
        return TestEnvironment(parent=Yuuno.instance())
