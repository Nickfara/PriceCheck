"""
    Модуль логирования
"""
import inspect

def log(text, lvl: int = 1):
    """
    Функция логирования проекта.

    :param text: Текст выводимый в консоль.
    :param lvl: Тип лога: 1 - простой текст. 2 - исключение. 3 - ошибка.
    """
    text = str(text)
    if lvl == 1:
        text = f'\033[32m\033[1m{text}\033[0m'
    elif lvl == 2:
        file = ''.join(str(inspect.stack()[1][0]).split(',')[1].split('\\')[-1].split("'"))
        file = f'[{file}]'
        func = inspect.currentframe().f_back.f_code.co_name
        line = inspect.currentframe().f_back.f_lineno
        func = f'[{func}]'

        if func == '<module>':
            func = ''

        text = f'\033[31m\033[1m[Исключение] - [{line}]|{file}|{func}: {text}\033[0m'
    elif lvl == 3:
        text = f'\033[31m\033[1m[Ошибка] {text}\033[0m'

    print(text)
