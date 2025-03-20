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
SECURE_VALIDATION_API = site_auth + '/credential-management/security-codes'