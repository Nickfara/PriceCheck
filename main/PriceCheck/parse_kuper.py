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

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(6)
    try:
        print('Ожидание начато.')
        driver.get("https://kuper.ru/")
    except TimeoutException:
        driver.execute_script("window.stop();")


    try:
        # Нажатие кнопки 'Войти'
        login_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/header/div/div[2]/div/div[5]/div/button')
        login_btn.click()
        time.sleep(1.5)
        # Нажатие кнопки 'Войти по Сбер ID'
        sber_id_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div/form/div[2]/button')
        sber_id_btn.click()
        time.sleep(2)
        # Отключение получения рекламы.
        ad_disable = driver.find_element(By.XPATH, '//*[@id="desktopContainer"]/div[1]/div/div[2]/div[2]/div/label/span')
        ad_disable.click()
        time.sleep(1)
        # Ввод номера телефона
        login_input = driver.find_element(By.XPATH, '//*[@id="desktopContainer"]/div[1]/div/form/div/input')
        login_input.click()
        login_input.send_keys(phone_number)
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

        check_response = session.get("https://kuper.ru/api/v3/external_partners/services")
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


def coop_sberid_login(phone_number: str=LOGIN, code_input_callback=code_input_callback) -> dict:
    """
    Авторизация на Купер.маркет через СБЕР ID.
    :param phone_number: номер телефона в формате +7ХХХХХХХХХХ
    :param code_input_callback: функция, возвращающая смс-код
    :return: cookies (dict)
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = Firefox()

    try:
        driver.get("https://kuper.ru/")  # 1. Заход на Купер

        # 2. Нажимаем "Войти"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Войти')]"))).click()

        # 3. Нажимаем "Сбер ID"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Сбер ID')]"))).click()

        # 4. Переключаемся на вкладку СБЕР ID
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[-1])
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "login")))

        # 5. Ввод номера телефона
        driver.find_element(By.ID, "login").send_keys(phone_number)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 6. Ввод кода из SMS
        time.sleep(2)
        code = code_input_callback()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "otp")))
        driver.find_element(By.ID, "otp").send_keys(code)

        # 7. Завершение авторизации
        WebDriverWait(driver, 15).until(lambda d: len(driver.window_handles) == 1)
        driver.switch_to.window(driver.window_handles[0])

        # Убедимся, что пользователь залогинен
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Мой профиль')]"))
        )

        # Получение cookies
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}

        print("✅ Авторизация прошла успешно.")
        return cookies

    except Exception as e:
        print("❌ Ошибка авторизации:", e)
        return {}

    finally:
        driver.quit()


coop_sberid_login()