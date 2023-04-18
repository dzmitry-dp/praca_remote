import socket
from threading import Thread


IP = "77.222.236.173"
PORT = 1489

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def forever_listen_server():
    while True:
        try:
            print('Ожидаю сообщений')
            in_data =  client.recv(4096)
            msg = in_data.decode('utf-8')

            if msg != '':
                print("Принято от сервера :" , msg)
            else:
                print("Принято от сервера :" , msg)
                print("Отключение клиента с msg = ''")
                client.close()
                break
        except ConnectionAbortedError:
            print("\nОтключение клиента ConnectionAbortedError")
            client.close()
            break

def send_to_server(data: str):
    client.sendall(bytes(data, 'UTF-8'))
    print("Отпаравлено :", data)

def connect_to_server():
    try:
        client.connect((IP, PORT))
    except ConnectionRefusedError:
        print("Подключение не установлено")
        return False
    else:
        # поток для входящей информации
        input_thread = Thread(target=forever_listen_server)
        input_thread.start()
        # input_thread.join()
        return True

if __name__ == '__main__':
    print('Start')
    if connect_to_server():
        # Поток для исходящей информации
        output_thread = Thread(target=send_to_server, args=['Pss ... I am here',])
        output_thread.start()
        output_thread.join()
    
    print('End')
