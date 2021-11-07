from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from common.utils import validate_parameters, send_message, get_message
from socket import socket, AF_INET, SOCK_STREAM
import sys
import json
import time


def process_answer(server_answer: dict):
    """
    Обрабатывает ответ сервера на отправленное сообщение о присутствии
    и возвращает строку с кодом

    :param server_answer: dict
    :return: str
    """
    if server_answer[RESPONSE] == 200:
        return '200: OK'
    else:
        return f'{server_answer[RESPONSE]}: {server_answer[ERROR]}'


def create_presence(account_name='Guest'):
    """
    Формирует сообщение серверу о присутствии

    :param account_name: str
    :return: dict
    """
    presence_message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return presence_message


def main():
    # Валидация параметров запуска
    server_port, server_address = validate_parameters(sys.argv)
    print(server_port, server_address)

    # Подключение к серверу и отправка сообщения о присутствии
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_address, server_port))
    presence_message = create_presence()
    send_message(client_socket, presence_message)

    # Получение ответа сервера
    try:
        answer = process_answer(get_message(client_socket))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера')


if __name__ == '__main__':
    main()
