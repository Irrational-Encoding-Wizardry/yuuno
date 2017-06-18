#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    version='0.5.0dev0',
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
    license="MIT license",
    zip_safe=False,
    keywords='yuuno',
    classifiers=[
        'Natural Language :: English',

        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',

        'License :: OSI Approved :: MIT License',

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
