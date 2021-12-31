import sys
from yuuno.autodiscover import discover_commands


def debug():
    from yuuno import __version__
    print(f"Yuuno v{__version__}")

    print()
    print("Registered commands:")
    from yuuno.autodiscover import discover_commands
    import inspect
    for name, cmd in discover_commands().items():
        module = inspect.getmodule(cmd)
        print(" ", name, module.__name__ + '.' + module.__name__)

    print()
    print("External environments:")
    from yuuno.autodiscover import discover_environments
    eps = {}
    for entrypoint in discover_environments(eps):
        print(" ", f"yuuno.{entrypoint} = {eps[entrypoint]!r}")

    print()
    print("External extensions:")
    from yuuno.autodiscover import discover_extensions
    for entrypoint in discover_extensions():
        print(" ", entrypoint)


def main():
    if len(sys.argv) == 1:
        print("You must enter a command. Use yuuno --help to see all available commands.")
        sys.exit(1)

    commands = discover_commands()
    if sys.argv[1] == "--help":
        print("Yuuno - Your library for your frame-server")
        print("Usage:")
        print("\tyuuno --help\t\tShows this help message.")
        for name, cmd in commands.items():
            doc = cmd.__doc__ or 'A lonely command. It refused to tell me something about it.'
            print(f"\tyuuno {name} [...]", doc, sep="\t")
        return
    
    command = sys.argv[1]
    if command == "version":
        from yuuno import __version__
        print(f"Yuuno v{__version__}")
    elif command == "debug":
        debug()
    elif command not in commands:
        print("Sub-Command not found.")
        print("Use yuuno --help to get a list of commands.")
        sys.exit(1)
    else:
        del sys.argv[0]
        commands[command]()


if __name__ == '__main__':
    main()