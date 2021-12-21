import json
from .variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ENCODING, MAX_PACKAGE_LENGTH
from socket import socket
import sys
import inspect
from decos import Log


@Log()
def get_message(sock: socket):
    """
    Декодирует и возвращает объект из сокета

    :param sock: socket сокет клиента
    :return: dict словарь сообщения из сокета
    (принято, что сервер и клиент обмениваются только словарями)
    """
    message = sock.recv(MAX_PACKAGE_LENGTH)
    message.decode(ENCODING)
    dict_message = json.loads(message)
    if isinstance(dict_message, dict):
        return dict_message
    else:
        raise ValueError


@Log()
def send_message(sock: socket, message: dict):
    """
    Переводит словарь в байты, записывает в указанный сокет

    :param sock: socket сокет клиента
    :param message: dict сообщение клиента
    """
    json_str = json.dumps(message)
    sock.send(json_str.encode(ENCODING))


@Log()
def validate_parameters(parameters: list):
    """
    Валидирует переданные параметры запуска скрипта из sys.argv,
    возвращает кортеж, где
    первый элемент - номер порта (int),
    второй элемент - адрес хоста (str),
    третий элемент - имя пользователя (str)

    :param parameters: list параметры запуска скрипта
    :return: tuple(port, address, mode,)
    """
    path = inspect.stack()[2][1]
    filename = path.split('/')[-1]

    try:
        if filename == 'client.py':
            if '-n' in parameters:
                username = parameters[parameters.index('-n') + 1]
            else:
                username = None
        else:
            username = None

    except IndexError:
        print("После параметра '-n' необходимо указать имя пользователя")
        sys.exit(1)

    try:
        if '-p' in parameters:
            port = int(parameters[parameters.index('-p') + 1])
        else:
            port = DEFAULT_PORT

        if port < 1024 or port > 65535:
            raise ValueError

    except IndexError:
        print("После параметра '-p' необходимо указать номер порта")
        sys.exit(1)
    except ValueError:
        print("Номер порта должен находиться в диапазоне от 1024 до 65535")
        sys.exit(1)

    try:
        if '-a' in parameters:
            address = str(parameters[parameters.index('-a') + 1])
        else:
            address = DEFAULT_IP_ADDRESS

    except IndexError:
        print("После параметра '-a' необходимо указать IP адрес, с которым будет работать сервер")
        sys.exit(1)

    return port, address, username
