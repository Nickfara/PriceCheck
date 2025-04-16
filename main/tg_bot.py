"""
 Телеграм бот
"""
import telebot

from log import log

from preset import t2b
from constants import TOKEN_TG_BOT, ADMIN_IDS

bot = telebot.TeleBot(TOKEN_TG_BOT)
cache = {'check_file': ''}

from T2 import commands, menu


# !/usr/bin/env python # -* - coding: utf-8-* -


def just_send(text_: str):
    """
    Простая отправка сообщений.
    Главная цель - отправка заявка в канал.

    :param text_: Сформированный текст.
    :return:
    """

    print(text_)
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
    response = commands.auth(call)

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
    response = commands.settings(call)
    if response is not None:
        commands.update_def_traffic(call)
        t2b(uid, data={'lvl_setting': 0}, type_='u')
        menu.home(call)


@bot.message_handler(commands=['help'])
def help_command(call):
    """
    Команда помощи в ТГ
    :param call: Параметры команды или сообщения
    """
    menu.help_create(call)


@bot.message_handler(commands=['to_job', 'from_job'])
def active_wait(call, text_=None):
    """

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

    print('Типа запуск')
    if uid in ADMIN_IDS:
        menu.admin_menu(call)
    else:
        commands.deauth(call, True)

    print('Типа запуск')


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
def default(call):
    """
    Обработчик нажатия кнопок

    :param call: Параметры команды или сообщения
    """

    menu.wait(call)
    uid = call.from_user.id
    cmd = call.data
    cmds = None
    cmdsd = None

    DB = t2b(uid)

    if '/' in cmd:
        cmds = cmd.split('/')[0]
        cmdsd = cmd.split('/')[1]

    if uid in ADMIN_IDS:
        if cmd == 'МТ2':
            menu.admin_login(call)
            return
        elif cmd == 'ОСТ':
            return
        elif cmd == 'ПТ':
            return
        elif cmd == 'ПРС':
            return
        elif cmd == 'Войти админ':
            response = commands.admin_auth(call)
            if response:
                t2b(uid, data={'stage_authorize': 2}, type_='u')
                # menu.home(call)
            else:
                log(response, 3)

    if DB['stage_authorize'] < 3:  # Если пользователь не авторизован
        if cmd == 'Войти':
            auth(call)
        elif cmd == 'СМС':
            commands.send_sms(call)
            menu.sms(call)
        elif cmd == 'Отмена':
            start(call.message)
    elif DB['stage_authorize'] == 3:  # Если пользователь авторизован
        if cmd == 'Главное меню':
            result = commands.home_menu(call)
            if result:
                menu.home(call)
        elif cmd == 'Профиль':
            result = commands.profile(call)
            if result:
                menu.profile(call, result)
        elif cmd == 'Запуск':
            menu.bot_select(call)
        elif cmd in ('Настройки', 'Назад'):
            t2b(uid, data={'lvl_setting': 0}, type_='u')
            settings(call)
        elif cmd == 'Авто-продажа':
            commands.run_auto(call, 'sell')
        elif cmd == 'Авто-поднятие':
            commands.run_auto(call, 'top')
        elif cmd == 'Поднять':
            response = commands.up(call)
            if response:
                menu.up(call)
            else:
                answer = f'Лотов нет\!\n\n'
                log(answer, 3)
                menu.bot_active(call, answer)
                stop(call)
        elif cmd == 'Отмена':
            result = commands.home_menu(call)
            if result:
                menu.home(call)
        elif cmd == 'Выйти из аккаунта':
            start(call.message)
        elif cmd == 'Интервал':
            t2b(uid, data={'lvl_setting': 1}, type_='u')
            settings(call)
        elif cmd == 'Количество':
            t2b(uid, data={'lvl_setting': 2}, type_='u')
            settings(call)
        elif cmd == 'Повторы':
            t2b(uid, data={'lvl_setting': 3}, type_='u')
            settings(call)
        elif cmd == 'Вид трафика':
            t2b(uid, data={'lvl_setting': 4}, type_='u')
            settings(call)
        elif cmd in ('Минуты', 'Гигабайты'):
            settings(call)
            t2b(uid, data={'lvl_setting': 0}, type_='u')
        elif cmd == 'Остановить':
            stop(call)
        elif cmd == 'Отозвать минуты':
            menu.remove_minutes_lots_confirm(call)
        elif cmd == 'Подтверждение отзыва минут':
            commands.remove_minutes_lots(call)
        elif cmds == 'del':
            lid = cmdsd
            commands.delete_confirm(call, lid)
        elif cmds == 'delconf':
            lid = cmdsd
            commands.delete_yes(call, lid)
        elif cmd == 'Редактировать лоты':
            commands.edit_lots(call)
        elif cmds == 'red':
            lid = cmdsd
            commands.redactor_lot(call, lid)
        elif cmds == 'top':
            lid = cmdsd
            commands.top(call, lid)
        elif cmds == 'emoji':
            lid = cmdsd
            commands.emoji(call, lid)
        elif cmds == 'name':
            lid = cmdsd
            commands.name(call, lid)
        elif cmds == 'save':
            lid = cmdsd
            commands.save(call, lid)
        elif call.data == 'price':
            commands.price(call)


def run():
    """
        Запуск телеграм бота
    """
    bot.polling()

run()