from Tele2 import base
from Tele2 import functions
from telebot import types
from log import log

base_u = base.update_users
base_g = base.get_user
cache_messages_ids = {}
check_sell_lot_save = [0]  # Переменная, которая выключает изменение сообщений
i = 0  # Переменная для нескольких попыток выдать ошибку функция error()


def reload(call, bot, answer, markup):
    uid = call.from_user.id

    if uid not in cache_messages_ids:
        cache_messages_ids[uid] = []
    if call.message.message_id not in cache_messages_ids[uid]:
        cache_messages_ids[uid].insert(0, call.message.message_id)
    if len(cache_messages_ids[uid]) > 5:
        cache_messages_ids[uid].pop(5)

    a1 = int(call.message.message_id)

    if check_sell_lot_save[0] == 0:
        for i in cache_messages_ids[uid]:
            if a1 < int(i):
                check_sell_lot_save[0] = 1
            else:
                check_sell_lot_save[0] = 0

    i = 0

    for message_id in range(1, 4):
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id - message_id))
        except:
            pass
    for message_id in range(1, 3):
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=(call.message.message_id + message_id))
        except:
            pass

    try:
        if check_sell_lot_save[0] == 0:

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=answer, reply_markup=markup, parse_mode='MarkdownV2')
        else:
            check_sell_lot_save[0] = 0
            log('Лот якобы продан! Или не якобы!)', 3)
            a = 0 / 'asd'  # Вызыва исключение, что бы сработало создание нового меню! При успешной продаже лота.
    except Exception as e:
        try:
            bot.send_message(call.message.chat.id, answer, reply_markup=markup, parse_mode='MarkdownV2')
            log('Создалось новое меню!', 1)
            log('Причина:')
            log(e, 2)
        except Exception as e:
            log('МЕНЮ ВООБЩЕ НЕ СОЗДАЛОСЬ!', 2)
            log('Причина:')
            log(e, 2)
            if i < 3:
                error(call, bot)
                i += 1
            else:
                i = 0


def wait(call, bot):
    answer = '⌛'
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='❌ Отмена', callback_data='Отмена')
    markup.add(item1)
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=answer, reply_markup=markup, parse_mode='MarkdownV2')
    except:
        pass


def error(call, bot, answer='Произошла ошибка\!\nПопробуйте ещё раз\.'):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='🏠 Главное меню', callback_data='Главное меню')
    item2 = types.InlineKeyboardButton(text='🚪 Выйти из аккаунта', callback_data='Выйти из аккаунта')
    markup.add(item1, item2)
    reload(call, bot, answer, markup)


def start(message, bot):
    markup = types.InlineKeyboardMarkup(row_width=2)
    print(message.from_user.id)
    if message.from_user.id in (828853360, 6890309136):
        answer = 'Привет Дима\!\n\nУ тебя есть 3 аккаунта\. \nВыбери один из них:'
        item1 = types.InlineKeyboardButton(text='📲 +7(992)022-88-48', callback_data='Войти1')
        item2 = types.InlineKeyboardButton(text='🔑 Другой аккаунт', callback_data='Войти')
        markup.add(item1, item2)
    else:
        answer = 'Приветствую тебя в магазине \nтрафика Теле2\! В первую очередь \nтебе необходимо авторизоваться\!'
        item1 = types.InlineKeyboardButton(text='🔑 Войти', callback_data='Войти')
        markup.add(item1)

    class call(object):
        def __init__(self):
            self.message = message  # либо call.message
            self.data = message.text
            self.from_user = message.from_user
            self.id = message.message_id

    call = call()
    reload(call, bot, answer, markup)


def home(call, bot):
    uid = call.from_user.id
    if base_g(uid)['lvl_autorize'] == 3:
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton(text='🟢 Запуск', callback_data='Запуск')
        item2 = types.InlineKeyboardButton(text='👤 Мой профиль', callback_data='Профиль')
        item3 = types.InlineKeyboardButton(text='🛠️ Настройки', callback_data='Настройки')
        markup.add(item1, item2, item3)
        answer = '🏠 *Главное меню\!* \n\nТут можно: \n*1\.* Запустить бота' \
                 '\n*2\.* Посмотреть профиль\n*3\.* Изменить настройки\!'
        reload(call, bot, answer, markup)


def bot_launch(call, bot):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton(text='🏷️ Авто-продажа', callback_data='Авто-продажа', row_width=2)
    item2 = types.InlineKeyboardButton(text='🔝 Авто-поднятие', callback_data='Авто-поднятие', row_width=2)
    item3 = types.InlineKeyboardButton(text='🏠 Главное меню', callback_data='Главное меню', row_width=1)
    markup.add(item1, item2, item3)
    answer = '🟢 *Запуск\.* \n\n*1\. "Авто\-продажа":*  \nАвтоматическая продажа \nтрафика\. По умолчанию: ' \
             '\nЛот \- 6 гигабайт\. \nВыставление \-  1 раз в 35 секунд\.\n\n*2\. "Авто\-поднятие":*' \
             '\nАвтоматическое поднятие \nактивных лотов в топ\. \nАктивные лоты, это те, \nкоторые ' \
             'уже выставлены \nна продажу\. По умолчанию: \nПоднимается 1 рандомный \nлот каждые 35 секунд\.',
    reload(call, bot, answer, markup)


def login_password(call, bot, answer):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='📩 Войти по СМС', callback_data='СМС')
    item2 = types.InlineKeyboardButton(text='❌ Отмена', callback_data='Отмена')
    markup.add(item1, item2)
    reload(call, bot, answer, markup)


def login_number(call, bot, answer):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='❌ Отмена', callback_data='Отмена')
    markup.add(item1)
    reload(call, bot, answer, markup)


def sms(call, bot):
    answer = 'Смс было отправлено на ваш телефон\. Пожалуйста, отправьте полученный код сюда\:'
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='❌ Отмена', callback_data='Отмена')
    markup.add(item1)
    reload(call, bot, answer, markup)


def security_code(call, bot, answer):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='❌ Отмена', callback_data='Отмена')
    markup.add(item1)
    reload(call, bot, answer, markup)


def bot_launch_on(call, bot, answer, check, sell_check):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='❌ Остановить', callback_data='Остановить')
    if check:
        markup.add(item1)
    if sell_check:
        check_sell_lot_save[0] = 1
    reload(call, bot, answer, markup)


def settings(call, bot, answer):
    uid = call.from_user.id
    lvl = base_g(uid)['lvl_setting']
    if lvl == 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton(text='🚧 Вид трафика', callback_data='Вид трафика')
        item2 = types.InlineKeyboardButton(text='📏 Количество', callback_data='Количество')
        item3 = types.InlineKeyboardButton(text='🕓 Интервал', callback_data='Интервал')
        item4 = types.InlineKeyboardButton(text='🔂 Повторы', callback_data='Повторы')
        item5 = types.InlineKeyboardButton(text='🏠 Главное меню', callback_data='Главное меню')
        markup.add(item1, item2, item3, item4, item5)
        reload(call, bot, answer, markup)
    elif lvl == 1 or lvl == 2 or lvl == 3:
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton(text='↩️ Назад', callback_data='Назад')
        markup.add(item1)
        reload(call, bot, answer, markup)
    elif lvl == 4:
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton(text='🌐 Гигабайты', callback_data='Гигабайты')
        item2 = types.InlineKeyboardButton(text='☎️ Минуты', callback_data='Минуты')
        item3 = types.InlineKeyboardButton(text='↩️ Назад', callback_data='Назад')
        markup.add(item1, item2, item3)
        reload(call, bot, answer, markup)
    else:
        log(f'Ошибка в натройках. lvl={lvl}', 3)


def profile(call, bot, answer):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton(text='🗑️ Мои лоты', callback_data='Редактировать лоты')
    item2 = types.InlineKeyboardButton(text='🚪 Выйти из аккаунта', callback_data='Выйти из аккаунта')
    item3 = types.InlineKeyboardButton(text='↩️ Назад', callback_data='Главное меню')
    markup.add(item1, item2, item3)
    reload(call, bot, answer, markup)


def delete_confrim(call, bot, lid, lots):
    lot_text = ''
    for i in lots:
        lot_text = f'_{str(lots[i]["value"])}_' + (
            '_ГБ_ ' if lots[i]['type'] == 'gigabyte' else ' минуты ') + \
                   f'за _{str(int(lots[i]["price"]))}₽_'
        if lots[i]['id'] == lid:
            break
    markup = types.InlineKeyboardMarkup(row_width=2)
    answer = f'Вы действительно хотите снять лот: {lot_text} с продажи\?'
    item1 = types.InlineKeyboardButton(text='🗑️ Да', callback_data=f'delconf/{lid}')
    item2 = types.InlineKeyboardButton(text='❌ Нет', callback_data='Редактировать лоты')
    markup.add(item1, item2)
    reload(call, bot, answer, markup)


def edit_lots(call, bot, lots):
    markup = types.InlineKeyboardMarkup(row_width=2)
    items = []
    if len(lots):
        answer = '*Список ваших, активных лотов:*'
        for i in lots:
            text = str(lots[i]['value'])
            text += (' ГБ ' if lots[i]['type'] == 'gb' else ' МИН ')
            text += f'за {str(int(lots[i]["price"]))}₽'
            items.append(types.InlineKeyboardButton(text=f'{text}', callback_data=f'red/{lots[i]["id"]}'))
    else:
        answer = "\n\nЛотов, находящихся на продаже нет\!"
    back_lots = types.InlineKeyboardButton(text='🗑 Отозвать все минуты', callback_data='Отозвать минуты')
    cancel = types.InlineKeyboardButton(text='❌ Отмена', callback_data='Профиль')
    markup.add(*items)
    markup.add(back_lots)
    markup.add(cancel)
    reload(call, bot, answer, markup)


def redactor_lot(call, bot, lid, lots):
    markup = types.InlineKeyboardMarkup(row_width=2)
    lot_text = ''
    ind = {}
    for i in lots:
        lot_text = functions.text_lot(lots, i)
        if lots[i]['id'] == lid:
            ind[0] = i
            break
    answer = f'*Настройки лота:* \n\n{lot_text}'
    item1 = types.InlineKeyboardButton(text='↩️ В топ', callback_data='top}')
    item2 = types.InlineKeyboardButton(text='↩️ Смайлики', callback_data='emoji')
    item3 = types.InlineKeyboardButton(text='↩️ Цена', callback_data='price')
    item4 = types.InlineKeyboardButton(text='↩️ Имя', callback_data='name')
    item5 = types.InlineKeyboardButton(text='🗑️ Удалить лот', callback_data='del')
    item6 = types.InlineKeyboardButton(text='↩️ Сохранить', callback_data='save')
    item7 = types.InlineKeyboardButton(text='↩️ Назад', callback_data='Редактировать лоты')
    markup.add(item1, item2, item3, item4, item5, item6, item7)
    reload(call, bot, answer, markup)


def emoji(call, bot, lots):
    emoji_cymbol = {'bomb': '💣', 'cat': '😸', 'cool': '😎', 'devil': '😈', 'rich': '🤑', 'scream': '😱',
                    'tongue': '😛', 'zipped': '🤐'}
    emojis = ''
    i = 0  # Временная переменная (Тут должен быть цикл какой-то)
    for emoji_text in lots[i]['emojis']:
        emojis += emoji_cymbol[emoji_text]
    cymbal_emoji = emojis if emojis != '' else 'Пусто\!'

    markup = types.InlineKeyboardMarkup(row_width=2)
    items = []
    cancel = types.InlineKeyboardButton(text='❌ Отмена', callback_data='Профиль')
    markup.add(cancel)
    answer = ''
    reload(call, bot, answer, markup)


def name(call, bot):
    markup = types.InlineKeyboardMarkup(row_width=2)
    answer = 'Выберите, отображать имя, при продаже трафика или нет\?:'
    item1 = types.InlineKeyboardButton(text='Да', callback_data='Имя Да')
    item2 = types.InlineKeyboardButton(text='Нет', callback_data='Имя Нет')
    item3 = types.InlineKeyboardButton(text='❌ Отмена', callback_data='Редактировать лоты')
    markup.add(item1, item2, item3)
    reload(call, bot, answer, markup)


def save(call, bot, lid):
    pass


def price(call, bot):
    markup = types.InlineKeyboardMarkup()
    answer = 'Укажите цену для выбранного лота:'
    item1 = types.InlineKeyboardButton(text='❌ Отмена', callback_data='Редактировать лоты')
    markup.add(item1)
    reload(call, bot, answer, markup)


def remove_minutes_lots_confrim(call, bot, answer):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton(text='🗑 '
                                            'Отозвать все минуты', callback_data='Подтверждение отзывания минут')
    item2 = types.InlineKeyboardButton(text='❌ Отмена', callback_data='Редактировать лоты')
    markup.add(item1, item2)
    reload(call, bot, answer, markup)


def remove_minutes_lots(call, bot, answer):
    markup = types.InlineKeyboardMarkup(row_width=2)
    reload(call, bot, answer, markup)

