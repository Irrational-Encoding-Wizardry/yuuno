
import json
from pathlib import Path

from ._version import __version__

HERE = Path(__file__).parent.resolve()

with (HERE / ".." / "packages" / "jupyterlab" / "package.json").open() as fid:
    data = json.load(fid)

def _jupyter_labextension_paths():
    return [{
        "src": "static",
        "dest": data["name"]
    }]



from .handlers import setup_handlers


def _jupyter_server_extension_points():
    return [{
        "module": "yuuno_jupyterlab"
    }]


def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    from yuuno.yuuno import Yuuno
    from yuuno_jupyterlab.environment import YuunoJupyterLabEnvironment

    yuuno = Yuuno.instance(parent=server_app)
    yuuno.environment = YuunoJupyterLabEnvironment(parent=yuuno, server=server_app)
    yuuno.start()

    setup_handlers(server_app.web_app)
    server_app.log.info("Registered YuunoLab extension at URL path /yuuno-jupyterlab")

# For backward compatibility with notebook server - useful for Binder/JupyterHub
load_jupyter_server_extension = _load_jupyter_server_extension

