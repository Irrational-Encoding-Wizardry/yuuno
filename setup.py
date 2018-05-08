#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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


from setuptools import setup, find_packages

with open('README.rst', encoding="utf8") as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst', encoding="utf8") as history_file:
    history = history_file.read()

requirements = [
    "jupyter",
    "traitlets",
    "jinja2",
    "ipywidgets<7",
    "pillow",

    "yuuno-core"
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='yuuno',
    version='1.0.0.dev2',
    description="Yuuno = Jupyter + VapourSynth",
    long_description=readme + '\n\n' + history,
    author="stuxcrystal",
    author_email='stuxcrystal@encode.moe',
    url='https://github.com/stuxcrystal/yuuno',
    packages=find_packages(exclude=("tests", )),
    package_dir={'yuuno_ipython': 'yuuno_ipython'},
    package_data={'yuuno_ipython': ['static/*']},
    include_package_data=True,
    install_requires=requirements,
    license="GNU Lesser General Public License v3 (LGPLv3)",
    zip_safe=False,
    keywords='yuuno',
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
            'ipy_comm = yuuno_ipython.comm.extension:YuunoKernelCommExtension'
        ]
    }
)
