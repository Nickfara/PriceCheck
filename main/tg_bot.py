token = '7306002854:AAHIc35yMOXyho4bcYYeAS3W5PP0ey_1HXk'

import telebot
from Tele2 import commands
from Tele2 import menu
from telebot import types
import json

from Tele2 import base
from log import log

base_u = base.update_users
base_g = base.get_user

from handler import t2b


bot = telebot.TeleBot(token)
cache = {'check_file': ''}


# !/usr/bin/env python # -* - coding: utf-8-* -
def create_call(message):
    class call(object):
        def __init__(self):
            self.message = message  # либо call.message
            self.data = message.text
            self.from_user = message.from_user
            self.id = message.message_id

    return call()


@bot.message_handler(commands=['send_price'])
def send_file(message):
    call = create_call(message)
    uid = call.from_user.id
    cache['check_file'] = 'send_file'
    bot.send_message(message.chat.id, 'Пожалуйста, отправьте файл для загрузки:')


@bot.message_handler(commands=['stop', 'exit'])
def exit(message):
    bot.stop_polling()

    try:
        bot.send_message(message.chat.id, 'Бот выключен!')
    except:
        bot.send_message('828853360', 'Бот выключен!')



@bot.message_handler(content_types='document')
def files(message):
    if cache['check_file'] == 'send_file':
        bot.reply_to(message, 'Загрузка...')
        try:
            call = create_call(message)
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = 'C:/users/Буфет/Documents/GitHub/PriceCheck/main/prices/' + message.document.file_name
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            try:
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id + 1, text='Загружено!')
            except:
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id + 2, text='Загружено!')
        except Exception as e:
            try:
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id + 1, text=str(e))
            except:
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id + 2, text='Загружено!')
            log(e, 2)
        cache['check_file'] = ''


def send(text):
    id = 828853360
    bot.send_message(chat_id=id, text=text)


@bot.message_handler(commands=['start'])
def start(message):
    call = create_call(message)
    commands.deauth(call, bot, True)


def auth(call):
    response = commands.auth(call, bot)
    if response:
        menu.home(call, bot)
    else:
        start(call.message)


def deauth(call):
    menu.wait(call, bot)
    uid = call.from_user.id
    commands.deauth(call, bot, True)
    t2b(uid, data={'stage_autorize': 0}, type_='u')


def run_auto(call, type_):
    menu.wait(call, bot)
    commands.run_auto(call, bot, type_)


def stop(call):
    commands.stop(call, bot)
    menu.home(call, bot)


def help_command(call):
    pass


def settings(call):
    menu.wait(call, bot)
    uid = call.from_user.id
    response = commands.settings(call, bot)
    if response is not None:
        commands.update_def_traffic(call)
        t2b(uid, data={'lvl_setting': 0}, type_='u')
        menu.home(call, bot)


@bot.message_handler(content_types='text')
def text(message):
    uid = message.from_user.id
    DB = t2b(uid)

    call = create_call(message)

    menu.wait(call, bot)
    
    if not DB['stage_autorize']:
        t2b(uid, data={'stage_autorize': 0}, type_='u')

    if DB['stage_autorize'] != None:
        if DB['stage_autorize'] == 1:
            if DB['status_sms'] == 1:
                t2b(uid, data={'auth_password': call.data, 'stage_autorize': 3}, type_='u')
            else:
                t2b(uid, data={'auth_password': call.data, 'stage_autorize': 2}, type_= 'u')
        elif DB['stage_autorize'] == 2:
            t2b(uid, data={'security_code': call.data}, type_= 'u')
        elif DB['stage_autorize'] == 0:
            t2b(uid, data={'auth_login': call.data, 'stage_autorize': 1}, type_= 'u')
        auth(call)
    if DB['lvl_setting']:
        if 4 > DB['lvl_setting'] > 0:
            if call.data != 'Интервал' and call.data != 'Количество' and call.data != 'Повторы':
                settings(call)
    if DB['lvl_redactor']:
        if DB['lvl_redactor'] == 1:
            commands.price_accept(call, bot)


@bot.callback_query_handler(func=lambda call: True)
def default(call):
    menu.wait(call, bot)
    uid = call.from_user.id
    cmd = call.data
    cmds = None
    cmdsd = None
    if '/' in cmd:
        cmds = cmd.split('/')[0]
        cmdsd = cmd.split('/')[1]
    DB = base_g(uid)

    if DB is None:
        base.create_user(uid, stage_autorize=0, lvl_setting=0)
        DB = base_g(uid)

    if DB['stage_autorize'] < 3:  # Если пользователь не авторизован
        if cmd == 'Войти':
            auth(call)
        elif cmd == 'Войти1':
            response = commands.admin_auth(call, bot)
            if response is not None:
                t2b(uid, data={'stage_autorize': 2}, type_= 'u')
                menu.home(call, bot)
            else:
                log(response, 3)
        elif cmd == 'СМС':
            commands.send_sms(call)
            menu.sms(call, bot)
        elif cmd == 'Отмена':
            commands.deauth(call, bot, True)
        else:
            auth(call)

    elif DB['stage_autorize'] == 3:  # Если пользователь авторизован
        if cmd == 'Главное меню':
            commands.houme_menu(call, bot)
        elif cmd == 'Отмена':
            commands.houme_menu(call, bot)
        elif cmd == 'Выйти из аккаунта':
            deauth(call)
        elif cmd == 'Запуск':
            menu.bot_launch(call, bot)
        elif cmd in ('Настройки', 'Назад'):
            t2b(uid, data={'lvl_setting': 0}, type_= 'u')
            settings(call)
        elif cmd == 'Авто-продажа':
            run_auto(call, 'sell')
        elif cmd == 'Авто-поднятие':
            run_auto(call, 'top')
        elif cmd == 'Интервал':
            t2b(uid, data={'lvl_setting': 1}, type_= 'u')
            settings(call)
        elif cmd == 'Количество':
            t2b(uid, data={'lvl_setting': 2}, type_= 'u')
            settings(call)
        elif cmd == 'Повторы':
            t2b(uid, data={'lvl_setting': 3}, type_= 'u')
            settings(call)
        elif cmd == 'Вид трафика':
            t2b(uid, data={'lvl_setting': 4}, type_= 'u')
            settings(call)
        elif cmd in ('Минуты', 'Гигабайты'):
            settings(call)
            t2b(uid, data={'lvl_setting': 0}, type_= 'u')
        elif cmd == 'Остановить':
            stop(call)
        elif cmd == 'Профиль':
            commands.profile(call, bot)
        elif cmd == 'Отозвать минуты':
            commands.remove_minutes_lots_confrim(call, bot)
        elif cmd == 'Подтверждение отзывания минут':
            commands.remove_minutes_lots(call, bot)
        elif cmds == 'del':
            lid = cmdsd
            commands.delete_confrim(call, bot, lid)
        elif cmds == 'delconf':
            lid = cmdsd
            commands.delete_yes(call, bot, lid)
        elif cmd == 'Редактировать лоты':
            commands.edit_lots(call, bot)
        elif cmds == 'red':
            lid = cmdsd
            commands.redactor_lot(call, bot, lid)
        elif cmds == 'top':
            lid = cmdsd
            commands.top(call, bot, lid)
        elif cmds == 'emoji':
            lid = cmdsd
            commands.emoji(call, bot, lid)
        elif cmds == 'name':
            lid = cmdsd
            commands.name(call, bot, lid)
        elif cmds == 'save':
            lid = cmdsd
            commands.save(call, bot, lid)
        elif call.data == 'price':
            commands.price(call, bot)
        elif call.data == 'Поднять':
            commands.up(call, bot)



try:
    open('data/t2.db')
    log('База данных проверена!', 1)
except:
    from Tele2 import database

    log('База данных Создана!', 1)
    #exit('')

def start():
    bot.polling()
