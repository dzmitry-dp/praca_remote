#!/bin/python
import socketserver
import hashlib
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from purpose import options
from ftp_server import start_listen_for_user


LOCALHOST = ''
PORT = 1489
FTP_PORT = 1488

def hash_raw(input_str: str, _salt: int) -> bytes: # input_str = ip, salt = port
    "Возвращаю байты хеша"
    salt = hex(_salt)
    input_str = input_str.replace(' ', '').replace('.', '')
    mix_variable = salt.encode() + input_str.encode()
    hash_from_ip_port: str = hashlib.sha1(mix_variable).hexdigest()
    return hash_from_ip_port.encode('utf-8')[:32]
    
class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class EventsHandler(socketserver.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_ip = None
        self.client_port = None

    def select_reaction(self, decode_data) -> json:
        "Выбираю реакцию сервера на входные данные"
        login = decode_data['signature']['name']
        password = decode_data['signature']['surname']

        if decode_data['header']['title'] == '': #
            return ''
        elif decode_data['header']['title'] == 'get_handshake': # если проверка связи / рукопожатие
            try:
                # свободен ли порт
                # если свободен, то создаем сервер
                # запустить ftp_server
                start_listen_for_user(login, password)
            except OSError:
                # если порт не свободен, то добавляем пользователя
                # добавляем пользователя в список пользователей
                print('New user')
            msg_purpose = 0 # рукопожатие произошло / проверка связи с сервером выполнена / отправляю порт где будет проходить обмен данными
            cert = self._get_public_key()
            return json.dumps(options[msg_purpose](login, password, FTP_PORT, cert))

    def _get_public_key(self) -> str:
        with open('./.ssl/cert.pem') as file:
            file_data = file.read()
        return file_data

    def handle(self):
        # ожидаю зашифрованные данные
        encrypted_data = self.request.recv(4096).strip()

        self.client_ip = self.client_address[0]
        self.client_port = self.client_address[1]
        # вычисляю ключ
        key: bytes = hash_raw(self.client_ip, PORT)

        # Расшифровываем данные
        cipher = AES.new(key, AES.MODE_CBC, b'\x00'*16)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        decode_data: dict = json.loads(decrypted_data.decode('utf-8'))

        print(f'Address: {self.client_address}')
        print(f'Key: {key}')
        print(f'Decoded Data: {decode_data}')
        print(f'Decoded Data Type: {type(decode_data)}')

        # выбираю реакцию на входящие данные от сервера
        if not decode_data:
            reaction = '' # клиент закрывает соединение
        else:
            reaction: json = self.select_reaction(decode_data)

        print(f'Send Reaction: {reaction}')

        # Зашифровываем данные
        cipher = AES.new(key, AES.MODE_CBC, b'\x00'*16)
        json_data = json.dumps(reaction)
        padded_data = pad(json_data.encode('utf-8'), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)

        self.request.sendall(encrypted_data)

        print('---')


if __name__ == '__main__':
    print('---')
    with ThreadingTCPServer((LOCALHOST, PORT), EventsHandler) as server:
        server.serve_forever()
