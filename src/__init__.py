# Ω*
#               ■          ■■■■■  
#               ■         ■■   ■■ 
#               ■        ■■     ■ 
#               ■        ■■       
#     ■■■■■     ■        ■■■      
#    ■■   ■■    ■         ■■■     
#   ■■     ■■   ■          ■■■■   
#   ■■     ■■   ■            ■■■■ 
#   ■■■■■■■■■   ■              ■■■
#   ■■          ■               ■■
#   ■■          ■               ■■
#   ■■     ■    ■        ■■     ■■
#    ■■   ■■    ■   ■■■  ■■■   ■■ 
#     ■■■■■     ■   ■■■    ■■■■■


"""
Copyright (c) 2020.5.28 [el.ideal-ideas]
This software is released under the MIT License.
see LICENSE.txt or following URL.
https://www.el-ideal-ideas.com/MocaSystem/LICENSE/
"""


# -- Imports --------------------------------------------------------------------------

from subprocess import call
from sys import executable
from pathlib import Path

# -------------------------------------------------------------------------- Imports --

# -- Check Requirements --------------------------------------------------------------------------

try:
    from .console_script import console_script
    from .moca_modules import console as moca_modules_console
except (ModuleNotFoundError, ImportError):
    with open(str(Path(__file__).parent.parent.joinpath('requirements.txt')), mode='r', encoding='utf-8') as __require:
        __requirements = __require.read().splitlines()
    call(f"{executable} -m pip install --upgrade pip {' '.join(__requirements)}", shell=True)
    del __requirements, __require
    from .console_script import console_script
    from .moca_modules import console as moca_modules_console

# -------------------------------------------------------------------------- Check Requirements --
