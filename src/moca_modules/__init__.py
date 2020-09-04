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
from multiprocessing import current_process

# -------------------------------------------------------------------------- Imports --

# -- Check Requirements --------------------------------------------------------------------------

try:
    from apsw import Connection
except (ModuleNotFoundError, ImportError):
    # install apsw module
    call(
        f"{executable} -m pip install --user https://github.com/rogerbinns/apsw/releases/download/3.32.2-r1/"
        f"apsw-3.32.2-r1.zip --global-option=fetch --global-option=--version --global-option=3.32.2 --global"
        f"-option=--all --global-option=build --global-option=--enable-all-extensions",
        shell=True
    )

try:
    from . import (
        moca_base_class, moca_file, moca_log, moca_utils, moca_variables, moca_config, moca_mail, moca_redis,
        moca_encrypt, moca_memory, moca_random, moca_sanic, moca_core_db, moca_console, moca_level_db, moca_users,
        moca_sms, moca_access,
    )
except (ModuleNotFoundError, ImportError):
    with open(str(Path(__file__).parent.joinpath('requirements.txt')), mode='r', encoding='utf-8') as __require_file:
        __requirements = __require_file.read().splitlines()
    call(f"{executable} -m pip install --upgrade pip {' '.join(__requirements)}", shell=True)
    del __requirements, __require_file
    from . import (
        moca_base_class, moca_file, moca_log, moca_utils, moca_variables, moca_config, moca_mail, moca_redis,
        moca_encrypt, moca_memory, moca_random, moca_sanic, moca_core_db, moca_console, moca_level_db, moca_users,
        moca_sms, moca_access,
    )

# -------------------------------------------------------------------------- Check Requirements --

# -- Shortcuts --------------------------------------------------------------------------

from .moca_utils import (
    location, caller_name, self_name, print_debug, print_info, print_warning, print_error, print_critical,
    print_license, save_license_to_file, install_modules, install_requirements_file, git_clone, wget, aio_wget,
    wcheck, aio_wcheck, wstatus, aio_wstatus, disk_speed, check_hash, get_time_string, print_with_color,
    add_extension, add_dot_jpg, add_dot_jpeg, add_dot_gif, add_dot_txt, add_dot_png, add_dot_csv, add_dot_rtf,
    add_dot_pdf, add_dot_md, add_dot_log, add_dot_json, add_dot_py, add_dot_cache, add_dot_pickle, add_dot_js,
    add_dot_css, add_dot_html, set_interval, set_timeout, on_other_thread, on_other_process, is_hiragana,
    is_small_hiragana, is_katakana, is_small_katakana, hiragana_to_katakana, katakana_to_hiragana, check_length,
    dump_json_beautiful, dumps_json_beautiful, contains_upper, contains_lower, contains_alpha, contains_digit,
    contains_symbol, only_consist_of, reset_private_key, to_hankaku, to_zenkaku, check_email_format, moca_dumps,
    moca_dump, moca_aio_dump, moca_loads, moca_load, moca_aio_load, print_only_in_main_process, set_process_name,
    html_escape, html_unescape, word_block,

)
from .moca_access import MocaAccess
from .moca_base_class import MocaClassCache, MocaNamedInstance
from .moca_config import MocaFileConfig
from .moca_console import console
from .moca_encrypt import MocaAES, MocaRSA
from .moca_file import MocaSynchronizedFile, MocaSynchronizedJsonFile, MocaSynchronizedJsonDictionary
from .moca_level_db import MocaLevelDB
from .moca_log import MocaFileLog, MocaAsyncFileLog
from .moca_mail import MocaMail
from .moca_memory import MocaMemory
from .moca_mysql import MocaMysql
from .moca_redis import MocaRedis
from .moca_sanic import MocaSanic, get_remote_address, get_args, json as sanic_json
from .moca_sms import MocaTwilioSMS
from .moca_users import MocaUsers
from .moca_variables import (
    tz, TIME_ZONE, core_json, PROCESS_ID, LICENSE, SHORT_PRIVATE_KEY, LONG_PRIVATE_KEY, RANDOM_KEY
)

# -------------------------------------------------------------------------- Shortcuts --

# -- Write PID File --------------------------------------------------------------------------

with open(str(Path(__file__).parent.joinpath('storage').joinpath('moca.pid')), mode='w', encoding='utf-8') as __pf:
    __pf.write(str(current_process().pid))
del __pf

# -------------------------------------------------------------------------- Write PID File --
