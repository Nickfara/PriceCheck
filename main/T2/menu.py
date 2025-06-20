"""
    Создание меню для ТГ бота
"""

import time
import re

from telebot import types
from telebot.apihelper import ApiTelegramException

from handlers_tgBot import bot
from functions import t2b
from log import log
from constants import ADMIN_IDS

ids_messages = {}  # Список ID сообщений
i = 0  # Несколько попыток выдать ошибку, функция error()
cancel_btn = ('❌ Отмена', 'Отмена')

admin_ids = ADMIN_IDS


def escape_markdown_v2(text: str) -> str:
    """
    Экранизирует специальные символы Telegram Markdown V2 в переданном тексте.
    :param text: Обычный текст
    :return: Экранизированный текст
    """

    escape_chars = r'_*[]()~`>#+-=|{}.!'
    result = re.sub(r'(?<!\\)([%s])' % re.escape(escape_chars), r'\\\1', str(text))

    log(f"""

Где-то допущена ошибка markdown в следующем сообщении:
        {text}
        
        Исправь ошибку сравнив с обработанным текстом:
        {result}
        """, 3)

    return result


# noinspection PyBroadException
def send(call, answer: str, btns: tuple, row_width: int = 3, edit_message: int = 1):
    """
    Отправка или редактирование сообщения

    :param edit_message: Статус возможности редактировать сообщение. По умолчанию 1.
    :param row_width: Количество кнопок в строке.
    :param call: Данные о команде или сообщении.
    :param answer: Текст для сообщения.
    :param btns: Кортеж с кнопками(('Текст', 'Команда'), ('Текст', 'Команда')).
    """
    status_edit = True
    status_mark = True
    uid = call.from_user.id
    mid = call.message.message_id

    btns_markup = []

    for lot in btns:  # Распаковка кортежа и создание списка готовых кнопок
        btns_markup.append(types.InlineKeyboardButton(text=lot[0], callback_data=lot[1]))

    markup = types.InlineKeyboardMarkup(row_width=row_width)  # Создание функции кнопок
    markup.add(*btns_markup)  # Наполнение функции кнопками

    for r in range(-8):  # Чистит сообщения вокруг текущего
        try:
            print(r)
            if r != 0: bot.delete_message(chat_id=uid, message_id=(mid + r))
        except:
            pass

    send = lambda: bot.send_message(chat_id=uid, text=answer, reply_markup=markup, parse_mode='MarkdownV2')
    edit = lambda: bot.edit_message_text(chat_id=uid, text=answer, message_id=mid, reply_markup=markup, parse_mode='MarkdownV2')
    send_mark = lambda: bot.send_message(chat_id=uid, text=escape_markdown_v2(answer), reply_markup=markup, parse_mode='MarkdownV2')
    edit_mark = lambda: bot.edit_message_text(chat_id=uid, text=escape_markdown_v2(answer), message_id=mid, reply_markup=markup, parse_mode='MarkdownV2')

    if edit_message:
        try:
            edit()  # Попытка отредактировать сообщение
        except:
            try:
                edit_mark()  # Попытка отредактировать сообщение с фильтром markdown
            except:
                try:
                    send()  # Попытка отправить новое сообщение
                except:
                    try:
                        send_mark()  # Попытка отправить новое сообщение с фильтром markdown
                    except Exception as e:
                        log(f"Не удалось отправить сообщение. Ошибка: {e}", 2)

    else:
        send()



# noinspection PyBroadException
def wait(call):
    """
    Создаёт смайлик с песочными часами, использующийся для ожидания работы бота.

    :param call: Данные о команде или сообщении
    """

    global new_message

    new_message = 1
    answer = '⌛'
    btns = (cancel_btn,)
    response = send(call, answer, btns)

    return response


def error(call, answer: str = 'Необработанная ошибка\!\nПопробуйте ещё раз\.'):
    """

    :param call: Данные о команде или сообщении
    :param answer: Текст с информацией об ошибке. (Не обязательно)
    """

    btns = (('🏠 Главное меню', 'Главное меню'), ('🚪 Выйти из аккаунта', 'Выйти из аккаунта'))

    response = send(call, answer, btns)

    return response


def start(call):
    """
    Отправляет приветствие с просьбой авторизации.

    :param call: Данные о команде или сообщении
    """

    row_width = 2

    if call.from_user.id in admin_ids:
        admin_menu(call)
        return
    else:
        answer = 'Приветствую тебя в магазине \nтрафика Теле2\! В первую очередь \nтебе необходимо авторизоваться\!'

        btns = (('🔑 Войти', 'Войти'),)

    response = send(call, answer, btns, row_width)

    return response


def home(call):
    """
    Отправляет меню с главным экраном.

    :param call: Данные о команде или сообщении
    """
    # raise Exception('Какого хуя до авторизации!')
    row_width = 2
    btns = (
        ('🟢 Запуск', 'Запуск'), ('👤 Мой профиль', 'Профиль'), ('🟢 Поднять', 'Поднять'), ('🛠️ Настройки', 'Настройки'))

    answer = '🏠 *Главное меню\!* \n\nТут можно: \n*1\.* Запустить бота' \
             '\n*2\.* Посмотреть профиль\n*3\.* Изменить настройки\!'
    response = send(call, answer, btns, row_width)
    print(response)

    return response


def help_create(call):
    """
    Отправляет сообщение с подсказками по командам.

    :param call: Данные о команде или сообщении
    """
    answer = """
    ['/start', '/deauth', '/unauthorize'] - Команды выполнят деавторизацию из Т2 аккаунта.
    ['stop', 'exit'] - Полностью остановят работу бота.
    '/send_price' - Запустит приёмник файлов.
    '/help' - Как вы уже заметили, отправляет данное сообщение.
    """
    markup = types.InlineKeyboardMarkup()
    bot.send_message(call.message.chat.id, answer, reply_markup=markup, parse_mode='MarkdownV2')
    return True


def admin_login(call):
    row_width = 2
    uid = call.from_user.id
    from T2.session_manager import get_api
    api = get_api(uid)

    stage_authorize = t2b(uid)['stage_authorize']
    if stage_authorize >= 3:

        lots = api.get_active_lots()
        if lots:
            response = home(call)
        else:
            response = api.refresh_tokens(call)
            if response:
                home(call)
            else:
                answer = 'При дополнительной проверке аутентификации возникла ошибка. Авторизуйтесь по новой!'
                response = send(call, answer, ())
                t2b(uid, type_='d')
                time.sleep(3)
                admin_menu(call)
    else:
        answer = 'Привет Дима\!\n\nУ тебя есть 1 аккаунт\. \nВыбери один из них:'
        btns = (('📲 +7(992)022-88-48', 'Войти админ'), ('🔑 Другой аккаунт', 'Войти'))
        response = send(call, answer, btns, row_width)

    return response


def admin_menu(call, new_message_=0):
    """

    :param call:
    :param new_message_:
    :return:
    """
    row_width = 2
    answer = 'Выберите раздел:'
    btns = (('Маркет Т2', 'МТ2'), ('Ожидание снижения', 'ОСТ'), ('Парсинг такси', 'ПТ'), ('Прайсер', 'ПРС'))
    response = send(call, answer, btns, row_width, edit_message=new_message_)

    return response


def settings(call, answer):
    """
    Отправляет меню настроек.

    :param call: Данные о команде или сообщении.
    :param answer: Принимает сформированные данные и настройках.
    """

    uid = call.from_user.id
    lvl = t2b(uid)['lvl_setting']

    if lvl == 0:
        row_width = 2
        btns = (('🚧 Вид трафика', 'Вид трафика'), ('📏 Количество', 'Количество'), ('🕓 Интервал', 'Интервал'),
                ('🔂 Повторы', 'Повторы'), ('🏠 Главное меню', 'Главное меню'))
    elif 0 < lvl < 4:
        row_width = 1
        btns = (('↩️ Назад', 'Назад'),)
    elif lvl == 4:
        row_width = 2
        btns = (('🌐 Гигабайты', 'Гигабайты'), ('☎️ Минуты', 'Минуты'), ('↩️ Назад', 'Назад'))
    else:
        row_width = 1
        answer = 'Произошла ошибка!'
        log(f'Ошибка в настройках. lvl={lvl}', 3)
        btns = (cancel_btn,)

    response = send(call, answer, btns, row_width)

    return response


def profile(call, answer):
    """
    Отправляет меню профиля.

    :param call: Данные о команде или сообщении.
    :param answer: Принимает сформированные данные о пользователе.
    """

    row_width = 2
    btns = (
        ('🗑️ Мои лоты', 'Редактировать лоты'), ('🚪 Выйти из аккаунта', 'Выйти из аккаунта'),
        ('↩️ Назад', 'Главное меню'))
    response = send(call, answer, btns, row_width)

    return response


def bot_select(call):
    """
    Отправляет меню с выбором типа запуска.

    :param call: Данные о команде или сообщении
    """

    row_width = 2
    btns = (
        ('🏷️ Авто-продажа', 'Авто-продажа'), ('🔝 Авто-поднятие', 'Авто-поднятие'), ('🏠 Главное меню', 'Главное меню'))

    answer = '🟢 *Запуск\.* \n\n*1\. "Авто\-продажа":*  \nАвтоматическая продажа \nтрафика\. По умолчанию: \nЛот \- 6 гигабайт\. \nВыставление \-  1 раз в 35 секунд\.\n\n*2\. "Авто\-поднятие":*\nАвтоматическое поднятие \nактивных лотов в топ\. \nАктивные лоты, это те, \nкоторые уже выставлены \nна продажу\. По умолчанию: \nПоднимается 1 рандомный \nлот, каждые 35 секунд\.'

    response = send(call, str(answer), btns, row_width)

    return response


def bot_active(call, answer, check=False, sell_check=False):
    """
    Отображает сообщение о работе бота, с таймером.

    :param call: Данные о команде или сообщении.
    :param answer: Сформированные данные о настройках и работе бота.
    :param check: При 'True' - добавляется кнопка остановки.
    :param sell_check: При 'True' - выключается редактирование сообщения, и происходит отправка нового сообщения.
    """

    markup = types.InlineKeyboardMarkup()
    btns = (('❌ Остановить', 'Остановить'),)
    item1 = types.InlineKeyboardButton(text='❌ Остановить', callback_data='Остановить')

    if check:
        markup.add(item1)

    if sell_check:
        global new_message
        new_message = 1

    response = send(call, answer, btns)

    return response


def up(call):
    """
    Отправляет сообщение об успехе поднятия лота в топ.

    :param call: Данные о команде или сообщении
    """

    answer = 'Лот был успешно поднят!'
    btns = ()

    send(call, answer, btns)
    time.sleep(3)
    response = home(call)

    return True


def get_lots(call, lots):
    """
    Отправляет меню с активными лотами.

    :param call: Данные о команде или сообщении
    :param lots: Список всех активных лотов
    """

    row_width = 2
    btns = (('🗑 Отозвать все минуты', 'Отозвать минуты'), ('❌ Отмена', 'Профиль'))
    items = []

    if len(lots):
        answer = '*Список ваших, активных лотов:*'
        for lot in lots:
            text = str(lots[lot]['value'])
            text += (' ГБ ' if lots[lot]['type'] == 'gb' else ' МИН ')
            text += f'за {str(int(lots[lot]["price"]))}₽'
            items.append(types.InlineKeyboardButton(text=f'{text}', callback_data=f'red/{lots[lot]["id"]}'))
    else:
        answer = "\n\nЛотов, находящихся на продаже нет\!"

    response = send(call, answer, btns, row_width)

    return response


def login_password(call):
    """
    Отправляет сообщение с просьбой ввести пароль.

    :param call: Данные о команде или сообщении
    """

    answer = 'Введите ваш пароль:'
    btns = (('📩 Войти по СМС', 'СМС'), cancel_btn)
    response = send(call, answer, btns)

    return response


def login_number(call, answer):
    """
    Отправляет сообщение с просьбой ввести номер телефона.

    :param call: Данные о команде или сообщении.
    :param answer: Принимает текст с информацией о действии.
    """

    btns = (cancel_btn,)
    response = send(call, answer, btns)

    return response


def sms(call):
    """
    Отправляет сообщение об успешной отправке СМС с кодом для входа на телефон.

    :param call: Данные о команде или сообщении
    """
    answer = 'Смс было отправлено на ваш телефон\. Пожалуйста, отправьте полученный код сюда\:'

    btns = (cancel_btn,)
    response = send(call, answer, btns)

    return response


def security_code(call):
    """
    Отправляет сообщение об успешной отправке кода подтверждения на почту.

    :param call: Данные о команде или сообщении
    """

    answer = 'На почту был отправлен проверочный код\! Пришлите его сюда:'
    on_sms = ('Войти по смс', 'СМС')
    btns = (cancel_btn, on_sms)
    response = send(call, answer, btns)

    return response


def delete_confirm(call, lid, answer):
    """
    Отправляет подтверждение о снятии лота с продажи.

    :param call: Данные о команде или сообщении.
    :param lid: ID лота.
    :param answer: Сформированный текст для подтверждения удаления.
    """

    row_width = 2
    btns = (('🗑️ Да', f'delconf/{lid}'), ('❌ Нет', 'Редактировать лоты'))
    response = send(call, answer, btns, row_width)

    return response


def redactor_lot(call, lid, lots):
    """
    Выводит меню настроек лота.

    :param call: Данные о команде или сообщении
    :param lid: ID выбранного лота
    :param lots: Список всех активных лотов
    """

    row_width = 2

    lot_text = ''
    ind = {}

    from functions import text_lot

    for lot in lots:
        lot_text = text_lot(lots, lot)
        if lots[lot]['id'] == lid:
            ind[0] = lot
            break

    answer = f'*Настройки лота:* \n\n{lot_text}'
    btns = (('↩️ В топ', 'top'), ('↩️ Смайлики', 'emoji'), ('↩️ Цена', 'price'), ('↩️ Имя', 'name'),
            ('🗑️ Удалить лот', 'del'), ('↩️ Сохранить', 'save'), ('↩️ Назад', 'Редактировать лоты'))

    response = send(call, answer, btns, row_width)

    return response


def emoji(call, lots):
    """

    :param call: Данные о команде или сообщении
    :param lots:
    """

    emoji_cymbol = {'bomb': '💣', 'cat': '😸', 'cool': '😎', 'devil': '😈', 'rich': '🤑', 'scream': '😱',
                    'tongue': '😛', 'zipped': '🤐'}
    emojis = ''
    i_ = 0  # Временная переменная (Тут должен быть цикл какой-то)

    for emoji_text in lots[i_]['emojis']:
        emojis += emoji_cymbol[emoji_text]

    row_width = 2
    btns = (('❌ Отмена', 'Профиль'),)
    answer = ''
    response = send(call, answer, btns, row_width)

    return response


def name(call):
    """
    Отправляет сообщение о том, нужно ли отображать имя или нет.

    :param call: Данные о команде или сообщении
    """

    row_width = 2

    btns = (('Да', 'Имя Да'), ('Нет', 'Имя Нет'), ('❌ Отмена', 'Редактировать лоты'))
    answer = 'Выберите, отображать имя, при продаже трафика или нет\?:'

    response = send(call, answer, btns, row_width)

    return response


# noinspection PyUnusedLocal
def save(call, lid):
    """

    :param call: Данные о команде или сообщении
    :param lid:
    """
    pass


def price(call):
    """
    Отправляет сообщение о том, что нужно написать цену для выбранного лота.
    :param call: Данные о команде или сообщении
    """

    btns = (('❌ Отмена', 'Редактировать лоты'),)
    answer = 'Укажите цену для выбранного лота:'

    response = send(call, answer, btns)

    return response


def remove_minutes_lots_confirm(call):
    """
    Отправляет сообщение с подтверждением отзыва минут.

    :param call: Данные о команде или сообщении
    """
    answer = 'Вы уверены, что хотите отозвать все активные лоты с минутами\?\nОтменить это действие не получится\!'

    row_width = 2
    btns = (('🗑 Подтвердить отзыв', 'Подтверждение отзыва минут'), ('❌ Отмена', 'Редактировать лоты'))

    response = send(call, answer, btns, row_width)

    return response


def remove_minutes_lots(call, answer):
    """
    Отправляет сообщение об удалении минут.

    :param call: Данные о команде или сообщении
    :param answer: Текст с сообщением
    """

    btns = ()
    response = send(call, answer, btns)

    return response
