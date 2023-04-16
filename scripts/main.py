import socket, threading

LOCALHOST = "159.223.25.102"
PORT = 1488

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((LOCALHOST, PORT))
print("Сервер запущен!")

class ClientThread(threading.Thread):
    def __init__(self,clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("Новое подключение: ", clientAddress)

    def run(self):
        print ("Подключение с клиента : ", clientAddress)

        msg = ''
        while True:
            data = self.csocket.recv(4096)
            msg = data.decode()
            print(f'Сообщение: {msg}')
  
            if msg == '':
                print("Отключение")
                break


if __name__ == '__main__':
    print('Start script')
    while True:
        print('Start "while"')
        server.listen(1)
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()
    print('End')