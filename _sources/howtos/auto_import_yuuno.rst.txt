==========================
Automatically import Yuuno
==========================

When you use Yuuno often, you probably want to load Yuuno automatically.

Follow these steps to do it.

Locate the IPython configuration
--------------------------------

1. IPython stores its configuration inside profiles. The default profile is called
   default. Create the default configuration for the default profile.

   .. code-block:: console

       $ ipython profile create default

   **You can skip this step when you already have a profile**

   .. note::

       You can replace `default` with something else. You need to replace `default`
       with the name of your profile in the following steps.

       To load IPython with this profile, use

       .. code-block:: console

           $ ipython --profile=<YourProfileName>

2. Find the path to the configuration to your profile.

   .. code-block:: console

       $ ipython locate profile default

3. Open the file `ipython_kernel_config.py` for editing.

   .. note::

      When using Yuuno inside the default IPython console, use `ipython_config.py`
      instead.

Adding Yuuno to the extension list
----------------------------------

This part assumes that you have the IPython config file open.

1. Locate the line starting with this code::

    #c.InteractiveShellApp.extensions

2. Remove the leading `#` from the line.

3. Insert into the brackets: `'yuuno'`

   .. note::

      If there are other things listed in the brackets, append the string into
      the brackets, separated by a comma.

4. The line should look like this::

    c.InteractiveShellApp.extensions = ['yuuno']
