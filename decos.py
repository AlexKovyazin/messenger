import os
import sys
import inspect
import logging.handlers
from functools import wraps

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


class Log:
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(self.path, 'logs', 'decorated.log')

    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)

            LOGGER.info(f'из функции {inspect.stack()[1][3]}\t'
                        f'вызвана функция {func.__name__}()\t'
                        f'модуля {func.__module__}\t'
                        f'c параметрами {args}, {kwargs}\t',
                        stacklevel=2)

            return result

        return decorated
