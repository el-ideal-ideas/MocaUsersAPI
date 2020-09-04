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

from src.moca_modules.moca_sanic import MocaSanic
from ssl import SSLContext
from sanic import Sanic
from src.moca_modules.moca_config import MocaFileConfig
from src.moca_modules.moca_log import MocaAsyncFileLog
from src.moca_modules.moca_utils import *
from src.moca_modules.moca_mysql import MocaMysql
from src.moca_modules.moca_redis import MocaRedis
from src.moca_modules.moca_mail import MocaMail
from src.moca_modules.moca_sms import MocaTwilioSMS
from src.moca_modules.moca_users import MocaUsers
from src.moca_modules.moca_access import MocaAccess
from pathlib import Path
from src.core import LOG_DIR, TOP_DIR, VERSION, USER_DIR
from pymysql import Warning
from warnings import filterwarnings

# -------------------------------------------------------------------------- Imports --

# -- Init --------------------------------------------------------------------------

filterwarnings('ignore', category=Warning)

# -------------------------------------------------------------------------- Init --

# -- API Server --------------------------------------------------------------------------


class MocaUsersAPIServer(MocaSanic):
    """
    The Users API Server.
    """

    def __init__(self, name: str, host: str, port: int, ssl: Optional[SSLContext] = None,
                 log_dir: Optional[Union[str, Path]] = None, internal_key_file: Optional[Union[str, Path]] = None,
                 access_log: bool = False, use_ipv6: bool = False, workers: int = 0, headers: dict = {}):
        """
        :param name: the name of the sanic server.
        :param host: the host address of the sanic server.
        :param port: the port of the sanic server.
        :param ssl: the ssl context of the sanic server.
        :param log_dir: the directory path of the logs.
        :param internal_key_file: the internal key file path. (the content of internal key file must be 1024 characters)
        :param access_log: logging access.
        :param use_ipv6: use ipv6
        :param workers: the number of workers,
                        if workers is 0, the workers number will be same to the number of cpu cores.
        :param headers: the response headers.
        """
        super().__init__(name, host, port, ssl, log_dir, internal_key_file, access_log, use_ipv6, workers, headers)

    @staticmethod
    async def before_server_start(app: Sanic, loop):
        set_process_name(f'MocaUsersAPI - Server Instances - {current_process().pid}')
        app.moca_config: MocaFileConfig = MocaFileConfig(TOP_DIR.joinpath('config.json'))
        app.moca_log: MocaAsyncFileLog = MocaAsyncFileLog(
            LOG_DIR.joinpath('usage.log'), LOG_DIR.joinpath('error.log'),
            log_rotate=app.moca_config.get('log_rotate', False)
        )
        await app.moca_log.init()
        app.mysql: MocaMysql = MocaMysql(
            app.moca_config.get('mysql_host', '127.0.0.1'),
            app.moca_config.get('mysql_port', 3306),
            app.moca_config.get('mysql_user', 'root'),
            app.moca_config.get('mysql_pass', 'pass'),
            app.moca_config.get('mysql_db', 'moca_users_api'),
        )
        app.redis: MocaRedis = MocaRedis(
            app.moca_config.get('redis_host', '127.0.0.1'),
            app.moca_config.get('redis_port', 6379),
            app.moca_config.get('redis_db_index', 0),
            app.moca_config.get('redis_pass', 'pass'),
        )
        app.moca_mail: MocaMail = MocaMail(
            app.moca_config.get('smtp_user_name', 'admin'),
            app.moca_config.get('smtp_password', 'pass'),
            app.moca_config.get('smtp_from_address', 'admin@sample.com'),
            app.moca_config.get('smtp_use_ssl', True),
            app.moca_config.get('smtp_host', 'mail.sample.com'),
            app.moca_config.get('smtp_port', 465),
        )
        app.moca_sms: MocaTwilioSMS = MocaTwilioSMS(
            app.moca_config.get('twilio_account_sid', ''),
            app.moca_config.get('twilio_auth_token', ''),
            app.moca_config.get('twilio_phone_number', ''),
        )
        app.moca_access: MocaAccess = MocaAccess(
            app.redis, app.mysql, app.moca_config.get('global_rate_limit', '256 per second')
        )
        app.moca_users: MocaUsers = MocaUsers(
            app.mysql, app.redis, app.moca_mail, app.moca_sms, USER_DIR,
            app.moca_config.get('user_name_max_length', 32),
            app.moca_config.get('user_name_min_length', 1),
            app.moca_config.get('user_name_only_ascii', False),
            app.moca_config.get('user_pass_max_length', 32),
            app.moca_config.get('user_pass_min_length', 8),
            app.moca_config.get('userpass_must_contain_alphabet', False),
            app.moca_config.get('userpass_must_contain_digits', False),
            app.moca_config.get('userpass_must_contain_upper', False),
            app.moca_config.get('userpass_must_contain_lower', False),
            app.moca_config.get('userpass_must_contain_symbols', False),
            app.moca_config.get('userpass_only_ascii', True),
            app.moca_config.get('userid_max_length', 32),
            app.moca_config.get('userid_min_length', 1),
            app.moca_config.get('email_is_required', False),
            app.moca_config.get('save_raw_password', False),
        )
        try:
            await app.moca_users.init_db()
            await app.moca_access.init_db()
        except Warning:
            pass

    @staticmethod
    async def after_server_start(app: Sanic, loop):
        print(f"MocaUsersAPIServer({VERSION}) started. <Process: {current_process().pid}>")

# -------------------------------------------------------------------------- API Server --
