token = '6890309136:AAGUjpef47Q4r3YOFBZCnFgPUxMRCJpX4YE'

import telebot
from Tele2 import commands
from Tele2 import menu
from telebot import types

bot = telebot.TeleBot(token)

from Tele2 import base
from log import log

base_u = base.update_users
base_g = base.get_user


def call_class(message):
    class call(object):
        def __init__(self):
            self.message = message  # либо call.message
            self.data = message.text
            self.from_user = message.from_user
            self.id = message.message_id

    return call()


@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    DB = base_g(uid)
    call = call_class(message)
    commands.deauth(call, bot, True)


@bot.message_handler(commands=['stop', 'exit'])
def exit(message):
    bot.stop_polling()
    from commands import active_bot
    print(active_bot)
    active_bot[2] = False

    try:
        bot.send_message(message.chat.id, 'Бот выключен!')
    except:
        bot.send_message('828853360', 'Бот выключен!')


def auth(call):
    menu.wait(call, bot)
    uid = call.from_user.id
    DB = base_g(uid)
    response = commands.auth(call, bot)
    if response is not None:
        base_u({'id': uid, 'lvl_autorize': 3})
        menu.home(call, bot)


def deauth(call):
    menu.wait(call, bot)
    uid = call.from_user.id
    commands.deauth(call, bot, True)
    base_u({'id': uid, 'lvl_autorize': 0})


def autosell(call):
    menu.wait(call, bot)
    commands.autosell(call, bot)


def autotop(call):
    menu.wait(call, bot)
    commands.autotop(call, bot)


def stop(call):
    menu.wait(call, bot)
    uid = call.from_user.id
    DB = base_g(uid)
    commands.stop(call, bot)
    menu.home(call, bot)


def help_command(call):
    pass


def settings(call):
    menu.wait(call, bot)
    uid = call.from_user.id
    DB = base_g(uid)
    item1 = types.InlineKeyboardButton(text='↩️ Назад', callback_data='Назад')
    response = commands.settings(call, bot)
    if response is not None:
        answer = 'Сохранено\!'
        commands.update_def_traffic(call)
        base_u({'id': uid, 'lvl_setting': 0})
        menu.home(call, bot)


@bot.message_handler(content_types='text')
def text(message):
    try:
        uid = message.from_user.id
        DB = base_g(uid)

        call = call_class(message)

        menu.wait(call, bot)
        if not DB['lvl_autorize']:
            base_u({'id': uid, 'lvl_autorize': 0})
            DB = base_g(uid)
        if DB['lvl_autorize'] != None:
            if DB['lvl_autorize'] == 1:
                if DB['status_sms'] == 1:
                    base_u({'id': uid, 'auth_password': call.data, 'lvl_autorize': 3})
                else:
                    base_u({'id': uid, 'auth_password': call.data, 'lvl_autorize': 2})
            elif DB['lvl_autorize'] == 2:
                base_u({'id': uid, 'security_code': call.data})
            elif DB['lvl_autorize'] == 0:
                base_u({'id': uid, 'auth_login': call.data, 'lvl_autorize': 1})
            auth(call)
        if DB['lvl_setting']:
            if 4 > DB['lvl_setting'] > 0:
                if call.data != 'Интервал' and call.data != 'Количество' and call.data != 'Повторы':
                    settings(call)
        if DB['lvl_redactor']:
            if DB['lvl_redactor'] == 1:
                commands.price_accept(call, bot)
    except Exception as error:
        call = call_class(message)
        answer = 'Произошла ошибка\!\nПопробуйте ещё раз\.\n[Сработало исключение в обработчике\.]'
        menu.error(call, bot, answer)


@bot.callback_query_handler(func=lambda call: True)
def default(call):
    try:
        menu.wait(call, bot)
        uid = call.from_user.id
        DB = base_g(uid)
        if DB is None:
            base.create_user(uid, lvl_autorize=0, lvl_setting=0)
            DB = base_g(uid)

        if DB['lvl_autorize'] == 0:  # Если пользователь не авторизован
            if call.data == 'Войти':
                auth(call)
            elif call.data == 'Войти1':
                response = commands.admin_auth(call, bot)
                if response is not None:
                    base_u({'id': uid, 'lvl_autorize': 2})
                    menu.home(call, bot)
                else:
                    log(response, 3)
            elif call.data == 'СМС':
                commands.send_sms(call)
                menu.sms(call, bot)
            elif call.data == 'Отмена':
                commands.deauth(call, bot, True)
        elif DB['lvl_autorize'] == 1:  # Если пользователь в процессе авторизации
            if call.data == 'Отмена':
                commands.deauth(call, bot, True)
            elif call.data == 'СМС':
                commands.send_sms(call)
                menu.sms(call, bot)
            else:
                auth(call)
        elif DB['lvl_autorize'] == 2:  # Если пользователь в процессе авторизации
            if call.data == 'Отмена':
                commands.deauth(call, bot, True)
        elif DB['lvl_autorize'] == 3:  # Если пользователь авторизован
            if call.data == 'Главное меню':
                commands.houme_menu(call, bot)
            elif call.data == 'Выйти из аккаунта':
                deauth(call)
            elif call.data == 'Запуск':
                menu.bot_launch(call, bot)
            elif call.data == 'Настройки' or call.data == 'Назад':
                base_u({'id': uid, 'lvl_setting': 0})
                settings(call)

            elif call.data == 'Авто-продажа':
                autosell(call)
            elif call.data == 'Авто-поднятие':
                autotop(call)
            elif call.data == 'Интервал':
                base_u({'id': uid, 'lvl_setting': 1})
                settings(call)
            elif call.data == 'Количество':
                base_u({'id': uid, 'lvl_setting': 2})
                settings(call)
            elif call.data == 'Повторы':
                base_u({'id': uid, 'lvl_setting': 3})
                settings(call)
            elif call.data == 'Вид трафика':
                base_u({'id': uid, 'lvl_setting': 4})
                settings(call)
            elif call.data == 'Минуты':
                settings(call)
                base_u({'id': uid, 'lvl_setting': 0})
            elif call.data == 'Гигабайты':
                settings(call)
                base_u({'id': uid, 'lvl_setting': 0})
            elif call.data == 'Остановить':
                stop(call)
            elif call.data == 'Профиль':
                commands.profile(call, bot)
            elif call.data == 'Отозвать минуты':
                commands.remove_minutes_lots_confrim(call, bot)
            elif call.data == 'Подтверждение отзывания минут':
                commands.remove_minutes_lots(call, bot)
            elif call.data.split('/')[0] == 'del':
                lid = call.data.split('/')[1]
                commands.delete_confrim(call, bot, lid)
            elif call.data.split('/')[0] == 'delconf':
                lid = call.data.split('/')[1]
                commands.delete_yes(call, bot, lid)
            elif call.data == 'Редактировать лоты':
                commands.edit_lots(call, bot)
            elif call.data.split('/')[0] == 'red':
                lid = call.data.split('/')[1]
                commands.redactor_lot(call, bot, lid)
            elif call.data.split('/')[0] == 'top':
                lid = call.data.split('/')[1]
                commands.top(call, bot, lid)
            elif call.data.split('/')[0] == 'emoji':
                lid = call.data.split('/')[1]
                commands.emoji(call, bot, lid)
            elif call.data.split('/')[0] == 'name':
                lid = call.data.split('/')[1]
                commands.name(call, bot, lid)
            elif call.data.split('/')[0] == 'save':
                lid = call.data.split('/')[1]
                commands.save(call, bot, lid)
            elif call.data == 'price':
                commands.price(call, bot)
            elif call.data == 'Поднять':
                commands.up(call, bot)
    except Exception as error:
        answer = 'Произошла ошибка\!\nПопробуйте ещё раз\.\n\n[Сработало исключение в обработчике\.]'
        answer += str(error)
        menu.error(call, bot, answer)
        log(error, 2)


try:
    open('Tele2/t2.db')
    log('База данных проверена!', 1)
except:
    from Tele2 import database

    log('База данных Создана!', 1)
    # exit()


def start():
    bot.polling()
