from common.variables import ACTION, PRESENCE, TIME, RESPONSE, ERROR, \
    MESSAGE, MESSAGE_TEXT, SENDER, EXIT, RECIPIENT, RESPONSE_200
from common.utils import validate_parameters, send_message, get_message
from socket import socket, AF_INET, SOCK_STREAM
from decos import Log
from exceptions import IncorrectDataReceivedError
import log.client_log_config
import sys
import json
import time
import logging
import threading


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
        return server_answer
    else:
        c_log.error('Сообщение о присутствии принято сервером с ошибкой')
        c_log.error(f'{server_answer}')
        return server_answer


@Log()
def create_presence(username: str):
    """
    Формирует сообщение серверу о присутствии

    :param username: str имя пользователя
    :return: dict сообщение о присутствии
    """
    c_log.info('Запущена функция create_presence()')

    presence_message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        SENDER: username
    }
    c_log.info('Сформировано сообщение о пристуствии')
    return presence_message


@Log()
def create_message(username: str):
    """
    Функция формирования сообщений.
    Запрашивает текст и получателя, возвращает словарь сообщения

    :param username: str имя пользователя
    :return: dict сообщение пользователю
    """
    message_text = input('Введите сообщение для отправки: ')
    recipient = input('Введите username получателя: ')
    c_log.info('Сообщение пользователя принято')

    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        SENDER: username,
        RECIPIENT: recipient,
        MESSAGE_TEXT: message_text
    }
    c_log.info(f'Сообщение пользователя {username} - {message_text} сформировано')
    return message_dict


def create_exit_message(username: str):
    """
    Создает сообщение о выходе клиента

    :param username: str имя пользователя
    :return: dict сообщение серверу о выходе клиента
    """

    message_dict = {
        ACTION: EXIT,
        TIME: time.time(),
        SENDER: username,
    }
    c_log.info(f'Сообщение о выходе пользователя {username} сформировано')
    return message_dict


@Log()
def message_from_server(sock: socket, username):
    """
    Получает сообщения от сервера и выводит их в консоль клиента

    :param sock: socket сокет клиента
    :param username: str имя пользователя
    :return: None
    """

    while True:
        try:
            message = get_message(sock)

            required_keys = {ACTION, SENDER, MESSAGE_TEXT}
            c_log.info('Запущена функция message_from_server()')

            if required_keys.issubset(set(message.keys())):
                if message[ACTION] == MESSAGE and message[RECIPIENT] == username:
                    local_time = time.localtime()
                    print(f'\n{local_time.tm_hour}:{local_time.tm_min} {message[SENDER]}:\n'
                          f'{message[MESSAGE_TEXT]}')
                    c_log.info(f'Получено сообщение от пользователя {message[SENDER]} {time.ctime(message[TIME])}: '
                               f'{message[MESSAGE_TEXT]}')
            else:
                c_log.error(f'Получено некорректное сообщение: {message}')
        except IncorrectDataReceivedError:
            c_log.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            c_log.critical(f'Потеряно соединение с сервером.')
            break


@Log()
def client_interactive(sock: socket, username: str):
    """
    Функция взаимодействия с клиентом

    :param sock: socket сокет клиента
    :param username: str имя пользователя
    :return: None
    """

    print(f'Имя пользователя - {username}')
    print_help()

    while True:
        command = input(f'{username}, введите команду: ')
        c_log.info(f'Клиент {username} ввёл команду "{command}"')

        if command.upper() == 'help'.upper():
            print_help()
        elif command.upper() == 'message'.upper():
            send_message(sock, create_message(username))
            c_log.info(f'Сообщение пользователя {username} отправлено на сервер')
        elif command.upper() == 'exit'.upper():
            send_message(sock, create_exit_message(username))
            time.sleep(0.5)
            c_log.info(f'Клиент {username} завершил работу')
            break
        else:
            print('Команда не распознана!')
            print_help()


@Log()
def print_help():
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Получатель и текст сообщения будут запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


def main():
    c_log.info('Запуск клиента')
    # Валидация параметров запуска и их присвоение переменным
    server_port, server_address, username = validate_parameters(sys.argv)

    # Подключение к серверу и отправка сообщения о присутствии
    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_address, server_port))
    except ConnectionRefusedError:
        c_log.critical('Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
        sys.exit(1)

    c_log.info(f'Установлено соединение с сервером на хосте {server_address}, порт {server_port}')

    # Запрашиваем имя пользователя пока клиент не введёт уникальное значение
    while True:
        if username is None:
            username = input('Введите имя пользователя: ')
        presence_message = create_presence(username)
        send_message(client_socket, presence_message)
        c_log.info('Отправлено сообщение о присутствии')

        # Получение ответа сервера и его проверка
        try:
            answer = process_answer(get_message(client_socket))
            c_log.info(f'Получен ответ от сервера {answer}')

            if answer == RESPONSE_200:
                break
            elif answer[ERROR] == 'invalid username':
                print(f'Имя пользователя {username} занято.')
                username = None
                continue

        except (ValueError, json.JSONDecodeError):
            c_log.error('ValueError! Не удалось декодировать сообщение сервера')

    # Запуск процессов получения сообщений и пользовательского интерфейса
    receiver = threading.Thread(target=message_from_server, args=(client_socket, username,))
    receiver.daemon = True
    receiver.start()

    interface = threading.Thread(target=client_interactive, args=(client_socket, username,))
    interface.daemon = True
    interface.start()
    c_log.info('Процессы запущены')

    # Watchdog основной цикл, если один из потоков завершён,
    # то значит или потеряно соединение или пользователь ввёл exit.
    # Поскольку все события обработываются в потоках,
    # достаточно просто завершить цикл.
    while True:
        time.sleep(1)
        if receiver.is_alive() and interface.is_alive():
            continue
        break


if __name__ == '__main__':
    main()
