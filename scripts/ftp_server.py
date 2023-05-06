from OpenSSL import SSL
from threading import Thread
import os
import ssl
import random
import logging

logging.basicConfig(filename='./static/logs/pyftpd.log', level=logging.DEBUG)

from pyftpdlib.handlers import ThrottledDTPHandler, TLS_FTPHandler
from pyftpdlib.servers import ThreadedFTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.filesystems import UnixFilesystem

CERTFILE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "../.ssl/public.crt"))

KEYFILE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "../.ssl/private.key"))

class MyHandler(TLS_FTPHandler):

    def on_connect(self):
        print(f"IP: {self.remote_ip} PORT: {self.remote_port} connected")

    def on_disconnect(self):
        # do something when client disconnects
        print(f"IP: {self.remote_ip} PORT: {self.remote_port} disconnected")
        print('---')

    def on_login(self, username):
        # do something when user login
        print(f"'{username}' loging")

    def on_logout(self, username):
        # do something when user logs out
        print(f"'{username}' logout")

    def on_file_sent(self, file):
        # do something when a file has been sent
        pass

    def on_file_received(self, file):
        # do something when a file has been received
        pass

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        pass

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        import os
        os.remove(file)

def start_listen_for_user(login: str, password: str, port: int):
    "Запуск ftp cервера для пользователя. Открытие случайного порта"
    print('[INFO]: ftp_server.py: start_listen_for_user()')
    authorizer = DummyAuthorizer()
    authorizer.add_user(login, password, homedir='./ftp', perm='elradfmwMT')
    print(f'[DEBUG]: login = {login}, password = {password}')

    ftps_handler = MyHandler
    ftps_handler.tls_control_required = True
    ftps_handler.tls_data_required = True
    ftps_handler.certfile = CERTFILE  # Указываем путь к сертификату сервера
    ftps_handler.keyfile = KEYFILE # Указываем путь к приватному ключу сервера
    ftps_handler.passive_ports = range(40000, 50000)
    ftps_handler.authorizer = authorizer

    ftp_server = ThreadedFTPServer(('', port), ftps_handler)
    print(f'[DEBUG]: Started ThreadedFTPServer by port: {port}')
    ### Отдельным потоком принимаем входящую информацию
    server_forever_thread = Thread(target = ftp_server.serve_forever, daemon = True, name = 'server_forever_thread')
    server_forever_thread.start()
    ###
    