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
from src.moca_modules.moca_variables import LICENSE
from src.core import VERSION, moca_log, moca_mysql, moca_redis
from src.moca_modules.moca_utils import print_error, print_warning
from src.server import server
from src.moca_modules.moca_access import MocaAccess
from asyncio import run

# -------------------------------------------------------------------------- Imports --

# -- Variables --------------------------------------------------------------------------

__doc__ = f"""

Welcome to MocaSystem(MocaUsersAPI).

Usage:
    moca.py run
    moca.py create-api-key
    moca.py --license
    moca.py --version
"""

# -------------------------------------------------------------------------- Variables --

# -- Console Script --------------------------------------------------------------------------


def console_script():
    try:
        args = docopt(__doc__)
        if args['--license']:
            print(LICENSE)
        elif args['--version']:
            print(VERSION)
        elif args['run']:
            server.run_server(True)
        elif args['create-api-key']:
            moca_access: MocaAccess = MocaAccess(moca_redis, moca_mysql, '1 per minute')
            print('Please input your reference or `*`')
            referer = input('Moca > ')
            print('Please input the rate limit of this api key. For example: 64 per minute')
            rate_limit = input('Moca > ')
            print('Please input the access limit of this api key.')
            access_limit = int(input('Moca > '))
            print('Please input the permission of this api key.')
            permission = input('Moca > ')
            status = run(moca_access.create_new_api_key(referer, rate_limit, access_limit, permission))
            if status[0] == 0:
                print('Your api key has been created successfully.')
                print('API-KEY: ' + status[1])
            else:
                print(status[1])
        else:
            print_warning("Unknown command.")
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as error:
        error_str = f"Some unknown error occurred。 <Exception: {error}>"
        print_error(error_str)
        moca_log.save(error_str, moca_log.LogLevel.ERROR)

# -------------------------------------------------------------------------- Console Script --
