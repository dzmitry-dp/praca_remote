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
        self.key = None
        self.client_ip = None
        self.client_port = None

    def _select_reaction(self, decode_data) -> json:
        "Выбираю реакцию сервера на входные данные"

        if decode_data == {}: # не удалось декодировать сообщение
            reaction = None
        elif decode_data['header']['title'] == 'get_handshake': # если проверка связи / рукопожатие
            login = decode_data['signature']['name']
            password = decode_data['signature']['surname']
            try:
                # свободен ли порт
                # если свободен, то создаем сервер
                start_listen_for_user(login, password, FTP_PORT)
                print(f'Port {FTP_PORT} is free')
            except OSError:
                # если порт не свободен, то его уже прослушивает скрипт
                print(f'The port: {FTP_PORT} is already occupied')
            msg_purpose = 0 # рукопожатие произошло / проверка связи с сервером выполнена / отправляю порт где будет проходить обмен данными
            cert = self._get_public_key()
            reaction = json.dumps(options[msg_purpose](login, password, FTP_PORT, cert))
        
        print(f'Send Reaction: {reaction}')
        return reaction

    def _get_public_key(self) -> str:
        with open('./.ssl/public.crt') as file:
            file_data = file.read()
        return file_data

    def _decrypt_input_msg(self, encrypted_data) -> json:
        # вычисляю ключ
        self.key: bytes = hash_raw(self.client_ip, PORT)
        # Расшифровываем данные
        cipher = AES.new(self.key, AES.MODE_CBC, b'\x00'*16)
        try:
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            decode_data: dict = json.loads(decrypted_data.decode('utf-8'))
        except ValueError:
            print('Failed to decode the message')
            return {}

        print(f'Key: {self.key}')
        print(f'Decoded Data: {decode_data}')

        return decode_data

    def _encrypt_output_msg(self, reaction) -> bytes:
        # Зашифровываем данные
        cipher = AES.new(self.key, AES.MODE_CBC, b'\x00'*16)
        json_data = json.dumps(reaction)
        padded_data = pad(json_data.encode('utf-8'), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        return encrypted_data

    def handle(self):
        # ожидаю зашифрованные данные
        input_data = self.request.recv(4096).strip()

        print(f'Address: {self.client_address}')
        self.client_ip = self.client_address[0]
        self.client_port = self.client_address[1]

        # декодирую входящее сооющение
        decode_data = self._decrypt_input_msg(input_data)
        # выбираю реакцию на входящие данные от сервера
        reaction: json = self._select_reaction(decode_data)
        
        if reaction != None:
            # кодирую ответ
            encrypted_data = self._encrypt_output_msg(reaction)
            # отправляю клиенту закодированное сообщение
            self.request.sendall(encrypted_data)

        print('---')

if __name__ == '__main__':
    print('---')
    with ThreadingTCPServer((LOCALHOST, PORT), EventsHandler) as server:
        server.serve_forever()
