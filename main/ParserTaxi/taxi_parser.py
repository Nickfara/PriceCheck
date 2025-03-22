"""
:config: Авторизационные данные для выполнения запроса о поездке.
"""
from datetime import datetime
from json import loads
from time import sleep

import requests
from log import log

from .config import clid, apikey, point1, point2
from .database import add
from tg_bot import just_send as send

active_bot_taxi = [False]


def get_price(latlon1, latlon2, type_=1):
    """
    Запрос данных о поездке в яндекс такси.

    :param type_:
    :param latlon1: Координаты местоположения точки отправления.
    :param latlon2: Координаты местоположения точки прибытия.
    :return: Возвращается список с ценой, временем ожидания и длительностью поездки.
    """

    type_ = 'вместе' if type_ == 1 else 'econom' if type_ == 2 else 'error'  # todo: Найти название класса тарифа 'Вместе'

    if type_ == 'error':
        return type_

    response = requests.get(
        f'https://taxi-routeinfo.taxi.yandex.net/taxi_info?clid={clid}&apikey={apikey}&rll={latlon1}~{latlon2}&class={type_}')

    data = loads(response.text)

    result = {
        'price': data['options'][0]['price'],
        'wait': data['options'][0]['waiting_time'],
        'duration': data['time'],
    }

    return result


def create(type_=1):
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

    data_to = get_price(point1, point2, type_)

    if data_to == 'error':
        return data_to

    data_from = get_price(point2, point1, type_)

    if data_from == 'error':
        return data_from

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


def wait_low_money(direction=0):
    """
        Функция для отслеживания падений в цене тарифа вместе

    :param direction:

    :return:
    """
    active_bot_taxi[0] = True
    cost = []
    direction = 'to_price' if direction == 'to_job' else 'from_price' if direction == 'to_home' else 'error'

    if direction == 'error': send('Неверное направление')

    while active_bot_taxi[0]:
        try:
            price = create(2)[direction]
            cost.insert(0, price)

            print(f"""
            direction: {direction}
            price: {price}
            cost: {cost}
            """)

            if len(cost) > 1:
                if price - cost[0] > 15 or price < 200:
                    text = f'Цена упала и стала: {price}'
                    send(text)

                if len(cost) > 5:
                    del cost[-1]  # Удаление последнего объекта, при превышении длинны
            else:
                text = f'Поиск падения цены активирован! Текущая цена: {price}'
                send(text)

            sleep(15)

        except Exception as e:
            log(e, 2)
