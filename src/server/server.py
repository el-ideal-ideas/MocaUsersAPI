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

from ssl import SSLContext
from src.core import moca_config, LOG_DIR, VERSION
from src.moca_modules.moca_utils import *
from src.moca_modules import get_args
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, text, raw
from src.moca_modules import sanic_json as json
from sanic.exceptions import Forbidden, NotFound
from .MocaUsersAPIServer import MocaUsersAPIServer
from secrets import compare_digest
from base64 import b64encode

# -------------------------------------------------------------------------- Imports --

# -- Variables --------------------------------------------------------------------------

users_api: Blueprint = Blueprint('users_api', 'users')

# -------------------------------------------------------------------------- Variables --

# -- Server --------------------------------------------------------------------------

ssl: Optional[SSLContext]
if isinstance(moca_config.get('certfile'), str) and \
        isinstance(moca_config.get('keyfile'), str) and \
        Path(moca_config.get('certfile')).is_file() and \
        Path(moca_config.get('keyfile')).is_file():
    ssl = MocaUsersAPIServer.create_ssl_context(moca_config.get('certfile'),
                                                moca_config.get('keyfile'))
else:
    ssl = None

server: MocaUsersAPIServer = MocaUsersAPIServer(
    'MocaUsersAPIServer',
    moca_config.get('host', '0.0.0.0'),
    moca_config.get('port', 5980),
    ssl,
    LOG_DIR,
    None,
    moca_config.get('access_log', True),
    moca_config.get('use_ipv6', False),
    moca_config.get('workers', 0),
    moca_config.get('headers', {})
)

app = server.app
server.add_blueprint(users_api)

# -------------------------------------------------------------------------- Server --

# -- Middleware --------------------------------------------------------------------------


@app.middleware('request')
async def global_ip_rate_limit(request: Request):
    if request.app.moca_access.check_ip_rate_limit(request):
        pass
    else:
        raise Forbidden('too many requests.')

# -------------------------------------------------------------------------- Middleware --

# -- Routes --------------------------------------------------------------------------


@users_api.route('/version', methods={'GET', 'POST', 'OPTIONS'})
async def version(request: Request) -> HTTPResponse:
    return text(VERSION)


@users_api.route('/insert_dummy_data', methods={'GET', 'POST', 'OPTIONS'})
async def insert_dummy_data(request: Request) -> HTTPResponse:
    root_pass, api_key = get_args(request, 'root_pass', 'api_key')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    if not (isinstance(root_pass, str) and root_pass.isascii() and (8 <= len(root_pass) <= 32)):
        raise Forbidden('root password format error.')
    if not compare_digest(root_pass, request.app.moca_config.get('root_pass', '')):
        raise Forbidden('invalid root password.')
    await request.app.moca_users.insert_dummy_data()
    return text('success.')


@users_api.route('/create_user', methods={'GET', 'POST', 'OPTIONS'})
async def create_user(request: Request) -> HTTPResponse:
    api_key, username, password, userid, email = get_args(request, 'api_key', 'username', 'password', 'userid', 'email')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.create_user(username, password, userid, email)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/check_userid', methods={'GET', 'POST', 'OPTIONS'})
async def check_userid(request: Request) -> HTTPResponse:
    api_key, userid = get_args(request, 'api_key', 'userid')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.check_userid(userid)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/send_email_verify_message', methods={'GET', 'POST', 'OPTIONS'})
async def send_email_verify_message(request: Request) -> HTTPResponse:
    api_key, userid = get_args(request, 'api_key', 'userid')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.send_email_verify_message(userid)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/add_email_address', methods={'GET', 'POST', 'OPTIONS'})
async def add_email_address(request: Request) -> HTTPResponse:
    api_key, userid, email, access_token = get_args(request, 'api_key', 'userid', 'email', 'access_token')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.add_email_address(userid, email, access_token)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/verify_email', methods={'GET', 'POST', 'OPTIONS'})
async def verify_email(request: Request) -> HTTPResponse:
    api_key, userid, token = get_args(request, 'api_key', 'userid', 'token')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.verify_email(userid, token)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/check_access_token', methods={'GET', 'POST', 'OPTIONS'})
async def check_access_token(request: Request) -> HTTPResponse:
    api_key, userid, access_token = get_args(request, 'api_key', 'userid', 'access_token')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.check_access_token(userid, access_token)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/login', methods={'GET', 'POST', 'OPTIONS'})
async def login(request: Request) -> HTTPResponse:
    api_key, userid, password = get_args(request, 'api_key', 'userid', 'password')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.login(userid, password, server.get_remote_address(request))
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/send_phone_login_code', methods={'GET', 'POST', 'OPTIONS'})
async def send_phone_login_code(request: Request) -> HTTPResponse:
    api_key, userid, phone = get_args(request, 'api_key', 'userid', 'phone')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.send_phone_login_code(userid, phone)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/login_by_phone', methods={'GET', 'POST', 'OPTIONS'})
async def login_by_phone(request: Request) -> HTTPResponse:
    api_key, userid, token, phone = get_args(request, 'api_key', 'userid', 'token', 'phone')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.login_by_phone(userid, token, phone, server.get_remote_address(request))
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/search_users_by_name', methods={'GET', 'POST', 'OPTIONS'})
async def search_users_by_name(request: Request) -> HTTPResponse:
    api_key, username = get_args(request, 'api_key', 'username')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.search_users_by_name(username)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/search_user_by_id', methods={'GET', 'POST', 'OPTIONS'})
async def search_user_by_id(request: Request) -> HTTPResponse:
    api_key, userid = get_args(request, 'api_key', 'userid')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.search_user_by_id(userid)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/search_users', methods={'GET', 'POST', 'OPTIONS'})
async def search_users(request: Request) -> HTTPResponse:
    api_key, keywords = get_args(request, 'api_key', 'keywords')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    data = await request.app.moca_users.search_users(keywords)
    return json(data)


@users_api.route('/save_profile', methods={'GET', 'POST', 'OPTIONS'})
async def save_profile(request: Request) -> HTTPResponse:
    api_key, userid, profile, access_token = get_args(request, 'api_key', 'userid', 'profile', 'access_token')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.save_profile(userid, profile, access_token)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_profile', methods={'GET', 'POST', 'OPTIONS'})
async def get_profile(request: Request) -> HTTPResponse:
    api_key, userid = get_args(request, 'api_key', 'userid')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.get_profile(userid)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_profiles', methods={'GET', 'POST', 'OPTIONS'})
async def get_profiles(request: Request) -> HTTPResponse:
    api_key, userid_list = get_args(request, 'api_key', 'userid_list')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    data = await request.app.moca_users.get_profiles(userid_list)
    return json(data)


@users_api.route('/add_phone_number', methods={'GET', 'POST', 'OPTIONS'})
async def add_phone_number(request: Request) -> HTTPResponse:
    api_key, userid, phone, access_token = get_args(request, 'api_key', 'userid', 'phone', 'access_token')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.add_phone_number(userid, phone, access_token)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/verify_phone', methods={'GET', 'POST', 'OPTIONS'})
async def verify_phone(request: Request) -> HTTPResponse:
    api_key, userid, code, access_token = get_args(request, 'api_key', 'userid', 'code', 'access_token')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.verify_phone(userid, code, access_token)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/has_verified_phone', methods={'GET', 'POST', 'OPTIONS'})
async def has_verified_phone(request: Request) -> HTTPResponse:
    api_key, userid = get_args(request, 'api_key', 'userid')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.has_verified_phone(userid)
    if status:
        return text('0')
    else:
        return text('1')


@users_api.route('/check_password', methods={'GET', 'POST', 'OPTIONS'})
async def check_password(request: Request) -> HTTPResponse:
    api_key, userid, password = get_args(request, 'api_key', 'userid', 'password')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.check_password(userid, password)
    if status:
        return text('0')
    else:
        return text('1')


@users_api.route('/start_two_step_verification', methods={'GET', 'POST', 'OPTIONS'})
async def start_two_step_verification(request: Request) -> HTTPResponse:
    api_key, userid, password = get_args(request, 'api_key', 'userid', 'password')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.start_two_step_verification(userid, password)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/stop_two_step_verification', methods={'GET', 'POST', 'OPTIONS'})
async def stop_two_step_verification(request: Request) -> HTTPResponse:
    api_key, userid, password = get_args(request, 'api_key', 'userid', 'password')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.stop_two_step_verification(userid, password)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/check_system_account_permission', methods={'GET', 'POST', 'OPTIONS'})
async def check_system_account_permission(request: Request) -> HTTPResponse:
    api_key, userid, password, permission = get_args(request, 'api_key', 'userid', 'password', 'permission')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.check_system_account_permission(userid, password, permission)
    if status:
        return text('0')
    else:
        return text('1')


@users_api.route('/get_my_login_log', methods={'GET', 'POST', 'OPTIONS'})
async def get_my_login_log(request: Request) -> HTTPResponse:
    api_key, userid, access_token = get_args(request, 'api_key', 'userid', 'access_token')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.get_my_login_log(userid, access_token)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_user_access_token', methods={'GET', 'POST', 'OPTIONS'})
async def get_user_access_token(request: Request) -> HTTPResponse:
    api_key, userid, password, target_userid = get_args(request, 'api_key', 'userid', 'password', 'target_userid')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.get_user_access_token(userid, password, target_userid)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/lock_my_account', methods={'GET', 'POST', 'OPTIONS'})
async def lock_my_account(request: Request) -> HTTPResponse:
    api_key, userid, password = get_args(request, 'api_key', 'userid', 'password')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.lock_my_account(userid, password)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/lock_user_account', methods={'GET', 'POST', 'OPTIONS'})
async def lock_user_account(request: Request) -> HTTPResponse:
    api_key, userid, password, target_userid = get_args(request, 'api_key', 'userid', 'password', 'target_userid')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.lock_user_account(userid, password, target_userid)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/reset_user_database', methods={'GET', 'POST', 'OPTIONS'})
async def reset_user_database(request: Request) -> HTTPResponse:
    root_pass, api_key = get_args(request, 'root_pass', 'api_key')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    if not (isinstance(root_pass, str) and root_pass.isascii() and (8 <= len(root_pass) <= 32)):
        raise Forbidden('root password format error.')
    if not compare_digest(root_pass, app.moca_config.get('root_pass', '')):
        raise Forbidden('invalid root password.')
    await request.app.moca_users.reset_user_database()
    return text('success.')


@users_api.route('/save_user_image', methods={'GET', 'POST', 'OPTIONS'})
async def save_user_image(request: Request) -> HTTPResponse:
    api_key, userid, access_token, key, image = get_args(request, 'api_key', 'userid', 'access_token', 'key', 'image')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.save_user_image(
        userid, access_token, key, image if isinstance(image, str) else image.body
    )
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_user_image', methods={'GET', 'POST', 'OPTIONS'})
async def get_user_image(request: Request) -> HTTPResponse:
    userid, key = get_args(request, 'userid', 'key')
    status = await request.app.moca_users.get_user_image(userid, key)
    return json({
        'status_code': status[0],
        'msg': status[1] if status[0] != 0 else 'data:image/jpeg;base64,' + b64encode(status[1]).decode('utf-8')
    })


@users_api.route('/get_user_image/<userid>/<key>', methods={'GET', 'POST', 'OPTIONS'})
async def get_user_image_raw(request: Request, userid, key) -> HTTPResponse:
    status = await request.app.moca_users.get_user_image(userid, key)
    if status[0] == 0:
        return raw(status[1], content_type='image/jpeg')
    else:
        raise NotFound('Not Found.')


@users_api.route('/save_big_icon', methods={'GET', 'POST', 'OPTIONS'})
async def save_big_icon(request: Request) -> HTTPResponse:
    api_key, userid, access_token, icon = get_args(request, 'api_key', 'userid', 'access_token', 'icon')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.save_big_icon(
        userid, access_token, icon if isinstance(icon, str) else icon.body
    )
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/save_small_icon', methods={'GET', 'POST', 'OPTIONS'})
async def save_small_icon(request: Request) -> HTTPResponse:
    api_key, userid, access_token, icon = get_args(request, 'api_key', 'userid', 'access_token', 'icon')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.save_small_icon(
        userid, access_token, icon if isinstance(icon, str) else icon.body
    )
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_big_icon', methods={'GET', 'POST', 'OPTIONS'})
async def get_big_icon(request: Request) -> HTTPResponse:
    userid = get_args(request, 'userid')[0]
    status = await request.app.moca_users.get_big_icon(userid)
    return json({
        'status_code': status[0],
        'msg': status[1] if status[0] != 0 else 'data:image/jpeg;base64,' + b64encode(status[1]).decode('utf-8')
    })


@users_api.route('/get_small_icon', methods={'GET', 'POST', 'OPTIONS'})
async def get_small_icon(request: Request) -> HTTPResponse:
    userid = get_args(request, 'userid')[0]
    status = await request.app.moca_users.get_small_icon(userid)
    return json({
        'status_code': status[0],
        'msg': status[1] if status[0] != 0 else 'data:image/jpeg;base64,' + b64encode(status[1]).decode('utf-8')
    })


@users_api.route('/get_big_icon/<userid>', methods={'GET', 'POST', 'OPTIONS'})
async def get_big_icon_raw(request: Request, userid) -> HTTPResponse:
    status = await request.app.moca_users.get_big_icon(userid)
    if status[0] == 0:
        return raw(status[1], content_type='image/jpeg')
    else:
        raise NotFound('Not Found.')


@users_api.route('/get_small_icon/<userid>', methods={'GET', 'POST', 'OPTIONS'})
async def get_small_icon_raw(request: Request, userid) -> HTTPResponse:
    status = await request.app.moca_users.get_small_icon(userid)
    if status[0] == 0:
        return raw(status[1], content_type='image/jpeg')
    else:
        raise NotFound('Not Found.')


@users_api.route('/save_user_file', methods={'GET', 'POST', 'OPTIONS'})
async def save_user_file(request: Request) -> HTTPResponse:
    api_key, userid, access_token, key, data = get_args(request, 'api_key', 'userid', 'access_token', 'key', 'data')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.save_user_file(
        userid, access_token, key, data if isinstance(data, str) else data.body
    )
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_user_file', methods={'GET', 'POST', 'OPTIONS'})
async def get_user_file(request: Request) -> HTTPResponse:
    api_key, userid, access_token, key = get_args(request, 'api_key', 'userid', 'access_token', 'key')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.get_user_file(
        userid, access_token, key
    )
    return json({
        'status_code': status[0],
        'msg': status[1] if status[0] != 0 else b64encode(status[1]).decode('utf-8'),
    })


@users_api.route('/get_user_file/raw', methods={'GET', 'POST', 'OPTIONS'})
async def get_user_file_raw(request: Request) -> HTTPResponse:
    api_key, userid, access_token, key = get_args(request, 'api_key', 'userid', 'access_token', 'key')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.get_user_file(
        userid, access_token, key
    )
    if status[0] == 0:
        return raw(b64encode(status[1]).decode('utf-8'))
    else:
        raise NotFound('Not Found.')


@users_api.route('/send_message', methods={'GET', 'POST', 'OPTIONS'})
async def send_message(request: Request) -> HTTPResponse:
    api_key, from_, to_, access_token, message = get_args(request, 'api_key', 'from', 'to', 'access_token', 'message')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.send_message(from_, to_, access_token, message)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_messages', methods={'GET', 'POST', 'OPTIONS'})
async def get_messages(request: Request) -> HTTPResponse:
    api_key, userid, access_token, start, limit = get_args(
        request, 'api_key', 'userid', 'access_token', ('start', int, 0), ('limit', int, 1024)
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.get_messages(userid, access_token, start, limit)
    return json({
        'status_code': status[0],
        'msg': status[1] if status[0] != 0 else [(item[0], item[1], item[2], str(item[3])) for item in status[1]]
    })


@users_api.route('/change_password', methods={'GET', 'POST', 'OPTIONS'})
async def change_password(request: Request) -> HTTPResponse:
    api_key, userid, old, new = get_args(request, 'api_key', 'userid', 'old', 'new')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.change_password(userid, old, new)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/has_verified_email', methods={'GET', 'POST', 'OPTIONS'})
async def has_verified_email(request: Request) -> HTTPResponse:
    api_key, userid = get_args(request, 'api_key', 'userid')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.has_verified_email(userid)
    if status:
        return text('0')
    else:
        return text('1')


@users_api.route('/get_user_email_list', methods={'GET', 'POST', 'OPTIONS'})
async def get_user_email_list(request: Request) -> HTTPResponse:
    api_key, userid_list = get_args(request, 'api_key', 'userid_list')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    data = await request.app.moca_users.get_user_email_list(userid_list)
    return json(data)


@users_api.route('/send_email_to_users', methods={'GET', 'POST', 'OPTIONS'})
async def send_email_to_users(request: Request) -> HTTPResponse:
    api_key, userid_list, title, body = get_args(request, 'api_key', 'userid_list', 'title', 'body')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    data = await request.app.moca_users.send_email_to_users(userid_list, title, body)
    return json(data)


@users_api.route('/get_user_phone_number', methods={'GET', 'POST', 'OPTIONS'})
async def get_user_phone_number(request: Request) -> HTTPResponse:
    api_key, userid_list = get_args(request, 'api_key', 'userid_list')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    data = await request.app.moca_users.get_user_phone_number(userid_list)
    return json(data)


@users_api.route('/send_sms_to_users', methods={'GET', 'POST', 'OPTIONS'})
async def send_sms_to_users(request: Request) -> HTTPResponse:
    api_key, userid_list, body = get_args(request, 'api_key', 'userid_list', 'body')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    data = await request.app.moca_users.send_sms_to_users(userid_list, body)
    return json(data)


@users_api.route('/forgot_password', methods={'GET', 'POST', 'OPTIONS'})
async def forgot_password(request: Request) -> HTTPResponse:
    api_key, userid = get_args(request, 'api_key', 'userid')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.forgot_password(userid)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/reset_password', methods={'GET', 'POST', 'OPTIONS'})
async def reset_password(request: Request) -> HTTPResponse:
    api_key, userid, password, token = get_args(request, 'api_key', 'userid', 'password', 'token')
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.reset_password(userid, password, token)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/save_my_user_data', methods={'GET', 'POST', 'OPTIONS'})
async def save_my_user_data(request: Request) -> HTTPResponse:
    api_key, userid, access_token, storage, data = get_args(
        request, 'api_key', 'userid', 'access_token', ('storage', int), 'data'
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.save_my_user_data(userid, access_token, storage, data)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_my_user_data', methods={'GET', 'POST', 'OPTIONS'})
async def get_my_user_data(request: Request) -> HTTPResponse:
    api_key, userid, access_token, storage = get_args(
        request, 'api_key', 'userid', 'access_token', ('storage', int)
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.get_my_user_data(userid, access_token, storage)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_other_user_data', methods={'GET', 'POST', 'OPTIONS'})
async def get_other_user_data(request: Request) -> HTTPResponse:
    api_key, userid, target_userid, access_token, storage = get_args(
        request, 'api_key', 'userid', 'target_userid', 'access_token', ('storage', int)
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.get_other_user_data(userid, access_token, target_userid, storage)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/save_other_user_data', methods={'GET', 'POST', 'OPTIONS'})
async def save_other_user_data(request: Request) -> HTTPResponse:
    api_key, userid, target_userid, access_token, storage, data = get_args(
        request, 'api_key', 'userid', 'target_userid', 'access_token', ('storage', int), 'data'
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.save_other_user_data(userid, access_token, target_userid, storage, data)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_user_count', methods={'GET', 'POST', 'OPTIONS'})
async def get_user_count(request: Request) -> HTTPResponse:
    api_key = get_args(request, 'api_key')[0]
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    count = await request.app.moca_users.get_user_count()
    return text(str(count))


@users_api.route('/get_locked_user_number', methods={'GET', 'POST', 'OPTIONS'})
async def get_locked_user_number(request: Request) -> HTTPResponse:
    api_key = get_args(request, 'api_key')[0]
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    count = await request.app.moca_users.get_locked_user_number()
    return text(str(count))


@users_api.route('/get_users_list', methods={'GET', 'POST', 'OPTIONS'})
async def get_users_list(request: Request) -> HTTPResponse:
    api_key, userid, password, start, limit = get_args(
        request, 'api_key', 'userid', 'password', ('start', int), ('limit', int)
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-SM-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    data = await request.app.moca_users.get_users_list(userid, password, start, limit)
    return json(data)


@users_api.route('/insert_data_to_storage', methods={'GET', 'POST', 'OPTIONS'})
async def insert_data_to_storage(request: Request) -> HTTPResponse:
    api_key, userid, access_token, key, data = get_args(
        request, 'api_key', 'userid', 'access_token', 'key', 'data'
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.insert_data_to_storage(userid, access_token, key, data)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/select_data_from_storage', methods={'GET', 'POST', 'OPTIONS'})
async def select_data_from_storage(request: Request) -> HTTPResponse:
    api_key, userid, access_token, key = get_args(
        request, 'api_key', 'userid', 'access_token', 'key'
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.select_data_from_storage(userid, access_token, key)
    return json({
        'status_code': status[0],
        'msg': status[1] if status[0] != 0 else [(item[0], item[1], str(item[2])) for item in status[1]],
    })


@users_api.route('/delete_data_from_storage_by_id', methods={'GET', 'POST', 'OPTIONS'})
async def delete_data_from_storage_by_id(request: Request) -> HTTPResponse:
    api_key, userid, access_token, content_id = get_args(
        request, 'api_key', 'userid', 'access_token', ('content_id', int)
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.delete_data_from_storage_by_id(userid, access_token, content_id)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/delete_data_from_storage_by_key', methods={'GET', 'POST', 'OPTIONS'})
async def delete_data_from_storage_by_key(request: Request) -> HTTPResponse:
    api_key, userid, access_token, key = get_args(
        request, 'api_key', 'userid', 'access_token', 'key'
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.delete_data_from_storage_by_key(userid, access_token, key)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/update_data_in_storage_by_id', methods={'GET', 'POST', 'OPTIONS'})
async def update_data_in_storage_by_id(request: Request) -> HTTPResponse:
    api_key, userid, access_token, content_id, data = get_args(
        request, 'api_key', 'userid', 'access_token', ('content_id', int), 'data'
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.update_data_in_storage_by_id(userid, access_token, content_id, data)
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/share_file', methods={'GET', 'POST', 'OPTIONS'})
async def share_file(request: Request) -> HTTPResponse:
    api_key, userid, access_token, filename, data, protection, time_limit, info = get_args(
        request, 'api_key', 'userid', 'access_token', 'filename', 'data', 'protection', ('time_limit', int), 'info'
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.share_file(
        userid, access_token, filename, data if isinstance(data, str) else data.body, protection, time_limit, info
    )
    return json({
        'status_code': status[0],
        'msg': status[1],
    })


@users_api.route('/get_shared_file', methods={'GET', 'POST', 'OPTIONS'})
async def get_shared_file(request: Request) -> HTTPResponse:
    api_key, key, protection = get_args(
        request, 'api_key', 'key', 'protection'
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.get_shared_file(key, protection)
    return json({
        'status_code': status[0],
        'msg': status[1] if status[0] != 0 else [b64encode(status[1][0]).decode('utf-8'), status[1][1], status[1][2]],
    })


@users_api.route('/get_shared_file/raw', methods={'GET', 'POST', 'OPTIONS'})
async def get_shared_file_raw(request: Request) -> HTTPResponse:
    api_key, key, protection = get_args(
        request, 'api_key', 'key', 'protection'
    )
    api_key_status = await request.app.moca_access.check_api_key(api_key, '-NR-', request)
    if api_key_status[0] != 0:
        raise Forbidden(api_key_status[1])
    status = await request.app.moca_users.get_shared_file(key, protection)
    if status[0] == 0:
        return raw(status[1][0])
    else:
        raise NotFound('Not Found.')

# -------------------------------------------------------------------------- Routes --
