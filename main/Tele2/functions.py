from log import log

def text_lot(lots, i):
    emoji_cymbol = {'bomb': '💣', 'cat': '😸', 'cool': '😎', 'devil': '😈', 'rich': '🤑', 'scream': '😱', 'tongue': '😛',
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
        emojis += emoji_cymbol[emoji_text]
    cymbal_emoji = emojis if emojis != '' else 'пусто\!'
    answer = f'_{str(lots[i]["value"])}_' + (
        '_ГБ_ ' if lots[i]['type'] == 'gb' else (' минут\(ы\) ' if lots[i]['type'] == 'min' else ' ед\.')) + \
             f'за _{str(int(lots[i]["price"]))}₽_'
    answer += f"\n\n*Эмодзи:* {cymbal_emoji}"
    answer += f'\n*Имя:* {lots[i]["name"] if lots[i]["name"] != None else "Аниномно"}'
    answer += f"\n*Создан:* {date} {time_str}"
    answer += '\n*Статус:* ' + ('В топе ⬆️' if lots[i]['status'] else 'В жопе ⬇️')
    return answer
