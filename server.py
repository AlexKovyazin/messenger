from common.variables import ACTION, TIME, ERROR, MAX_CONNECTIONS, PRESENCE, MESSAGE, \
    SENDER, RECIPIENT, RESPONSE_200, RESPONSE_400, EXIT
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import get_message, send_message, validate_parameters
from decos import Log
from exceptions import ClientLostConnection
import log.server_log_config
import sys
import logging
import select


s_log = logging.getLogger('server')


@Log()
def process_client_message(message: dict, messages_list: list, client_socket: socket,
                           clients_list: list, names: dict):
    """
    Обрабатывает сообщения клиентов

    :param message: dict сообщение клиента
    :param messages_list: list список сообщений на отправку
    :param client_socket: socket сокет клиента
    :param clients_list: list список подключенных клиентов
    :param names: dict словарь {username: socket,}
    :return:
    """
    s_log.info('Запущена функция process_client_message()')

    required_keys = {ACTION, TIME, SENDER}

    if required_keys.issubset(set(message.keys())):
        if message[ACTION] == PRESENCE:
            if message[SENDER] not in names.keys():
                names[message[SENDER]] = client_socket
                s_log.info('Проверка пройдена. Сообщение корректно')
                send_message(client_socket, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'invalid username'
                s_log.warning(f'Имя пользователя {message[SENDER]} занято')
                send_message(client_socket, response)

            return

        if message[ACTION] == MESSAGE:
            if message[SENDER] in names and message[RECIPIENT] in names:
                messages_list.append(message)
                s_log.info('Сообщение добавлено в список на отправку')
            else:
                response = RESPONSE_400
                response[ERROR] = 'Отправитель или получатель не зарегестрированы'
                send_message(client_socket, response)
            return

        if message[ACTION] == EXIT:
            clients_list.remove(client_socket)
            names[message[SENDER]].close()
            del names[message[SENDER]]
            s_log.info(f'Клиент {message[SENDER]} вышел')
            return

    else:
        s_log.error('Проверка не пройдена. Сообщение не корректно')
        return RESPONSE_400


@Log()
def process_message_to_send(message: dict, names: dict, listen_socks: list):
    """
    Обработка отправляемого сообщения

    :param message: dict сообщение клиента
    :param names: dict словарь {username: socket,}
    :param listen_socks: list список подключенных сокетов
    :return:
    """
    s_log.debug(f'{type(message)}')
    if message[RECIPIENT] in names.keys() and names[message[RECIPIENT]] in listen_socks:

        send_message(names[message[RECIPIENT]], message)
        s_log.info(f'Сообщение клиента {message[SENDER]} отправлено клиенту {message[RECIPIENT]}')
    elif message[RECIPIENT] in names and names[message[RECIPIENT]] not in listen_socks:
        raise ConnectionError
    else:
        s_log.error(
            f'Пользователь {message[RECIPIENT]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


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
    names = {}  # {username: socket}

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
                receive_data_list, send_data_list, error_list = \
                    select.select(clients_list, clients_list, error_list, 0)
        except OSError:
            pass

        # Принимаем сообщения клиентов. Если там есть сообщения со статусом MESSAGE -
        # добавляем их в messages_list через функцию process_client_message()
        if receive_data_list:
            for client_message_sock in receive_data_list:
                try:
                    process_client_message(get_message(client_message_sock), messages_list,
                                           client_message_sock, clients_list, names)
                except ClientLostConnection:
                    s_log.info(f'Клиент {client_message_sock.getpeername()} отключился от сервера')
                    clients_list.remove(client_message_sock)

        # Если есть сообщения ожидающие отправки, и клиенты ожидающие получения, отправляем сообщения
        for message in messages_list:
            s_log.debug(f'message - {message}')
            try:
                process_message_to_send(message, names, send_data_list)
                s_log.debug('Вызвана функция process_message_to_send')
            except ClientLostConnection:
                s_log.info(f'Клиент {message[RECIPIENT]} отключился от сервера')
                clients_list.remove(names[message[RECIPIENT]])
                del names[message[RECIPIENT]]
        messages_list.clear()


if __name__ == '__main__':
    main()
