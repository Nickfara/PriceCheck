"""
    Модуль логирования
"""
import inspect
import logging

CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0

lvl_log = INFO

for log_name in ("TeleBot", "asyncio", "requests", "urllib3", "websocket"):
    logging.getLogger(log_name).setLevel(lvl_log)

def log(text, lvl: int = 1):
    """
    Функция логирования проекта.

    :param text: Текст выводимый в консоль.
    :param lvl: Тип лога: 1 - простой текст. 2 - исключение. 3 - ошибка.
    """

    text = str(text)

    if lvl_log > 0:
        if lvl == 1 and lvl_log <= 20:
            text = f'✅ \033[1m{text}\033[0m'
        elif lvl == 2 and lvl_log <= 50:
            file = ''.join(str(inspect.stack()[1][0]).split(',')[1].split('\\')[-1].split("'"))
            file = f'[{file}]'
            func = inspect.currentframe().f_back.f_code.co_name
            line = inspect.currentframe().f_back.f_lineno
            func = f'[{func}]'

            if func == '<module>':
                func = ''

            text = f'\033[31m\033[1m[ИСКЛЮЧЕНИЕ] — [{file}]|{func}|{line}: {text}\033[0m'
        elif lvl == 3 and lvl_log <= 40:
            file = ''.join(str(inspect.stack()[1][0]).split(',')[1].split('\\')[-1].split("'"))
            file = f'[{file}]'
            func = inspect.currentframe().f_back.f_code.co_name
            line = inspect.currentframe().f_back.f_lineno
            func = f'[{func}]'

            if func == '<module>':
                func = ''

            text = f'\033[31m\033[1m[ОШИБКА] — {file}|{func}: \033[0m{text}\033[0m'
        elif lvl == 3 and lvl_log <= 10:
            text = f'\033[1m[ОТЛАДКА]: {text}\033[0m'
        else:
            return
        print(text)


