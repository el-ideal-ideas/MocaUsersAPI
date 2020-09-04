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

from docopt import docopt
from .moca_utils import print_warning, print_info, print_license, git_clone, get_time_string
from .moca_core_db import put, get, delete
from .moca_variables import SELF_PATH, TMP_DIR, VERSION
from .moca_sanic import start_debug_mode, stop_debug_mode
from shutil import rmtree, move
from pathlib import Path
from sys import exit
from leveldb import LevelDBError
from time import sleep

# -------------------------------------------------------------------------- Imports --

# -- Console --------------------------------------------------------------------------


def console(name: str):
    __doc__ = f"""
    
    Welcome to MocaModules.
    
    Usage:
        {name} <module> <command> [<values>...]
        {name} --help | -h
        {name} --license
        {name} --version
        {name} --tako
        
    Details:
        moca update
            Update moca modules. (Get latest source code from github.)
        sanic debug on
            Start debug mode for MocaSanic module.
        sanic debug off
            Stop debug mode for MocaSanic module.
        core-db clear
            Clear moca-core-database. Don't run this command when your system is running.
        core-db put <key: string> <value: string>
            Add a data to moca-core-database. Don't run this command when your system is running.
        core-db get <key: string>
            Get a data from moca-core-database. Don't run this command when your system is running.
        core-db delete <key: string>
            Delete a data from moca-core-database. Don't run this command when your system is running.
    
    """

    args = docopt(__doc__)

    # debug
    if '#debug' in args['<values>']:
        print(args)

    if args['-h'] or args['--help']:
        print(__doc__)
    elif args['--license']:
        print_license()
    elif args['--version']:
        print('MocaModules - ' + VERSION)
    elif args['--tako']:
        for _ in range(10):
            print('いあ！いあ！めんだこちゃん！ふたぐん!')
            sleep(0.2)
        print('https://twitter.com/Mendako_Vtuber')
    elif args['<module>'] == 'core-db':
        if args['<command>'] == 'clear':
            print_warning("This command will clear the moca-core-database."
                          " Don't run this command when your system is running.")
            while True:
                print('continue? [Y/n]', end='')
                res = input()
                if res in ('Y', 'Yes', 'yes', 'y', ' ', ''):
                    rmtree(str(Path(__file__).parent.joinpath('storage').joinpath('core.db')))
                    Path(__file__).parent.joinpath('storage').joinpath('core-tiny-db.json').unlink()
                    print_info("moca-core-database was cleared.")
                    exit(0)
                elif res in ('N', 'No', 'no', 'n'):
                    exit(0)
        elif args['<command>'] == 'put':
            if len(args['<values>']) == 2:
                try:
                    if put(args['<values>'][0].encode(), args['<values>'][1]):
                        print_info("Success!")
                    else:
                        print_warning("Failed...")
                except LevelDBError:
                    print_warning("Resource temporarily unavailable.")
            else:
                print_warning("Arguments number error.")
        elif args['<command>'] == 'get':
            if len(args['<values>']) == 1:
                try:
                    print(get(args['<values>'][0].encode()))
                except LevelDBError:
                    print_warning("Resource temporarily unavailable.")
            else:
                print_warning("Arguments number error.")
        elif args['<command>'] == 'delete':
            if len(args['<values>']) == 1:
                try:
                    print(delete(args['<values>'][0].encode()))
                except LevelDBError:
                    print_warning("Resource temporarily unavailable.")
            else:
                print_warning("Arguments number error.")
        else:
            print_warning("Unknown command.")
    elif args['<module>'] == 'moca':
        if args['<command>'] == 'update':
            print('getting source code from github.')
            path = TMP_DIR.joinpath('moca_modules_update' + get_time_string())
            old_storage = Path(__file__).parent.joinpath('storage')
            storage = TMP_DIR.joinpath('moca_modules_storage' + get_time_string())
            old_flags = Path(__file__).parent.joinpath('flags')
            old_core_json = Path(__file__).parent.joinpath('core.json')
            core_json = TMP_DIR.joinpath('moca_modules_core_json' + get_time_string())
            flags = TMP_DIR.joinpath('moca_modules_flags' + get_time_string())
            git_clone('https://github.com/el-ideal-ideas/MocaModules.git', path)
            print('Saving modified data.')
            move(str(old_storage), str(storage))
            move(str(old_flags), str(flags))
            move(str(old_core_json), str(core_json))
            rmtree(str(SELF_PATH))
            print('removed old source code.')
            print('updating source code.')
            move(str(path.joinpath('moca_modules')), str(SELF_PATH))
            rmtree(str(old_storage))
            rmtree(str(old_flags))
            old_core_json.unlink(missing_ok=True)
            move(str(storage), str(old_storage))
            move(str(flags), str(old_flags))
            move(str(core_json), str(old_core_json))
            print('clean up temporary files.')
            rmtree(str(path))
            print('-------------------------------')
            print('Update moca modules successfully.')
            print('-------------------------------')
        else:
            print_warning("Unknown command.")
    elif args['<module>'] == 'sanic':
        if args['<command>'] == 'debug':
            if args['<values>'][0] == 'on':
                start_debug_mode()
                print_info('Started debug mode.')
            elif args['<values>'][0] == 'off':
                stop_debug_mode()
                print_info('Stopped debug mode.')
            else:
                print_warning("Unknown command.")
        else:
            print_warning("Unknown command.")
    else:
        print_warning("Unknown module.")

# -------------------------------------------------------------------------- Console --
