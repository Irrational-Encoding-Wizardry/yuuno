from yuuno.core.environment import Environment


class YuunoJupyterLabEnvironment(Environment):

    def additional_extensions(self):
        result = [
            "yuuno.multi_scripts.extension.MultiScriptExtension"
        ]

        return result

    def initialize(self):
        pass

    def deinitialize(self):
        pass
