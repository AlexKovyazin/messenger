import unittest
from client import process_answer, create_presence
from common.variables import RESPONSE, ERROR, ACTION, TIME, USER, ACCOUNT_NAME


class TestClient(unittest.TestCase):
    def setUp(self):
        self.response_400 = {
            RESPONSE: 400,
            ERROR: 'Bad request'
        }
        self.response_200 = {
            RESPONSE: 200
        }

    def test_process_answer_type_200(self):
        self.assertIsInstance(process_answer(self.response_200), str)

    def test_process_answer_type_400(self):
        self.assertIsInstance(process_answer(self.response_400), str)

    def test_process_answer_200(self):
        self.assertEqual(process_answer(self.response_200), '200: OK')

    def test_process_answer_400(self):
        self.assertEqual(process_answer(self.response_400), '400: Bad request')

    def test_create_presence_type(self):
        self.assertIsInstance(create_presence(), dict)

    def test_create_presence_is_ACTION(self):
        self.assertIn(ACTION, create_presence(),
                      f"key {ACTION} is not in presence_message dict")

    def test_create_presence_is_TIME(self):
        self.assertIn(TIME, create_presence(),
                      f"key {TIME} is not in presence_message dict")

    def test_create_presence_is_USER(self):
        self.assertIn(USER, create_presence(),
                      f"key {USER} is not in presence_message dict")

    def test_create_presence_TIME_type(self):
        self.assertIsInstance(create_presence()[TIME], float)

    def test_create_presence_ACCOUNT_NAME_type(self):
        self.assertIsInstance(create_presence()[USER][ACCOUNT_NAME], str)

    def test_create_presence_special_account_name(self):
        self.assertEqual(create_presence(account_name='Ivan')[USER][ACCOUNT_NAME], 'Ivan',
                         "the resulting dictionary account_name is not equal "
                         "to the account_name passed to the function")


if __name__ == '__main__':
    unittest.main()
