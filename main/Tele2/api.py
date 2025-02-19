import json
import time

import requests
from Tele2 import base
from log import log

base_u = base.update_users
base_g = base.get_user

SECURITY_BYPASS_HEADERS = {
    'Connection': 'keep-alive',
    'Tele2-User-Agent': '"mytele2-app/3.17.0"; "unknown"; "Android/9"; "Build/12998710"',
    'X-API-Version': '1',
    'User-Agent': 'okhttp/4.2.0'
}

site_api = 'https://ekt.t2.ru/api'
site_auth = 'https://ekt.t2.ru/auth/realms/tele2-b2c'

MAIN_API = site_api + '/subscribers/'
SMS_VALIDATION_API = site_api + '/validation/number/'
TOKEN_API = site_auth + '/protocol/openid-connect/token'
SECURE_API = site_auth + '/credential-management/security-codes'


def errors(response):
    if response.status_code == 200:
        return {'status': True, 'text': 'Успешно', 'response': response}
    elif response.status_code == 404:
        return {'status': False, 'text': 'Ошибка в ссылке api', 'response': response}
    elif response.status_code == 403:
        return {'status': False, 'text': 'Ошибка запроса', 'response': response}
    elif response.status_code == 401:
        return {'status': False, 'text': 'Ошибка авторизации', 'response': response}
    elif response.text == 'Password authorization unavailable':
        return {'status': False, 'text': 'Почта не подтверждена, в качестве двухфакторной аутентификации.', 'response': response}
    else:
        try:
            log(str(response.reason), 3)
        except:
            log(str(response), 3)
        try:
            log(str(response.json()), 3)
        except:
            log('JSON - не конвертирутся', 3)
        if 'meta' in response.json():
            if 'status' in response.json()['meta']:
                if response.json()['meta']['status'] == 'bp_err_noTraffic':
                    return {'status': False, 'text': 'Недостаточно трафика', 'response': response}
        elif 'error_description' in response.json():
            return {'status': False, 'text': response.json()['error_description'], 'response': response}


def auth(uid):
    DB = base_g(uid)

    s = requests.Session()  # Создание сессии

    data = {"client_id": "digital-suite-web-app", "grant_type": "password", "username": DB["auth_login"],
            "password": DB["auth_password"],
            "password_type": ("password" if DB["status_sms"] == 0 else 'sms_code'), }  # Данные для авторизации
    if DB["status_sms"] == 0:
        data['security_code_token'] = DB['security_code_token']
        data['security_code'] = DB['security_code']
    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    response = s.post(TOKEN_API, data=data)
    response = errors(response)
    if not response['status']:
        return response
    elif response['status']:
        try:
            token = response['response'].json()['access_token']  # Получение токена из успешной авторизации
            s.headers.update({'Authorization': 'Bearer {}'.format(token)})  # Добавление токена в заголовок

            # Сохранение токена в базе данных
            base_u({'id': uid, 'token': token})
            return response
        except:
            return response


def security_code(uid):
    DB = base_g(uid)
    s = requests.Session()  # Создание сессии

    data = {"client_id": "digital-suite-web-app", "grant_type": "password",
            "username": DB["auth_login"], "password": DB["auth_password"],
            "password_type": "password"}  # Данные для авторизации

    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    response = s.post(SECURE_API, json=data)
    response = errors(response)
    return response


def send_sms(uid):
    DB = base_g(uid)
    sms_post_url = SMS_VALIDATION_API + DB["auth_login"]
    s = requests.Session()  # Создание сессии
    s.headers.update({'Authorization': 'Bearer {}'.format(DB["token"])})
    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    response = s.post(sms_post_url, json={'sender': 'Tele2'})
    response = errors(response)
    return response


def sell_lot(uid, lot_for_sell):
    DB = base_g(uid)
    lot = lot_for_sell

    s = requests.Session()  # Создание сессии
    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    s.headers.update({'Authorization': 'Bearer {}'.format(DB["token"])})
    base_api = MAIN_API + DB["auth_login"]
    response = s.put(f'{base_api}/exchange/lots/created', json=lot)
    response = errors(response)
    try:
        price = str(int(lot_for_sell['price']))
    except:
        price = str(int(lot_for_sell['cost']['amount']))
    emoji = lot_for_sell['emojis']
    name = lot_for_sell['name']
    data = (name, emoji, price)
    if response['status']:
        lot_id = response['response'].json()['data']['id']
        rename(uid, lot_id, data)

    return response


def delete(uid, lot_id):
    DB = base_g(uid)
    s = requests.Session()  # Создание сессии
    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    s.headers.update({'Authorization': 'Bearer {}'.format(DB["token"])})
    base_api = MAIN_API + DB["auth_login"]
    response = s.delete(f'{base_api}/exchange/lots/created/{str(lot_id)}')
    response = errors(response)

    return response


def top(uid, lot_id):
    DB = base_g(uid)

    s = requests.Session()  # Создание сессии
    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    s.headers.update({'Authorization': 'Bearer {}'.format(DB["token"])})
    base_api = MAIN_API + DB["auth_login"]
    data = {"lotId": lot_id}
    data = json.dumps(data)

    repeat = 0
    while repeat < 3:
        response = s.put(f'{base_api}/exchange/lots/premium', data)
        if response.ok:
            repeat = 3
        else:
            log('Ошибка поднятия в топ. Повторение попытки.', 3)
            time.sleep(1)
        repeat += 1

    response = errors(response)
    return response

    # Выведение активных лотов на экран!


def get_lots(uid):
    DB = base_g(uid)
    s = requests.Session()  # Создание сессии
    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    s.headers.update({'Authorization': 'Bearer {}'.format(DB["token"])})
    base_api = MAIN_API + DB["auth_login"]
    # Запрос к странице со списком лотов
    response = s.get(f'{base_api}/exchange/lots/created')
    response = errors(response)

    all_traffic = response['response'].json()['data']
    # Фильтрация активных лотов
    active_traffic = {}
    i = 0
    for lot in all_traffic:
        data_lot = {}
        if lot['status'] == 'active':
            data_lot['id'] = lot['id']
            data_lot['value'] = lot['volume']['value']
            data_lot['type'] = lot['volume']['uom']
            data_lot['status'] = lot['isPremium']
            data_lot['name'] = lot['seller']['name']
            data_lot['emojis'] = lot['seller']['emojis']
            data_lot['creationDate'] = lot['creationDate']
            data_lot['price'] = lot['cost']['amount']

            active_traffic[str(i)] = data_lot
            i += 1

    # Вывод на экран только активных лотов
    response = dict(response)
    response['active_traffic'] = active_traffic
    return response

    # Выставить лот


def get_name(uid):
    DB = base_g(uid)
    token = DB["token"]
    s = requests.Session()  # Создание сессии
    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    s.headers.update({'Authorization': 'Bearer {}'.format(token)})
    base_api = MAIN_API + DB["auth_login"]
    response = s.get(f'{base_api}/exchange/seller/name')
    response = errors(response)
    return response


def get_rests(uid, i=0):
    DB = base_g(uid)
    try:
        s = requests.Session()  # Создание сессии
        s.headers.update(
            {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
        s.headers.update({'Authorization': 'Bearer {}'.format(DB["token"])})
        base_api = MAIN_API + DB["auth_login"]
        response = s.get(f'{base_api}/rests')
        response = errors(response)
        if response['status']:
            response_json = response['response'].json()
        else:
            return response
        rests = list(response_json['data']['rests'])
        sellable = [a for a in rests if a['type'] == 'tariff']
        rest_info = {
            'data': int(
                sum(a['remain'] for a in sellable if a['uom'] == 'mb') / 1024),
            'voice': int(
                sum(a['remain'] for a in sellable if a['uom'] == 'min'))
        }
        response = dict(response)
        response['rests'] = rest_info
        return response
    except:
        if i < 10:
            get_rests(uid, i=i + 1)
        else:
            pass


def get_balance(uid):
    DB = base_g(uid)
    s = requests.Session()  # Создание сессии
    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    s.headers.update({'Authorization': 'Bearer {}'.format(DB["token"])})
    base_api = MAIN_API + DB["auth_login"]
    response = s.get(f'{base_api}/balance')
    response = errors(response)
    return response


def get_statistics(uid):
    DB = base_g(uid)
    s = requests.Session()  # Создание сессии
    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    s.headers.update({'Authorization': 'Bearer {}'.format(DB["token"])})
    base_api = MAIN_API + DB["auth_login"]
    response = s.get(f'{base_api}/exchange/statistics')
    response = errors(response)
    return response


def rename(uid, lot_id, data_imp):
    DB = base_g(uid)
    data = {
        "showSellerName": data_imp[0],
        "emojis": data_imp[1],
        "cost": {
            "amount": data_imp[2],
            "currency": "rub"
        }
    }
    data = json.dumps(data)
    s = requests.Session()  # Создание сессии
    s.headers.update(
        {'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
    s.headers.update({'Authorization': 'Bearer {}'.format(DB["token"])})
    base_api = MAIN_API + DB["auth_login"]
    response = s.patch(f'{base_api}/exchange/lots/created/{lot_id}', data)
    response = errors(response)
    return response
