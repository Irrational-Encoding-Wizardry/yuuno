import sys
import subprocess


def jupyter():
    """Commands for Yuuno 4 IPython"""
    if len(sys.argv) == 1:
        print("Use 'yuuno jupyter --help' for a full help page.")
        sys.exit(1)

    if sys.argv[1] == "--help":
        print("Yuuno for IPython and Jupyter")
        print("Usage:")
        print("\tyuuno jupyter --help\tShow this help page.")
        print("\tyuuno jupyter run\tRuns the Jupyter notebook.")
        print("\tyuuno jupyter install\tInstalls and enables all required notebook extensions.")
        print("\tyuuno jupyter version\tShows the version of Yuuno 4 Jupyter.")
        return
    
    executable = sys.executable
    if sys.argv[1] == "run":
        print("Yuuno is now automatically integrating into Jupyter.")
        print("Run 'jupyter notebook' (without quotes) instead.")
        sys.exit(1)
    elif sys.argv[1] == "install":
        print("Yuuno is now automatically integrating into Jupyter.")
        print("Nothing to do.")
        return

    elif sys.argv[1] == "version":
        try:
            import vapoursynth as vs
        except ImportError:
            vs_ver = "Failed to import. (Is vapoursynth installed?)"
        except Exception as e:
            vs_ver = f"Failed to import: {e!r}"
        else:
            if hasattr(vs, "__version__"):
                vs_ver = f"{vs.__version__[0]}.{vs.__version__[1]}"
            else:
                vs_ver = vs.core.version()
                
        from yuuno_ipython import __version__ as y4ipy_ver
        if "--for-debug" in sys.argv:
            import json
            from yuuno import __version__ as ycore_ver
            print(
                 '{',
                f'  "yuuno": "{ycore_ver}",',
                f'  "yuuno-core": "{ycore_ver}",',
                f'  "python": {json.dumps(tuple(sys.version_info))},',
                f'  "vapoursynth": {json.dumps(vs_ver)}',
                 '}',
                
                sep="\n")
        else:
            print(f"Yuuno for IPython v{y4ipy_ver}")
    else:
        print("Command not found.")
        print("Use 'yuuno jupyter --help' for a full help page.")
        sys.exit(1)
