#!/bin/python
import socketserver
import hashlib
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


LOCALHOST = ''
PORT = 1489

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

    def handle(self):
        encrypted_data = self.request.recv(4096).strip()
        
        self.client_ip = self.client_address[0]
        self.client_port = self.client_address[1]

        key: bytes = hash_raw(self.client_ip, PORT)

        # Создаем объект расшифрования
        cipher = AES.new(key, AES.MODE_CBC, key[:16])
        # Расшифровываем данные
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        # Преобразуем расшифрованные данные в JSON
        decode_data = json.loads(decrypted_data.decode('utf-8'))

        print(f'Address: {self.client_address}')
        print(f'Key: {key}')
        print(f'Encripted Data: {encrypted_data}')
        print(f'Decoded Data: {decode_data}')

        msg = 'Hi'
        self.request.sendall(bytes(msg, 'UTF-8'))

        # self.request.sendall(bytes(msg, 'UTF-8'))
        
        # # Открываем файл на сервере
        # with open('file.txt', 'rb') as file:
        #     # Читаем содержимое файла
        #     file_data = file.read()
        #     # Отправляем содержимое файла клиенту
        #     self.request.sendall(file_data)


if __name__ == '__main__':
    with ThreadingTCPServer((LOCALHOST, PORT), EventsHandler) as server:
        server.serve_forever()
