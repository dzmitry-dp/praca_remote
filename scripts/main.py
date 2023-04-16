import socket, threading

LOCALHOST = "159.223.25.102"
PORT = 1489

class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        print ("Новое подключение: ", client_address)

    def run(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                msg = data.decode('utf-8')
                print(f"Сообщение: {msg}")

                if msg == '':
                    print("Отключение клиента")
                    self.client_socket.shutdown(socket.SHUT_WR)
                    break
            except ConnectionResetError:
                break
        
if __name__ == '__main__':
    print('Start script')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LOCALHOST, PORT))
    print("Сервер запущен!")
    while True:
        print('Start "while"')
        try:
            server.listen(1)
            client_sock, client_address = server.accept()
            newthread = ClientThread(client_sock, client_address)
            newthread.start()
        except KeyboardInterrupt:
            print("\nОтключение сервера")
            server.close()
            break
    print('\nEnd')