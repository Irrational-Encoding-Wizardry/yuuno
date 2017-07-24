=================================
Run vapoursynth scripts via Yuuno
=================================

You can run vapoursynth scripts (.vpy) using the line magic `%runvpy` with takes a path as an argument.

It will return a dictionary with all outputs defined by the vpy-file so you can use it
to encode or further modify the clip.

Simple example:
---------------

Here is a simple example::

    %runvpy test.vpy

Upon successful execution it will return a dictionary with your outputs.
