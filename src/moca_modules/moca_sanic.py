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

from typing import *
from pathlib import Path
from sanic import Sanic, Blueprint
from sanic.server import HttpProtocol
from sanic.response import HTTPResponse, text, json as original_json
from functools import partial
from sanic.request import Request
from logging import INFO
from sanic.log import logger, LOGGING_CONFIG_DEFAULTS
from sanic.exceptions import Forbidden, InvalidUsage
from sanic.websocket import WebSocketProtocol
from ssl import SSLContext, Purpose, create_default_context
from uuid import uuid4
from socket import AF_INET6, SOCK_STREAM, socket
from .moca_variables import CPU_COUNT, tz, LICENSE, FLAGS_PATH
from .moca_utils import print_warning, print_info
from multiprocessing import current_process
from datetime import datetime
from time import time
from .moca_base_class import MocaNamedInstance, MocaClassCache

try:
    from ujson import dumps as dumps_
    json_dumps = partial(dumps_, ensure_ascii=False)
except (ImportError, ModuleNotFoundError):
    from json import dumps as dumps_

    # This is done in order to ensure that the JSON response is
    # kept consistent across both ujson and inbuilt json usage.
    json_dumps = partial(dumps_, separators=(",", ":"), ensure_ascii=False)

# -------------------------------------------------------------------------- Imports --

# -- Private Functions --------------------------------------------------------------------------


def json(body, status=200, headers=None, content_type="application/json", dumps=json_dumps, **kwargs):
    return original_json(body, status=200, headers=None,
                         content_type="application/json", dumps=json_dumps, ensure_ascii=False, **kwargs)

# -------------------------------------------------------------------------- Private Variables --

# -- Moca Sanic --------------------------------------------------------------------------


class MocaSanic(MocaNamedInstance, MocaClassCache):
    """
    Sanic: Async Python 3.6+ web server/framework | Build fast. Run fast. https://sanicframework.org/

    Attributes
    ----------
    self._name: str
        the name of this server.
    self._host: str
        the host address.
    self._port: int
        the port number.
    self._ssl: Optional[SSLContext]
        ssl context for this server.
    self._access_log: bool
        the access log flag.
    self._ipv6: bool
        the ipv6 flag.
    self._workers: int
        the workers number.
    self._internal_key: str
        the internal key
    self._app: Sanic
        the sanic application
    self._blueprint_list: List[Blueprint]
        all blueprint in this list will be added to the app.
    self._middleware_list: List[Tuple[str, Callable]]
        all middleware in this list will be added to the app.
    self._pid: Optional[int]
        the process id of the main process.
    self._headers: dict
        the response headers.
    """

    VERSION: str = '1.0.0'

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
        MocaClassCache.__init__(self)
        MocaNamedInstance.__init__(self, name)
        # setup logging
        if log_dir is not None:
            self._setup_logging(name, Path(log_dir))
        # set name
        self._name: str = name
        # set host
        self._host: str = host
        # set port
        self._port: int = port
        # set ssl
        self._ssl: Optional[SSLContext] = ssl
        # set access log flag
        self._access_log: bool = access_log
        # set ipv6 flag
        self._ipv6: bool = use_ipv6
        # set workers number
        self._workers: int = workers if workers != 0 else CPU_COUNT
        # set headers
        self._headers: dict = headers
        # set internal key
        self._internal_key: str
        if internal_key_file is None:
            self._internal_key = ''
        elif Path(internal_key_file).is_file():
            with open(str(internal_key_file), mode='r', encoding='utf-8') as file:
                self._internal_key = file.read()
        else:
            self._internal_key = self.create_internal_key_file(internal_key_file)
        # set blueprint list
        self._blueprint_list: List[Blueprint] = []
        # set middleware list
        self._middleware_list: List[Tuple[str, Callable]] = []
        # set application
        self._app: Sanic = Sanic(name)
        # set pid
        self._pid: Optional[int] = current_process().pid

    @property
    def name(self) -> str:
        return self._name

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def ssl(self) -> Optional[SSLContext]:
        return self._ssl

    @property
    def access_log(self) -> bool:
        return self._access_log

    @property
    def ipv6(self) -> bool:
        return self._ipv6

    @property
    def workers(self) -> int:
        return self._workers

    @property
    def app(self) -> Sanic:
        return self._app

    @property
    def blueprint_list(self) -> List[Blueprint]:
        return self._blueprint_list

    @property
    def middleware_list(self) -> List[Tuple[str, Callable]]:
        return self._middleware_list

    @property
    def headers(self) -> dict:
        return self._headers

    def add_response_header(self, key: str, value: str) -> None:
        """Add a response header."""
        self._headers[key] = value

    @staticmethod
    def _setup_logging(server_name: str, log_dir: Path) -> None:
        """
        Setup logging for sanic application.
        This function must be called before instantiate the Sanic App.
        """
        logger.setLevel(INFO)
        LOGGING_CONFIG_DEFAULTS['handlers']['root_file'] = {
            'class': 'logging.FileHandler',
            'formatter': 'generic',
            'filename': str(log_dir.joinpath(server_name).joinpath('root.log'))
        }
        LOGGING_CONFIG_DEFAULTS['handlers']['error_file'] = {
            'class': 'logging.FileHandler',
            'formatter': 'generic',
            'filename': str(log_dir.joinpath(server_name).joinpath('error.log'))
        }
        LOGGING_CONFIG_DEFAULTS['handlers']['access_file'] = {
            'class': 'logging.FileHandler',
            'formatter': 'access',
            'filename': str(log_dir.joinpath(server_name).joinpath('access.log'))
        }
        LOGGING_CONFIG_DEFAULTS['loggers']['sanic.root']['handlers'][0] = 'root_file'
        LOGGING_CONFIG_DEFAULTS['loggers']['sanic.error']['handlers'][0] = 'error_file'
        LOGGING_CONFIG_DEFAULTS['loggers']['sanic.access']['handlers'][0] = 'access_file'
        log_dir.joinpath(server_name).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def create_ssl_context(cert: str, key: str) -> SSLContext:
        """Create a SSLContext."""
        ssl_context = create_default_context(Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile=cert, keyfile=key)
        return ssl_context

    @staticmethod
    def create_internal_key_file(path: Union[str, Path]) -> str:
        """Create a random key file."""
        key = ''.join([uuid4().hex for _ in range(32)])
        with open(str(path), mode='w', encoding='utf-8') as file:
            file.write(key)
        return key

    @staticmethod
    def get_remote_address(request: Request) -> str:
        """Get remote address"""
        return request.remote_addr if request.remote_addr != '' else request.ip

    @staticmethod
    def _get_param(json_data: dict, request: Request, key: str, type_: Any = None, default: Any = None):
        data = json_data.get(key,
                             request.args.get(key,
                                              request.form.get(key,
                                                               request.headers.get(key.upper().replace('_', '-'),
                                                                                   request.files.get(key)))))
        if type_ is None:
            return data
        elif type(data) is type_:
            return data
        elif type(data) is str and type_ is int:
            try:
                return int(data)
            except (ValueError, TypeError):
                return default
        else:
            return default

    @staticmethod
    def get_args(request: Request, *args) -> Tuple:
        """Get arguments."""
        try:
            json_data = request.json if isinstance(request.json, dict) else {}
        except InvalidUsage:
            json_data = {}
        return tuple([MocaSanic._get_param(json_data, request, key) if isinstance(key, str) else
                      MocaSanic._get_param(json_data, request, key[0], key[1]) if len(key) == 2 else
                      MocaSanic._get_param(json_data, request, key[0], key[1], key[2]) for key in args])

    @staticmethod
    def start_debug_mode() -> None:
        """Start debug mode."""
        with open(str(FLAGS_PATH.joinpath('.sanic_debug')), mode="w") as file:
            file.write('いあ！いあ！めんだこちゃん！ふたぐん！')

    @staticmethod
    def stop_debug_mode() -> None:
        """Stop debug mode."""
        FLAGS_PATH.joinpath('.sanic_debug').unlink(missing_ok=True)

    @staticmethod
    def _is_debug_mode() -> bool:
        return FLAGS_PATH.joinpath('.sanic_debug').is_file()

    def _init_app(self) -> None:
        """Initialize the sanic application."""
        # ------ Version ------
        @self._app.route('/version', methods={'GET', 'POST', 'OPTIONS'})
        async def version(request: Request) -> HTTPResponse:
            return text(MocaSanic.VERSION)

        # ------ License ------
        @self._app.route('/license', methods={'GET', 'POST', 'OPTIONS'})
        async def show_license(request: Request) -> HTTPResponse:
            return text(LICENSE)

        # ------ Mochi ------
        @self._app.route('/mochi', methods={'GET', 'POST', 'OPTIONS'})
        async def mochi(request: Request) -> HTTPResponse:
            return text('もっちもっちにゃんにゃん')

        # ------ 10086 ------
        @self._app.route('/10086', methods={'GET', 'POST', 'OPTIONS'})
        async def tushan(request: Request) -> HTTPResponse:
            return text('雁过拔毛，兽走留皮。')

        # ------ Ping ------
        @self._app.route('/ping', methods={'GET', 'POST', 'OPTIONS'})
        async def ping(request: Request) -> HTTPResponse:
            return text('success')

        # ------ DateTime ------
        @self._app.route('/datetime', methods={'GET', 'POST', 'OPTIONS'})
        async def date_time(request: Request) -> HTTPResponse:
            return text(str(datetime.now(tz=tz)))

        # ------ Epoch ------
        @self._app.route('/epoch', methods={'GET', 'POST', 'OPTIONS'})
        async def get_seconds_since_epoch(request: Request) -> HTTPResponse:
            return text(str(time()))

        # ------ Echo ------
        @self._app.route('/echo', methods={'GET', 'POST', 'OPTIONS'})
        async def echo(request: Request) -> HTTPResponse:
            try:
                json_data = request.json if isinstance(request.json, dict) else {}
            except InvalidUsage:
                json_data = {}
            message = str(json_data.get('message', request.args.get(
                'message', request.form.get('message'))))
            if len(message) >= 1000:
                raise Forbidden('message is too long.')
            else:
                return text(message)

        # ------ Request ------
        @self._app.route('/check-request', methods={'GET', 'POST', 'OPTIONS'})
        async def check_request(request: Request) -> HTTPResponse:
            data = {
                'ip': request.ip,
                'headers': dict(request.headers),
                'json': request.json,
                'form': request.form,
                'files': request.files,
                'token': request.token,
                'cookies': request.cookies,
                'port': request.port,
                'socket': request.socket,
                'server_name': request.server_name,
                'forwarded': request.forwarded,
                'server_port': request.server_port,
                'remote_addr': request.remote_addr,
                'scheme': request.scheme,
                'host': request.host,
                'content_type': request.content_type,
                'match_info': request.match_info,
                'path': request.path,
                'query_string': request.query_string,
                'url': request.url,
            }
            return json(data)

        # ------ Status ------
        @self._app.route('/status', methods={'GET', 'POST', 'OPTIONS'})
        async def status(request: Request) -> HTTPResponse:
            return text(f'{self._name} is working...')

        # ------ Check internal key ------
        if self._internal_key != '':
            @self._app.middleware('request')
            async def check_internal_key(request: Request):
                if request.headers.get('Moca-Internal-Key') != self._internal_key:
                    raise Forbidden('Invalid internal key.')

        # ------ Set response headers ------
        @self._app.middleware('response')
        async def set_response_headers(request: Request, response: HTTPResponse):
            response.headers.update(self._headers)

        # ------ Set debug middleware ------
        if self._is_debug_mode():
            @self._app.middleware('request')
            async def before(request: Request):
                try:
                    json_data = request.json if isinstance(request.json, dict) else {}
                except InvalidUsage:
                    json_data = {}
                print()
                print('-- Receive a request -------------------------')
                print('-- url --')
                print(request.url)
                print('-- ip --')
                print(request.ip)
                print('-- json --')
                print(json_data)
                print('-- args --')
                print(request.args)
                print('-- form --')
                print(request.form)
                print('-- header --')
                print(request.headers)
                print('------------------------- Receive a request --')
                print()

            @self._app.middleware('response')
            async def after(request: Request, response: HTTPResponse):
                print()
                print('-- The response -------------------------')
                print('-- status --')
                print(response.status)
                print('-- body --')
                print(response.body)
                print('-- headers --')
                print(response.headers)
                print('-- content type --')
                print(response.content_type)
                print('------------------------- The response --')
                print()

        for blueprint in self._blueprint_list:
            self.app.blueprint(blueprint)

        for middleware_type, middleware in self._middleware_list:
            self._app.register_middleware(middleware, middleware_type)

        self._app.register_listener(self.before_server_start, 'before_server_start')
        self._app.register_listener(self.after_server_start, 'after_server_start')
        self._app.register_listener(self.before_server_stop, 'before_server_stop')
        self._app.register_listener(self.after_server_stop, 'after_server_stop')

    def add_blueprint(self, blueprint: Blueprint) -> None:
        """Add a blueprint."""
        self._blueprint_list.append(blueprint)

    def add_middleware(self, middleware: Callable, middleware_type: str) -> None:
        """Add a middleware"""
        self._middleware_list.append((middleware_type, middleware))

    def static(self, uri: str, directory: Union[str, Path]) -> None:
        """Set a static directory for sanic server."""
        self._app.static(uri, str(directory))

    @staticmethod
    async def before_server_start(app: Sanic, loop):
        pass

    @staticmethod
    async def after_server_start(app: Sanic, loop):
        pass

    @staticmethod
    async def before_server_stop(app: Sanic, loop):
        pass

    @staticmethod
    async def after_server_stop(app: Sanic, loop):
        pass

    def run_server(self, websocket: bool = False):
        """Run Sanic server."""
        self._init_app()
        try:
            if self._is_debug_mode():
                print_info('Running MocaSanic module on debug mode.')
            if self._ipv6:
                sock = socket(AF_INET6, SOCK_STREAM)
                sock.bind((self._host, self._port))
                self._app.run(sock=sock,
                              access_log=self._access_log,
                              ssl=self._ssl,
                              debug=True if self._is_debug_mode() else False,
                              workers=self._workers,
                              protocol=HttpProtocol if not websocket else WebSocketProtocol)
            else:
                self._app.run(host=self._host,
                              port=self._port,
                              access_log=self._access_log,
                              ssl=self._ssl,
                              debug=True if self._is_debug_mode() else False,
                              workers=self._workers,
                              protocol=HttpProtocol if not websocket else WebSocketProtocol)
        except OSError as os_error:
            print_warning(f'Sanic Http Server stopped. Please check your port is usable. <OSError: {os_error}>')
        except Exception as other_error:
            print_warning(f'Sanic Http Server stopped, unknown error occurred. <Exception: {other_error}>')
        finally:
            if self._ipv6:
                sock.close()

# -------------------------------------------------------------------------- Moca Sanic --

# -- Utilities --------------------------------------------------------------------------


def get_remote_address(request: Request) -> str:
    return MocaSanic.get_remote_address(request)


def get_args(request: Request, *args) -> Tuple:
    return MocaSanic.get_args(request, *args)


def start_debug_mode() -> None:
    MocaSanic.start_debug_mode()


def stop_debug_mode() -> None:
    MocaSanic.stop_debug_mode()

# -------------------------------------------------------------------------- Utilities --
