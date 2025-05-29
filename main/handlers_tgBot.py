"""
Здесь определяются команды телеграм бота и происходит непосредственный запуск бота.
"""
import telebot

from log import log

from functions import t2b
from constants import TOKEN_TG_BOT, ADMIN_IDS

from handlers_registry import get_admin_commands, get_user_commands, get_param_commands

bot = telebot.TeleBot(TOKEN_TG_BOT)
cache = {'check_file': ''}

from T2 import commands, menu


# !/usr/bin/env python # -* - coding: utf-8-* -


def just_send(text_: str):
    """
    Простая отправка сообщений.
    Главная цель - отправка заявок в канал.

    :param text_: Сформированный текст.
    :return:
    """

    bot.send_message(chat_id=ADMIN_IDS[0], text=text_)


def create_call(message):
    """
    Конвертирование 'message' в 'call'
        
    :param message: Данные о команде или сообщении
    :return: call
    """

    class Call(object):
        """
            Класс 'call' созданный из 'message'
        """

        def __init__(self):
            self.message = message  # либо call.message
            self.data = message.text
            self.from_user = message.from_user
            self.id = message.message_id

    return Call()


def auth(call):
    """
    Авторизация пользователя

    :param call: Параметры команды или сообщения
    """

    response = commands.Auth.stage_filter(call)

    if response == 2:
        menu.home(call)
    elif response == 0:
        start()


def stop(call):
    """
    Остановка работы бота

    :param call: Параметры команды или сообщения
    """
    commands.stop(call)
    menu.home(call)


def settings(call):
    """
    Вызов команды настроек
    :param call: Параметры команды или сообщения
    """

    menu.wait(call)
    uid = call.from_user.id
    response = commands.Settings.stage_filter(call)
    if response is not None:
        commands.update_def_traffic(call)
        t2b(uid, data={'lvl_setting': 0}, type_='u')
        menu.home(call)


@bot.message_handler(commands=['help'])
def help_command(call):
    """
    Команда 'помощь' в ТГ
    :param call: Параметры команды или сообщения
    """
    menu.help_create(call)


@bot.message_handler(commands=['to_job', 'from_job'])
def active_wait(call, text_=None):
    """
    Ожидание падения цены

    :param call:
    :param text_:
    """
    from ParserTaxi.taxi_parser import wait_low_money
    if text_:
        call.data = text_
    wait_low_money(call.data)


@bot.message_handler(commands=['send_price'])
def send_file(message):
    """
    Активация режима принятия файлов
    
    :param message:  Параметры команды или сообщения
    """
    cache['check_file'] = 'send_file'
    bot.send_message(message.chat.id, 'Пожалуйста, отправьте файл для загрузки:')


@bot.message_handler(commands=['stop', 'exit'])
def close(message):
    """
    Остановка бота
    
    :param message: Параметры команды или сообщения
    """
    bot.stop_polling()

    # noinspection PyBroadException
    try:
        bot.send_message(message.chat.id, 'Бот выключен!')
    except:
        bot.send_message(ADMIN_IDS[0], 'Бот выключен!')


@bot.message_handler(commands=['start', 'deauth', 'unauthorize'])
def start(message):
    """
    Деавторизация пользователя

    :param message:  Параметры команды или сообщения
    """

    call = create_call(message)
    menu.wait(call)
    uid = call.from_user.id


    if uid in ADMIN_IDS:
        commands.deauth(call)
        return menu.admin_menu(call)
    else:
        commands.deauth(call, True)


# noinspection PyBroadException
@bot.message_handler(content_types=['document'])
def files(message):
    """
    Загрузка файлов из ТГ бота

    :type message: object
    :param message:  Параметры команды или сообщения
    """
    if cache['check_file'] == 'send_file':
        bot.reply_to(message, 'Загрузка...')
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = 'C:/users/Буфет/Documents/GitHub/PriceCheck/main/data/prices/' + message.document.file_name
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
            log(str(e), 2)
        cache['check_file'] = ''


@bot.message_handler(content_types=['text'])
def text(message):
    """
    Обработчик текстовых сообщений
    :param message: Параметры команды или сообщения
    """
    call = create_call(message)

    uid = message.from_user.id
    DB = t2b(uid)
    text_ = call.data

    menu.wait(call)

    if 'работ' in text_.lower() and len(text_) < 11:
        active_wait(call, text_='to_job')  # Запуск ожидания такси до работы
        return

    if 'дом' in text_.lower() and len(text_) < 11:
        active_wait(call, text_='to_home')  # Запуск ожидания такси до дома
        return

    if not DB['stage_authorize']:
        t2b(uid, data={'stage_authorize': 0}, type_='u')

    if DB['stage_authorize'] is not None:
        if DB['stage_authorize'] == 1:
            if DB['status_sms'] == 1:
                t2b(uid, data={'auth_password': call.data, 'stage_authorize': 2}, type_='u')
            else:
                t2b(uid, data={'auth_password': call.data, 'stage_authorize': 2}, type_='u')
        elif DB['stage_authorize'] == 2:
            t2b(uid, data={'security_code': call.data}, type_='u')
        elif DB['stage_authorize'] == 0:
            t2b(uid, data={'auth_login': call.data, 'stage_authorize': 1}, type_='u')
        auth(call)
        return

    if DB['lvl_setting']:
        if 4 > DB['lvl_setting'] > 0:
            if text_ not in ('Интервал', 'Количество', 'Повторы'):
                settings(call)
                return

    if DB['lvl_redactor']:
        if DB['lvl_redactor'] == 1:
            commands.price_accept(call)
            return


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id
    cmd = call.data
    cmds, cmdsd = (cmd.split('/') + [None])[:2]
    DB = t2b(uid)

    admin_commands = get_admin_commands(uid, t2b, menu, commands, log)
    user_commands = get_user_commands(uid, t2b, menu, commands, settings, log, stop)
    param_commands = get_param_commands(commands)

    if uid in ADMIN_IDS and cmd in admin_commands:
        log(f"Административная команда получена: {cmd}", 1)
        return admin_commands[cmd](call)

    if DB.get('stage_authorize', 0) < 3:
        if cmd == 'Войти':
            log('Авторизация запрошена', 1)
            return auth(call)
        elif cmd == 'СМС':
            log('Отправка СМС', 1)
            commands.send_sms(call)
            return menu.sms(call)
        elif cmd == 'Отмена':
            return start(call.message)

    elif DB.get('stage_authorize') == 3:
        if cmd in user_commands:
            log(f"Пользовательская команда получена: {cmd}", 1)
            return user_commands[cmd](call)
        if cmds in param_commands and cmdsd:
            log(f"Команда с параметрами получена: {cmds} {cmdsd}", 2)
            return param_commands[cmds](call, cmdsd)
        if cmd == 'price':
            return commands.price(call)

    log(f'Неизвестная команда: "{cmd}" от пользователя {uid}', 3)


def run():
    """
        Запуск телеграм бота
    """
    bot.polling()


run()
