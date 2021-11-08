import unittest
import time
import json
from common.utils import get_message, send_message, validate_parameters
from common.variables import ACTION, TIME, ENCODING, DEFAULT_PORT, DEFAULT_IP_ADDRESS


class TestSocket:
    """
    Тестовый класс для тестирования отправки и получения,
    при создании требует словарь, который будет прогонятся
    через тестовую функцию
    """
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        """
        Тестовая функция отправки, корретно  кодирует сообщение,
        так-же сохраняет что должно было отправлено в сокет.
        message_to_send - то, что отправляем в сокет
        :param message_to_send:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        # кодирует сообщение
        self.encoded_message = json_test_message.encode(ENCODING)
        # сохраняем что должно было отправлено в сокет
        self.received_message = message_to_send

    def recv(self, max_len):
        """
        Получаем данные из сокета
        :param max_len:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.message_dict = {
            ACTION: "msg",
            TIME: time.time(),
            "to": "PyMalchik",
            "from": "AlexK",
            "encoding": ENCODING,
            "message": 'Hi there!'
        }
        self.test_socket = TestSocket(self.message_dict)

    def test_get_message(self):
        self.assertIsInstance(get_message(self.test_socket), dict)

        wrong_socket = TestSocket('string')
        self.assertRaises(ValueError, get_message, wrong_socket)

    def test_send_message(self):
        self.assertIs(self.test_socket.received_message, None)

        send_message(self.test_socket, self.message_dict)

        self.assertIsInstance(self.test_socket.received_message, bytes)
        self.assertEqual(self.test_socket.received_message, json.dumps(self.message_dict).encode(ENCODING))

    def test_validate_parameters(self):
        test_parameters = ['-p', '8800', '-a', '127.0.0.50']

        self.assertEqual(validate_parameters(['-p', '8800', '-a', '127.0.0.50'])[0], int(test_parameters[1]))
        self.assertEqual(validate_parameters(['-p', '8800', '-a', '127.0.0.50'])[1], str(test_parameters[3]))

        self.assertEqual(validate_parameters(['-a', '127.0.0.50'])[0], DEFAULT_PORT)
        self.assertEqual(validate_parameters(['-p', '8800'])[1], DEFAULT_IP_ADDRESS)


if __name__ == '__main__':
    unittest.main()
