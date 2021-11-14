from socket import socket, AF_INET, SOCK_STREAM
from common.variables import ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from common.utils import get_message, send_message, validate_parameters
import sys
import logging
import log.server_log_config


s_log = logging.getLogger('server')


def process_client_message(message: dict):
    """
    Проверяет сообщение пользователя о присутствии и возвращает ответ с кодом

    :param message: dict
    :return: dict
    """
    s_log.info('Запущена функция process_client_message()')

    required_keys = {ACTION, TIME, USER}

    if required_keys.issubset(set(message.keys())) and \
            message[ACTION] == 'presence' and \
            ACCOUNT_NAME in message[USER].keys() and \
            message[USER][ACCOUNT_NAME] == 'Guest':

        s_log.info('Проверка пройдена. Сообщение корректно')

        return {RESPONSE: 200}
    else:

        s_log.error('Проверка не пройдена. Сообщение не корректно')

        return {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }


def main():
    s_log.info('Запуск сервера')

    # Валидация параметров запуска
    listen_port, listen_address = validate_parameters(sys.argv)

    # Подготовка к соединению клиента с сервером
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((listen_address, listen_port))
    server_socket.listen(5)

    s_log.info(f'Сервер запущен на хосте {listen_address}, порт {listen_port}')

    while True:
        client_sock, addr = server_socket.accept()

        s_log.info(f'Установлено соединение с клиентом {addr}')
        try:
            client_message = get_message(client_sock)

            response = process_client_message(client_message)
            send_message(client_sock, response)

            s_log.info('Сообщение клиента обработано, отправлен ответ')
            client_sock.close()
        except ValueError:
            s_log.error('ValueError! Получено некорректное сообщение от клиента')
            client_sock.close()


if __name__ == '__main__':
    main()
