def send_ssl_port(login: str, password: str, port: int) -> dict:
    "Возвращаю словарь запроса на сервер. Проверка соединения"
    return {
        'header': {
            'title': 'send_ssl_port',
            'name': login,
            'surname': password,
        },
        'payload' : {
            'port': port,
            'file': '/home/dp/Personal/Projects/Praca/praca_remote/.ssl/cert.pem'
        },
        'signature': {
        }
    }

options = {
    0 : send_ssl_port, # проверка связи с сервером
}