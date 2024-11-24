import inspect


def log(text):

    file = ''.join(str(inspect.stack()[1][0]).split(',')[1].split('\\')[-1].split("'"))
    file = f'[{file}]'
    func = inspect.currentframe().f_back.f_code.co_name
    line = inspect.currentframe().f_back.f_lineno
    func = f'[{func}]'
    if func == '<module>':
        func = ''
    print(f'[{line}]|{file}|{func}: {text}')
