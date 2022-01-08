#!/usr/bin/env bash
if [ -e /etc/NIXOS ]; then
    echo A flake is provided. Use the flake instead.
    exit 1
fi

if [ -e ./venv ]; then
    rm -rf ./venv
fi
python3 -m venv venv
venv/bin/pip install jupyter jupyterlab jupyter_packaging git+https://github.com/vapoursynth/vapoursynth

if [ "$1" == "dev" ]; then
  venv/bin/pip install -e .
  venv/bin/jupyter-nbextension install yuuno_ipython --py --sys-prefix --symlink
  venv/bin/jupyter-nbextension enable yuuno_ipython --py --sys-prefix
  venv/bin/jupyter-labextension install yuuno_jupyterlab --sys-prefix --symlink
  venv/bin/jupyter-labextension enable yuuno_jupyterlab --sys-prefix
else
  OLD_PATH=$PATH
  . venv/bin/activate
  python setup.py egg_info
  pip install -r *.egg-info/requires.txt
  rm -rf *.egg-info
  python setup.py install
  deactivate
fi

