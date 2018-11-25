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
        return
    
    executable = sys.executable
    if sys.argv[1] == "run":
        subprocess.check_call([executable, "-m", "notebook"] + sys.argv[2:])
        return
    if sys.argv[1] == "install":
        subprocess.check_call([executable, "-m", "notebook.nbextensions", "enable", "--py", "--sys-prefix", "widgetsnbextension"])
        subprocess.check_call([executable, "-m", "notebook.nbextensions", "install", "--py", "--sys-prefix", "yuuno_ipython"])
        subprocess.check_call([executable, "-m", "notebook.nbextensions", "enable", "--py", "--sys-prefix", "yuuno_ipython"])
        return
        
    print("Command not found.")
    print("Use 'yuuno jupyter --help' for a full help page.")
    sys.exit(1)