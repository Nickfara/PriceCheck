import json
import random
import time

from Tele2 import api
from Tele2 import base
from Tele2 import functions
from Tele2 import menu
from telebot import types
import math

base_u = base.update_users
base_g = base.get_user

from Tele2 import config
from log import log

def_account = config.account
def_traffic = config.add_traffic()
cache = {}
cache_lot = {}
stop_timer = [False]


def auth(call, bot):
    """
    Функция авторизации.
    :param call:
    :param bot:
    :return:
    """
    uid = call.from_user.id
    DB = base_g(uid)
    data = call.data

    # При отсутствии аккаунта в БД, создаётся таблица
    if DB is None:
        log('Создание аккаунта!', 1)
        base.create_user(uid)

    # Если пользователь не авторизован, происходит авторизация
    if DB['stage_autorize'] < 3:
        # Форматирование номера телефона
        if data[0] == '8':
            data = '7'.join(data.split('8'))
        elif data[0] == '+' and data[1] == '7':
            data = '7'.join(data.split('+7'))

        # 1 Этап - Добавление номера телефона (Номер успешно добавлен)
        if len(str(data)) == 11 and (data[0] == '7') and data[1] == '9' and DB['stage_autorize'] == 0:
            base_u({'id': uid, 'auth_login': data, 'stage_autorize': 1})
            answer = 'Введите ваш пароль:'
            menu.login_password(call, bot, answer)

        # 1 Этап - Добавление номера телефона:
        elif DB['stage_autorize'] == 0:
            answer = 'Введите ваш номер телефона, \nв формате: [79000000000]'
            menu.login_number(call, bot, answer)

        # 2 Этап - Проверка кода подтверждения:
        elif DB['stage_autorize'] == 1:
            # Если включено подтверждение кодом:
            if DB['status_sms'] == 0:
                # Если пароль не указан:
                if len(str(DB['auth_password'])) == 0 or DB['auth_password'] == None:
                    base_u({'id': uid, 'auth_password': data, 'security_code': ''})

                response = api.security_code(uid)

                # При успешной отправке кода:
                if response['status']:
                    base_u({'id': uid, 'stage_autorize': 2, 'auth_password': DB['auth_password'],
                            'security_code_token': response['response'].json()['security_code_token']})
                    answer = 'На почту был отправлен проверочный код\! Пришлите его сюда:'
                    menu.security_code(call, bot, answer)
            else:
                base_u({'id': uid, 'stage_autorize': 2})

        # 3 Этап - Проведение и проверка авторизации:
        elif DB['stage_autorize'] == 2:
            response = api.auth(uid)

            # При успешной авторизации:
            if response['status']:
                base_u(
                    {'id': uid, 'config_count': def_traffic[0]['volume']['value'], 'config_autotime': def_traffic[1][0],
                     'stage_autorize': 3, 'status_sms': 0, 'config_uom': def_traffic[0]['volume']['uom'],
                     'config_repit': def_traffic[1][1], 'config_price': def_traffic[0]['cost']['amount'],
                     'config_type': def_traffic[0]['trafficType']})
                cache[uid] = {'status_autosell': 0, 'status_autotop': 0, 'status_lagg': 0}

                update_def_traffic(call)
                return DB

            # При неудаче - возврат к 1 этапу:
            else:
                base.delete_user(uid)
                base.create_user(uid)
                answer = 'Неверные данные, попробуйте сначала\!' \
                         '\nВведите ваш номер телефона, в формате: [79000000000]'
                log('При авторизации, были введены неверные данные.', 3)
                menu.login_number(call, bot, answer)

    # Пользователь уже авторизован.
    else:
        answer = 'Вы уже авторизованы\!'
        log(answer, 3)
        return DB


def admin_auth(call, bot):
    """
    Функция предназначена для авторизации админа.

    :param call:
    :param bot:
    :return:
    """
    deauth(call, bot, False)
    uid = call.from_user.id
    DB = base_g(uid)
    data = call.data

    deauth(call, bot, False)

    # Создание аккаунта:
    if DB is None:
        log('Создание аккаунта')
        base.create_user(uid, lvl_autorize=2, lvl_setting=0)

    # Авторизация в +7 (992)022-88-48
    if data == 'Войти1':
        log('Вход в +7 (992)022-88-48', 1)
        base_u({'id': uid, 'stage_autorize': 1, 'auth_login': '79920228848', 'auth_password': '649UPY'})
        response = auth(call, bot)
        return response


def deauth(call, bot, lobby):
    """
    Функция деавторизации.
    :param call:
    :param bot:
    :param lobby:
    :return:
    """
    try:
        uid = call.from_user.id
        DB = base_g(uid)

        if DB:
            base.delete_user(uid)

        if lobby:
            menu.start(call.message, bot)

        log('Пользователь удалён.', 1)
        return True

    except KeyError:
        log('Ошибка удаления пользователя!', 3)
        return False


def houme_menu(call, bot):
    """
    Функция открытия главного экрана.
    :param call:
    :param bot:
    """
    uid = call.from_user.id
    cache[uid] = {'status_autosell': 0, 'status_autotop': 0, 'status_lagg': 0}
    menu.home(call, bot)


# Меню настроек
def settings(call, bot):
    """

    :param call:
    :param bot:
    :return:
    """
    uid = call.from_user.id
    DB = base_g(uid)
    data = call.data

    config_uom = DB['config_uom']
    if DB['lvl_setting'] == 0:
        name = ("🌐 *Вид:* Гигабайты" if DB['config_uom'] == "gb" else "☎️ *Вид:* Минуты")
        name2 = ("ГБ" if DB['config_uom'] == "gb" else "МИН")
        answer = f'🛠️ *Настройки\.* \n\nТекущие: \n{name}\. ' \
                 f'\n📏 *Количество:* {DB["config_count"]}{name2} за {DB["config_price"]}₽' \
                 f'\n🕓 *Интервал:* {DB["config_autotime"]} секунд\.' \
                 f'\n🔂 *Повторы:* {DB["config_repit"]} раз\(а\)\.'
        menu.settings(call, bot, answer)
    elif DB['lvl_setting'] == 1:
        try:
            int(str(data))
            base_u({'id': uid, 'config_autotime': call.message.text})
            return True
        except:
            answer = '🛠️ *Настройки\.* \n\nНапишите количество секунд, \nчерез которое будут повторяться \nподнятие и выставление\. ' \
                     '\nИсключительно цифрами, например: 5'
            menu.settings(call, bot, answer)
    elif DB['lvl_setting'] == 2:

        try:
            config_price = int(str(data))
        except:
            answer = '🛠️ *Настройки\.* \n\nПринимаются исключительно цифры.'
            menu.settings(call, bot, answer)
            return False

        if config_uom == 'gb':
            base_u({'id': uid, 'config_count': data, 'config_price': str(math.ceil(config_price * 15))})
        elif config_uom == 'min':
            base_u({'id': uid, 'config_count': data, 'config_price': str(math.ceil(int(data) / 1.25))})
        return True

    elif DB['lvl_setting'] == 3:
        try:
            int(str(data))
            base_u({'id': uid, 'config_repit': call.message.text})
            return True
        except:
            answer = '🛠️ *Настройки\.* \n\nНапишите количество повторов, \nчерез которое бот закончит \nподнятие или ' \
                     'выставление\. Указав 0, повторения будут бесконечны\. ' \
                     '\nИсключительно цифрами, например: 10'
            menu.settings(call, bot, answer)
            return False
    elif DB['lvl_setting'] == 4:
        if data == 'Минуты':
            base_u({'id': uid, 'config_type': 'voice', 'config_count': '62', 'config_price': '50', 'config_uom': 'min'})
            return True
        elif data == 'Гигабайты':
            base_u({'id': uid, 'config_type': 'data', 'config_count': '6', 'config_price': '90', 'config_uom': 'gb'})
            return True
        else:
            answer = '🛠️ *Настройки\.* \n\nВыберите нужный для вас тип трафика:'
            menu.settings(call, bot, answer)


def profile(call, bot):
    """

    :param call:
    :param bot:
    :return:
    """
    global allow_voice, allow_data, incom

    uid = call.from_user.id
    response = api.get_rests(uid)
    check = True

    def auth_error_message(response):  # Вывод сообщения, об ошибке авторизации
        if 'Ошибка авторизации' == response['text']:
            answer = 'Ошибка авторизации\! \nВойдите в аккаунт заново\.'
            menu.error(call, bot, answer)
        else:
            menu.error(call, bot)

    if response['status']:
        allow_traffic = response['rests']
    else:
        log('❌ Ошибка response в функции profile файла commands - get_rests', 3)
        log(response, 3)
        allow_traffic = {'data': ''}
        check = False
        auth_error_message(response)

        return False

    response = api.get_statistics(uid)
    if response['status']:
        statistics = response['response'].json()['data']
    else:
        log('❌ Ошибка response в функции profile файла commands - get_statistics', 3)
        log(response, 3)
        statistics = {"soldVoice": {"value": ''}}
        check = False
        auth_error_message(response)

        return False

    response = api.get_balance(uid)
    if response['status']:
        balance = response['response'].json()['data']['value']
    else:
        log('❌ Ошибка response в функции profile файла commands - get_balance', 3)
        log(response, 3)
        balance = ''
        check = False
        auth_error_message(response)

        return False

    response = api.get_name(uid)
    if response['status']:
        username = response['response'].json()['data']
    else:
        username = ''
        check = False
        auth_error_message(response)

        return False

    DB = base_g(uid)  # Оно здесь, потому что сначала обновляются данные, потом копируются

    if check:
        balance = str(balance).split('.')
        if len(str(balance[0])) > 3:
            balance2 = list(balance[0])
            balance2.insert(-3, "'")
            balance = ''.join(balance2) + '\.' + balance[1]
        else:
            balance = balance[0] + '\.' + balance[1]
        income = str(int(statistics["totalIncome"]["amount"]))
        if len(str(income)) > 3:
            income = list(income)
            income.insert(-3, "'")
            income = ''.join(income)

        allow_data = str(int(statistics["soldData"]["value"]))
        if len(allow_data) > 3:
            allow_data = list(allow_data)
            allow_data.insert(-3, "'")
            allow_data = ''.join(allow_data)
        allow_voice = str(int(statistics["soldVoice"]["value"]))
        if len(allow_voice) > 3:
            allow_voice = list(allow_voice)
            allow_voice.insert(-3, "'")
            allow_voice = ''.join(allow_voice)
    answer = f'👤 *Профиль\.* \n\nЗдравствуйте, {username}\!\n\n'

    answer += f'💰 *Баланс:* _{balance}₽_\n'
    answer += f'✅ *Доступно:* {str(allow_traffic["data"])} ГБ и {str(allow_traffic["voice"])} МИН\.\n'
    answer += f'🛒 *Продано:* {allow_data} ГБ\ и' \
              f' {allow_voice} МИН\.\n'
    answer += f'📈 *Доход:* {income}₽\.\n\n'
    menu.profile(call, bot, answer)


# Авто-продажа
def autosell(call, bot):
    """

    :param call:
    :param bot:
    """
    global answer
    print('\033[32m\n\033[1m\033[44mКоманда: autosell\033[0m')
    uid = call.from_user.id
    DB = base_g(uid)

    if uid not in cache:  # Добавление аккаунта в кэш, если его нет
        cache[uid] = {'status_lagg': 0, 'status_autosell': 0, 'status_autotop': 0}

    if DB:
        if DB['stage_autorize'] == 3:
            if cache[uid]['status_autosell'] == 0:
                if cache[uid]['status_lagg'] == 0:
                    count = 0
                    cache[uid]['status_autosell'] = 1
                    seller_lot = [0, 0]
                    while cache[uid]['status_autosell'] == 1:
                        if DB['config_repit'] != 0:
                            count += 1

                        lots = get_lots_refresh(call)
                        if count == 0:
                            seller_lot[0] = len(lots)
                        seller_lot[1] = len(lots)

                        check_sell(call, bot, uid, lots)  # Проверка (Продался ли лот)

                        if count <= int(DB['config_repit']):
                            response = api.sell_lot(uid, def_traffic[0])
                            # Проверка на успешное выполнение
                            if response['status']:
                                answer = 'Лот успешно выставлен\!'
                                menu.bot_launch_on(call, bot, answer, False, False)
                                time.sleep(2)
                                at = DB['config_autotime']
                                answer = 'Авто\-продажа работает\!\n'

                                if int(DB['config_repit']) > 0:
                                    answer += '\n*Осталось:* ' + str(
                                        int(DB['config_repit']) - count) + ' раз\(а\)'
                                second_text = ' секунд' if (str(at)[len(at) - 1] in ('5', '6', '7', '8', '9', '0') or (
                                    str(at)[0] == '1' if len(str(at)) > 1 else False)) else (
                                    ' секунды' if str(at)[len(at) - 1] in ('2', '3', '4') else ' секунда')

                                answer3 = answer + '\n*Ожидание:* ' + str(
                                    at) + second_text  # Первоначальное добавление таймера
                                menu.bot_launch_on(call, bot, answer3, True, False)

                                cache[uid]['status_lagg'] = 1
                                cache[uid]['timer'] = 0
                                stop_timer[0] = False
                                while cache[uid]['timer'] < int(at):
                                    if stop_timer[0]:
                                        cache[uid]['timer'] = int(at)
                                    else:
                                        at = DB['config_autotime']
                                        time.sleep(0.85)
                                        cache[uid]['timer'] += 1
                                        ct = str(int(at) - int(cache[uid]['timer']))
                                        second_text2 = ' секунд' if (str(ct)[len(ct) - 1] in (
                                            '5', '6', '7', '8', '9', '0') or (
                                                                         (True if str(at)[0] == '1' else False) if len(
                                                                             str(ct)) > 1 else False)) else (
                                            ' секунды' if str(ct)[len(ct) - 1] in (
                                                '2', '3', '4') else ' секунда')
                                        answer2 = answer + '\n*Ожидание:* ' + ct + second_text2  # Изменение таймера
                                        menu.bot_launch_on(call, bot, answer2, True, False)
                                cache[uid]['status_lagg'] = 0
                            else:
                                if 'Недостаточно трафика' == response['text']:
                                    answer = 'Недостаточно трафика\!'
                                    menu.bot_launch_on(call, bot, answer, False, False)
                                    time.sleep(2)
                                    stop(call, bot)
                                elif 'Ошибка авторизации' == response['text']:
                                    answer = 'Ошибка авторизации\! \nВойдите в аккаунт заново\.'
                                    menu.error(call, bot, answer)
                                else:
                                    menu.error(call, bot)
                                break

                        else:
                            answer = f'Авто\-продажа завершена\!'
                            answer += f'\nПродано: {seller_lot[0] - seller_lot[1]} лотов за сеанс\.'
                            menu.bot_launch_on(call, bot, answer, False, False)
                            stop(call, bot)
                            break
                else:
                    answer = 'Ожидание после выставления не окончено\! cache[uid][\'status_lagg\'] = 1'
                    log(answer, 3)
            else:
                answer = 'Цикл автопродажи уже запущен\! cache[uid][\'status_autosell\'] = 1'
                log(answer, 3)
        else:
            answer = 'Вы не закончили авторизацию\! Авторизуйтесь, используя команду: /start'
            log('autosell', '\033[31m' + answer + '\033[0m')
            deauth(call, bot, True)
    else:
        answer = 'Вы не авторизованы\! Авторизуйтесь, используя команду: /start'
        log(answer, 3)
        deauth(call, bot, True)


# Авто-поднятие
def autotop(call, bot):
    """

    :param call:
    :param bot:
    """
    uid = call.from_user.id
    DB = base_g(uid)
    if uid not in cache:  # Добавление аккаунта в кэш, если его нет
        cache[uid] = {'status_lagg': 0, 'status_autosell': 0, 'status_autotop': 0}
    if DB:
        if DB['stage_autorize'] == 3:
            if cache[uid]['status_autotop'] == 0:
                if cache[uid]['status_lagg'] == 0:
                    cache[uid]['status_autotop'] = 1
                    count = 0
                    seller_lot = [0, 0]

                    while cache[uid]['status_autotop'] == 1:
                        lots = get_lots_refresh(call)

                        check_sell(call, bot, uid, lots)  # Проверка (Продался ли лот)

                        if count == 0:
                            seller_lot[0] = len(lots)
                        seller_lot[1] = len(lots)

                        if len(lots) > 0:
                            rand_id = random.randint(0, len(lots) - 1)
                            lot_id = lots[f'{rand_id}']['id']

                            if not lots[str(rand_id)]['status']:
                                if lots[str(rand_id)]['status'] != 'revoked':
                                    if DB['config_repit'] != 0:
                                        count += 1
                                    if count <= int(DB['config_repit']):
                                        response = api.top(uid, lot_id)
                                        if response['status']:
                                            answer_lot = functions.text_lot(lots, f'{rand_id}')

                                            answer = f'Лот успешно поднят в топ\:\n\n{answer_lot}'
                                            log('Лот поднят в топ!', 1)
                                            menu.bot_launch_on(call, bot, answer, False, False)
                                            time.sleep(2)

                                            at = DB['config_autotime']
                                            answer = 'Авто\-поднятие работает\!\n'
                                            if int(DB['config_repit']) > 0:
                                                answer += '\n*Осталось:* ' + str(
                                                    int(DB['config_repit']) - count) + ' раз\(а\)'
                                            second_text = ' секунд' if (
                                                    str(at)[len(at) - 1] in ('5', '6', '7', '8', '9', '0') or (
                                                str(at)[0] == '1' if len(str(at)) > 1 else False)) else (
                                                ' секунды' if str(at)[len(at) - 1] in ('2', '3', '4') else ' секунда')
                                            answer3 = answer + '\n*Ожидание:* ' + str(
                                                at) + second_text  # Первоначальное добавление таймера
                                            menu.bot_launch_on(call, bot, answer3, True, False)
                                            cache[uid]['status_lagg'] = 1
                                            cache[uid]['timer'] = 0
                                            stop_timer[0] = False
                                            while cache[uid]['timer'] < int(at):
                                                if stop_timer[0]:
                                                    cache[uid]['timer'] = int(at)
                                                else:
                                                    time.sleep(0.85)
                                                    cache[uid]['timer'] += 1
                                                    ct = str(int(at) - int(cache[uid]['timer']))
                                                    second_text2 = ' секунд' if (str(ct)[len(ct) - 1] in (
                                                        '5', '6', '7', '8', '9', '0') or ((True if str(at)[
                                                                                                       0] == '1' else False) if len(
                                                        str(ct)) > 1 else False)) else (
                                                        ' секунды' if str(ct)[len(ct) - 1] in (
                                                            '2', '3', '4') else ' секунда')
                                                    answer2 = answer + '\n*Ожидание:* ' + ct + second_text2  # Изменение таймера
                                                    menu.bot_launch_on(call, bot, answer2, True, False)
                                            cache[uid]['timer'] = 0
                                            cache[uid]['status_lagg'] = 0
                                        else:
                                            if 'Ошибка авторизации' == response['text']:
                                                answer = 'Ошибка авторизации\! \nВойдите в аккаунт заново\.'
                                                menu.error(call, bot, answer)
                                                break
                                            else:
                                                answer = 'Данный лот уже продан\!' if 'is not in ACTIVE status.' in str(
                                                    response['text']) else str(response['text'])
                                                log(answer, 3)
                                                menu.bot_launch_on(call, bot, answer, False, False)
                                                time.sleep(2)
                                    else:
                                        answer = f'Авто\-поднятие завершено\!'
                                        answer += f'\nПродано: {seller_lot[0] - seller_lot[1]} лотов за сеанс\.'
                                        log(answer, 1)
                                        menu.bot_launch_on(call, bot, answer, False, True)
                                        stop(call, bot)
                                        break
                                else:
                                    answer = f'Попался удалённый лот\!'
                                    log(answer, 3)
                                    menu.bot_launch_on(call, bot, answer, False, False)
                            else:
                                answer = f'Попался лот находящийся уже в топе\!'
                                log(answer, 3)
                                menu.bot_launch_on(call, bot, answer, False, False)
                        else:
                            answer = f'Лотов нет\!\n\n'
                            log(answer, 3)
                            menu.bot_launch_on(call, bot, answer, False, False)
                            stop(call, bot)
                            break
                else:
                    answer = 'Ожидание после выставление не окончено\! cache[uid][\'status_lagg\'] = 1'
                    log(answer, 3)
            else:
                answer = 'Цикл автотопа уже запущен\! cache[uid][\'status_autotop\'] = 1'
                log(answer, 3)
        else:
            answer = 'Вы не закончили авторизацию\! Авторизуйтесь, используя команду: /auth'
            log('Авторизация не завершена!', 3)
            deauth(call, bot, False)
    else:
        answer = 'Вы не авторизованы\! Авторизуйтесь, используя команду: /auth'
        log('Авторизация не завершена!', 3)
        deauth(call, bot, False)


# Остановка бота
def stop(call, bot):
    """

    :param call:
    :param bot:
    """
    uid = call.from_user.id
    DB = base_g(uid)
    if uid in cache:
        cache[uid]['status_autotop'] = 0
        cache[uid]['status_autosell'] = 0
        stop_timer[0] = True
        DB = base_g(uid)
        time.sleep(1.5)  # Ожидание для безопасности
        response = api.get_lots(uid)
        if response['status']:
            base_u({'id': uid, 'list_lots': json.dumps(response['active_traffic'])})  # Обновление списка лотов
        else:
            log(response['text'], 3)
    menu.home(call, bot)


def remove_minutes_lots_confrim(call, bot):
    """

    :param call:
    :param bot:
    """
    answer = 'Вы уверены, что хотите отозвать все активные лоты с минутами\?\nОтменить это действие не получится\!'
    menu.remove_minutes_lots_confrim(call, bot, answer)


def remove_minutes_lots(call, bot):
    """

    :param call:
    :param bot:
    """
    uid = call.from_user.id
    minutes = get_lots_refresh(call, delete_minutes=True)
    filtered_minutes = []
    for i in minutes:
        if minutes[i]['type'] == 'min':
            lid = minutes[i]['id']
            filtered_minutes.append(minutes[i]['id'])
            api.delete(uid, lid)
    if len(filtered_minutes) > 0:
        answer = 'Все лоты с минутами успешно отозваны\!'
    else:
        answer = 'Активных лотов с минутами нет\!'

    menu.remove_minutes_lots(call, bot, answer)
    time.sleep(3)
    menu.home(call, bot)


def update_def_traffic(call):
    """

    :param call:
    """
    uid = call.from_user.id
    DB = base_g(uid)
    def_traffic[0]['volume']['value'] = DB["config_count"]
    def_traffic[0]['volume']['uom'] = DB['config_uom']
    def_traffic[0]['cost']['amount'] = DB["config_price"]
    def_traffic[0]['trafficType'] = DB["config_type"]


# Получение списка активных лотов
def get_lots_refresh(call, delete_minutes=False):
    """

    :param call:
    :param delete_minutes:
    :return:
    """
    uid = call.from_user.id
    response = api.get_lots(uid)
    if response['status']:
        base_u({'id': uid, 'list_lots': json.dumps(response['response'].json()['data'])})
    base_u({'id': uid, 'list_lots': json.dumps(api.get_lots(uid)['active_traffic'])})
    DB = base_g(uid)

    all_lots = json.loads(DB['list_lots'])
    lots = {}
    i = 0
    if delete_minutes:
        for obj in all_lots:
            if all_lots[obj]['type'] == 'min':
                lots[i] = all_lots[obj]
                i += 1
    else:
        if DB['config_type'] == 'data':  # Отсеивание нужного типа трафика
            for obj in all_lots:
                if all_lots[obj]['type'] == 'gb':
                    lots[str(i)] = all_lots[obj]
                    i += 1
        elif DB['config_type'] == 'volume':
            for obj in all_lots:
                if all_lots[obj]['type'] == 'min':
                    lots[i] = all_lots[obj]
                    i += 1
        else:
            lots = all_lots
    return lots


# Проверка на продажу лота
def check_sell(call, bot, uid, lots):
    """

    :param call:
    :param bot:
    :param uid:
    :param lots:
    """
    if uid in cache_lot:
        if len(lots) < len(cache_lot[uid]):
            answer = f'Лот продан\!'
            menu.bot_launch_on(call, bot, answer, False, True)
            time.sleep(3)

    cache_lot[uid] = lots


def send_sms(call):
    """

    :param call:
    """
    uid = call.from_user.id
    base_u({'id': uid, 'status_sms': 1, 'lvl_autorize': 1})
    api.send_sms(uid)


def delete_confrim(call, bot, lid):
    """

    :param call:
    :param bot:
    :param lid:
    """
    uid = call.from_user.id
    DB = base_g(uid)
    lots = json.loads(DB['list_lots'])
    menu.delete_confrim(call, bot, lid, lots)


def delete_yes(call, bot, lid):
    """

    :param call:
    :param bot:
    :param lid:
    """
    uid = call.from_user.id
    api.delete(uid, lid)
    answer = 'Лот успешно удалён\!'
    markup = types.InlineKeyboardMarkup(row_width=2)
    menu.reload(call, bot, answer, markup)
    time.sleep(1)
    profile(call, bot)


def edit_lots(call, bot):
    """

    :param call:
    :param bot:
    """
    uid = call.from_user.id
    response = api.get_lots(uid)
    if response['status']:
        base_u({'id': uid, 'list_lots': json.dumps(response['active_traffic'])})
    DB = base_g(uid)
    lots = json.loads(DB['list_lots'])
    menu.edit_lots(call, bot, lots)


def redactor_lot(call, bot, lid):
    """

    :param call:
    :param bot:
    :param lid:
    """
    uid = call.from_user.id
    if uid not in cache:
        cache[uid] = {'status_lagg': 0, 'status_autosell': 0, 'status_autotop': 0}
    cache[uid]['lid'] = lid

    response = api.get_lots(uid)
    if response['status']:
        base_u({'id': uid, 'list_lots': json.dumps(response['active_traffic'])})
    DB = base_g(uid)
    lots = json.loads(DB['list_lots'])
    menu.redactor_lot(call, bot, lid, lots)


def top(call, bot, lid):
    """

    :param call:
    :param bot:
    :param lid:
    """
    uid = call.from_user.id
    DB = base_g(uid)
    lots = dict(json.loads(DB['list_lots']))
    response = api.top(uid, lid)
    lot = {}
    if response['status']:
        for i in lots:
            lot[0] = i
            if lots[i]['id'] == lid:
                break
        answer_lot = functions.text_lot(lots, lot[0])

        answer = f'Лот "{answer_lot}" \n\- успешно поднят в топ\!'
        log(answer, 1)
        bot.send_message(call.message.chat.id, answer, parse_mode='MarkdownV2')
        time.sleep(2)
        redactor_lot(call, bot, lid)


def name(call, bot, lid):
    pass


def price(call, bot):
    """

    :param call:
    :param bot:
    """
    menu.price(call, bot)
    uid = call.from_user.id
    base_u({'id': uid, 'lvl_redactor': 1})


def price_accept(call, bot):
    """

    :param call:
    :param bot:
    """
    uid = call.from_user.id
    data = call.data

    lid = cache[uid]['lid']
    lots = dict(json.loads(base_g(uid)['list_lots']))
    lot = {}

    for i in lots:
        lot[0] = i
        if lots[i]['id'] == lid:
            break

    price = str(int(data))
    emoji = lots[lot[0]]["emojis"]
    name = True if lots[lot[0]]['name'] != None else False
    data = (name, emoji, price)
    api.rename(uid, lots[lot[0]], data)
    lots = json.loads(base_g(uid)['list_lots'])
    time.sleep(3)
    redactor_lot(call, bot, lid)


def emoji(call, bot, lid):
    """

    :param call:
    :param bot:
    :param lid:
    """
    menu.emoji(call, bot, lid)
    uid = call.from_user.id
    base_u({'id': uid, 'lvl_redactor': 2})


def save(call, bot, lid):
    """

    :param call:
    :param bot:
    :param lid:
    """
    pass


def up(call, bot):
    """

    :param call:
    :param bot:
    """
    uid = call.from_user.id

    lots = get_lots_refresh(call)
    rand_id = random.randint(0, len(lots) - 1)
    lot_id = lots[f'{rand_id}']['id']

    api.top(uid, lot_id)
    menu.up(call, bot)
