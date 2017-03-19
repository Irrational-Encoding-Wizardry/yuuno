Yuuno
=====

.. image:: https://img.shields.io/badge/version-0.2.0-blue.svg?style=flat-square
.. image:: https://img.shields.io/badge/vapoursynth-R36-brightgreen.svg?style=flat-square
.. image:: https://img.shields.io/badge/vapoursynth-R35-green.svg?style=flat-square


Yuuno connects `VapourSynth <http://vapoursynth.com>`_ with the `Jupyter Notebook <http://jupyter.org>`_. It allows you to write your filters and preview them over the browser.

Installation
------------

The installation is easy. Just use those two commands.

.. code:: batch

   $ py -3.6 -m pip install yuuno
   $ py -3.6 -m notebook.nbextensions enable --py --sys-prefix widgetsnbextension

.. note::

   Python needs to be on PATH for this command to work*

Running Jupyter
---------------

Start Jupyter by executing this command.

.. topic:: Starting Jupyter

  You can start Jupyter anywhere you like using this command:

  .. code:: bash

     $ py -3.6 -m notebook

  Create a notebook at the destination of your choice. Note that the code will be executed in the directory the notebook is saved in.

.. topic:: Enabling Yuuno in your notebook

  Run this code once:

  .. code:: python

    %load_ext yuuno
    %yuuno install
