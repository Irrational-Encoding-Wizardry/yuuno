class SettingsContainer(object):

    DEFAULTS = {
        'yuv_matrix': '709',
        'csp': 'None',
        'tile_size': '540',
    }

    def __init__(self):
        self.reset()

    def reset(self):
        for k, v in SettingsContainer.DEFAULTS.items():
            setattr(self, k, v)

settings = SettingsContainer()


