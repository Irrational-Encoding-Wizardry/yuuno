=======
History
=======

Planned Releases
----------------

* `Yuuno 0.5.0 (1.0.0a1)`: 2017-06-25
* `Yuuno 0.6.0 (1.0.0b1)`: 2017-07-20
* `Yuuno 1.0.0rc1`: 2017-10-09 (Feature freeze 2017-08-15)
* `Yuuno 1.0.0`: 2017-10-12


0.5.0a0 (2017-06-18)
--------------------

Rewrite of the yuuno codebase to prepare for Yuuno 1.0.0-release.

* You don't have to do %yuuno install anymore.
* To configure settings while in your IPython-shell, use the %config-magic, which is available in any IPython installation.
* The minimum Python-version of Yuuno is Python 3.6. Make sure you are running this version when upgrading.
* Using %unload_ext yuuno you can now completely deactivate Yuuno on your notebook.
* The %encode-magic has become more robust now.
* There is a %render-magic now, which does everything %encode does but stores the output into a io.BytesIO.
* All interactive applications are now IPython-magics.
* %preview returns a Preview-object. By changing the clip-Attribute of these objects, you can change the clip without losing the frame number.

0.4.0 (2017-05-18)
------------------

* Allow vapoursynth.VideoFrames to be inline-rendered.
* Fixed incorrect aspect-ratio on all ipywidget based features.
* Add f-string parsing inside %encode. (Will fallback to regular string.format for Python < 3.6) [thanks for the idea @🎌eXmendiC]
* Switched to Jinja2 Templates for Raw-HTML output
* Omit iCCP-chunk since apparently the csp has to be set manually by the user on media players. Of course it can be changed back at any time.
