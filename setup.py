#!/usr/bin/env python
import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "yuuno",
    version = "0.0.1",
    author = "StuxCrystal",
    author_email = "stuxcrystal@encode.moe",
    description = ("Glue for jupyter and vapoursynth"),
    license = "MIT",
    keywords = "vapoursynth frameserver jupyter ipython",
    url = "https://github.com/stuxcrystal/yuuno",
    packages=['yuuno'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        'jupyter', 'Pillow'
    ]
)
