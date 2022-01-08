=======
History
=======

1.4.0 (Moscow)
---------------

* Reintegrated Yuuno Core into Yuuno proper.
* I am using a nix-flakes now.
* You don't need to manually install the extension anymore.
* It works with APIv4 now.
* In %%vspreview if there are only two outputs, automatically start diff-view.
* Yuuno now works with JupyterLab
* Added rudimentary audio support. You cannot encode audio right now but if it's the output of a cell
  it will show a simple audio player. It however requires VapourSynth R58 to work.

1.3.0 (Jakarta)
----------------

* We use our own Output Code now. This should allow us more flexibility.

1.2.0 (New York)
----------------

* Added %%vspreview and %%vspipe (which just emulates vspipe for now) implements a new workflow for
  Yuuno users.
* %diff is now an alias for %preview
* Previews can now do a diff.
* Removed the completely useless %show
* Instead of showing the first frame, we are now showing a preview on browsers. It will gracefully degrade.
* Auto-Completion for core.* works again!

1.1.0 (São Paulo)
-----------------

* Removed %inspect and %compare (See deprecation of 1.0.0)
* Recreated %encode and %preview in JavaScript.
* Added %reattach to reattach to encodes.

1.0.0 (Marun Field)
-------------------

* Split up the core-parts of Yuuno into its own repository.
* Show log messages sent from VapourSynth
* From VapourSynth R44 onwards, we can reset core objects.
* Deprecated %inspect and %compare

0.8.0 (Glastig Uaine)
---------------------

* Now I name my releases because I feel like it.
* Fixed color profile not included in PNGs by default. Do so by emitting an sRGB-chunk.
* Completed first version of Comm-Protocol for Yuuno-Kernels.
* Added progressbar to %encode-magic.
* Added support for R41+ alpha clips. (Also with R43+ AlphaOutputTuple support: vapoursynth/#362)
* Use %show for IPython. It will convert the clip to a PIL image. (Can also work for Alpha-Tuples pre R41).

0.7.0
-----

* Added support for clips with variable video formats
* Added support for zlib compression and ICCP-chunk on PNG outputter

0.6.0 (2017-07-24)
------------------

* `%runvpy` can now return the outputs of a vapoursynth-script (.vpy) as a dict.
* Settings of VapourSynth cores are now exposed as configuration variables
* [Misc] Extracted `%encode` and stuck it inside its own sub-package.

0.5.0 (2017-06-18)
------------------

Rewrite of the yuuno codebase to prepare for Yuuno 1.0.0-release.

* You don't have to do `%yuuno install` anymore.
* To configure settings while in your IPython-shell, use the %config-magic, which is available in any IPython installation.
* The minimum Python-version of Yuuno is Python 3.6. Make sure you are running this version when upgrading.
* Using `%unload_ext yuuno` you can now completely deactivate Yuuno on your notebook.
* The `%encode`-magic has become more robust now.
* There is a `%render`-magic now, which does everything %encode does but stores the output into a io.BytesIO.
* All interactive applications are now IPython-magics.
* %preview returns a Preview-object. By changing the clip-Attribute of these objects, you can change the clip without losing the frame number.

0.4.0 (2017-05-18)
------------------

* Allow `vapoursynth.VideoFrames` to be inline-rendered.
* Fixed incorrect aspect-ratio on all `ipywidget` based features.
* Add f-string parsing inside `%encode`. (Will fallback to regular string.format for Python < 3.6) [thanks for the idea @🎌eXmendiC]
* Switched to Jinja2 Templates for Raw-HTML output
* Omit iCCP-chunk since apparently the csp has to be set manually by the user on media players. Of course it can be changed back at any time.

0.3.0 (2017-03-20)
------------------

* An ICCP-chunk is now sent along with the PNG. Currently the default is the 709-CSP ICC. Color-Managed browsers will honor this chunk.
* The variables `core` (referencing the current VS-Core) and `vs` (as a referece to the vapoursynth) will now be pushed to the user-namespace on Yuuno activation.
* `%yuuno install` is now the installation command
* `%yuuno version` shows the current version of yuuno
* `%yuuno help` shows the help for Yuuno.
* `%yuuno get` and `%yuuno set` can be used for configuring Yuuno.
* You have to use `%load_ext yuuno` for initiating yuuno now.
