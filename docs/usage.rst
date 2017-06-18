=====
Usage
=====

What is Yuuno?
--------------

Yuuno is an extension for IPython and provides formatting and automatic namespace inclusions
for the `IPython Shell`_ as well as the `Jupyter IPython Kernel`_ so that video-clips provided
by frame-servers such as `VapourSynth`_ can be introspected inside the shell.

How do I use it?
----------------

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

You can hover over the preview to switch to the second clip.

When you are satisfied with your result, you can then output your clip to an encoder using y4m or raw format::

    clip = core.std.BlankClip()
    %encode --y4m clip x264 --demuxer y4m - --frames {len(clip)}

This should yield the process output of the x264-encoder (which requires, that you have it installed, of course)

.. _IPython Shell: https://ipython.org
.. _Jupyter IPython Kernel: http://jupyter.org
.. _VapourSynth: http://www.vapoursynth.com
