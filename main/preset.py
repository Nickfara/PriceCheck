"""
Пресеты с функциями

"""

import json


def text_lot(lots, i):
    """
    Генерация текста для сообщения с данными о лоте.

    :param lots: Список всех лотов.
    :param i: Вероятно id нужного лота
    :return: Готовый текст
    """

    emoji_symbol = {'bomb': '💣', 'cat': '😸', 'cool': '😎', 'devil': '😈', 'rich': '🤑', 'scream': '😱', 'tongue': '😛',
                    'zipped': '🤐'}

    date_time_str = lots[i]['creationDate'].split('+')[0]
    date = date_time_str.split('T')[0]
    date = date.split('-')
    months = ['янв\.', 'фев\.', 'мар\.', 'апр\.', 'мая', 'июня',
              'июля', 'авг\.', 'сен\.', 'окт\.', 'ноя\.', 'дек\.']
    date = f'{date[2]} {months[int(date[1]) - 1]}'
    time_str = date_time_str.split('T')[1].split('.')[0].split(':')
    time_str = time_str[0] + ':' + time_str[1]
    emojis = ''
    for emoji_text in lots[i]['emojis']:
        print(emoji_text)
        emojis += emoji_symbol[emoji_text]
    cymbal_emoji = emojis if emojis != '' else 'пусто\!'
    answer = f'_{str(lots[i]["value"])}_' + (
        '_ГБ_ ' if lots[i]['type'] == 'gb' else (' минут\(ы\) ' if lots[i]['type'] == 'min' else ' ед\.')) + \
             f'за _{str(int(lots[i]["price"]))}₽_'
    answer += f"\n\n*Эмодзи:* {cymbal_emoji}"
    answer += f'\n*Имя:* {lots[i]["name"] if lots[i]["name"] is not None else "Анонимно"}'
    answer += f"\n*Создан:* {date} {time_str}"
    answer += '\n*Статус:* ' + ('В топе ⬆️' if lots[i]['status'] else 'В жопе ⬇️')
    return answer


# noinspection PyTypeChecker
def t2b(uid, data: dict = True, type_='g'):
    """
    Обработчик базы пользователей

    :param uid: ID пользователя (Обязательно)
    :param data: Словарь с данными пользователя (При типе 'u')
    :param type_: Тип действия: ('g'- получить [default], 'u' - обновить, 'd' - сброс)
    :return: Набор данных о пользователе (При типе 'g')
    """
    uid = str(uid)
    default = {'auth_login': '', 'auth_password': '', 'status_run_auto': 0, 'status_lagg': 0,
               'status_sms': 0, 'stage_authorize': 0, 'lvl_setting': 0, 'lvl_redactor': 0,
               'security_code': '', 'security_code_token': '', "config_count": 6, "config_autotime": 35,
               "config_uom": "gb", "config_repeat": 20, "config_price": 90, "config_type": "data"}

    with open(f'data/t2b.json') as f:
        if type_ == 'u':
            file = json.load(f)
            for i in data:
                file[uid][i] = data[i]
            with open(f'data/t2b.json', 'w') as f2:
                json.dump(file, f2)
        elif type_ == 'g':
            file = json.load(f)
            if uid in file:
                return file[uid]
            else:
                file[uid] = default

                with open('data/t2b.json', 'w') as f2:
                    json.dump(file, f2)
                    return file[uid]
        elif type_ == 'd':
            file = json.load(f)
            if uid in file:
                file[uid] = default
                with open(f'data/t2b.json', 'w') as f2:
                    json.dump(file, f2)
