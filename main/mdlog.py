import inspect


def log(text):
    try:
        file = ''.join(str(inspect.stack()[1][0]).split(',')[1].split('\\')[-1].split("'"))
        file = f'[{file}]'
        try:
            func = inspect.currentframe().f_back.f_code.co_name
        except:
            func = ''
        line = inspect.currentframe().f_back.f_lineno
        func = f'[{func}]'
        print(f'[{line}]|{file}|{func}: {text}')
    except:
        print(text)
