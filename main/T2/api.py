"""
    API доступ к T2 и функционал
"""

import json
import time

import requests

from log import log
from preset import t2b

s = requests.Session()  # Создание сессии
s.headers.update({'T2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными

SECURITY_BYPASS_HEADERS = {
    'Connection': 'keep-alive',
    'T2-User-Agent': '"mytele2-app/3.17.0"; "unknown"; "Android/9"; "Build/12998710"',
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
    """
    Данная функция реализует проверку успешности выполнения запроса по API.
    В случае неудачи, проводится анализ и выдаётся удобный ответ.
    При помощи удобного ответа, можно напрямую передать информацию о причине ошибки.

    :param response: Ответ от сервера T2
    :return: JSON со статусом, отредактированным текстом и самим 'response'
    """
    status = False
    text = ''

    if response.status_code == 200:
        status = True
        text = 'Успешно'
    elif response.status_code == 404:
        text = 'Ошибка в ссылке api'
    elif response.status_code == 403:
        text = 'Ошибка запроса'
    elif response.status_code == 401:
        text = 'Ошибка авторизации'
    elif response.text == 'Password authorization unavailable':
        text = 'Почта не подтверждена, в качестве двух-факторной аутентификации.'
    else:
        if 'reason' in dir(response):
            text = str(response.reason)

        if 'json' in dir(response):
            rj = response.json()
            if 'meta' in response:
                if 'status' in rj['meta']:
                    status_error = rj['meta']['status']

                    if status_error == 'bp_err_noTraffic':
                        text = 'Недостаточно трафика'
                    elif 'error_description' in rj:
                        text = rj['error_description']

        else:
            text = f'Ошибка преобразования JSON. Response:\n{response}'
        log(text, 2)

    return {'status': status, 'text': text, 'response': response}


def auth(uid):
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :return: Ответ сервера
    """
    DB = t2b(uid)

    #DB = {}
    # DB["auth_password"] = '459DxU'
    # DB["auth_login"] = '79920228848'
    # DB["status_sms"] = 1

    data = {"client_id": "digital-suite-web-app", "grant_type": "password", "username": DB["auth_login"],
            "password": DB["auth_password"], "password_type": ("password" if DB["status_sms"] == 0 else 'sms_code'), }  # Данные для авторизации

    if DB["status_sms"] == 0:
        data['security_code_token'] = DB['security_code_token']
        data['security_code'] = ''

    sms_post_url = 'https://ekt.t2.ru/api/validation/number/79920228848'
    res = s.post(sms_post_url, json={'sender': 'T2'})

    response = s.post(TOKEN_API, data=data)

    print(response)

    response = errors(response)

    if not response['status']:
        return response
    elif response['status']:
        try:
            token = response['response'].json()['access_token']  # Получение токена из успешной авторизации
            s.headers.update({'Authorization': 'Bearer {}'.format(token)})  # Добавление токена в заголовок

            # Сохранение токена в базе данных
            data_upd = {'id': uid, 'token': token}
            t2b(uid, data_upd, 'u')

            return response
        except EncodingWarning:
            return response

def security_code(uid):
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :return: Ответ сервера.
    """

    DB = t2b(uid)

    data = {"client_id": "digital-suite-web-app", "grant_type": "password",
            "username": DB["auth_login"], "password": DB["auth_password"],
            "password_type": "password"}  # Данные для авторизации

    response = s.post(SECURE_API, json=data)
    response = errors(response)

    return response


def send_sms(uid):
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :return: Ответ сервера.
    """
    DB = t2b(uid)
    sms_post_url = SMS_VALIDATION_API + DB["auth_login"]

    response = s.post(sms_post_url, json={'sender': 'T2'})
    response = errors(response)
    return response


def sell_lot(uid, lot_for_sell):
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :param lot_for_sell: Данные о том, какой лот необходимо создать.
    :return: Ответ сервера.
    """
    DB = t2b(uid)
    lot = lot_for_sell

    base_api = MAIN_API + DB["auth_login"]
    response = s.put(f'{base_api}/exchange/lots/created', json=lot)
    response = errors(response)
    try:
        price = str(int(lot['price']))
    except TypeError:
        price = str(int(lot['cost']['amount']))
    emoji = lot['emojis']
    name = lot['name']
    data = (name, emoji, price)
    if response['status']:
        lot_id = response['response'].json()['data']['id']
        rename(uid, lot_id, data)

    return response


def delete(uid, lot_id):
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :param lot_id: ID выставленного лота.
    :return: Ответ сервера.
    """
    DB = t2b(uid)

    base_api = MAIN_API + DB["auth_login"]
    response = s.delete(f'{base_api}/exchange/lots/created/{str(lot_id)}')
    response = errors(response)

    return response


def top(uid, lot_id):
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :param lot_id: ID выставленного лота.
    :return: Ответ сервера.
    """
    response = None
    DB = t2b(uid)

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
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :return: Ответ сервера.
    """
    DB = t2b(uid)

    base_api = MAIN_API + DB["auth_login"]
    # Запрос к странице со списком лотов
    repeat = 0
    active_traffic = None
    response = None

    while repeat < 3:
        response = s.get(f'{base_api}/exchange/lots/created')

        active_traffic = {}
        if response:
            all_traffic = response.json()['data']
            # Фильтрация активных лотов

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

            repeat = 3
        else:
            log('Ошибка получения лотов. Повторение попытки.', 3)
            time.sleep(1)
            repeat += 1

    response = errors(response)
    return response, active_traffic

    # Выставить лот


def get_name(uid):
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :return: Ответ сервера.
    """
    DB = t2b(uid)
    token = DB["token"]

    s.headers.update({'Authorization': 'Bearer {}'.format(token)})
    base_api = MAIN_API + DB["auth_login"]
    response = s.get(f'{base_api}/exchange/seller/name')
    response = errors(response)
    return response


def get_rests(uid, i=0):
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :param i: Переменная содержит в себе номер попытки выполнить запрос. (Увеличивается в случае неудач)
    :return: Ответ сервера.
    """
    DB = t2b(uid)
    try:
        base_api = MAIN_API + DB["auth_login"]
        response = s.get(f'{base_api}/rests')
        print(response)
        response = errors(response)
        print(response)

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
    except EncodingWarning:
        if i < 10:
            get_rests(uid, i=i + 1)
        else:
            pass


def get_balance(uid):
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :return: Ответ сервера. Содержит баланс номера телефона.
    """
    DB = t2b(uid)

    base_api = MAIN_API + DB["auth_login"]
    response = s.get(f'{base_api}/balance')
    response = errors(response)
    return response


def get_statistics(uid):
    """

    :param uid: ID выставленного лота.
    :return: Ответ сервера.
    """
    DB = t2b(uid)

    base_api = MAIN_API + DB["auth_login"]
    response = s.get(f'{base_api}/exchange/statistics')
    response = errors(response)
    return response


def rename(uid, lot_id, data_imp):
    """

    :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
    :param lot_id: ID выставленного лота.
    :param data_imp: # Данные лота (Теоретически)
    :return: Ответ сервера.
    """
    DB = t2b(uid)
    data = {
        "showSellerName": data_imp[0],
        "emojis": data_imp[1],
        "cost": {
            "amount": data_imp[2],
            "currency": "rub"
        }
    }
    data = json.dumps(data)

    base_api = MAIN_API + DB["auth_login"]
    response = s.patch(f'{base_api}/exchange/lots/created/{lot_id}', data)
    response = errors(response)
    return response
