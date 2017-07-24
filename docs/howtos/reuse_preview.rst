=====================
Reuse Preview Widgets
=====================

How to reuse `%preview`-widgets to retrain the currently shown frame while changing
the clip to be previewed.

Step by step
------------

1. Create a preview and show it::

    my_preview = %preview
    display(my_preview)

   This should show a simple preview widget without an image.

   .. important::

      Make sure this code is run in its own cell as Yuuno will only save the frame when switching the clip
      of the preview instance.

   .. note::

      On older IPython versions you might need to import `display` manually. Do so using::

          from IPython.display import display

2. Assign a clip to the preview-widget::

    my_preview.clip = core.std.BlankClip(color=[0,0,255])

   You should see the clip on the preview-widget created in the first step. Repeat step 2 for every time
   you want to replace your preview.
