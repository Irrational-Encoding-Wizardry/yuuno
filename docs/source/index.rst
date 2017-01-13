.. Yuuno documentation master file, created by
   sphinx-quickstart on Fri Jan 13 19:14:31 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Yuuno
=====

Yuuno incorporates VapourSynth into Jupyter.


Installing and running
----------------------

To install Yuuno, run these two commands in your console.

.. code:: bash

   $ pip install yuuno
   $ jupyter nbextension enable --py --sys-prefix widgetsnbextension

To run it:

.. code:: bash

   $ jupyter notebook

.. note::

   Python must be available on your PATH. If it is not installed on your path, the jupyter command will fail
   will report a missing file.

Using Yuuno
-----------

Initiating Yuuno

.. code:: python

   >>> from yuuno import *
   >>> yuuno.install()

For the rest, please refer to the `tutorial here</tutorial.html>`_.


API Documentation
-----------------

.. toctree::
   :maxdepth: 2
   :glob:

   yuuno.rst
   yuuno.*


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
