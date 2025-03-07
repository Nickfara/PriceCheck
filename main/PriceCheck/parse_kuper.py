import json
import time

import requests
from selenium.webdriver import Chrome as Firefox

from log import log

# !/usr/bin/env python # -* - coding: utf-8-* -

cookies = {}
try:
    with open('../data/cookies_kuper.json') as f:
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

    with open('../data/cookies_kuper.json', 'w') as f:
        json.dump(cookies, f)
        return True


def auth_check():
    for i in range(1, 2):
        s = requests.Session()  # Создание сессии

        try:
            with open('../data/cookies_mshop.json') as f:
                cookies = json.load(f)
        except:
            cookies = {}

        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        response = s.get(url='https://kuper.ru/api/next/page_part/browser_head')

        if response:
            log('Проверка авторизации успешно завершена!', 1)
            return s
        else:
            if response.status_code in (400, 401, 403, 200):
                log('Ошибка доступа.\n Повторная авторизация!', 3)
                if i < 2:
                    auth()  # Авторизация через selenium
                else:
                    log('Ошибка авторизации!!!', 3)
                    return False
            else:
                log(f'Ошибка запроса. Статус: {response.status_code}. Подробнее: {response.reason}', 3)
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
    try:
        response.json()
    except:
        log(f'JSON - не конвертируется! Ошибка поиска!:\n{response.text}', 3)


session = auth_check()

responses = find(session)


def test():
    credentials = {
        'email': 'asd@asd.asd',
        'password': '123123123',
        'latitude': '45.0001',
        'longitude': '36.0001'
    }
