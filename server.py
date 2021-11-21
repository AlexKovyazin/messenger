from socket import socket, AF_INET, SOCK_STREAM
from common.variables import ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    ERROR, MAX_CONNECTIONS, PRESENCE, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message, validate_parameters
import sys
import logging
import select
import time
import log.server_log_config
from decos import Log
from exceptions import ClientLostConnection


s_log = logging.getLogger('server')


@Log()
def process_client_message(message: dict, messages_list: list, client_socket: socket):
    """
    Проверяет сообщение пользователя о присутствии и возвращает ответ с кодом

    :param client_socket: socket
    :param messages_list: list
    :param message: dict
    :return: dict
    """
    s_log.info('Запущена функция process_client_message()')

    required_keys = {ACTION, TIME, USER}

    if required_keys.issubset(set(message.keys())) and \
            message[ACTION] == PRESENCE and \
            ACCOUNT_NAME in message[USER].keys() and \
            message[USER][ACCOUNT_NAME] == 'Guest':
        s_log.info('Проверка пройдена. Сообщение корректно')
        send_message(client_socket, {RESPONSE: 200})
        return

    elif required_keys.issubset(set(message.keys())) and \
            message[ACTION] == MESSAGE and \
            ACCOUNT_NAME in message[USER].keys():
        s_log.info('Сообщение добавлено в список на отправку')
        messages_list.append((message[USER][ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return

    else:
        s_log.error('Проверка не пройдена. Сообщение не корректно')
        return {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }


def main():
    s_log.info('Запуск сервера')

    # Валидация параметров запуска
    parameters = validate_parameters(sys.argv)
    listen_port = parameters[0]
    listen_address = parameters[1]

    # Подготовка к соединению клиента с сервером
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((listen_address, listen_port))
    server_socket.settimeout(0.5)

    # Список клиентов, очередь сообщений
    clients_list = []
    messages_list = []

    # Ожидаем клиентов
    server_socket.listen(MAX_CONNECTIONS)
    s_log.info(f'Сервер запущен на хосте {listen_address}, порт {listen_port}')

    # Принимаем клиентов, добавляем в список
    while True:
        try:
            client_sock, addr = server_socket.accept()
            clients_list.append(client_sock)
            s_log.info(f'Установлено соединение с клиентом {addr}')
        except OSError:
            pass

        # Создаем списки для функции select()
        receive_data_list = []
        send_data_list = []
        error_list = []

        try:
            if clients_list:
                receive_data_list, send_data_list, error_list = select.select(clients_list, clients_list, error_list, 0)
        except OSError:
            pass

        # Принимаем сообщения клиентов. Если там есть сообщения о статусом MESSAGE -
        # добавляем их в messages_list через функцию process_client_message()
        if receive_data_list:
            for client_message_sock in receive_data_list:
                try:
                    process_client_message(get_message(client_message_sock), messages_list, client_message_sock)
                except ClientLostConnection:
                    s_log.info(f'Клиент {client_message_sock.getpeername()} отключился от сервера')
                    clients_list.remove(client_message_sock)

        # Если есть сообщения ожидающие отправки, и клиенты ожидающие получения, отправляем сообщения
        if messages_list and send_data_list:
            message = {
                ACTION: MESSAGE,
                SENDER: messages_list[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages_list[0][1]
            }
            del messages_list[0]

            for waiting_client in send_data_list:
                try:
                    send_message(waiting_client, message)
                except ClientLostConnection:
                    s_log.info(f'Клиент {waiting_client.getpeername()} отключился от сервера')
                    clients_list.remove(waiting_client)


if __name__ == '__main__':
    main()
