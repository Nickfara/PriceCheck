"""
    Команды для Т2 бота
"""

import json
import math
import random
import time

from handlers_tgBot import bot
from T2 import config, menu
from T2.session_manager import get_api

from functions import (text_lot, t2b)
from log import log
from constants import (NUMBER_T2, PASSWORD_T2, SECRET_FORMAT_NUMBER_T2)

def_account = config.account
def_traffic = config.add_traffic()
cache = {}
cache_lot = {}
stop_timer = [False]


class Auth:
    @staticmethod
    def stage_filter(call):
        uid = call.from_user.id
        DB = t2b(uid)
        data = call.data

        if DB['stage_authorize'] < 3:
            if DB['stage_authorize'] == 0:
                return Auth.stage_0_login_number(uid, DB, data, call)
            elif DB['stage_authorize'] == 1:
                return Auth.stage_1_password_or_sms(uid, DB, data, call)
            elif DB['stage_authorize'] == 2:
                return Auth.stage_2_complete_auth(uid, DB, data, call)
        else:
            log("Уже авторизован", 3)
            return 2

    @staticmethod
    def stage_0_login_number(uid, DB, data, call):
        phone = normalize_phone_number(data)
        if len(phone) == 11 and phone.startswith('79'):
            t2b(uid, {'auth_login': phone, 'stage_authorize': 1}, 'u')
            menu.login_password(call)
            return 1
        else:
            menu.login_number(call, 'Введите номер телефона в формате 7900...')
            return 1

    @staticmethod
    def stage_1_password_or_sms(uid, DB, data, call):
        api = get_api(uid)

        if DB['status_sms'] == 0:
            if not DB.get('auth_password'):
                t2b(uid, {'auth_password': data}, 'u')

            response = api.send_security_code(uid)
            if response and 'security_code_token' in response:
                t2b(uid, {
                    'stage_authorize': 2,
                    'security_code_token': response['security_code_token']
                }, 'u')
                menu.security_code(call)
                return True
            else:
                log("Ошибка отправки security code", 3)
        else:
            api.send_sms_code()
            t2b(uid, {'stage_authorize': 2}, 'u')
            menu.sms(call)
            return True
        return None

    @staticmethod
    def stage_2_complete_auth(uid, DB, data, call):
        api = get_api(uid)
        try:
            if DB['status_sms'] == 0:
                token = api.auth_with_password(DB['auth_login'], DB['security_code'], DB['security_code_token'], DB['auth_password'])
            else:
                token = api.auth_with_code(DB['auth_login'], data)

            if token:
                access_token, refresh_token = token
                t2b(uid, {
                    'token': access_token,
                    'refresh_token': refresh_token,
                    'stage_authorize': 3,
                    'status_sms': 0
                }, 'u')
                update_def_traffic(call)
                cache[uid] = {'status_run_auto': 0, 'status_lagg': 0}
                return 2
        except Exception as e:
            log(f"Ошибка авторизации: {e}", 3)
            t2b(uid, type_='d')
            t2b(uid)
            menu.login_number(call, 'Неверные данные. Введите номер телефона в формате 7900...')
            return 0


class Settings():
    @staticmethod
    def stage_filter(call):
        uid = call.from_user.id
        DB = t2b(uid)
        data = call.data

        config_uom = DB['config_uom']

        if DB['lvl_setting'] == 0:
            Settings.open_menu(uid, DB, data, config_uom, call)
        elif DB['lvl_setting'] == 1:
            Settings.interval(uid, DB, data, config_uom, call)
        elif DB['lvl_setting'] == 2:
            Settings.count(uid, DB, data, config_uom, call)
        elif DB['lvl_setting'] == 3:
            Settings.repeat(uid, DB, data, config_uom, call)
        elif DB['lvl_setting'] == 4:
            Settings.type(uid, DB, data, config_uom, call)

    @staticmethod
    def open_menu(uid, DB, data, config_uom, call):
        name_ = ("🌐 *Вид:* Гигабайты" if DB['config_uom'] == "gb" else "☎️ *Вид:* Минуты")
        name2 = ("ГБ" if DB['config_uom'] == "gb" else "МИН")
        answer = f'🛠️ *Настройки\.* \n\nТекущие: \n{name_}\. ' \
                 f'\n📏 *Количество:* {DB["config_count"]}{name2} за {DB["config_price"]}₽' \
                 f'\n🕓 *Интервал:* {DB["config_autotime"]} секунд\.' \
                 f'\n🔂 *Повторы:* {DB["config_repeat"]} раз\(а\)\.'
        res = menu.settings(call, answer)
        return res

    @staticmethod
    def interval(uid, DB, data, config_uom, call):
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

    @staticmethod
    def count(uid, DB, data, config_uom, call):
        uid = call.from_user.id
        DB = t2b(uid)
        data = call.data

        config_uom = DB['config_uom']

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

    @staticmethod
    def repeat(uid, DB, data, config_uom, call):
        uid = call.from_user.id
        DB = t2b(uid)
        data = call.data

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

    @staticmethod
    def type(uid, DB, data, config_uom, call):
        uid = call.from_user.id
        DB = t2b(uid)
        data = call.data

        config_uom = DB['config_uom']

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


def admin_auth(call):
    """
    Авторизация под админским номером.

    :param call: CallbackQuery
    :return: Bool об успехе или неудаче завершения.
    """
    deauth(call)  # Деавторизация, в качестве исключения ошибок.
    uid = call.from_user.id
    log(f'Вход в {SECRET_FORMAT_NUMBER_T2}')
    t2b(uid, {
        'auth_login': NUMBER_T2,
        'auth_password': PASSWORD_T2,
        'status_sms': 0,
        'stage_authorize': 1  # 1 в случае если выше 0
    }, 'u')
    return Auth.stage_filter(call)


def deauth(call, lobby=False):
    """
    Сброс авторизации.

    :param call: CallbackQuery.
    :param lobby: Если выполнено из лобби, выполняется start.
    :return: Boolean о результате работы.
    """
    uid = call.from_user.id
    try:
        t2b(uid, type_='d')
        if lobby:
            menu.start(call.message)
        log(f'Пользователь {uid} удалён.')
        return True
    except KeyError:
        log(f'Ошибка удаления пользователя {uid}', 3)
        return False


def home_menu(call):
    """
    Функция открытия главного экрана.

    :param call: CallbackQuery
    """

    uid = call.from_user.id
    cache[uid] = {'status_run_auto': 0, 'status_lagg': 0}
    return True


def profile(call):
    """
    Генерация меню профиля.

    :param call: Объект CallbackQuery
    """
    uid = call.from_user.id
    api = get_api(uid)

    try:
        rests = api.get_rests()
        stats = api.get_statistics()
        balance = api.get_balance()
        name = api.get_name()
    except Exception as e:
        log(f'Ошибка при запросе профиля: {e}', 3)
        menu.error(call)
        return False

    if not all([rests, stats, balance, name]):
        log(f'Некорректные данные в профиле: rests={rests}, stats={stats}, balance={balance}, name={name}', 3)
        menu.error(call)
        return False

    # Форматирование чисел
    def fmt(num):
        s = f"{int(num):,}".replace(',', "'")
        return s

    answer = (
        f"👤 *Профиль*\n\n"
        f"Здравствуйте, {name['data']}!\n\n"
        f"💰 *Баланс:* _{fmt(balance)}₽_\n"
        f"✅ *Доступно:* {rests['data']} ГБ и {rests['voice']} МИН\n"
        f"🛒 *Продано:* {fmt(stats['soldData']['value'])} ГБ и {fmt(stats['soldVoice']['value'])} МИН\n"
        f"📈 *Доход:* {fmt(stats['totalIncome']['amount'])}₽\n"
    )

    return answer


def timer(answer, at, count, uid, call, DB):
    """
    Работа таймера при запуске бота.

    :param DB: База данных
    :param answer: Текст
    :param at: Время
    :param count: Количество повторений
    :param uid: ID пользователя
    :param call: CallbackQuery
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


def run_auto(call, type_='sell'):
    """
    Запускает авто-продажу или авто-поднятие.

    :param call: CallbackQuery
    :param type_: 'sell' или 'top'
    """
    uid = call.from_user.id
    DB = t2b(uid)
    api = get_api(uid)

    if DB['stage_authorize'] != 3:
        log("Пользователь не авторизован", 3)
        menu.bot_active(call, "Авторизуйтесь, используя команду: /auth")
        return

    if cache.get(uid, {}).get('status_run_auto') == 1:
        log("Автоматическая работа уже запущена", 3)
        menu.bot_active(call, "Цикл уже запущен!")
        return

    cache[uid] = {'status_run_auto': 1, 'status_lagg': 0}
    count = 0
    seller_lot = [0, 0]

    while cache[uid]['status_run_auto']:
        lots = get_lots_refresh(call)  # Список активных лотов
        check_sell(call, uid, lots)  # Проверка (Продался лота на факт продажи)

        if count == 0:
            seller_lot[0] = len(lots)
        seller_lot[1] = len(lots)

        if count >= DB['config_repeat'] and DB['config_repeat'] > 0:
            break

        if type_ == 'sell':
            result = api.sell_lot(def_traffic[0])
            if result:
                menu.bot_active(call, "Лот успешно выставлен!")
                time.sleep(2)
                timer("Авто-продажа работает", DB['config_autotime'], count, uid, call, DB)
            else:
                menu.bot_active(call, "Ошибка при выставлении лота.")
                stop(call)
                break
        elif type_ == 'top':
            if lots:
                rand_id = random.choice(list(lots.keys()))
                lot_id = lots[rand_id]['id']
                result = api.top(lot_id)
                if result:
                    menu.bot_active(call, f"Лот #{lot_id} успешно поднят!")
                    time.sleep(2)
                    timer("Авто-поднятие работает", DB['config_autotime'], count, uid, call, DB)
                else:
                    menu.bot_active(call, "Ошибка при поднятии в топ.")
                    stop(call)
                    break
            else:
                menu.bot_active(call, "Нет доступных лотов.")
                stop(call)
                break

        count += 1

    stop(call)


def stop(call):
    """
    Остановка автоматической работы.

    :param call: CallbackQuery
    """
    uid = call.from_user.id
    cache[uid]['status_run_auto'] = 0
    stop_timer[0] = True

    api = get_api(uid)
    lots = api.get_active_lots()
    if lots:
        t2b(uid, {'list_lots': json.dumps(lots)}, 'u')
    else:
        log("Не удалось получить активные лоты", 3)

    return menu.home(call)


def remove_minutes_lots(call):
    """

    :param call: CallbackQuery
    """

    uid = call.from_user.id
    DB = t2b(uid)

    api = get_api(uid)
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

    :param call: CallbackQuery
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
    Получение активных лотов с возможностью фильтрации по типу

    :param call: CallbackQuery
    :param delete_minutes: bool, если True — фильтровать только минуты
    """
    uid = call.from_user.id
    api = get_api(uid)
    DB = t2b(uid)

    response = api.get_active_lots()
    if not response:
        log('Ошибка при получении лотов', 3)
        return {}

    # Фильтрация
    type_filter = 'min' if delete_minutes else ('gb' if DB['config_type'] == 'data' else 'min')
    filtered = {str(i): lot for i, lot in enumerate(response) if lot['volume']['uom'] == type_filter}

    # Сохраняем в БД (на всякий случай)
    t2b(uid, {'list_lots': json.dumps(filtered)}, 'u')

    return filtered


def check_sell(call, uid, lots):
    """
    Проверка на продажу лота

    :param call: CallbackQuery.
    :param uid: ID пользователя.
    :param lots: Список всех активных лотов.
    """

    if uid in cache_lot and len(lots) < len(cache_lot[uid]):
        log("Лот продан", 2)
        menu.bot_active(call, "Лот продан!", sell_check=True)
        time.sleep(2.5)
        return True

    cache_lot[uid] = lots
    return False


def send_sms(call):
    """
    Отправка SMS с кодом подтверждения
    :param call: CallbackQuery
    """
    uid = call.from_user.id
    t2b(uid, {'status_sms': 1, 'stage_authorize': 1}, 'u')
    result = Auth.stage_filter(call)
    return bool(result)


def delete_confirm(call, lid):
    """
    Подтверждение удаления лота.

    :param call: CallbackQuery.
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

    :param call: CallbackQuery.
    :param lid: ID лота.
    """

    uid = call.from_user.id
    DB = t2b(uid)

    api = get_api(uid)
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

    :param call: CallbackQuery
    """
    uid = call.from_user.id
    DB = t2b(uid)

    api = get_api(uid)
    get_lots = api.get_lots(uid)
    response = get_lots['response']

    if response:
        data_upd = {'list_lots': json.dumps(['active_traffic'])}
        t2b(uid, data_upd, 'u')

    DB = t2b(uid)
    lots = json.loads(DB['list_lots'])
    res = menu.get_lots(call, lots)
    return res


def redactor_lot(call, lid):
    """
    Редактирование лота.

    :param call: CallbackQuery
    :param lid: ID лота.
    """
    uid = call.from_user.id
    DB = t2b(uid)

    api = get_api(uid)

    if uid not in cache:
        cache[uid] = {'status_lagg': 0, 'status_run_auto': 0}
    cache[uid]['lid'] = lid

    response = api.get_lots(uid)
    if response:
        data_upd = {'list_lots': json.dumps(response['active_traffic'])}
        t2b(uid, data_upd, 'u')

    DB = t2b(uid)
    lots = json.loads(DB['list_lots'])
    res = menu.redactor_lot(call, lid, lots)
    return res


# noinspection PyTypeChecker
def top(call, lid):
    """

    :param call: CallbackQuery
    :param lid:
    """
    uid = call.from_user.id
    DB = t2b(uid)

    api = get_api(uid)
    lots = dict(json.loads(DB['list_lots']))
    response = api.top(uid, lid)
    lot = {}
    if response:
        if response:
            for i in lots:
                lot[0] = i
                if lots[i]['id'] == lid:
                    answer_lot = text_lot(lots, lot[0])

                    answer = f'Лот "{answer_lot}" \n\- успешно поднят в топ\!'
                    log(answer)
                    bot.send_message(call.message.chat.id, answer, parse_mode='MarkdownV2')
                    break

            time.sleep(2)
            res = redactor_lot(call, lid)
            return res


def name(call_, lid_):
    """

    :param call_: CallbackQuery
    :param lid_:
    """
    return call_, lid_


def price(call):
    """

    :param call: CallbackQuery
    """

    res = menu.price(call)
    uid = call.from_user.id
    data_upd = {'lvl_redactor': 1}
    t2b(uid, data_upd, 'u')
    return res


# noinspection PyTypeChecker
def price_accept(call):
    """

    :param call: CallbackQuery
    """
    uid = call.from_user.id
    DB = t2b(uid)

    api = get_api(uid)
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

    :param call: CallbackQuery
    :param lid:
    """
    res = menu.emoji(call, lid)
    uid = call.from_user.id
    data_upd = {'lvl_redactor': 2}
    t2b(uid, data_upd, 'u')
    return res


def save(call, lid):
    """

    :param call: CallbackQuery
    :param lid:
    """
    return call, lid


def up(call):
    """

    :param call: CallbackQuery
    """
    uid = call.from_user.id
    DB = t2b(uid)

    api = get_api(uid)

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


def normalize_phone_number(number: str) -> str:
    """
    Приведение номера к формату 79XXXXXXXXX
    """
    number = number.strip()
    if number.startswith('+7'):
        return '7' + number[2:]
    elif number.startswith('8'):
        return '7' + number[1:]
    return number
