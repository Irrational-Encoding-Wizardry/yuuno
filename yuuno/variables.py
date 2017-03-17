def install():
    import vapoursynth
    from yuuno.features import install as install_mgr
    
    if hasattr(vapoursynth, "core"):
        core = vapoursynth.core
    else:
        core = vapoursynth.get_core()

    install_mgr.ipy.push({'core': core, 'vs': vapoursynth})

