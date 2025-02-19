"""
:config: Авторизационные данные для выполнения запроса о поездке.
"""
from datetime import datetime
from json import loads
from time import sleep

import requests

from .config import clid, apikey, point1, point2
from .database import add
from log import log

active_bot_taxi = [False]


def get_price(latlon1, latlon2):
    """
    Запрос данных о поездке в яндекс такси.

    :param latlon1: Координаты местоположения точки отправления.
    :param latlon2: Координаты местоположения точки прибытия.
    :return: Возвращается список с ценой, временем ожидания и длительностью поездки.
    """
    response = requests.get(
        f'https://taxi-routeinfo.taxi.yandex.net/taxi_info?clid={clid}&apikey={apikey}&rll={latlon1}~{latlon2}&class=econom')

    data = loads(response.text)
    result = {
        'price': data['options'][0]['price'],
        'wait': data['options'][0]['waiting_time'],
        'duration': data['time'],
    }
    return result


def create():
    """
    Создание списка с данными о поездке в обе стороны.
    [ts] - Настоящие дата и время.
    [to_price] - Стоимость поездки до работы.
    [from_price] - Стоимость поездки с работы.
    [to_wait] - Время ожидания такси до работы.
    [from_wait] - Время ожидания такси с работы.
    [to_duration] - Длительность поездки до работы.
    [from_duration] - Длительность поездки до дома.

    :return: Возвращается список с данными выше о поездке в обе стороны.
    """

    data_to = get_price(point1, point2)
    data_from = get_price(point2, point1)
    res_item = {
        "ts": datetime.now().strftime("%d.%m.%Y %H:%M:%S %A"),
        "to_price": data_to.get('price'),
        "from_price": data_from.get('price'),
        "to_wait": data_to.get('wait'),
        "from_wait": data_from.get('wait'),
        "to_duration": data_to.get('duration'),
        "from_duration": data_from.get('duration'),
    }
    return res_item


def run():
    """
    Запуск цикла запросов прайса.

    :return: Ничего
    """
    while active_bot_taxi[0]:
        try:
            price = create()
            add(price)
            sleep(60)
        except Exception as e:
            log(e, 2)
