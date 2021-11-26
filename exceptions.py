class ClientLostConnection(Exception):
    """Исключение вызванное отключением клиента от сервера в процессе работы"""
    def __str__(self):
        return 'Клиент отключился от сервера в процессе работы'


class IncorrectDataReceivedError(Exception):
    """Исключение вызванное неверным форматом полученных данных"""
    def __str__(self):
        return 'Принято некорректное сообщение'
