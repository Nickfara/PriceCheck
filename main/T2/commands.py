"""
    Команды для Т2 бота
"""

import json
import math
import random
import time

from tg_bot import bot
from T2 import config, menu
from T2.api import T2Api as api

from preset import t2b, text_lot
from log import log
from constants import NUMBER_T2, PASSWORD_T2, SECRET_FORMAT_NUMBER_T2

def_account = config.account
def_traffic = config.add_traffic()
cache = {}
cache_lot = {}
stop_timer = [False]


def auth(call):
    """
    Функция авторизации.
    
    :param call: Данные о команде или сообщении.
    :return: Данные о пользователе.
    """

    uid = call.from_user.id
    DB = t2b(uid)
    data = call.data

    print(DB['stage_authorize'])
    print(DB['status_sms'])

    # Если пользователь не авторизован, происходит авторизация
    if DB['stage_authorize'] < 3:
        # Форматирование номера телефона
        if data[0] == '8':
            data = '7'.join(data.split('8'))
        elif data[0] == '+' and data[1] == '7':
            data = '7'.join(data.split('+7'))

        # 1 Этап - Добавление номера телефона (Номер успешно добавлен)
        if len(str(data)) == 11 and (data[0] == '7') and data[1] == '9' and DB['stage_authorize'] == 0:
            data_upd = {'auth_login': data, 'stage_authorize': 1}
            t2b(uid, data_upd, 'u')
            res = menu.login_password(call)
            return 1

        # 1 Этап - Добавление номера телефона:
        elif DB['stage_authorize'] == 0:
            answer = 'Введите ваш номер телефона, \nв формате: [79000000000]'
            res = menu.login_number(call, answer)
            return 1

        # 2 Этап - Проверка кода подтверждения:
        elif DB['stage_authorize'] == 1:
            # Если включено подтверждение кодом:
            if DB['status_sms'] == 0:
                # Если пароль не указан:
                if len(str(DB['auth_password'])) == 0 or DB['auth_password'] is None:
                    data_upd = {'auth_password': data, 'security_code': ''}
                    t2b(uid, data_upd, 'u')

                response = api.security_code(uid)
                print('хуй')
                print(response)

                # При успешной отправке кода:
                if response['status']:
                    data_upd = {'stage_authorize': 2, 'auth_password': DB['auth_password'],
                                'security_code_token': response['response'].json()['security_code_token']}
                    t2b(uid, data_upd, 'u')
                    res = menu.security_code(call)
                    return 1
            else:
                response = api.send_sms(uid)
                print('ОТПРАВЛОЕНО СМС')
                print(response)
                data_upd = {'stage_authorize': 2}
                t2b(uid, data_upd, 'u')


        # 3 Этап - Проведение и проверка авторизации:
        elif DB['stage_authorize'] == 2:
            response = api.auth(uid)

            # При успешной авторизации:
            if response['status']:
                data_upd = {'stage_authorize': 3, 'status_sms': 0}

                cache[uid] = {'status_run_auto': 0, 'status_lagg': 0}
                t2b(uid, data_upd, 'u')
                update_def_traffic(call)
                return 2

            # При неудаче - возврат к 1 этапу:
            else:
                t2b(uid, type_='d')
                t2b(uid)
                answer = 'Неверные данные, попробуйте сначала\!' \
                         '\nВведите ваш номер телефона, в формате: [79000000000]'
                log(f'При авторизации, были введены неверные данные. \n {response}', 3)
                menu.login_number(call, answer)
                return 0

    # Пользователь уже авторизован.
    else:
        answer = 'Вы уже авторизованы\!'
        log(answer, 3)
        return 2


def admin_auth(call):
    """
    Функция предназначена для авторизации админа.

    :param call: Данные о команде или сообщении
    :return: Bool об успехе или неудаче завершения.
    """

    # deauth(call)
    uid = call.from_user.id
    DB = t2b(uid)
    data = call.data

    # deauth(call)

    # Создание аккаунта:
    if DB is None:
        log('Создание аккаунта')
        t2b(uid)

    # Авторизация в SECRET_FORMAT_NUMBER_T2
    if data == 'Войти админ':
        log(f'Вход в {SECRET_FORMAT_NUMBER_T2}')
        data_upd = {'stage_authorize': 1, 'auth_login': NUMBER_T2, 'auth_password': PASSWORD_T2}
        t2b(uid, data_upd, 'u')
        response = auth(call)
        return response


def deauth(call, lobby=False):
    """
    Функция деавторизации.

    :param call: Данные о команде или сообщении.
    :param lobby: Если выполнено из лобби, выполняется start.
    :return: Boolean о результате работы.
    """
    try:
        uid = call.from_user.id
        DB = t2b(uid)

        if DB:
            t2b(uid, type_='d')

        if lobby:
            menu.start(call.message)

        log('Пользователь удалён.')
        return True

    except KeyError:
        log('Ошибка удаления пользователя!', 3)
        return False


def home_menu(call):
    """
    Функция открытия главного экрана.

    :param call: Данные о команде или сообщении
    """

    uid = call.from_user.id
    cache[uid] = {'status_run_auto': 0, 'status_lagg': 0}
    return True


# Меню настроек
def settings(call):
    """
    Функция генерации и изменения настроек.

    :param call: Данные о команде или сообщении.
    :return: Boolean о результате работы.
    """

    uid = call.from_user.id
    DB = t2b(uid)
    data = call.data

    config_uom = DB['config_uom']
    if DB['lvl_setting'] == 0:
        name_ = ("🌐 *Вид:* Гигабайты" if DB['config_uom'] == "gb" else "☎️ *Вид:* Минуты")
        name2 = ("ГБ" if DB['config_uom'] == "gb" else "МИН")
        answer = f'🛠️ *Настройки\.* \n\nТекущие: \n{name_}\. ' \
                 f'\n📏 *Количество:* {DB["config_count"]}{name2} за {DB["config_price"]}₽' \
                 f'\n🕓 *Интервал:* {DB["config_autotime"]} секунд\.' \
                 f'\n🔂 *Повторы:* {DB["config_repeat"]} раз\(а\)\.'
        res = menu.settings(call, answer)
        return res
    elif DB['lvl_setting'] == 1:
        try:
            int(data)
            data_upd = {'config_autotime': call.message.text}
            t2b(uid, data_upd, 'u')
            return True
        except TypeError:
            answer = '🛠️ *Настройки\.* \n\nНапишите количество секунд, \nчерез которое будут повторяться \nподнятие и выставление\. ' \
                     '\nИсключительно цифрами, например: 5'
            menu.settings(call, answer)
            return False
    elif DB['lvl_setting'] == 2:
        try:
            config_price = int(data)
        except TypeError:
            answer = '🛠️ *Настройки\.* \n\nПринимаются исключительно цифры.'
            menu.settings(call, answer)
            return False

        data_upd = {'config_count': data, 'config_price': math.ceil(config_price * 15) if config_uom == 'gb' else
        {'config_count': data, 'config_price': math.ceil(int(data) / 1.25) if config_uom == 'min' else None}}

        t2b(uid, data_upd, 'u')

        return True

    elif DB['lvl_setting'] == 3:
        try:
            int(data)
            data_upd = {'config_repeat': call.message.text}
            t2b(uid, data_upd, 'u')
            return True
        except TypeError:
            answer = '🛠️ *Настройки\.* \n\nНапишите количество повторов, \nчерез которое бот закончит \nподнятие или ' \
                     'выставление\. Указав 0, повторения будут бесконечны\. ' \
                     '\nИсключительно цифрами, например: 10'
            menu.settings(call, answer)
            return False
    elif DB['lvl_setting'] == 4:
        if data == 'Минуты':
            data_upd = {'config_type': 'voice', 'config_count': 62, 'config_price': 50, 'config_uom': 'min'}
            t2b(uid, data_upd, 'u')
            return True
        elif data == 'Гигабайты':
            data_upd = {'config_type': 'data', 'config_count': 6, 'config_price': 90, 'config_uom': 'gb'}
            t2b(uid, data_upd, 'u')
            return True
        else:
            answer = '🛠️ *Настройки\.* \n\nВыберите нужный для вас тип трафика:'
            menu.settings(call, answer)
            return True


def profile(call):
    """
    Генерация меню профиля.

    :param call: Данные о команде или сообщении
    :return: bool о результате работы.
    """

    allow_voice = None
    allow_data = None
    income = None
    check = True

    uid = call.from_user.id
    response = api.get_rests(uid)

    def auth_error_message(response_):  # Вывод сообщения, об ошибке авторизации
        """

        :param response_:
        """

        if 'Ошибка авторизации' == response_['text']:
            from tg_bot import start
            start(call.message)
            return False
        else:
            menu.error(call)
            return False

    if response['status']:
        allow_traffic = response['rests']
    else:
        log('❌ Ошибка response в функции profile файла commands - get_rests', 3)
        log(response, 3)
        auth_error_message(response)

        return False

    response = api.get_statistics(uid)

    if response['status']:
        statistics = response['response'].json()['data']
    else:
        log('❌ Ошибка response в функции profile файла commands - get_statistics', 3)
        log(response, 3)
        auth_error_message(response)

        return False

    response = api.get_balance(uid)

    if response['status']:
        balance = response['response'].json()['data']['value']
    else:
        log('❌ Ошибка response в функции profile файла commands - get_balance', 3)
        log(response, 3)
        auth_error_message(response)

        return False

    response = api.get_name(uid)

    if response['status']:
        username = response['response'].json()['data']
    else:
        auth_error_message(response)

        return False

    t2b(uid)  # Оно здесь, потому что сначала обновляются данные, потом копируются

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
    answer += f'✅ *Доступно:* {allow_traffic["data"]} ГБ и {allow_traffic["voice"]} МИН\.\n'
    answer += f'🛒 *Продано:* {allow_data} ГБ\ и' \
              f' {allow_voice} МИН\.\n'
    answer += f'📈 *Доход:* {income}₽\.\n\n'
    res = answer
    return res


def timer(answer, at, count, uid, call, DB):
    """
    Работа таймера при запуске бота.

    :param DB: База данных
    :param answer: Текст
    :param at: Время
    :param count: Количество повторений
    :param uid: ID пользователя
    :param call: Данные о команде или сообщении
    """

    rand_time = random.randint(0, 5)  # Рандомизация времени ожидания
    at += rand_time

    if DB['config_repeat'] > 0:
        answer += '\n*Осталось:* ' + str(
            DB['config_repeat'] - count) + ' раз\(а\)'
    second_text = ' секунд' if (str(at)[len(str(at)) - 1] in ('5', '6', '7', '8', '9', '0')
                                or (str(at)[0] == '1' if len(str(at)) > 1 else False)) \
        else (' секунды' if str(at)[len(str(at)) - 1] in ('2', '3', '4') else ' секунда')

    answer3 = answer + '\n*Ожидание:* ' + str(
        at) + second_text  # Первоначальное добавление таймера
    menu.bot_active(call, answer3, True)

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
            second_text2 = ' секунд' if (str(ct)[len(ct) - 1] in ('5', '6', '7', '8', '9', '0')
                                         or ((True if str(at)[0] == '1' else False) if len(str(ct)) > 1 else False)) \
                else (' секунды' if str(ct)[len(ct) - 1] in ('2', '3', '4') else ' секунда')
            answer2 = answer + '\n*Ожидание:* ' + ct + second_text2  # Изменение таймера
            menu.bot_active(call, answer2, True)
    cache[uid]['timer'] = 0
    cache[uid]['status_lagg'] = 0


def run_auto(call, type_=''):
    """
    Запуск работы бота.

    :param call: Данные о команде или сообщении
    :param type_: Тип работы ('sell' - продажа, 'top' - поднятие).
    """

    uid = call.from_user.id
    DB = t2b(uid)

    if uid not in cache:  # Добавление аккаунта в кэш, если его нет
        cache[uid] = {'status_lagg': 0, 'status_run_auto': 0}

    if DB and DB['stage_authorize'] == 3 and cache[uid]['status_run_auto'] == 0 and cache[uid]['status_lagg'] == 0:
        count = 0
        cache[uid]['status_run_auto'] = 1
        seller_lot = [0, 0]

        while cache[uid]['status_run_auto'] == 1:
            lots = get_lots_refresh(call)  # Список активных лотов
            check_sell(call, uid, lots)  # Проверка (Продался ли лот)

            if count == 0:
                seller_lot[0] = len(lots)

            seller_lot[1] = len(lots)

            if count <= DB['config_repeat']:

                if type_ == 'sell':

                    response = api.sell_lot(uid, def_traffic[0])
                    print(response)
                    if response['status']:
                        answer = 'Лот успешно выставлен\!'
                        menu.bot_active(call, answer)
                        time.sleep(2)
                        at = DB['config_autotime']
                        answer = 'Авто\-продажа работает\!\n'
                        timer(answer, at, count, uid, call, DB)
                    else:
                        if 'Недостаточно трафика' == response['text']:
                            answer = 'Недостаточно трафика\!'
                            menu.bot_active(call, answer)
                            time.sleep(2)
                            stop(call)
                        elif 'Ошибка авторизации' == response['text']:
                            from tg_bot import start
                            start(call.message)
                        else:
                            menu.error(call)
                        break
                elif type_ == 'top':
                    if len(lots) > 0:
                        rand_id = random.randint(0, len(lots) - 1)
                        lot_id = lots[f'{rand_id}']['id']
                        if not lots[str(rand_id)]['status']:
                            if lots[str(rand_id)]['status'] != 'revoked':

                                if DB['config_repeat'] != 0:
                                    count += 1
                                if count <= DB['config_repeat']:
                                    response = api.top(uid, lot_id)
                                    if response:
                                        if response['status']:
                                            answer_lot = text_lot(lots, f'{rand_id}')
                                            answer = f'Лот успешно поднят в топ\:\n\n{answer_lot}'
                                            log('Лот поднят в топ!')
                                            menu.bot_active(call, answer)
                                            time.sleep(2)

                                            at = DB['config_autotime']
                                            answer = 'Авто\-поднятие работает\!\n'
                                            timer(answer, at, count, uid, call, DB)
                                        else:
                                            if 'Ошибка авторизации' == response['text']:
                                                from tg_bot import start
                                                start(call.message)
                                                break
                                            else:
                                                answer = 'Данный лот уже продан\!' if 'is not in ACTIVE status.' in str(
                                                    response['text']) else str(response['text'])
                                                log(answer, 3)
                                                menu.bot_active(call, answer)
                                                time.sleep(2)
                                else:
                                    answer = f'Авто\-поднятие завершено\!'
                                    answer += f'\nПродано: {seller_lot[0] - seller_lot[1]} лотов за сеанс\.'
                                    log(answer)
                                    menu.bot_active(call, answer, sell_check=True)
                                    stop(call)
                                    break

                            else:
                                answer = f'Попался удалённый лот\!'
                                log(answer, 3)
                                menu.bot_active(call, answer)
                        else:
                            answer = f'Попался лот находящийся уже в топе\!'
                            log(answer, 3)
                            menu.bot_active(call, answer)
                    else:
                        answer = f'Лотов нет\!\n\n'
                        log(answer, 3)
                        menu.bot_active(call, answer, )
                        stop(call)
                        break
                else:
                    answer = 'Неверный тип запуска!'
                    log(answer, 3)
    else:
        if not DB or DB['stage_authorize'] != 3:
            answer = 'Авторизуйтесь, используя команду: /auth'
            deauth(call)
        elif cache[uid]['status_run_auto'] != 0:
            answer = 'Цикл авто-продажи уже запущен\! cache[uid][\'status_run_auto\'] = 1'
        elif cache[uid]['status_lagg'] != 0:
            answer = 'Ожидание после выставления не окончено\! cache[uid][\'status_lagg\'] = 1'
        else:
            answer = 'Неизвестная ошибка в run_auto!'

        log(answer, 3)


def stop(call):
    """
    Остановка работы бота.

    :param call: Данные о команде или сообщении
    """
    uid = call.from_user.id

    if uid in cache:
        cache[uid]['status_run_auto'] = 0
        stop_timer[0] = True
        time.sleep(1.5)  # Ожидание для безопасности
        get_lots = api.get_lots(uid)
        response = get_lots[0]
        active_traffic = get_lots[1]

        if response['status']:
            data_upd = {'list_lots': json.dumps(active_traffic)}  # Обновление списка лотов
            t2b(uid, data_upd, 'u')
        else:
            log(response['text'], 3)
            menu.bot_active(call, response['text'])

    res = menu.home(call)
    return res


def remove_minutes_lots(call):
    """

    :param call: Данные о команде или сообщении
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

    menu.remove_minutes_lots(call, answer)
    time.sleep(3)
    res = menu.home(call)
    return True


def update_def_traffic(call):
    """

    :param call: Данные о команде или сообщении
    """
    uid = call.from_user.id
    DB = t2b(uid)
    def_traffic[0]['volume']['value'] = DB["config_count"]
    def_traffic[0]['volume']['uom'] = DB['config_uom']
    def_traffic[0]['cost']['amount'] = DB["config_price"]
    def_traffic[0]['trafficType'] = DB["config_type"]

    return True


def get_lots_refresh(call, delete_minutes=False):
    """
    Получение списка активных лотов.

    :param call: Данные о команде или сообщении
    :param delete_minutes: bool об: удаляются ли минуты или нет. Умолчание: 'False'.
    :return:
    """
    uid = call.from_user.id
    get_lots = api.get_lots(uid)
    response = get_lots[0]['response']
    active_lots = get_lots[1]
    lots = {}

    if response.ok:
        data_upd = {'list_lots': json.dumps(response.json()['data'])}
        t2b(uid, data_upd, 'u')

        data_upd = {'list_lots': json.dumps(active_lots)}
        t2b(uid, data_upd, 'u')
        DB = t2b(uid)

        all_lots = json.loads(DB['list_lots'])

        i = 0
        type_ = DB['config_type']
        type_ = 'gb' if type_ == 'data' else 'min' if type_ == 'volume' else False

        # Отсеивание нужного типа трафика
        if type_:
            for obj in all_lots:
                if delete_minutes:
                    type_ = 'min'
                if all_lots[obj]['type'] == type_:
                    lots[str(i)] = all_lots[obj]
                    i += 1
        else:
            lots = all_lots

        return lots

    return lots


def check_sell(call, uid, lots):
    """
    Проверка на продажу лота

    :param call: Данные о команде или сообщении.
    :param uid: ID пользователя.
    :param lots: Список всех активных лотов.
    """

    if uid in cache_lot:
        if len(lots) < len(cache_lot[uid]):
            answer = f'Лот продан\!'
            menu.bot_active(call, answer, sell_check=True)
            time.sleep(3)
            return True

    cache_lot[uid] = lots
    return False


def send_sms(call):
    """
    Отправка СМС

    :param call: Данные о команде или сообщении
    """

    uid = call.from_user.id
    data_upd = {'status_sms': 1, 'stage_authorize': 1}
    t2b(uid, data_upd, 'u')
    response = api.send_sms(uid)
    return response['status']


def delete_confirm(call, lid):
    """
    Подтверждение удаления лота.

    :param call: Данные о команде или сообщении.
    :param lid: ID лота.
    """

    uid = call.from_user.id
    DB = t2b(uid)
    lots = json.loads(DB['list_lots'])
    lot_text = ''

    for lot in lots:
        lot_text = f'_{str(lots[lot]["value"])}_' + (
            '_ГБ_ ' if lots[lot]['type'] == 'gigabyte' else ' минуты ') + \
                   f'за _{str(int(lots[lot]["price"]))}₽_'
        if lots[lot]['id'] == lid:
            break

    answer = f'Вы действительно хотите снять лот: {lot_text} с продажи\?'

    res = menu.delete_confirm(call, lid, answer)
    return res


def delete_yes(call, lid):
    """
    Удаление лота.

    :param call: Данные о команде или сообщении.
    :param lid: ID лота.
    """

    uid = call.from_user.id
    response = api.delete(uid, lid)

    if response:
        answer = 'Лот успешно удалён\!'
    else:
        answer = 'Возникла ошибка при удалении\!'

    row_width = 2

    menu.send(call, answer, (), row_width)
    time.sleep(1)

    res = profile(call)
    return res


def edit_lots(call):
    """
    Меню редактирование лотов.

    :param call: Данные о команде или сообщении
    """
    uid = call.from_user.id
    get_lots = api.get_lots(uid)
    response = get_lots['response']

    if response['status']:
        data_upd = {'list_lots': json.dumps(['active_traffic'])}
        t2b(uid, data_upd, 'u')

    DB = t2b(uid)
    lots = json.loads(DB['list_lots'])
    res = menu.get_lots(call, lots)
    return res


def redactor_lot(call, lid):
    """
    Редактирование лота.

    :param call: Данные о команде или сообщении
    :param lid: ID лота.
    """
    uid = call.from_user.id
    if uid not in cache:
        cache[uid] = {'status_lagg': 0, 'status_run_auto': 0}
    cache[uid]['lid'] = lid

    response = api.get_lots(uid)
    if response['status']:
        data_upd = {'list_lots': json.dumps(response['active_traffic'])}
        t2b(uid, data_upd, 'u')

    DB = t2b(uid)
    lots = json.loads(DB['list_lots'])
    res = menu.redactor_lot(call, lid, lots)
    return res


# noinspection PyTypeChecker
def top(call, lid):
    """

    :param call: Данные о команде или сообщении
    :param lid:
    """
    uid = call.from_user.id
    DB = t2b(uid)
    lots = dict(json.loads(DB['list_lots']))
    response = api.top(uid, lid)
    lot = {}
    if response:
        if response['status']:
            for i in lots:
                lot[0] = i
                if lots[i]['id'] == lid:
                    break
            answer_lot = text_lot(lots, lot[0])

            answer = f'Лот "{answer_lot}" \n\- успешно поднят в топ\!'
            log(answer)
            bot.send_message(call.message.chat.id, answer, parse_mode='MarkdownV2')
            time.sleep(2)
            res = redactor_lot(call, lid)
            return res


def name(call_, lid_):
    """

    :param call_: Данные о команде или сообщении
    :param lid_:
    """
    return call_, lid_


def price(call):
    """

    :param call: Данные о команде или сообщении
    """

    res = menu.price(call)
    uid = call.from_user.id
    data_upd = {'lvl_redactor': 1}
    t2b(uid, data_upd, 'u')
    return res


# noinspection PyTypeChecker
def price_accept(call):
    """

    :param call: Данные о команде или сообщении
    """
    uid = call.from_user.id
    data = call.data

    lid = cache[uid]['lid']
    lots = dict(json.loads(t2b(uid)['list_lots']))
    lot = {}

    for i in lots:
        lot[0] = i
        if lots[i]['id'] == lid:
            break

    price_ = str(int(data))
    emoji_ = lots[lot[0]]["emojis"]
    name_ = True if lots[lot[0]]['name'] is not None else False
    data = (name_, emoji_, price_)
    api.rename(uid, lots[lot[0]], data)
    time.sleep(3)
    res = redactor_lot(call, lid)
    return res


def emoji(call, lid):
    """

    :param call: Данные о команде или сообщении
    :param lid:
    """
    res = menu.emoji(call, lid)
    uid = call.from_user.id
    data_upd = {'lvl_redactor': 2}
    t2b(uid, data_upd, 'u')
    return res


def save(call, lid):
    """

    :param call: Данные о команде или сообщении
    :param lid:
    """
    return call, lid


def up(call):
    """

    :param call: Данные о команде или сообщении
    """
    uid = call.from_user.id

    lots = get_lots_refresh(call)

    print('lots')
    print(lots)

    if len(lots) > 0:
        rand_id = random.randint(0, len(lots) - 1)
        lot_id = lots[f'{rand_id}']['id']

        response = api.top(uid, lot_id)
        if response:
            return True
        else:
            return False
    else:

        return False
