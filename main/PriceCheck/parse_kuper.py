import json
import os
import time
from datetime import datetime

import requests

from fake_useragent import UserAgent
from requests import Response, Session

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Firefox


import time

from log import log

ua = UserAgent()
random_ua = ua.random

# !/usr/bin/env python # -* - coding: utf-8-* -

cookies = {}

LOGIN = "(992) 022-88-48"
COOKIES_FILE = "../data/cookies_kuper.json"


def login_and_get_cookies(phone_number: str) -> dict:
    """
    Авторизуется на kuper и возвращает cookies для дальнейших запросов.
    :param phone_number: Номер телефона.
    :return: Куки файлы.
    """

    options = Options()
    options.binary_location = r"A:\Program Files\Google\Chrome\Application\chrome.exe"

    #options.add_argument("--headless")  # Убери, если хочешь видеть браузер, верни, если не хочешь его видеть.
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = Firefox()
    driver.set_page_load_timeout(6)
    try:
        print('Ожидание начато.')
        driver.get("https://kuper.ru/")
    except TimeoutException:
        driver.execute_script("window.stop();")


    try:
        enter = True
        while True:
            try:
                # Скипаем рекламу
                skip_ad_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div/div[2]/header/button/div')
                skip_ad_btn.click()
                break
            except:
                try:
                    # Нажатие кнопки 'Войти'
                    login_btn = driver.find_element(By.XPATH,
                                                    '//*[@id="__next"]/div[1]/div/header/div/div[2]/div/div[5]/div/button')
                    login_btn.click()
                    enter = False # Выключение повторныъ попыток нажать кнопку войти
                    break
                except:
                    time.sleep(1)

        while enter:
            try:
                # Нажатие кнопки 'Войти'
                login_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/header/div/div[2]/div/div[5]/div/button')
                login_btn.click()
                break
            except:
                time.sleep(1)

        while True:
            try:
                # Нажатие кнопки 'Войти по Сбер ID'
                sber_id_btn = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/form/div[2]/button")
                sber_id_btn.click()
                break
            except:
                time.sleep(1)

        while True:
            try:
                # Отключение получения рекламы.
                ad_disable = driver.find_element(By.XPATH, '//*[@id="desktopContainer"]/div[1]/div/div[2]/div[2]/div/label/span')
                ad_disable.click()
                break
            except:
                time.sleep(1)

        while True:
            try:
                # Ввод номера телефона
                login_input = driver.find_element(By.XPATH, '//*[@id="desktopContainer"]/div[1]/div/form/div/input')
                login_input.click()
                login_input.send_keys(phone_number)
                break
            except:
                time.sleep(1)

        try:
            send_code = driver.find_element(By.XPATH, '//*[@id="desktopContainer"]/div[1]/div/form/button')
            send_code.click()
            time.sleep(25)
        except TimeoutException:
            driver.execute_script("window.stop();")

        cookies = driver.get_cookies()
        session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}

        return session_cookies

    except Exception as e:
        print("Ошибка авторизации:", e)
        return {}

    finally:
        driver.quit()


def get_valid_session(phone_number=LOGIN, cookies_file=COOKIES_FILE) -> Session:
    """Проверка куки файлы на актуальность и получение актуального объекта сессии.

        :param phone_number: Логин.
        :type phone_number: str
        :param cookies_file: Путь к файлу с куки.
        :type cookies_file: str
        :return: Объект сессии.
        """
    # 1. Попытка загрузить сохранённые cookies
    if os.path.exists(cookies_file):
        with open(cookies_file) as f:
            data = json.load(f)
            cookies = data['shops']
            date_time_ = data['time']

        session = requests.Session()
        session.cookies.update(cookies)

        # Конвертация даты и времени в словарь. 2025-05-31 21:40:54.997495 > {'year': 2025, 'month': 05, 'day': 31, 'hours': 21, 'minute': 40}
        # date_time = date_time_.split(' ')
        # date = date_time[0].split('-')
        # time = date_time[1].split('.')[0].split(":")
        # dtd = {
        #     "year": int(date[0]),
        #     "month": int(date[1]),
        #     "day": int(date[2]),
        #     "hours": int(time[0]),
        #     "minute": int(time[1])
        # }
        #
        # now_dt = str(datetime.now())
        # date_time = now_dt.split(' ')
        # date = date_time[0].split('-')
        # time = date_time[1].split('.')[0].split(":")
        # dtdn = {
        #     "year": int(date[0]),
        #     "month": int(date[1]),
        #     "day": int(date[2]),
        #     "hours": int(time[0]),
        #     "minute": int(time[1])
        # }
        #
        # # Проверка прошедшего времени.
        # minutes_old = dtd['minute'] + dtd['hours'] * 60 + dtd['day'] * 24 * 60 + dtd['month'] * 30 * 24 * 60 + dtd['year'] * 12 * 30 * 24 * 60
        # minutes_new = dtdn['minute'] + dtdn['hours'] * 60 + dtdn['day'] * 24 * 60 + dtdn['month'] * 30 * 24 * 60 + dtdn['year'] * 12 * 30 * 24 * 60
        # difference = minutes_new - minutes_old
        #
        #
        # if difference < 60:
        #     return session
        # else:
        #     print("[!] Cookies устарели. Требуется переавторизация.")

        check_response = session.get("https://kuper.ru/api/shipments/active")
        print(check_response)
        if check_response.ok:
            return session
    # 3. Получаем новые cookies через Selenium
    cookies = login_and_get_cookies(phone_number)

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


def code_input_callback():
    return input()


def find(cookies_file=COOKIES_FILE, text='Сахар'):
    link = 'https://kuper.ru/api/web/v1/products'

    data = {
        'ads_identity': {'ads_promo_identity': {'placement_uid': "cg4tmrigsvdveog2p240", 'site_uid': "c9qep2jupf8ugo3scn10"}},
        'filter': [
            {"key": "brand", "values": []},
            {"key": "permalinks","values": []},
            {"key": "price","values": []},
            {"key": "discounted","values": []},
            {"key": "root_category","values": []}
        ],
        'page': "1",
        'per_page': "24",
        'q': text,
        'store_id': "66",
        'tenant_id': "sbermarket"
    }


    headers = {
        'accept':
        'application/json, text/plain, */*',
        'accept-encoding':
        'gzip, deflate, br, zstd',
        'accept-language':
        'ru,en;q=0.9',
        'baggage':
        'sentry-environment=client,sentry-release=r25-06-11-1896-176f596d,sentry-public_key=f9d0a0afb8d5420bb353a190580ae049,sentry-',
        'referer': 'https://kuper.ru/metro/search?ads_identity.ads_promo_identity.placement_uid=cg4tmrigsvdveog2p240&ads_identity.ads_promo_identity.site_uid=c9qep2jupf8ugo3scn10&anonymous_id=43df9a32-9a0d-433d-9970-ab1091dd2d11&keywords=%D0%A1%D0%90%D0%A5%D0%90%D0%A0%5C&sid=66',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sentry-trace': '50aaeaf67a1b48bbb653790a065fab18-8669d2535644039c-0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Safari/605.1.15'
    }

    with open(cookies_file) as f:
        data_temp = json.load(f)
        cookies = data_temp['shops']


    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)
    token = session.get('https://kuper.ru/api/v3/external_partners/services', json={
    "services": [
        {
            "id": 1,
            "kind": "sber_prime"
        }
    ]
})
    print(token.text)
    response = session.post(link, data=data)
    #print(response.text)

find()


