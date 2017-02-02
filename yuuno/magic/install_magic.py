from IPython.core.magic import register_line_magic


def yuuno(line):
    """
    Activates yuuno on the given notebook
    
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
    
    Example: Only enable inlines
    >>> %yuuno !all inlines
    
    Example: Only include everything except inspections
    >>> %yuuno !inspections
    """
    features = {}
    for feature in line.split(" "):
        val = feature.startswith("!")
        if val:
            feature=feature[1:]
        features[feature] = not val
        
    from yuuno import install
    install(**features)


def install_yuuno_command():
    register_line_magic(yuuno)
