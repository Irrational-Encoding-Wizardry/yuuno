from yuuno.yuuno import Yuuno
from yuuno.core.extension import Extension


class YuunoLabKernelExtension(Extension):

    @classmethod
    def is_supported(cls):
        try:
            import IPython
        except ImportError:
            return False

        from yuuno.ipython.environment import YuunoIPythonEnvironment
        if not isinstance(Yuuno.instance().environment, YuunoIPythonEnvironment):
            return False

        return True

    @property
    def ipython(self):
        return self.parent.environment.ipython

    @property
    def logger(self):
        return self.parent.logger

    def lab_connect(self, comm, msg):
        pass

    def initialize(self):
        self.ipython.kernel.comm_manager.register_target("yuuno.lab", self.lab_connect)

    def deinitialize(self):
        self.ipython.kernel.comm_manager.unregister_target("yuuno.lab")
