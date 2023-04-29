def send_ssl_port(login: str, password: str, port: int) -> dict:
    "Возвращаю словарь запроса на сервер. Проверка соединения"
    return {
        'header': {
            'title': 'send_ssl_port',
        },
        'payload' : {
            'port': port,
        },
        'signature': {
            'name': login,
            'surname': password,
        }
    }

options = {
    0 : send_ssl_port, # проверка связи с сервером
}