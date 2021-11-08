import unittest
import time
from server import process_client_message
from common.variables import RESPONSE, ERROR, ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE


class TestServer(unittest.TestCase):
    def setUp(self):
        self.correct_client_dict = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }
        # not correct value for key ACTION
        self.not_correct_client_dict_1 = {
            ACTION: 'not presence',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }
        # TIME key missing
        self.not_correct_client_dict_2 = {
            ACTION: PRESENCE,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }
        # USER key missing
        self.not_correct_client_dict_3 = {
            ACTION: PRESENCE,
            TIME: time.time()
        }
        # ACCOUNT_NAME is not equal to 'Guest'
        self.not_correct_client_dict_4 = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Ivan'
            }
        }

    def test_process_client_message(self):
        self.assertIsInstance(process_client_message(self.correct_client_dict), dict)
        self.assertIsInstance(process_client_message(self.not_correct_client_dict_1), dict)

        self.assertEqual(process_client_message(self.correct_client_dict), {RESPONSE: 200})
        self.assertEqual(process_client_message(self.not_correct_client_dict_1), {RESPONSE: 400, ERROR: 'Bad request'})
        self.assertEqual(process_client_message(self.not_correct_client_dict_2), {RESPONSE: 400, ERROR: 'Bad request'})
        self.assertEqual(process_client_message(self.not_correct_client_dict_3), {RESPONSE: 400, ERROR: 'Bad request'})
        self.assertEqual(process_client_message(self.not_correct_client_dict_4), {RESPONSE: 400, ERROR: 'Bad request'})


if __name__ == '__main__':
    unittest.main()
