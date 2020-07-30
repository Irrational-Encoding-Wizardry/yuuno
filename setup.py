#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2018 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os

from distutils.log import INFO
from distutils.command.build import build

from setuptools import setup, find_packages
from setuptools.command.sdist import sdist
from setuptools.command.install import install
from setuptools.command.build_py import build_py


DIRNAME = os.path.dirname(__file__) if __file__ else os.getcwd()


class NPMBuild(build_py):

    def get_js_package_manager(self):
        import shutil
        npm = shutil.which("npm")
        if npm is None:
            raise RuntimeError("Couldn't find NPM.")
        
        cmd = shutil.which("yarn")
        if shutil.which("yarn") is not None:
            return cmd
        else:
            return npm

    def popen(self, cmd, *args, **kwargs):
        self.announce(f"running command: {cmd}", level=INFO)
        import shlex
        import subprocess
        return subprocess.check_call(shlex.split(cmd), *args, **kwargs)

    def run(self):
        cwd = DIRNAME

        if os.path.exists(os.path.join(cwd, "yuuno_ipython", "build", "extension.js")):
            self.announce(f"cleaning build target.", level=INFO)
            import shutil
            shutil.rmtree(os.path.join(cwd, "yuuno_ipython", "build"))

        jspath = os.path.join(cwd, 'yuuno-jupyter')
        pm = self.get_js_package_manager()
        self.popen(f'"{pm}" install', cwd=jspath)
        self.popen(f'"{pm}" run build', cwd=jspath)


class SDistNPM(sdist):
    def run(self):
        if not os.path.exists(os.path.join(DIRNAME, "yuuno_ipython", "build", "extension.js")):
            self.run_command('build_npm')
        super().run()


class Install(install):
    def run(self):
        cwd = DIRNAME
        if not os.path.exists(os.path.join(cwd, "yuuno_ipython", "build", "extension.js")):
            print("NOT FOUND")
            if not os.path.exists(os.path.join(cwd, 'yuuno-jupyter')):
                raise RuntimeError("Couldn't find uncompiled javascript source. Did you package it incorrectly?")
            self.run_command('build_npm')
        super().run()


class Build(build):

    def run(self):
        if not os.path.exists(os.path.join(DIRNAME, 'yuuno-jupyter')):
            self.announce("Skipping NPM build as the sources are not provided.", level=INFO)
        else:
            self.run_command('build_npm')
        super().run()

with open('README.rst', encoding="utf8") as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', encoding="utf8") as history_file:
    history = history_file.read()

requirements = [
    "jupyter",
    "traitlets",
    "jinja2",
    "ipywidgets",
    "pillow",

    "yuuno-core"
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='yuuno',
    version='1.3',
    description="Yuuno = Jupyter + VapourSynth",
    long_description=readme + '\n\n' + history,
    author="stuxcrystal",
    author_email='stuxcrystal@encode.moe',
    url='https://github.com/stuxcrystal/yuuno',
    packages=find_packages(exclude=("tests", )),
    package_dir={'yuuno_ipython': 'yuuno_ipython'},
    package_data={'yuuno_ipython': ['static/*', 'build/*']},
    include_package_data=True,
    install_requires=requirements,
    license="GNU Lesser General Public License v3 (LGPLv3)",
    zip_safe=False,
    keywords='yuuno',
    cmdclass={
        'sdist': SDistNPM,
        'build': Build,
        'build_npm': NPMBuild,
        'install': Install
    },
    classifiers=[
        'Natural Language :: English',

        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',

        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        'Programming Language :: Python :: 3.6',

        'Framework :: IPython',
        'Framework :: Jupyter',

        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Multimedia :: Video :: Non-Linear Editor',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'yuuno.environments': [
            'load_ipython_extension = yuuno_ipython.ipython.environment:load_ipython_extension',
            'unload_ipython_extension = yuuno_ipython.ipython.environment:unload_ipython_extension'
        ],
        'yuuno.extensions': [
            'ipy_vs = yuuno_ipython.ipy_vs.extension:IPythonVapoursynthExtension',
        ],
        'yuuno.commands': [
            'jupyter = yuuno_ipython.commands:jupyter'
        ]
    }
)
