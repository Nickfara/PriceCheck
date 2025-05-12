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
        self.s = requests.Session()  # пересоздаем

    def __aenter__(self):
        self.s(headers={
            'Authorization': f'Bearer {self.access_token}',
            **SECURITY_BYPASS_HEADERS
        })
        return self

    def __aexit__(self, *args):
        self.s.close()
    
    def safe_request(self, method, url: str, json_: dict = None, data: dict = None, headers: dict = None, params=None,
                     timeout=10):
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
            response = self.s.request(
                method=method.upper(),
                url=url,
                json=json_,
                data=data,
                params=params,
                headers=headers,
                timeout=timeout
            )

            if not response.ok:
                log(f"[{method.upper()}] HTTP {response.status_code}: {response.text}", 2)

                if response.status_code == 401 and self.refresh_token:
                    log("Токен истёк. Обновляю...", 2)
                    new_tokens = self.refresh_tokens(self.refresh_token)
                    if new_tokens:
                        self.access_token, self.refresh_token = new_tokens
                        self.s.headers.update({'Authorization': f'Bearer {self.access_token}'})

                        # Повторная попытка
                        response = self.s.request(
                            method=method.upper(),
                            url=url,
                            json=json_,
                            data=data,
                            params=params,
                            headers=headers,
                            timeout=timeout
                        )
                else:
                    return None

            try:
                return response.json()
            except (JSONDecodeError, ValueError) as e:
                log(f"[{method.upper()}] Ошибка парсинга JSON: {e} \nОтвет: {response.text}", 2)
                return None

        except RequestException as e:
            log(f"[{method.upper()}] Сетевая ошибка: {e}")
            return None

    def check_if_authorized(self):
        """

        :return: 
        """
        url = self.profile_api
        response = self.safe_request(method="GET", url=url)
        return response

    def send_sms_code(self):
        """

        :return: 
        """
        url = self.sms_post_url
        payload = {'sender': 'Tele2'}

        data = self.safe_request(method="POST", url=url, json_=payload)

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

        data = self.safe_request(method="POST", url=url, json_=payload)

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

        data = self.safe_request(method="POST", url=url, json_=payload)

        if data:
            if 'access_token' in data and 'refresh_token' in data:
                return data['access_token'], data['refresh_token']
        return None

    def auth_with_password(self, phone_number: str, security_code: str, security_code_token: str, password: str):
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
            'username': phone_number,
            'password': password,
            'password_type': 'password',
            'security_code_token': security_code_token,
            'security_code': security_code
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = self.safe_request(method="POST", url=url, data=payload, headers=headers)

        if data:
            if 'access_token' in data and 'refresh_token' in data:
                self.phone_number = phone_number
                return data['access_token'], data['refresh_token']
        return None

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

        data = self.safe_request(method="POST", url=url, data=payload)

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

        result = self.safe_request(method="PUT", url=url, json_=update_data)

        if result:
            return result

        log(f'Ошибка поднятия лота. API вернул: {result.status_code}', 3)
        return None

    def top(self, lot_id):
        """

        :param lot_id: 
        :return: 
        """
        url = self.top_api
        update_data = {"lotId": lot_id}
        repeat = 0

        while repeat < 3:
            result = self.safe_request(method="PUT", url=url, json_=update_data)
            if result:
                return result
            else:
                log(f'Ошибка поднятия в топ. API вернул: {result.status_code}Повторение попытки.', 3)
                time.sleep(1)
            repeat += 1

        return None

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
        result = self.safe_request(method="PATCH", url=url, json_=data)

        if result:
            return result

        log(f'Ошибка модификации имени. API вернул: {result.status_code}', 3)
        return None

    def return_lot(self, lot_id):
        """

        :param lot_id: 
        :return: 
        """
        url = f'{self.market_api}/{lot_id}'

        return self.safe_request(method="DELETE", url=url)

    def get_balance(self):
        """

        :return: 
        """
        url = self.balance_api

        response = self.safe_request(method="GET", url=url)
        if response:
            return response['data']['value']

        return response

    def get_active_lots(self):
        """

        :return: 
        """
        url = self.market_api

        response = self.safe_request(method="GET", url=url)
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

        response = self.safe_request(method="GET", url=url)

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
        response = self.safe_request(method="GET", url=url)

        return response

    def get_statistics(self):
        """

        :return: 
        """
        url = self.statistics_api
        response = self.safe_request(method="GET", url=url)

        return response
