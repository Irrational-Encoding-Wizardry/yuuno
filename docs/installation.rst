.. highlight:: shell

============
Installation
============

TL;DR
-----

Yuuno requires Python 3.6 or later. To support VapourSynth, you need VapourSynth R36 or later.
To install it use these commands:

.. code-block:: console

    $ pip install yuuno
    $ jupyter nbextension enable --py widgetsnbextension

Stable release
--------------

To install yuuno, run this command in your terminal:

.. code-block:: console

    $ pip install yuuno

This is the preferred method to install yuuno, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for yuuno can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/stuxcrystal/yuuno

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/stuxcrystal/yuuno/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/stuxcrystal/yuuno
.. _tarball: https://github.com/stuxcrystal/yuuno/tarball/master


Enabling interactive applications
---------------------------------

The interactive application which Yuuno provides for better introspection
rely on the third-party extension `ipywidgets`. This is how you activate this extension:

.. code-block:: console

    $ jupyter nbextension enable --py widgetsnbextension

Refer to this documentation for installation inside virtual environments (such as virtualenv and venv): `ipywidgets Documentation`_

.. _ipywidgets Documentation:  https://ipywidgets.readthedocs.io/en/latest/user_install.html


