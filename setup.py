#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal
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

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "jupyter",
    "traitlets",
    "jinja2",
    "ipywidgets",
    "pillow"
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='yuuno',
    version='0.5.0',
    description="Yuuno = Jupyter + VapourSynth",
    long_description=readme + '\n\n' + history,
    author="stuxcrystal",
    author_email='stuxcrystal@encode.moe',
    url='https://github.com/stuxcrystal/yuuno',
    packages=find_packages(exclude=("tests", )),
    package_dir={'yuuno': 'yuuno'},
    package_data={'yuuno': ['data/*']},
    include_package_data=True,
    install_requires=requirements,
    license="GNU Lesser General Public License v3 (LGPLv3)",
    zip_safe=False,
    keywords='yuuno',
    classifiers=[
        'Natural Language :: English',

        'Development Status :: 4 - Beta',

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
    tests_require=test_requirements
)
