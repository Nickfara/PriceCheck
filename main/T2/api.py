"""
    API доступ к T2 и функционал
"""

import json
import time

import requests

from requests.exceptions import JSONDecodeError, RequestException

from log import log
from functions import t2b



from T2.constants import SECURITY_BYPASS_HEADERS, MAIN_API, SMS_VALIDATION_API, TOKEN_API, SECURE_VALIDATION_API


def safe_request(method, url, json_=None, headers=None, params=None, timeout=10):
    """

    :param method: 
    :param url: 
    :param json_: 
    :param headers: 
    :param params: 
    :param timeout: 
    :return: 
    """
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            json=json_,
            params=params,
            headers=headers,
            timeout=timeout
        )

        if not response.ok:
            log(f"[{method.upper()}] HTTP {response.status_code}: {response.text}", 2)
            return None

        try:
            return response.json()
        except (JSONDecodeError, ValueError) as e:
            log(f"[{method.upper()}] Ошибка парсинга JSON: {e} \nОтвет: {response.text}", 2)
            return None

    except RequestException as e:
        log(f"[{method.upper()}] Сетевая ошибка: {e}")
        return None


class T2Api:
    """
    api для работы с Т2 market.
    """
    s = requests.Session()  # Создание сессии
    s.headers.update({'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными

    access_token: str

    def __init__(self, phone_number: str, access_token: str = '',
                 refresh_token: str = ''):
        base_api = MAIN_API + phone_number
        self.phone_number = phone_number
        self.market_api = f'{base_api}/exchange/lots/created'
        self.top_api = f'{base_api}/exchange/lots/premium'
        self.rests_api = f'{base_api}/rests'
        self.profile_api = f'{base_api}/profile'
        self.name_api = f'{base_api}/exchange/seller/name'
        self.balance_api = f'{base_api}/balance'
        self.statistics_api = f'{base_api}/exchange/statistics'
        self.sms_post_url = SMS_VALIDATION_API + phone_number
        self.security_post_url = SECURE_VALIDATION_API
        self.auth_post_url = TOKEN_API
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("session", None)  # безопасно удалить requests.Session
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.session = requests.Session()  # пересоздаем

    def __aenter__(self):
        self.session = self.s(headers={
            'Authorization': f'Bearer {self.access_token}',
            **SECURITY_BYPASS_HEADERS
        })
        return self

    def __aexit__(self, *args):
        self.session.close()

    def check_if_authorized(self):
        """

        :return: 
        """
        url = self.profile_api
        response = safe_request("GET", url)
        return response

    def send_sms_code(self):
        """

        :return: 
        """
        url = self.sms_post_url
        payload = {'sender': 'Tele2'}

        data = safe_request("POST", url, json_=payload)

        return data

    def send_security_code(self, uid):
        """

        :param uid: 
        :return: 
        """
        url = self.security_post_url
        DB = t2b(uid)
        payload = {
            "client_id": "digital-suite-web-app",
            "grant_type": "password",
            "username": DB["auth_login"],
            "password": DB["auth_password"],
            "password_type": "password"
        }

        data = safe_request("POST", url, json_=payload)

        return data

    def auth_with_code(self, sms_code: str):
        """

        :param phone_number: 
        :param sms_code: 
        :return: 
        """
        url = self.auth_post_url
        payload = {
            'client_id': 'digital-suite-web-app',
            'grant_type': 'password',
            'username': self.phone_number,
            'password': sms_code,
            'password_type': 'sms_code'
        }

        data = safe_request("POST", url, json_=payload)

        if data:
            return data['access_token'], data['refresh_token']

    def auth_with_password(self, security_code_token: str, password: str):
        """

        :param phone_number: 
        :param security_code_token: 
        :param password: 
        :return: 
        """
        url = self.auth_post_url
        payload = {
            'client_id': 'digital-suite-web-app',
            'grant_type': 'password',
            'username': self.phone_number,
            'password': password,
            'password_type': 'password',
            'security_code_token': security_code_token
        }

        data = safe_request("POST", url, data=payload)

        if data:
            return data['access_token'], data['refresh_token']

    def refresh_tokens(self, refresh_token: str):
        """

        :param refresh_token: 
        :return: 
        """
        url = self.auth_post_url
        payload = {
            'client_id': 'digital-suite-web-app',
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }

        data = safe_request("POST", url, data=payload)

        if data:
            return data['access_token'], data['refresh_token']

    def sell_lot(self, lot):
        """

        :param lot: 
        :return: 
        """
        url = self.market_api
        update_data = {
            'trafficType': lot['lot_type'],
            'cost': {'amount': lot['price'], 'currency': 'rub'},
            'volume': {'value': lot['amount'],
                       'uom': 'min' if lot['lot_type'] == 'voice' else 'gb'}
        }

        result = safe_request("PUT", url, json_=update_data)
        return result

    def top(self, lot_id):
        """

        :param lot_id: 
        :return: 
        """
        url = self.top_api
        update_data = {"lotId": lot_id}
        result = None
        repeat = 0

        while repeat < 3:
            result = safe_request("PUT", url, json_=update_data)
            if result:
                return result
            else:
                log('Ошибка поднятия в топ. Повторение попытки.', 3)
                time.sleep(1)
            repeat += 1
        return result

    @staticmethod
    def patch_name(uid, lot_id, data_imp):
        """

        :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
        :param lot_id: ID выставленного лота.
        :param data_imp: # Данные лота (Теоретически)
        :return: Ответ сервера.
        """

        DB = t2b(uid)
        base_api = MAIN_API + DB["auth_login"]
        url = f'{base_api}/exchange/lots/created/{lot_id}'
        data = {
            "showSellerName": data_imp[0],
            "emojis": data_imp[1],
            "cost": {
                "amount": data_imp[2],
                "currency": "rub"
            }
        }
        data = json.dumps(data)

        return safe_request("PATCH", url, json_=data)

    def return_lot(self, lot_id):
        """

        :param lot_id: 
        :return: 
        """
        url = f'{self.market_api}/{lot_id}'

        return safe_request("DELETE", url)

    def get_balance(self):
        """

        :return: 
        """
        url = self.balance_api

        response = safe_request("GET", url)
        if response:
            return response['data']['value']

        return response

    def get_active_lots(self):
        """

        :return: 
        """
        url = self.market_api

        response = safe_request("GET", url)
        if response:
            lots = list(response['data'])
            active_lots = [a for a in lots if a['status'] == 'active']
            return active_lots

        return response

    def get_rests(self):
        """

        :return: 
        """
        url = self.rests_api

        response = safe_request("GET", url)

        if response:
            rests = list(response['data']['rests'])
            sellable = [a for a in rests if a['type'] == 'tariff']

            return {
                'data': int(
                    sum(a['remain'] for a in sellable if a['uom'] == 'mb') / 1024),
                'voice': int(
                    sum(a['remain'] for a in sellable if a['uom'] == 'min'))
            }

        return response

    def get_name(self):
        """

        :return: Ответ сервера.
        """

        url = self.name_api
        response = safe_request("GET", url)

        return response

    def get_statistics(self):
        """

        :return: 
        """
        url = self.statistics_api
        response = safe_request("GET", url)

        return response
