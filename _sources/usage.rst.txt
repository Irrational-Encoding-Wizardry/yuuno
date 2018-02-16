=====
Usage
=====

What is Yuuno?
--------------

Yuuno is an extension for IPython and provides formatting and automatic namespace inclusions
for the `IPython Shell`_ as well as the `Jupyter IPython Kernel`_ so that video-clips provided
by frame-servers such as `VapourSynth`_ can be introspected inside the shell.

I never used Jupyter. How do I start it?
----------------------------------------

To start Jupyter in order to use Yuuno, use this code.

.. code-block:: console

    $ jupyter notebook

Your browser should navigate to a file-list after Jupyter has been initialized.

Here you can choose an existing notebook-file ending with ".ipynb" or create a new one
by clicking on "New" and then selecting "Python 3"

When you select or create a new notebook, you will be able to enter code into cells.
By pressing Shift+Enter you will be able to execute the code.

How do I use Yuuno?
-------------------

Before you can enjoy Yuuno, you need to explicitely enable it inside your Jupyter Notebook::

    %load_ext yuuno

After you have done this, values like `vs` and `core` have been pushed into your namespace so you
don't have to import vapoursynth and get its core instance.

You can immediately preview the first frame of the clip when it is the result of a cell inside your notebook::

    core.std.BlankClip(color=[0,255,255])

Which should yield a cyan colored blank clip.

To be able to select your desired frame, use the `%preview` line magic that Yuuno provides::

    %preview core.std.BlankClip(color=[0,255,255])

Doing this, you will now see a simple player that let's you select an arbitrary frame from your clip.

To compare between two or more clips use the `%diff`-magic::

    %diff core.std.BlankClip(color=[0,255,255]), core.std.BlankClip(color=[255,255,0])

You can hover over the preview to switch to the second clip which should be yellow.

When you are satisfied with your result, you can then output your clip to an encoder using y4m or raw format::

    clip = core.std.BlankClip(format=vs.YUV444P8)
    %encode clip --y4m x264 --demuxer y4m - --frames {len(clip)} --output test.mp4

This should yield the process output of the x264-encoder (which requires, that you have it installed, of course)

.. _IPython Shell: https://ipython.org
.. _Jupyter IPython Kernel: http://jupyter.org
.. _VapourSynth: http://www.vapoursynth.com
