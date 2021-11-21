class WrongMode(Exception):
    """
    Исключение вызванное несоответствием режима запуска клиента допустимым значениям 'send'/'listen'
    """
    pass


class ClientLostConnection(Exception):
    """
    Исключение вызванное отключением клиента от сервера в процессе работы
    """
    pass
