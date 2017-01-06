Yuuno
=====

Yuuno allows the Jupyther Kernel to show frames from VapourSynth VideoNodes.

## Installation

### Installation for Windows users
Insert your python version where appropriate

    C:\> py -3.5 -m pip install -r requirements.txt
    C:\> py -3.5 -m jupyter nbextension enable --py --sys-prefix widgetsnbextension

### Installation for other operating systems
Make sure python-pip is installed on your system. Make sure that pip
is installing requirements for the correct python interpreter.

    $ pip install -r requirements.txt
    $ jupyter nbextension enable --py --sys-prefix widgetsnbextension



## Running jupyter
    
### Running for Windows users
Insert your python version where appropriate

    C:\> py -3.5 -m jupyter notebook

Follow the instructions given in the log.

### Running for other operating Systems
Just run:
    
    $ jupyter notebook
