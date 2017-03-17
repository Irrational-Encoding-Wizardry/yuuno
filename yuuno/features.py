from functools import wraps

from yuuno import inspection
from yuuno import variables
from yuuno import magic
from yuuno.magic import install_magic
from yuuno.formatters import inlines


class FeatureManager(object):
    """
    This class manages the features added to the system
    using the installation.
    """
    
    def __init__(self):
        self.installed = set()
        self.features = {}
        self.ipy = None
        self.auto = []
    
    def feature(self, name=None, *, auto=False):
        def _decorator(func):
            feature = func.__name__
            if name is not None:
                feature = name
            
            @wraps(func)
            def _wrapper(*args, **kwargs):
                if feature not in self.installed:
                    self.installed.add(feature)
                return func(*args, **kwargs)
            
            self.features[feature] = _wrapper
            if auto:
                self.auto.append(feature)
                
            return func
        return _decorator
        
    def initialize(self, ipy=None):
        self.ipy = ipy
        for name in self.auto:
            self.features[name]()
            self.installed.add(name)
            
    def install(self, **feature_filter):
        """
        Performs an installation.
        
        Set `all=False` to disable autoloading of all features. Each
        other keyword will decided if a feature should be enabled.
        
        If the parameter evaluates to false it will not be enabled.
        If it evaluates to true it will be enabled.
        If omitted it will be enabled by default except `all=False`
        has been passed to the keyword-argument list.
        
        See also: `%yuuno`-line magic.
        """
        default = feature_filter.pop("all", True)
        
        for feature, func in self.features.items():
            if not feature_filter.get(feature, default):
                continue
            func()
    __call__ = install
    
    
install = FeatureManager()

# Default-Features are defined here
install.feature("inspection")(inspection.install)
install.feature("magic")(magic.install)
install.feature("inline")(inlines.install)
install.feature("variables")(variables.install)

# Autoregister the Yuuno-Command
install.feature("yuuno", auto=True)(install_magic.install_yuuno_command)



__all__ = ["install"]
            
