from IPython.core.magic import register_line_magic


class _CommandManager(object):

    def __init__(self):
        self.commands = {}

    def register(self, name):
        def _decorator(func):
            self.commands[name] = func
            return func
        return _decorator

    def get_description(self, name):
        doc = self.commands[name].__doc__
        doc = doc.split("\n")
        doc = (l.strip() for l in doc)
        doc = "\n".join(doc)
        doc = doc.strip()
        return doc

    def execute(self, name, args):
        if name not in self.commands:
            return "Unknown command"
        return self.commands[name](args)

    def __iter__(self):
        return iter(self.commands)


commands = _CommandManager()


@commands.register("install")
def install(line):
    """Installs features of Yuuno to the current IPython-Interpreter

    You can include a list of all features to enable
    as a space-separated list of features.
    
    If the feature is prefixed with a '!' the feature
    will explicitly excluded from the feature list.
    
    By default all features will be activated unless
    explicitely disabled. To switch this mode include
    a '!all' into the list.
    
    The following features exist:
    * `inline`: Inline rendering of clips
    * `magic`: Enable additional cell and line magic
    * `inspection`: Pre R35: Better inspections
    * `variables`: Adds commonly used variables to the environment
    
    Example: Only enable inlines
    >>> %yuuno install !all inlines
    
    Example: Only include everything except inspections
    >>> %yuuno install !inspections"""
    features = {}
    for feature in line.split(" "):
        val = feature.startswith("!")
        if val:
            feature=feature[1:]
        features[feature] = not val
                
    from yuuno import install
    return install(**features)


@commands.register("version")
def version(line):
    """Returns the version of yuuno."""
    from yuuno import __version__
    return __version__


@commands.register("help")
def help(line):
    """Returns the help for the subcommands."""
    if line:
        print(commands.get_description(line.split(" ")[0]))
    else:
        for command in commands:
            print(
                command,
                commands.get_description(command).split("\n")[0],
                sep=" - "
            )

def yuuno(line):
    """
    Controls yuuno
    """
    
    command, *line = line.split(" ", 1)
    if not len(line):
        line = ""
    else:
        line = line[0]

    if not command:
        return "Use %yuuno help for more information"

    return commands.execute(command, line)
    

def install_yuuno_command():
    register_line_magic(yuuno)
