def send_ssl_port(login: str, password: str, port: int, cert: str) -> dict:
    "Клиент совершил 'рукопожатие'. Ему нужно отправить актуальные данные"
    return {
        'header': {
            'title': 'send_ssl_port', # название сообщения
            'name': login, # имя кому предназначено
            'surname': password, # фамилия
        },
        'payload' : {
            'ftp_port': port, # номер порта по которому сейчас доступен ftp сервер
            'cert': cert, # публичный сертификат доступа к ftp серверу
        },
        'signature': {
            'update': False # требуются ли клиенту обновления
        }
    }

options = {
    0 : send_ssl_port, # проверка связи с сервером
}