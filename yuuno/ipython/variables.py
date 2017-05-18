def install():
    import vapoursynth
    from yuuno.ipython.features import install as install_mgr
    from yuuno.ipython.widgets import preview, inspect
    from yuuno.ipython.widgets import dump, compare
    from yuuno.ipython.widgets import diff
    
    if hasattr(vapoursynth, "core"):
        core = vapoursynth.core
    else:
        core = vapoursynth.get_core()

    install_mgr.ipy.push({'core': core, 'vs': vapoursynth})
    install_mgr.ipy.push({
        'preview': preview,
        'inspect': inspect,
        'dump': dump,
        'compare': compare,
        'diff': diff
    })
