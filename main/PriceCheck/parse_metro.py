"""
    Парсинг сайта Metro SHOP
"""

import json
import time
import requests

from bs4 import BeautifulSoup as Bs
from fake_useragent import UserAgent
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from log import log

ua = UserAgent()
random_ua = ua.random

# !/usr/bin/env python # -* - coding: utf-8-* -

cookies = {}
# noinspection SpellCheckingInspection
profile = {
    'customerId': "6431100029141862",  # Настроен при авторизации
    't_time': "1732197309446",  # Настроен при авторизации
    'storeId': "00030",  # Настроен при авторизации
    'CallTreeId': '9755E2A3-2006-4DA2-994E-9BF29CFBEF1E||BTEX-7823725F-E53A-4554-97E2-1DAE9C8B44BF',
    # Неизвестно где получить
    'fsdAddressId': "6431100029141862994-4G20RSEO",  # Настроен при авторизации
    'requestId': "BTEX-b4feec02-f281-11e5-1d1c-165a286dd641",  # Неизвестно где получить
    'state': 'c9a8411d2fb14ef689aef1a1390c5085',
    'cartId': "f039c83f-8484-4cc9-bf2f-a63e96b6e864",
    'sessionid': ''
}
# noinspection PyBroadException
try:
    with open('../data/cookies_mshop.json') as f:
        cookies = json.load(f)['shops']
except:
    cookies = {'shops': []}


# noinspection SpellCheckingInspection
def cirkle(numb, lengue=0):
    """

    :param numb:
    :param lengue:
    :return:
    """
    try:
        float(numb)
    except TypeError:
        log('Число не является дробным', 3)
        return None

    numb = str(numb)
    right_numb = numb.split('.')[1]
    left_numb = numb.split('.')[0]

    while len(right_numb) > lengue:

        if int(right_numb[-1]) >= 5:
            add = 1
        else:
            add = 0

        if len(right_numb) > 2:
            right_numb = right_numb[:-1]
            new_last_numb = str(int(right_numb[-1]) + add)
            right_numb = right_numb[:-1]
            right_numb += new_last_numb
        else:
            new = int(left_numb) + add
            return new

    new = str(left_numb) + '.' + str(right_numb)
    return float(new)


# noinspection SpellCheckingInspection
def create_link(data):
    """

    :param data:
    :return:
    """
    fullname = data['scheme'] + '://' + data['host'] + data['filename']
    fulldata = []
    for i in data["query"]:
        fulldata.append(f'{i}={data["query"][i]}')
    fulldata = '&'.join(fulldata)
    fulllink = fullname + '?' + fulldata

    return fulllink


# noinspection SpellCheckingInspection
def new_auth():
    """
        Возможно новая функция авторизации
    """
    s = requests.Session()
    k = s.get(url='https://idam.metro-cc.ru/web/captchaConfig?clientId=BTEX&realmId=SSO_CUST_RU').json()['siteKey']
    s.post(url=f'https://www.recaptcha.net/recaptcha/enterprise/reload?k={k}')
    s.post(url=f'https://www.recaptcha.net/recaptcha/enterprise/clr?k={k}')
    c4 = s.get(url=create_link({
        "scheme": "https",
        "host": "www.recaptcha.net",
        "filename": "/recaptcha/enterprise/anchor",
        "query": {
            "ar": "1",
            "k": k,
            "co": "aHR0cHM6Ly9pZGFtLm1ldHJvLWNjLnJ1OjQ0Mw..",
            "hl": "en",
            "v": "pPK749sccDmVW_9DSeTMVvh2",
            "size": "invisible",
            "cb": "2a9awybl7uln"
        }
    }))
    rc_token = Bs(c4.text, 'html.parser').find(id='recaptcha-token')['value']

    s.get(url='https://www.google.com/js/bg/W8CPGdzYmlcjn--3_xeFmudIk8Wv0vupGU9Bdr5QE-g.js')
    s.get(url='https://www.recaptcha.net/recaptcha/enterprise/webworker.js?hl=en&v=pPK749sccDmVW_9DSeTMVvh2')
    s.post(url=f'https://www.recaptcha.net/recaptcha/enterprise/reload?k={k}')
    s.post(url=f'https://www.recaptcha.net/recaptcha/enterprise/clr?k={k}')

    '''for url_numb in (c1, c2, c3, c4, c5, c6, c7, c8):
        log(f'c{i}:')
        try:
            log(url_numb.json())
            log(url_numb.text)
            log('\n\n\n')
        except:
            try:
                log(url_numb.reason)
                log(url_numb.text)
                log('END!\n\n\n')
            except:
                log(url_numb)
                log('\n\n\n')
        i += 1'''

    data_auth = {
        "user_id": "bokova_shura@mail.ru",
        "password": "Dlink1980!!!",
        "user_type": "CUST",
        "client_id": "BTEX",
        "response_type": "code",
        "country_code": "RU",
        "locale_id": "ru-RU",
        "realm_id": "SSO_CUST_RU",
        "account_id": "",
        "redirect_url": "https://mshop.metro-cc.ru/shop/portal/my-orders/all?idamRedirect=1",
        "state": profile['state'],
        "nonce": "",
        "scope": "openid+clnt=BTEX",
        "code_challenge": "X24I_T1kLXCRhV-o24wLBVRODgj9AULUni3HeJ_21G4",
        "code_challenge_method": "S256",
        "rc_token": rc_token
    }
    authenticate = s.post(url='https://idam.metro-cc.ru/web/authc/authenticate', data=data_auth)
    try:
        authenticate.json()['url']
    except EncodingWarning:
        pass
    except KeyError:
        pass

    date_get_url = s.get(url=create_link({
        "scheme": "https",
        "host": "idam.metro-cc.ru",
        "filename": "/authorize/api/oauth2/authorize",
        "query": {
            "client_id": "BTEX",
            "redirect_uri": "https://mshop.metro-cc.ru/ordercapture/uidispatcher/static/silent-redirect.html",
            "response_type": "code",
            "scope": "openid clnt=BTEX",
            "state": profile['state'],
            "code_challenge": "Cm15FKICW2IPESm1D5WpY38M8HHGPYqbyQSrGyVIi4k",
            "code_challenge_method": "S256",
            "prompt": "none",
            "realm_id": "SSO_CUST_RU",
            "country_code": "RU",
            "locale_id": "ru-RU"
        }
    }))
    r_url = Bs(date_get_url.text, 'html.parser').find('script')
    r_url = \
        str(r_url).split("var locationUrl = '")[1].split('window.location = htmlDecode(locationUrl);')[0].split("';")[0]
    r_data = r_url.split(';')

    for i in r_data:
        item = i.split('=')
        if item[0] == 'state':
            profile['state'] = item[1]

    data_access_token = {
        "grant_type": "authorization_code",
        "redirect_uri": "https://mshop.metro-cc.ru/ordercapture/uidispatcher/static/silent-redirect.html",
        "code": "dc598fb5-fdda-49ed-8da5-b9d040bc253b",  # СОдержится в ссылке r_url возможно следующая строка тоже там
        "code_verifier": "fb200a7bf7f4492e8a28d0919a8fd815f31f383b5fba4e29ba6f96caa32c7a2402faee2bfb324cf8ac2c58f83e5dd22d",
        "client_id": "BTEX"
    }
    s.post(url='https://idam.metro-cc.ru/authorize/api/oauth2/access_token', data=data_access_token)
    s.post(
        url='https://mshop.metro-cc.ru/explore.login.v1/auth/loginWithIdamAccessToken?country=RU')
    singleSignOn = s.post(url='https://mshop.metro-cc.ru/explore.login.v1/auth/singleSignOn')
    try:
        singleSignOn.json()
    except EncodingWarning:
        log(singleSignOn.text, 3)


# noinspection SpellCheckingInspection,PyBroadException
def auth():
    """

    :return:
    """
    browser = Firefox()  # Загрузка браузера

    url = "https://idam.metro-cc.ru/web/Signin?state=a22fc20c7a8f4cc29527582a9b69f480&scope=openid+clnt%3DBTEX&locale_id=ru-RU&redirect_uri=https%3A%2F%2Fmshop.metro-cc.ru%2Fshop%2Fportal%2Fmy-orders%2Fall%3FidamRedirect%3D1&client_id=BTEX&country_code=RU&realm_id=SSO_CUST_RU&user_type=CUST&DR-Trace-ID=idam-trace-id&code_challenge=X24I_T1kLXCRhV-o24wLBVRODgj9AULUni3HeJ_21G4&code_challenge_method=S256&response_type=code"

    browser.get(url)
    # browser.execute_script("document.body.style.zoom='15%'")
    while True:
        try:
            try:
                browser.find_element('user_id').send_keys("bokova_shura@mail.ru")  # Ввод логина
                browser.find_element('password').send_keys("Dlink1980!!!")  # Ввод пароля
            except:
                browser.find_element(By.XPATH, '//*[@id="user_id"]').send_keys("bokova_shura@mail.ru")  # Ввод логина
                browser.find_element(By.XPATH, '//*[@id="password"]').send_keys("Dlink1980!!!")  # Ввод пароля
            break
        except:
            time.sleep(1)

    while True:
        try:
            try:
                browser.find_element('submit').click()  # Нажатие кнопки "Войти
            except:
                browser.find_element(By.XPATH, '//*[@id="submit"]').click()
            break
        except:
            time.sleep(1)

    log('Успешная авторизация!')
    repeat = 0
    while True:
        try:
            browser.find_element(By.XPATH,
                                 '/html/body/div[1]/div/div/div[2]/div[2]/div[3]/div[3]/div/div/div/div/div/div/div[1]/div/div').click()
            break
        except:
            time.sleep(1)
            repeat += 1
            if repeat > 10:
                break
            # browser.execute_script("document.body.style.zoom='15%'")

    log('Выбор адреса доставки выполнен!')
    cookies_ = {'shops': browser.get_cookies()}

    with open('../data/cookies_mshop.json', 'w') as f_:
        # noinspection PyTypeChecker
        json.dump(cookies_, f_)
        return True


# noinspection SpellCheckingInspection, PyBroadException
def auth_check():
    """

    :return:
    """
    for i in range(1, 2):
        s = requests.Session()  # Создание сессии
        url = f'https://mshop.metro-cc.ru/explore.border.v1/orderlist/country/RU/customerid/{profile["customerId"]}?rows=10&locale=ru-RU&selectedCustomerStore={profile["storeId"]}'

        try:
            with open('../data/cookies_mshop.json') as f_:
                cookies_ = json.load(f_)['shops']
        except:
            cookies_ = {'shops': []}

        for cookie in cookies_:
            # noinspection PyTypeChecker
            s.cookies.set(cookie['name'], cookie['value'])

        response = s.get(url=url)
        try:
            response_reauth = s.post(url='https://mshop.metro-cc.ru/explore.login.v1/auth/singleSignOn')
            s.cookies.set('compressedJWT', response_reauth.json()['compressedJWT'])
        except:
            pass

        if response:
            getProfile = s.get(create_link({
                "scheme": "https",
                "host": "mshop.metro-cc.ru",
                "filename": f"/ordercapture/checkout/customer/RU/{profile['customerId']}/1",
                "query": {
                    "__t": profile['t_time']
                }
            }))
            getProfile = getProfile.json()["data"]
            profile['customerId'] = getProfile['customerId']
            profile['fsdAddressId'] = getProfile['addresses']
            for i2 in getProfile['addresses']:
                if getProfile['addresses'][i2]['buildingName'] == "БУФЕТ":
                    profile['fsdAddressId'] = getProfile['addresses'][i2]['hash']
                    profile['storeId'] = getProfile['addresses'][i2]['deliveryStore']
                    profile['t_time'] = \
                        s.get(
                            url='https://mshop.metro-cc.ru/ordercapture/uidispatcher/rest/min-stable-ui-version').json()[
                            "timestampUtc"]
                    break

            url_info = s.get(
                url=f'https://mshop.metro-cc.ru/ordercapture/customercart/carts/alias/current?customerId={profile["customerId"]}&cardholderNumber=1&storeId={profile["storeId"]}&country=RU&locale=ru-RU&fsdAddressId={profile["fsdAddressId"]}&__t={profile["t_time"]}')
            profile['cartId'] = url_info.json()['data']['cartId']
            return s
        else:
            if response.status_code in (400, 401, 403):
                log('Ошибка доступа.\n Повторная авторизация!', 3)
                if i < 2:
                    auth()  # Авторизация через selenium
                else:
                    log('Ошибка авторизации!!!', 3)
                    return False
            else:
                log(f'Ошибка запроса. Статус: {response.status_code}. Подробнее: {response.reason}', 3)
                return False


# noinspection SpellCheckingInspection
def search(text):
    """

    :param text:
    :return:
    """
    s = auth_check()
    # profile['sessionid'] = s.headers.items() # Попытка достать сессион айди

    if s:
        s.headers.update({
            'CallTreeId': profile['CallTreeId']
        })

        # Словарь для генерации ссылки:
        data_url_findID = {
            "scheme": "https",
            "host": "mshop.metro-cc.ru",
            "filename": "/searchdiscover/articlesearch/search",
            "query": {
                "storeId": profile['storeId'],
                "language": "ru-RU",
                "country": "RU",
                "query": text,
                "rows": "6",  # Количество полученных объектов
                "page": "1",
                "filter": "delivery_mode:METRO_DELIVERY",
                "facets": "true",
                "categories": "true",
                "customerId": profile['customerId'],
                "__t": profile['t_time']
            }
        }

        url_findID = create_link(data_url_findID)  # Генерация ссылки для поиска айди
        s.headers.update({'Content-Type': 'application/json', 'Priority': 'u=4'})
        ids = s.get(url=url_findID).json()['resultIds']  # Получение айди найденных товаров
        ids_text = '&ids='.join(ids)
        items = s.get(
            url=f'https://mshop.metro-cc.ru/evaluate.article.v1/betty-variants?storeIds={profile["storeId"]}&ids={ids_text}&country=RU&locale=ru-RU&customerId={profile["customerId"]}&__t={profile["t_time"]}')  # Получение товаров

        try:
            objects = items.json()['result']
            result = []
            for object_ in objects:
                name = objects[object_]['variantSelector']['0032']
                data = objects[object_]['variants']['0032']['bundles']['0021']
                price = \
                    data['stores']['00030']['possibleDeliveryModes']['METRO_DELIVERY']['possibleFulfillmentTypes'][
                        'FSD'][
                        'sellingPriceInfo']['finalPrice']
                bundleId = data['bundleId']['bettyBundleId']

                if 'minOrderQuantity' in data:
                    minOrderQuantity = data['minOrderQuantity']
                else:
                    minOrderQuantity = 1

                result.append({'name': ''.join(name.split(',')), 'price': price, 'bundleId': bundleId,
                               'minOrderQuantity': minOrderQuantity})
        except Exception as e:
            log(e, 2)
            result = None

        return result


# noinspection SpellCheckingInspection
def add_cart(obj):
    """

    :param obj:
    :return:
    """
    s = auth_check()
    if s:

        temp_url = {
            "scheme": "https",
            "host": "mshop.metro-cc.ru",
            "filename": f"/ordercapture/customercart/carts/{profile['cartId']}/items",
            "query": {
                "country": "RU",
                "locale": "ru-RU",
                "fsdAddressId": profile["fsdAddressId"],
                "storeId": profile['storeId'],
                "customerId": profile['customerId'],
                "cardholderNumber": "1",
                "__t": profile['t_time']
            }
        }
        url = create_link(temp_url)

        data = {
            'bundleId': obj['bundleId'],
            'customerId': profile['customerId'],
            'quantity': 1,  # Количество товара
            'requestId': profile['requestId']  # Непонятный айди запроса, неизвестно, что это
        }

        s.headers.update({'Content-Type': 'application/json'})

        result = s.post(url=url, json=data)

        if result:
            return result
        else:
            return 'Ошибка:' + str(result.reason) + '. Более подробно:' + str(result.text)
    else:
        result = None
    return result


# noinspection SpellCheckingInspection
def remove_cart(item):
    """

    :param item:
    :return:
    """
    s = auth_check()
    if s:

        url = (f'https://mshop.metro-cc.ru/ordercapture/customercart/carts/{profile["cartId"]}/items/'
               f'{item["bundleId"]}?customerId={profile["customerId"]}&cardholderNumber=1&storeId={profile["storeId"]}&country=RU&locale=ru-RU&'
               f'fsdAddressId={profile["fsdAddressId"]}&requestId={profile["requestId"]}')

        s.headers.update({'Content-Type': 'application/json', 'Priority': 'u=4'})
        result = s.delete(url=url)
        log(result.json())
        if result:
            return result
        else:
            return 'Ошибка:' + str(result.reason) + '. Более подробно:' + str(result.text)
    else:
        result = None
    return result
