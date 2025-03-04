import inspect


def log(text: str, type: int = 1):
    if type == 1:
        text = f'\033[32m\033[1m{text}\033[0m'
    elif type == 2:
        file = ''.join(str(inspect.stack()[1][0]).split(',')[1].split('\\')[-1].split("'"))
        file = f'[{file}]'
        func = inspect.currentframe().f_back.f_code.co_name
        line = inspect.currentframe().f_back.f_lineno
        func = f'[{func}]'

        if func == '<module>':
            func = ''

        text = f'\033[31m\033[1m[Исключение] - [{line}]|{file}|{func}: {text}\033[0m'
    elif type == 3:
        text = f'\033[31m\033[1m[Ошибка] {text}\033[0m'

    print(text)
