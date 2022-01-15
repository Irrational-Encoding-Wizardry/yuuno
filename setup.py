#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2018 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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

try:
    from Cython.Build import cythonize
    extensions = cythonize("yuuno/vs/_audioop.pyx")
except ImportError:
    extensions = []


DIRNAME = os.path.dirname(__file__) if __file__ else os.getcwd()


class NPMBuild(build_py):
    ENV_NAME = ""
    JS_PROJECT_PATH = ""
    SUCCESS_FILE = ""
    TARGET_PATH = ""

    @classmethod
    def for_build(cls, **args):
        return type("NPMBuild", (cls,), args)

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
        target_dir = os.path.join(cwd, self.TARGET_PATH)# "yuuno_ipython", "build")
        target_file = os.path.join(target_dir, self.SUCCESS_FILE)# "extension.js")

        if os.path.exists(self.JS_PROJECT_PATH):
            if os.path.exists(target_file):
                self.announce(f"cleaning build target.", level=INFO)
                import shutil
                shutil.rmtree(target_dir)

        if os.environ.get(self.ENV_NAME, ""):
            compiled_path = os.environ[self.ENV_NAME]
            if not os.path.exists(os.path.join(compiled_path, self.SUCCESS_FILE)):
                raise EnvironmentError("Could not find built extension.")

            import shutil
            shutil.copytree(compiled_path, target_dir)

            self.announce("Used build from environment.")
            return

        if os.path.exists(self.JS_PROJECT_PATH):
            jspath = os.path.join(cwd, self.JS_PROJECT_PATH)
            pm = self.get_js_package_manager()
            self.popen(f'"{pm}" install', cwd=jspath)
            self.popen(f'"{pm}" run build', cwd=jspath)
        elif os.path.exists(target_file):
            self.announce("source distribution with prebuilt binaries detected. Skipping build.")
        else:
            raise EnvironmentError("sdist without prebuild javascript.")


class SDistNPM(sdist):
    def run(self):
        if not os.path.exists(os.path.join(DIRNAME, "yuuno_ipython", "build", "jupyter.js")):
            self.run_command('build')
        super().run()


class Install(install):
    def run(self):
        cwd = DIRNAME
        if not os.path.exists(os.path.join(cwd, "yuuno_ipython", "build", "jupyter.js")):
            self.run_command('build')
        super().run()


class Build(build):

    def run(self):
        self.run_command('build_npm_ipython')
        self.run_command('build_npm_lab')
        super().run()

with open('README', encoding="utf8") as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', encoding="utf8") as history_file:
    history = history_file.read()

requirements = [
    "jupyter",
    "jupyterlab",
    "traitlets",
    "jinja2",
    "ipywidgets",
    "pillow",
    "psutil"
]

test_requirements = []

extras_requires = {
    'vapoursynth': ['vapoursynth', 'vsutil']
}


def recursive(path, prefix, extras=None):
    if extras is None:
        extras = {}
    for dirpath, _, files in os.walk(path):
        kdpath = dirpath[len(path):]
        if not files and not extras.get(kdpath, ()): continue
        npath = f"{path}{kdpath}" if kdpath else path
        npfx = f"{prefix}{kdpath}" if kdpath else prefix
        yield (npfx, [f"{npath}/{file}" for file in files] + extras.get(npfx, []))


setup(
    name='yuuno',
    version='1.4',
    description="Yuuno = Jupyter + VapourSynth",
    long_description=readme + '\n\n' + history,
    long_description_content_type = "text/plain",
    author="cid-chan",
    author_email='cid+yuuno@cid-chan.moe',
    url='https://github.com/Irrational-Encoding-Wizardry/yuuno',
    packages=find_packages(exclude=("tests", )),
    data_files=[
        ("share/jupyter/nbextensions/@yuuno", [
            "yuuno_ipython/build/jupyter.js",
            "yuuno_ipython/build/jupyter.js.map",
            "yuuno_ipython/build/worker.js",
            "yuuno_ipython/build/worker.js.map",
        ]),

        ("etc/jupyter/nbconfig/notebook.d", [
            "yuuno_ipython/config/nbconfig/notebook.d/yuuno-jupyter.json"
        ]),

        *recursive("yuuno_jupyterlab/static", "share/jupyter/labextensions/@yuuno/jupyterlab", {
            "share/jupyter/labextensions/@yuuno/jupyterlab": [
                "yuuno_jupyterlab/config/labextensions/install.json"
            ]
        }),
    ],
    package_dir={'yuuno_ipython': 'yuuno_ipython'},
    package_data={'yuuno_ipython': ['static/*', 'build/*']},
    # ext_modules=extensions,
    include_package_data=True,
    install_requires=requirements,
    license="GNU Affero General Public License v3 (AGPLv3)",
    zip_safe=False,
    keywords='yuuno',
    cmdclass={
        'sdist': SDistNPM,
        'build': Build,
        'build_npm_ipython': NPMBuild.for_build(
            ENV_NAME = "COMPILED_YUUNO_JS",
            JS_PROJECT_PATH = "yuuno-jupyter",
            SUCCESS_FILE = "jupyter.js",
            TARGET_PATH = "yuuno_ipython/build"
        ),
        'build_npm_lab': NPMBuild.for_build(
            ENV_NAME = "COMPILED_YUUNO_LAB_JS",
            JS_PROJECT_PATH = "yuuno-jupyterlab-js",
            SUCCESS_FILE = "package.json",
            TARGET_PATH = "yuuno_jupyterlab/static"
        ),
        'install': Install
    },
    classifiers=[
        'Natural Language :: English',

        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',

        'License :: OSI Approved :: GNU Affero General Public License v3',

        'Programming Language :: Python :: 3.9',

        'Framework :: Jupyter',
        'Framework :: Jupyter :: JupyterLab',
        'Framework :: Jupyter :: JupyterLab :: 3',
        'Framework :: Jupyter :: JupyterLab :: Extensions',
        'Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt',

        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Multimedia :: Video :: Non-Linear Editor',

    ],
    entry_points={
        'console_scripts': ['yuuno=yuuno.console_scripts:main']
    }
)
