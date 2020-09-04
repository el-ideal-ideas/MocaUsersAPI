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

from src.moca_modules.moca_config import MocaFileConfig
from src.moca_modules.moca_log import MocaFileLog
from pathlib import Path
from src.moca_modules.moca_redis import MocaRedis
from src.moca_modules.moca_mysql import MocaMysql

# -------------------------------------------------------------------------- Imports --

# -- Variables --------------------------------------------------------------------------

VERSION: str = '1.0.0'

TOP_DIR: Path = Path(__file__).parent.parent.parent
LOG_DIR: Path = TOP_DIR.joinpath('log')
LOG_DIR.mkdir(parents=True, exist_ok=True)
USER_DIR: Path = TOP_DIR.joinpath('user_data')
USER_DIR.mkdir(parents=True, exist_ok=True)

moca_config: MocaFileConfig = MocaFileConfig(TOP_DIR.joinpath('config.json'))

moca_log: MocaFileLog = MocaFileLog(
    LOG_DIR.joinpath('usage.log'), LOG_DIR.joinpath('error.log'), log_rotate=moca_config.get('log_rotate', False)
)

moca_mysql: MocaMysql = MocaMysql(
    moca_config.get('mysql_host', '127.0.0.1'),
    moca_config.get('mysql_port', 3306),
    moca_config.get('mysql_user', 'root'),
    moca_config.get('mysql_pass', 'pass'),
    moca_config.get('mysql_db', 'moca_users_api'),
)

moca_redis: MocaRedis = MocaRedis(
    moca_config.get('redis_host', '127.0.0.1'),
    moca_config.get('redis_port', 6379),
    moca_config.get('redis_db_index', 0),
    moca_config.get('redis_pass', 'pass'),
)

# -------------------------------------------------------------------------- Variables --
