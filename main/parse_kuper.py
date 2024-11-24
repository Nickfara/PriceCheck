from http.client import responses

from mdlog import log as print
from selenium.webdriver import Chrome as Firefox
from selenium.webdriver.common.by import By

import requests
import json
import time

cookies = {}
try:
    with open('cookies_kuper.json', 'r') as f:
        cookies = json.load(f)
except:
    cookies = {}

token = {
    "csrf_param": "authenticity_token",
    "csrf_token": "8iIvoh9zROZxGzmM94tBbEa6SyRMrQLD23YCvyrm8KEQYNJEYsB4APKVRavB/d5+WQOrHUpWJjYES+ck6hyk1g=="
}


def auth():
    browser = Firefox()  # Загрузка браузера

    url = "https://kuper.ru/"

    browser.get(url)
    # browser.execute_script("document.body.style.zoom='15%'")


    time.sleep(60)

    cookies = browser.get_cookies()

    with open('cookies_kuper.json', 'w') as f:
        json.dump(cookies, str(f))
        return True

def auth_check():
    for i in range(1, 2):
        s = requests.Session()  # Создание сессии

        try:
            with open('cookies_mshop.json', 'r') as f:
                cookies = json.load(f)
        except:
            cookies = {}

        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        response = s.get(url='https://kuper.ru/api/next/page_part/browser_head')

        if response:
            print('Проверка авторизации успешно завершена!')
            return s
        else:
            if response.status_code in (400, 401, 403, 200):
                print('Ошибка доступа.\n Повторная авторизация!')
                if i < 2:
                    auth() # Авторизация через selenium
                else:
                    print('Ошибка авторизации!!!')
                    return False
            else:
                print(f'Ошибка запроса. Статус: {response.status_code}. Подробнее: {response.reason}')
                return False

def find(s):
    data = {
        "store_id": "66",
        "page": "1",
        "per_page": "24",
        "tenant_id": "sbermarket",
        "filter": [
            {
                "key": "brand",
                "values": []
            },
            {
                "key": "permalinks",
                "values": []
            },
            {
                "key": "price",
                "values": []
            },
            {
                "key": "discounted",
                "values": []
            },
            {
                "key": "root_category",
                "values": []
            }
        ],
        "q": "Сметана",
        "ads_identity": {
            "ads_promo_identity": {
                "placement_uid": "cg4tmrigsvdveog2p240",
                "site_uid": "c9qep2jupf8ugo3scn10"
            }
        }
    }
    response = s.post('https://kuper.ru/api/web/v1/products')
    print(response)
    try:
        print(response.json())
    except:
        print('JSON - не конвертируется! Ошибка поиска!')
        print(response.text)


session = auth_check()

responses = find(session)

print(responses)

def test():
    credentials = {
        'email': 'asd@asd.asd',
        'password': '123123123',
        'latitude': '45.0001',
        'longitude': '36.0001'
    }


def