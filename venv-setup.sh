#!/usr/bin/env bash
if [ -e /etc/NIXOS ]; then
    echo A flake is provided. Use the flake instead.
    exit 1
fi

if [ -e ./venv ]; then
    rm -rf ./venv
fi
python3 -m venv venv
venv/bin/pip install jupyterlab vapoursynth

if [ "$1" == "dev" ]; then
  venv/bin/pip install -e .
  venv/bin/jupyter-nbextension install yuuno_ipython --py --sys-prefix --symlink
  venv/bin/jupyter-nbextension enable yuuno_ipython --py --sys-prefix
else
  venv/bin/python setup.py egg_info
  venv/bin/pip install -r *.egg-info/requires.txt
  rm -rf *.egg-info
  venv/bin/python setup.py install
fi

