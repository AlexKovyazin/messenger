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

    def test_process_answer(self):
        self.assertIsInstance(process_answer(self.response_200), str)
        self.assertIsInstance(process_answer(self.response_400), str)

        self.assertEqual(process_answer(self.response_200), '200: OK')
        self.assertEqual(process_answer(self.response_400), '400: Bad request')

    def test_create_presence(self):
        self.assertIsInstance(create_presence(), dict)

        self.assertIn(ACTION, create_presence(),
                      f"key {ACTION} is not in presence_message dict")
        self.assertIn(TIME, create_presence(),
                      f"key {TIME} is not in presence_message dict")
        self.assertIn(USER, create_presence(),
                      f"key {USER} is not in presence_message dict")

        self.assertIsInstance(create_presence()[TIME], float)
        self.assertIsInstance(create_presence()[USER][ACCOUNT_NAME], str)

        self.assertEqual(create_presence(account_name='Ivan')[USER][ACCOUNT_NAME], 'Ivan',
                         "the resulting dictionary account_name is not equal "
                         "to the account_name passed to the function")


if __name__ == '__main__':
    unittest.main()
