import time

from aiohttp import ClientSession, ContentTypeError, ClientResponse

from T2.constants import SECURITY_BYPASS_HEADERS, MAIN_API, SMS_VALIDATION_API, TOKEN_API, SECURE_VALIDATION_API


async def _try_parse_to_json(response: ClientResponse):
    try:
        response_json = await response.json()
        return response_json
    except ContentTypeError:
        return None


def _is_ok(response: ClientResponse):
    return response.status == 200


class Tele2Api:
    s = requests.Session()  # Создание сессии
    s.headers.update({'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными

    access_token: str

    def __init__(self, phone_number: str, access_token: str = '',
                 refresh_token: str = ''):
        base_api = MAIN_API + phone_number
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

    async def __aenter__(self):
        self.session = ClientSession(headers={
            'Authorization': f'Bearer {self.access_token}',
            **SECURITY_BYPASS_HEADERS
        })
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    async def check_if_authorized(self):
        response = await self.session.get(self.profile_api)
        return _is_ok(response)

    async def send_sms_code(self):
        response = await self.session.post(self.sms_post_url, json={'sender': 'Tele2'})
        print(response)
        response_json = await _try_parse_to_json(response)
        print(response_json)
        return await response_json

    async def send_security_code(self, uid):
        """

        :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
        :return: Ответ сервера.
        """

        DB = t2b(uid)

        response = await self.session.post(self.security_post_url, json={
            "client_id": "digital-suite-web-app",
            "grant_type": "password",
            "username": DB["auth_login"],
            "password": DB["auth_password"],
            "password_type": "password"
        })
        response_json = await _try_parse_to_json(response)
        return response_json

    async def auth_with_code(self, phone_number: str, sms_code: str):
        response = await self.session.post(self.auth_post_url, data={
            'client_id': 'digital-suite-web-app',
            'grant_type': 'password',
            'username': phone_number,
            'password': sms_code,
            'password_type': 'sms_code'
        })
        if _is_ok(response):
            response_json = await _try_parse_to_json(response)
            return response_json['access_token'], response_json['refresh_token']

    async def auth_with_password(self, phone_number: str, security_code_token: str, password: str):
        response = await self.session.post(self.auth_post_url, data={
            'client_id': 'digital-suite-web-app',
            'grant_type': 'password',
            'username': phone_number,
            'password': password,
            'password_type': 'password',
            'security_code_token': security_code_token
        })
        if _is_ok(response):
            response_json = await _try_parse_to_json(response)
            return response_json['access_token'], response_json['refresh_token']

    async def refresh_tokens(self, refresh_token: str):
        response = await self.session.post(self.auth_post_url, data={
            'client_id': 'digital-suite-web-app',
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        })
        if _is_ok(response):
            response_json = await _try_parse_to_json(response)
            return response_json['access_token'], response_json['refresh_token']

    async def sell_lot(self, lot):
        response = await self.session.put(self.market_api, json={
            'trafficType': lot['lot_type'],
            'cost': {'amount': lot['price'], 'currency': 'rub'},
            'volume': {'value': lot['amount'],
                       'uom': 'min' if lot['lot_type'] == 'voice' else 'gb'}
        })

        return await _try_parse_to_json(response)

    async def top(self, uid, lot_id):
        repeat = 0
        while repeat < 3:
            response = await self.session.put(self.top_api, json={"lotId": lot_id})
            if response.ok:
                repeat = 3
            else:
                log('Ошибка поднятия в топ. Повторение попытки.', 3)
                time.sleep(1)
            repeat += 1

        return await _try_parse_to_json(response)

    async def rename(self, uid, lot_id, data_imp):
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

    async def return_lot(self, lot_id):
        response = await self.session.delete(f'{self.market_api}/{lot_id}')
        return await _try_parse_to_json(response)

    async def get_balance(self):
        response = await self.session.get(self.balance_api)
        if _is_ok(response):
            response_json = await _try_parse_to_json(response)
            return response_json['data']['value']

    async def get_active_lots(self):
        response = await self.session.get(self.market_api)
        if _is_ok(response):
            response_json = await _try_parse_to_json(response)
            lots = list(response_json['data'])
            active_lots = [a for a in lots if a['status'] == 'active']
            return active_lots

    async def get_rests(self):
        response = await self.session.get(self.rests_api)
        response_json = await _try_parse_to_json(response)
        rests = list(response_json['data']['rests'])
        sellable = [a for a in rests if a['type'] == 'tariff']
        return {
            'data': int(
                sum(a['remain'] for a in sellable if a['uom'] == 'mb') / 1024),
            'voice': int(
                sum(a['remain'] for a in sellable if a['uom'] == 'min'))
        }

    async def get_name(self, uid):
        """

        :param uid: ID пользователя в telegram, который является ID пользователя в базе данных.
        :return: Ответ сервера.
        """
        response = await self.session.get(self.name_api)
        response_json = await _try_parse_to_json(response)
        return response_json

    async def get_statistics(self, uid):
        response = await self.session.get(self.statistics_api)
        response_json = await _try_parse_to_json(response)
        return response_json
