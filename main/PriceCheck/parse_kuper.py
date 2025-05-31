"""
    todo Парсинг приложения купер
"""
import json
import time
import requests

from selenium.webdriver import Chrome as Firefox

from log import log

# !/usr/bin/env python # -* - coding: utf-8-* -

cookies = {}
# noinspection PyBroadException
try:
    # noinspection SpellCheckingInspection
    with open('../data/cookies_kuper.json') as f:
        cookies = json.load(f)
except:
    cookies = {}

# noinspection SpellCheckingInspection
token = {
    "csrf_param": "authenticity_token",
    "csrf_token": "8iIvoh9zROZxGzmM94tBbEa6SyRMrQLD23YCvyrm8KEQYNJEYsB4APKVRavB/d5+WQOrHUpWJjYES+ck6hyk1g=="
}


def auth():
    """

    :return:
    """
    browser = Firefox()  # Загрузка браузера

    url = "https://kuper.ru/"

    browser.get(url)
    # browser.execute_script("document.body.style.zoom='15%'")

    time.sleep(60)

    cookies_ = browser.get_cookies()

    # noinspection SpellCheckingInspection
    with open('../data/cookies_kuper.json', 'w') as f_:
        # noinspection PyTypeChecker
        json.dump(cookies_, f_)
        return True


# noinspection PyBroadException
def auth_check():
    """

    :return:
    """
    for i in range(1, 2):
        s = requests.Session()  # Создание сессии

        try:
            # noinspection SpellCheckingInspection
            with open('../data/cookies_mshop.json') as f_:
                cookies_ = json.load(f_)
        except:
            cookies_ = {}

        for cookie in cookies_:
            s.cookies.set(cookie['name'], cookie['value'])

        response = s.get(url='https://kuper.ru/api/next/page_part/browser_head')

        if response:
            log('Проверка авторизации успешно завершена!')
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


# noinspection PyBroadException
def find(s):
    """

    :param s:
    """

    response = s.post('https://kuper.ru/api/web/v1/products')
    try:
        response.json()
    except:
        log(f'JSON - не конвертируется! Ошибка поиска!:\n{response.text}', 3)


session = auth_check()

find(session)
