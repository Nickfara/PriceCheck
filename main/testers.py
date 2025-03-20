import requests

import fake_useragent

UA = fake_useragent.fake.load()

s = requests.Session()  # Создание сессии
#s.headers.update({'T2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными

SECURITY_BYPASS_HEADERS = {
    'Connection': 'keep-alive',
    'T2-User-Agent': '"mytele2-app/3.17.0"; "unknown"; "Android/9"; "Build/12998710"',
    'X-API-Version': '1',
    'User-Agent': 'okhttp/4.2.0'
}

site_api = 'https://t2.ru/api'
site_auth = 'https://ekt.t2.ru/auth/realms/tele2-b2c'

MAIN_API = site_api + '/subscribers/'
SMS_VALIDATION_API = site_api + '/validation/number/'
TOKEN_API = site_auth + '/protocol/openid-connect/token'
SECURE_API = site_auth + '/credential-management/security-codes'

response  = s.post(SMS_VALIDATION_API + '79920228848', json={'sender': 'Tele2'})

print(response)

'https://ekt.t2.ru/api/validation/number/79920228848'