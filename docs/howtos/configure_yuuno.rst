=================
Configuring Yuuno
=================

There are two ways to configure Yuuno.

The first way is to temporarily configure Yuuno inside your notebook.
This also allows you to see the current settings.

The second way is defining the settings by a configuration file.

We will discuss both ways here.


Configuring Yuuno inside the current session
--------------------------------------------

IPython provides you with the `%config`-magic. It allows you to configure
the settings of IPython itself as well as the settings of Yuuno.

Entering this magic without any arguments, will generate a list of categories
of settings::

    %config
    Available objects for config:
         AliasManager
         DisplayFormatter
         HistoryManager
         IPCompleter
         IPKernelApp
         LoggingMagics
         MagicsManager
         PrefilterManager
         ScriptMagics
         StoreMagics
         VapourSynth
         Yuuno
         YuunoIPythonEnvironment
         ZMQInteractiveShell

By entering one of those settings you can configure those settings.

Important for us is `YuunoIPythonnEnvironment` which lets you define defaults and
`VapourSynth` where you can configure how VapourSynth converts its clips to RGB24.

By entering this section as a parameter to `%config` you can see a list of settings::

    %config YuunoIPythonEnvironment
    ...
    YuunoIPythonEnvironment.inspect_default_sizes=<List>
        Current: [1.0, 2.0, 5.0]
        Default values for the inspect widget
    YuunoIPythonEnvironment.inspect_resizer=<CaselessStrEnum>
        Current: 'NEAREST'
        Choices: ['NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS']
        Which PIL scaler should be used to resize the image?
    ...

You can set a setting using this syntax::

    %config YuunoIPythonEnvironment.inspect_resizer='BILINEAR'

Permanently set a value
-----------------------

Yuuno is configured using the IPython configuration mentioned in :ref:`Automatically import Yuuno <Locate the IPython configuration>`.

Yuuno has the same configuration values as in the impermanent configuration. However, all sections, except
`Yuuno` itself, are subsections of the Yuuno section.

Permanently set the configuration above like this::

    c.Yuuno.YuunoIPythonEnvironment.inspect_resizer = 'BILINEAR'

Save the file and restart your notebook-kernel.
