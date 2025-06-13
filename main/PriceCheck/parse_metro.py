"""
    Парсинг сайта Metro SHOP
"""

import json
import os
import time
from datetime import datetime
from json import JSONDecodeError

import requests

from fake_useragent import UserAgent
from requests import Response, Session

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Firefox
import time

from log import log

ua = UserAgent()
random_ua = ua.random

# !/usr/bin/env python # -* - coding: utf-8-* -

cookies = {}
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
LOGIN_CHECK_URL = f'https://mshop.metro-cc.ru/explore.border.v1/orderlist/country/RU/customerid/{profile["customerId"]}?rows=10&locale=ru-RU&selectedCustomerStore={profile["storeId"]}'  # Приватный API для проверки актуальности КУКИ файлов
LOGIN = "bokova_shura@mail.ru"
PASSWORD = "Dlink1980!!!"
COOKIES_FILE = "data/cookies_mshop.json"


# noinspection SpellCheckingInspection
def cirkle(numb: float, lengue: int = 0) -> float | None:
    """
    Округление дробного числа до нужно количество цифр после запятой.
    :param numb: Дробное число.
    :param lengue: Количество цифр, необходимое после запятой.
    :return: Возвращается дробное число, при успехе, либо None.
    """
    try:
        float(numb)
    except TypeError:
        log('Число не является дробным', 3)
        return

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
    Генерация ссылки для поиска.
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
def search(text: str) -> list | None:
    """
    Поиск на сайте mshop.

    :param text: Наименование товара.
    :return: Список из словарей: {'name': 'наименование товара', 'price': 'цена', 'bundleId': 'id товара': 'Минимальное количество для заказа'}
    """
    log("Начато выполнение поиска в mshop.")
    s = get_valid_session()
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
        requests = s.get(url=url_findID)  # Получение айди найденных товаров
        ids = requests.json()['resultIds']

        ids_text = '&ids='.join(ids)
        items = s.get(
            url=f'https://mshop.metro-cc.ru/evaluate.article.v1/betty-variants?storeIds={profile["storeId"]}&ids={ids_text}&country=RU&locale=ru-RU&customerId={profile["customerId"]}&__t={profile["t_time"]}')  # Получение товаров
        try:
            objects = items.json()['result']
        except JSONDecodeError:
            if items.status_code == 403:
                log('Доступ запрещён. Производится повторная авторизация.', 3)
                get_valid_session(forced=True)
                items = s.get(
                    url=f'https://mshop.metro-cc.ru/evaluate.article.v1/betty-variants?storeIds={profile["storeId"]}&ids={ids_text}&country=RU&locale=ru-RU&customerId={profile["customerId"]}&__t={profile["t_time"]}')  # Получение товаров
                if items.status_code != 200:
                    log(f'Повторная авторизация не помогла. Ошибка: {items}')
                    return []
            else:
                log(f'Непонятная ошибка: {items}', 3)
                return []
            log(f"""
    Ошибка декодирования JSON.
    items.status_code = {items.status_code}""", 3)
            return []

        result = []
        for object_ in objects:
            try:
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
                log(f'Проблема получение объекта: {e}', 2)

        return result


# noinspection SpellCheckingInspection
def add_cart(obj: dict) -> Response | str | None:
    """
    Добавить товар в корзину на сервере.
    :param obj: Добавляемый товар {'name': 'наименование товара', 'price': 'цена', 'bundleId': 'id товара': 'Минимальное количество для заказа'}
    :return: Результат работы.
    """
    s = get_valid_session()
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
def remove_cart(item) -> Response | str | None:
    """
    Удалить товар из корзины на сервере.

    :param item: Добавляемый товар: {'name': 'наименование товара', 'price': 'цена', 'bundleId': 'id товара': 'Минимальное количество для заказа'}
    :return: Результат работы.
    """
    s = get_valid_session()
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


def login_and_get_cookies(email: str, password: str) -> dict:
    """
    Авторизуется на mshop.metro-cc.ru и возвращает cookies для дальнейших запросов.
    :param email: Логин.
    :param password: Пароль.
    :return: Куки файлы.
    """

    options = Options()

    options.add_argument("--headless")  # Убери, если хочешь видеть браузер, верни, если не хочешь его видеть.
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = Firefox()
    log(driver)
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    res = driver.get("https://mshop.metro-cc.ru/")
    log(res)

    try:
        # Ввод логина
        while True:
            try:
                login_input = driver.find_element(By.NAME, "user_id")
                break
            except:
                time.sleep(1)
        log(login_input)
        login_input.send_keys(email)

        # Ввод пароля
        while True:
            try:
                password_input = driver.find_element(By.NAME, "password")
                break
            except:
                time.sleep(1)
        log(password_input)
        password_input.send_keys(password)

        # Подтверждение входа
        while True:
            try:
                submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Войти') and @type='submit']")
                break
            except:
                time.sleep(1)
        submit_btn.click()

        time.sleep(12)  # Ожидание редиректа

        cookies = driver.get_cookies()
        session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}

        return session_cookies

    except Exception as e:
        print("Ошибка авторизации:", e)
        return {}

    finally:
        driver.quit()


def get_valid_session(email=LOGIN, password=PASSWORD, cookies_file=COOKIES_FILE, forced=False) -> Session:
    """Проверка куки файлы на актуальность и получение актуального объекта сессии.

        :param email: Логин.
        :type email: str
        :param password: Пароль.
        :type password: str
        :param cookies_file: Путь к файлу с куки.
        :type cookies_file: str
        :return: Объект сессии.
        """
    # 1. Попытка загрузить сохранённые cookies
    if os.path.exists(cookies_file):
        if not forced:
            with open(cookies_file) as f:
                data = json.load(f)
                cookies = data['shops']
                date_time_ = data['time']

            # Конвертация даты и времени в словарь. 2025-05-31 21:40:54.997495 > {'year': 2025, 'month': 05, 'day': 31, 'hours': 21, 'minute': 40}
            date_time = date_time_.split(' ')
            date = date_time[0].split('-')
            time = date_time[1].split('.')[0].split(":")
            dtd = {
                "year": int(date[0]),
                "month": int(date[1]),
                "day": int(date[2]),
                "hours": int(time[0]),
                "minute": int(time[1])
            }

            now_dt = str(datetime.now())
            date_time = now_dt.split(' ')
            date = date_time[0].split('-')
            time = date_time[1].split('.')[0].split(":")
            dtdn = {
                "year": int(date[0]),
                "month": int(date[1]),
                "day": int(date[2]),
                "hours": int(time[0]),
                "minute": int(time[1])
            }

            # Проверка прошедшего времени.
            minutes_old = dtd['minute'] + dtd['hours'] * 60 + dtd['day'] * 24 * 60 + dtd['month'] * 30 * 24 * 60 + dtd[
                'year'] * 12 * 30 * 24 * 60
            minutes_new = dtdn['minute'] + dtdn['hours'] * 60 + dtdn['day'] * 24 * 60 + dtdn['month'] * 30 * 24 * 60 + \
                          dtdn['year'] * 12 * 30 * 24 * 60
            difference = minutes_new - minutes_old

            if difference < 60:
                session = requests.Session()
                session.cookies.update(cookies)
                return session
            else:
                log("[!] Cookies устарели. Требуется переавторизация.", 3)
        else:
            log('Запущена принудительная авторизация!')
    # 3. Получаем новые cookies через Selenium
    cookies = login_and_get_cookies(email, password)

    if cookies:
        # 4. Сохраняем их
        with open(cookies_file, 'w') as f:
            # noinspection PyTypeChecker
            cookies_ = {'shops': cookies, 'time': str(datetime.now())}
            f.seek(0)  # Возвращение к началу файла для записи
            json.dump(cookies_, f)
            f.truncate()  # Удаление остатка старого файла

        # 5. Обновляем Session
        session = requests.Session()
        session.cookies.update(cookies)
        return session
    else:
        print(f"Ошибка авторизации: {cookies}")
        return None
