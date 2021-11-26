"""Лаунчер"""

import subprocess

PROCESS = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESS.append(subprocess.Popen('python server.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE, encoding='cp437'))
        PROCESS.append(subprocess.Popen('python client.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE, encoding='cp437'))
        PROCESS.append(subprocess.Popen('python client.py -n ken',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE, encoding='cp437'))
        PROCESS.append(subprocess.Popen('python client.py -n django',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE, encoding='cp437'))
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
