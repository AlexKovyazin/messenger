from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from common.utils import validate_parameters, send_message, get_message
from socket import socket, AF_INET, SOCK_STREAM
import sys
import json
import time
import logging
import log.client_log_config
from decos import Log


c_log = logging.getLogger('client')


@Log()
def process_answer(server_answer: dict):
    """
    Обрабатывает ответ сервера на отправленное сообщение о присутствии
    и возвращает строку с кодом

    :param server_answer: dict
    :return: str
    """
    c_log.info('Запущена функция process_answer()')

    if server_answer[RESPONSE] == 200:
        c_log.info('Сообщение о пристутсвии принято сервером без ошибок')
        return '200: OK'
    else:
        c_log.error('Сообщение о присутствии принято сервером с ошибкой ')
        return f'{server_answer[RESPONSE]}: {server_answer[ERROR]}'


@Log()
def create_presence(account_name='Guest'):
    """
    Формирует сообщение серверу о присутствии

    :param account_name: str
    :return: dict
    """
    c_log.info('Запущена функция create_presence()')

    presence_message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    c_log.info('Сформировано сообщение о пристуствии')
    return presence_message


def main():
    c_log.info('Запуск клиента')

    # Валидация параметров запуска
    server_port, server_address = validate_parameters(sys.argv)

    # Подключение к серверу и отправка сообщения о присутствии
    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_address, server_port))
    except ConnectionRefusedError:
        c_log.critical('Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
        sys.exit(1)

    c_log.info(f'Установлено соединение с сервером на хосте {server_address}, порт {server_port}')

    presence_message = create_presence()
    send_message(client_socket, presence_message)

    c_log.info('Отправлено сообщение о присутствии')

    # Получение ответа сервера
    try:
        answer = process_answer(get_message(client_socket))
        c_log.info(f'Получен ответ от сервера {answer}')
    except (ValueError, json.JSONDecodeError):
        c_log.error('ValueError! Не удалось декодировать сообщение сервера')


if __name__ == '__main__':
    main()
