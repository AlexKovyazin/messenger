import logging.handlers
import os


PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'logs', 'client.log')

filename = os.getcwd() + r'\logs\server_log.txt'

formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

handler = logging.FileHandler(PATH, encoding='utf-8')
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

log = logging.getLogger('client')
log.setLevel(logging.DEBUG)
log.addHandler(handler)


if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    log.addHandler(console)

    log.info('Test start')
