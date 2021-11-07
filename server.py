from socket import socket, AF_INET, SOCK_STREAM
from common.variables import ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from common.utils import get_message, send_message, validate_parameters
import sys


def process_client_message(message: dict):
    """
    Проверяет сообщение пользователя о присутствии и возвращает ответ с кодом

    :param message: dict
    :return: dict
    """
    if message[ACTION] == 'presence' and \
            message[TIME] and \
            message[USER] and \
            message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    else:
        return {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }


def main():
    # Валидация параметров запуска
    listen_port, listen_address = validate_parameters(sys.argv)
    print(listen_port, listen_address)

    # Соединение клиента с сервером
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((listen_address, listen_port))
    server_socket.listen(5)

    while True:
        client_sock, addr = server_socket.accept()
        try:
            client_message = get_message(client_sock)
            print(client_message)

            response = process_client_message(client_message)
            send_message(client_sock, response)

            client_sock.close()
        except ValueError:
            print("Получено некорректное сообщение")
            client_sock.close()


if __name__ == '__main__':
    main()
