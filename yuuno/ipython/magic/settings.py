from yuuno.ipython.magic.yuuno_command import commands
from yuuno.core.settings import settings, SettingsContainer


@commands.register("get")
def get_setting(line):
    """Retrieves a configuration value from the Yuuno Settings store.

    Example:
    >>> %yuuno get csp
    '709'

    Following settings exist:
    * `yuv_matrix`:   The matrix to use when converting vapoursynth
    |                 clips from YUV to RGB.
    * `csp`:          The ICC-Profile to add to the PNG-files generated
    |                 by Yuuno.
    * `tile_size`:    Large images are split into smaller tiles to prevent
    |                 the browser from crashing. This setting defines the
    |                 size of each tile.
    """
    if not line:
        return "Existing settings: %s"%(
            ", ".join(SettingsContainer.DEFAULTS.keys())
        )
    return getattr(settings, line.split(" ")[0], "<unset>")


@commands.register("set")
def set_settings(line):
    """Sets a value.

    Example:
    >>> %yuuno set yuv_matrix 601

    See `%yuuno help get` for an overview of existing settings.
    """
    setting, *conf = line.split(" ", 1)
    if not len(conf):
        conf = ""
    else:
        conf = conf[0]

    if not conf:
        val = SettingsContainer.DEFAULTS.get(setting, None)
    else:
        val = conf

    setattr(settings, setting, val)
