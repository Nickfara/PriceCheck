import time
import json
import requests

from mdlog import log as print
from bs4 import BeautifulSoup as bs
from selenium.webdriver import Chrome as Firefox
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
ua = UserAgent()
random_ua = ua.random
from os import listdir
from os.path import isfile, join

# !/usr/bin/env python # -* - coding: utf-8-* -

log = True
cookies = {}
profile = {
    'customerId': "6431100029141862", # Настроен при авторизации
    't_time': "1732197309446", # Настроен при авторизации
    'storeId': "00030", # Настроен при авторизации
    'CallTreeId': '9755E2A3-2006-4DA2-994E-9BF29CFBEF1E||BTEX-7823725F-E53A-4554-97E2-1DAE9C8B44BF', # Неизвестно где получить
    'fsdAddressId': "6431100029141862994-4G20RSEO", # Настроен при авторизации
    'requestId': "BTEX-b4feec02-f281-11e5-1d1c-165a286dd641", # Неизвестно где получить
    'state':'c9a8411d2fb14ef689aef1a1390c5085',
    'cartId': "f039c83f-8484-4cc9-bf2f-a63e96b6e864",
    'sessionid': ''
}

try:
    with open('cookies_mshop.json', 'r') as f:
        cookies = json.load(f)
except:
    cookies = {}

def cirkle(numb, lengue=0):
    try:
        float(numb)
    except:
        print('Число не является дробным')
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
            right_numb = right_numb + new_last_numb
        else:
            right_numb = ''
            new = int(left_numb) + add
            return new

    new = str(left_numb) + '.' + str(right_numb)
    return float(new)

def create_link(data):
    fullname = data['scheme'] + '://' + data['host'] + data['filename']
    fulldata = []
    for i in data["query"]:
        fulldata.append(f'{i}={data["query"][i]}')
    fulldata = '&'.join(fulldata)
    fulllink = fullname + '?' + fulldata

    return fulllink

def new_auth():
    s = requests.Session()
    k = s.get(url='https://idam.metro-cc.ru/web/captchaConfig?clientId=BTEX&realmId=SSO_CUST_RU').json()['siteKey']
    c1 = s.post(url=f'https://www.recaptcha.net/recaptcha/enterprise/reload?k={k}')
    c2 = s.post(url=f'https://www.recaptcha.net/recaptcha/enterprise/clr?k={k}')
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
    rc_token = bs(c4.text, 'html.parser').find(id='recaptcha-token')['value']

    c5 = s.get(url='https://www.google.com/js/bg/W8CPGdzYmlcjn--3_xeFmudIk8Wv0vupGU9Bdr5QE-g.js')
    c6 = s.get(url='https://www.recaptcha.net/recaptcha/enterprise/webworker.js?hl=en&v=pPK749sccDmVW_9DSeTMVvh2')
    c7 = s.post(url=f'https://www.recaptcha.net/recaptcha/enterprise/reload?k={k}')
    c8 = s.post(url=f'https://www.recaptcha.net/recaptcha/enterprise/clr?k={k}')
    i = 1

    '''for url_numb in (c1, c2, c3, c4, c5, c6, c7, c8):
        print(f'c{i}:')
        try:
            print(url_numb.json())
            print(url_numb.text)
            print('\n\n\n')
        except:
            try:
                print(url_numb.reason)
                print(url_numb.text)
                print('END!\n\n\n')
            except:
                print(url_numb)
                print('\n\n\n')
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
        url_redirect = authenticate.json()['url']
    except:
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
    r_url = bs(date_get_url.text, 'html.parser').find('script')
    r_url = str(r_url).split("var locationUrl = '")[1].split('window.location = htmlDecode(locationUrl);')[0].split("';")[0]
    r_data = r_url.split(';')
    temp = 0
    for i in r_data:
        item = i.split('=')
        if item[0] == 'state':
            profile['state'] = item[1]
            temp = item[1]


    data_access_token = {
                    "grant_type": "authorization_code",
                    "redirect_uri": "https://mshop.metro-cc.ru/ordercapture/uidispatcher/static/silent-redirect.html",
                    "code": "dc598fb5-fdda-49ed-8da5-b9d040bc253b", # СОдержится в ссылке r_url возможно следующая строка тоже там
                    "code_verifier": "fb200a7bf7f4492e8a28d0919a8fd815f31f383b5fba4e29ba6f96caa32c7a2402faee2bfb324cf8ac2c58f83e5dd22d",
                    "client_id": "BTEX"
                }
    access_token = s.post(url='https://idam.metro-cc.ru/authorize/api/oauth2/access_token', data=data_access_token)
    loginWithIdamAcessToken = s.post(url='https://mshop.metro-cc.ru/explore.login.v1/auth/loginWithIdamAccessToken?country=RU')
    singleSignOn = s.post(url='https://mshop.metro-cc.ru/explore.login.v1/auth/singleSignOn')
    try:
        print(singleSignOn.json())
    except:
        print(singleSignOn.text)
    print(loginWithIdamAcessToken.cookies)

def auth():
    browser = Firefox()  # Загрузка браузера

    if log: print(str('Начало авторизации!'))
    url = "https://idam.metro-cc.ru/web/Signin?state=a22fc20c7a8f4cc29527582a9b69f480&scope=openid+clnt%3DBTEX&locale_id=ru-RU&redirect_uri=https%3A%2F%2Fmshop.metro-cc.ru%2Fshop%2Fportal%2Fmy-orders%2Fall%3FidamRedirect%3D1&client_id=BTEX&country_code=RU&realm_id=SSO_CUST_RU&user_type=CUST&DR-Trace-ID=idam-trace-id&code_challenge=X24I_T1kLXCRhV-o24wLBVRODgj9AULUni3HeJ_21G4&code_challenge_method=S256&response_type=code"

    browser.get(url)
    #browser.execute_script("document.body.style.zoom='15%'")

    browser.find_element(By.ID, 'user_id').send_keys("bokova_shura@mail.ru")  # Ввод логина
    browser.find_element(By.ID, 'password').send_keys("Dlink1980!!!")  # Ввод пароля

    while True:
        try:
            browser.find_element(By.ID, 'submit').click()  # Нажатие кнопки "Войти
            break
        except:
            time.sleep(1)

    if log: print(str('Успешная авторизация!'))

    while True:
        try:
            browser.find_element(By.XPATH,
                                 '/html/body/div[1]/div/div/div[2]/div[2]/div[3]/div[3]/div/div/div/div/div/div/div[1]/div/div').click()
            break
        except:
            time.sleep(1)
            #browser.execute_script("document.body.style.zoom='15%'")

    if log: print(str('Выбор адреса доставки выполнен!'))
    cookies = browser.get_cookies()



    with open('cookies_mshop.json', 'w') as f:
        json.dump(cookies, f)
        return True

def auth_check():
    for i in range(1, 2):
        s = requests.Session()  # Создание сессии
        url = f'https://mshop.metro-cc.ru/explore.border.v1/orderlist/country/RU/customerid/{profile['customerId']}?rows=10&locale=ru-RU&selectedCustomerStore={profile['storeId']}'
        data = {}

        try:
            with open('cookies_mshop.json', 'r') as f:
                cookies = json.load(f)
        except:
            cookies = {}

        for cookie in cookies:
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
            for i in getProfile['addresses']:
                if getProfile['addresses'][i]['buildingName'] == "БУФЕТ":
                    profile['fsdAddressId'] = getProfile['addresses'][i]['hash']
                    profile['storeId'] = getProfile['addresses'][i]['deliveryStore']
                    profile['t_time'] = s.get(url='https://mshop.metro-cc.ru/ordercapture/uidispatcher/rest/min-stable-ui-version').json()["timestampUtc"]
                    break

            url_info = s.get(url=f'https://mshop.metro-cc.ru/ordercapture/customercart/carts/alias/current?customerId={profile["customerId"]}&cardholderNumber=1&storeId={profile["storeId"]}&country=RU&locale=ru-RU&fsdAddressId={profile["fsdAddressId"]}&__t={profile["t_time"]}')
            profile['cartId'] = url_info.json()['data']['cartId']
            url_info = url_info.json()['data']
            return s
        else:
            if response.status_code in (400, 401, 403):
                print('Ошибка доступа.\n Повторная авторизация!')
                if i < 2:
                    auth() # Авторизация через selenium
                else:
                    print('Ошибка авторизации!!!')
                    return False
            else:
                print(f'Ошибка запроса. Статус: {response.status_code}. Подробнее: {response.reason}')
                return False


def search(text):
    s = auth_check()
    #profile['sessionid'] = s.headers.items() # Попытка достать сессион айди

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
                            "rows": "6", # Количество полученных объектов
                            "page": "1",
                            "filter": "delivery_mode:METRO_DELIVERY",
                            "facets": "true",
                            "categories": "true",
                            "customerId": profile['customerId'],
                            "__t": profile['t_time']
                        }
                    }

        url_findID = create_link(data_url_findID) # Генерация ссылки для поиска айди
        ids = s.get(url=url_findID).json()['resultIds'] # Получение айди найденных товаров
        ids_text = '&ids='.join(ids)
        print(ids_text)
        items = s.get(url=f'https://mshop.metro-cc.ru/evaluate.article.v1/betty-variants?storeIds={profile['storeId']}&ids={ids_text}&country=RU&locale=ru-RU&customerId={profile['customerId']}&__t={profile['t_time']}')  # Получение товаров

        try:
            objects = items.json()['result']
            print(objects)
            result = []
            for object in objects:
                name = objects[object]['variantSelector']['0032']
                data = objects[object]['variants']['0032']['bundles']['0021']
                print(name)
                price = data['stores']['00030']['possibleDeliveryModes']['METRO_DELIVERY']['possibleFulfillmentTypes']['FSD']['sellingPriceInfo']['finalPrice']
                bundleId = data['bundleId']['bettyBundleId']

                if 'minOrderQuantity' in data:
                    minOrderQuantity = data['minOrderQuantity']
                else:
                    minOrderQuantity = 1
                quantity = 0 # Количество товара добавляемого в корзину
                requestId = "BTEX-b4feec02-f281-11e5-1d1c-165a286dd641" # Непонятный айди запроса,хз что это

                result.append({'name': ''.join(name.split(',')), 'price': price, 'bundleId': bundleId, 'minOrderQuantity': minOrderQuantity})
        except Exception as e:
            print(e)
            result = None

        return result


def add_cart(object, count=0):
    s = auth_check()
    if s:
        if count == 0:
            count = int(object['minOrderQuantity'])
        temp_url= {
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
            'bundleId': object['bundleId'],
            'customerId': profile['customerId'],
            'quantity': 1, # Количество товара
            'requestId': profile['requestId']  # Непонятный айди запроса,хз что это
        }

        print(data)
        s.headers.update({'Content-Type': 'application/json'})

        result = s.post(url=url, json=data)
        result2 = s.get(
            url=f'https://mshop.metro-cc.ru/ordercapture/article/articles?country=RU&locale=ru-RU&'
                f'customerId={profile['customerId']}&storeId={profile["storeId"]}&addressId={profile["fsdAddressId"]}&bundleIds={object["bundleId"]}&__t={profile['t_time']}')

        print(result.json())
        print(result2.json())
        if result:
            return result
        else:
            return 'Ошибка:' + str(result.reason) + '. Более подробно:' + str(result.text)
    else:
        result = None
    return result

def remove_cart(item):
    s = auth_check()
    if s:

        url = (f'https://mshop.metro-cc.ru/ordercapture/customercart/carts/{profile['cartId']}/items/'
               f'{item["bundleId"]}?customerId={profile['customerId']}&cardholderNumber=1&storeId={profile["storeId"]}&country=RU&locale=ru-RU&'
               f'fsdAddressId={profile["fsdAddressId"]}&requestId={profile["requestId"]}')

        data = {
            'customerId': profile['customerId'],
            'quantity': 12,  # Количество товара
            'requestId': profile['requestId']  # Непонятный айди запроса,хз что это
        }

        s.headers.update({'Content-Type': 'application/json'})
        result = s.delete(url=url)
        print(result.json())
        if result:
            return result
        else:
            return 'Ошибка:' + str(result.reason) + '. Более подробно:' + str(result.text)
    else:
        result = None
    return result