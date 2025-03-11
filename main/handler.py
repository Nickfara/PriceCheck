"""
    Функции сопутствующие всему проекту
"""
from log import log

import asyncio
import json


# !/usr/bin/env python # -* - coding: utf-8-* -


async def async_start(start):
    """

    :param start:
    """
    loop = asyncio.get_event_loop()
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor()
    # noinspection PyTypeChecker
    await loop.run_in_executor(executor, start)


async def background_load(self):
    """

    :param self:
    """

    # noinspection PyTypeChecker, PyBroadException
    def start():
        """
            Функция запуска
        """
        from tg_bot import run
        run()

        log('TG бот включен!')

        import ParserTaxi.taxi_parser as tp
        tp.run()
        log('Парсер такси включен!')

        with open('data/cache_prices.json') as f:
            result = json.load(f)
            result_filtered = filter_shops(result)
            self.base_price = result_filtered
            log('Прайс загружен в кэш!')

        try:
            with open('data/cache_cart.json', 'w') as f:
                json.dump({'cart': []}, f)
        except:
            pass

        self.activate_enter_finder()
        log('Поиск по нажатию "enter" включен!')

    await async_start(start)


async def refresh(self):
    """

    :param self:
    """

    def start():
        """
            Функция запуска
        """
        from PriceCheck.read_doc import scanner
        scanner('')
        log('Сканирование прайсов запущено!')
        with open('data/cache_prices.json') as f:
            result = json.load(f)
            result_filtered = filter_shops(result)
            self.base_price = result_filtered
            log('Отсканированы файлы и обновлён кэш!')

        with open('data/config.json') as f:
            data = json.load(f)
            if data['metro_active']:  # Если метро включено в настройках, запускает авторизацию
                from PriceCheck import parse_metro
                parse_metro.auth_check()
                # self.checkbox_parser_metro.active = True
                log('MShop авторизован!')

    await async_start(start)


async def send_to_cart(item, parse_metro):
    """

    :param item:
    :param parse_metro:
    """

    def start():
        """
            Функция запуска
        """

        parse_metro.add_cart(item)
        log(f'Товар: "{item["name"]}" добавлен в корзину!')

    await async_start(start)


async def remove_from_cart(item, parse_metro):
    """

    :param item:
    :param parse_metro:
    """

    def start():
        """
            Функция запуска
        """
        parse_metro.remove_cart(item)
        log(f'Товар: "{item["name"]}" удалён из корзины!')

    await async_start(start)


def filter_shops(items: list):
    """

    :param items:
    :return:
    """
    shops = []
    items_filtered = []
    with open('data/config.json') as f:
        config = json.load(f)
        for shop in config['shops']:
            if shop['active']:
                shops.append(shop['seller'])

    for item in items:
        if item in shops:
            items_filtered.append(item)
    return items_filtered


def get_cart():
    """

    :return:
    """
    with open('data/cache_cart.json') as f:
        cart = json.load(f)
        return cart['cart']


def add_cart(item:dict):
    """

    :param item:
    :return:
    """
    cart = get_cart()
    cart.append(item)
    cart = {'cart': cart}
    with open('data/cache_cart.json', 'w') as f:
        # noinspection PyTypeChecker
        json.dump(cart, f)
        return True


def send_cart(self):
    """

    :param self:
    """
    for shop in self.send_text:
        if len(self.send_text[shop]) > 1:
            text_cart = (((
                              'Екатерина' if shop.lower() == 'матушка' else 'Ульяна' if shop.lower() == 'алма' else '') + ', добрый день!\nЗаявка на завтра:') if shop.lower() not in (
                'metro', 'купер') else 'METRO:') + '\n' + self.send_text[shop]
            from tg_bot import just_send
            just_send(text_cart)


def remove_cart(item:dict):
    """

    :param item:
    :return:
    """
    cart = get_cart()
    cart.remove(item)
    cart = {'cart': cart}
    with open('data/cache_cart.json', 'w') as f:
        # noinspection PyTypeChecker
        json.dump(cart, f)
        return True


def preset(name, back_list, new):
    """

    :param name:
    :param back_list:
    :param new:
    :return:
    """
    name_ = None
    if type(back_list) not in (list, tuple):
        return None

    for i in back_list:
        if i in name.lower():
            name_ = new.join(name.lower().split(i))
            break
    return name_


def filter_names(name):
    """

    :param name:
    :return:
    """
    base = {
        'куриное': ('цб', 'цыпленка-бройлеров', 'цыпленка бройлера', 'кур.грудки', 'цыпленка'),
        'филе грудки': ('филе  грудки',)
    }

    all_check = {}
    find_type = None
    name_ = name

    for i in base:
        for i2 in base[i]:
            all_check[i2] = i  # Наполнение всех вариантов замен

    for i in all_check:
        if i in name:
            find_type = all_check[i]
            break

    if find_type:
        back_list = base[find_type]
        new = find_type
        if type(back_list) not in (list, tuple):
            return None

        for i in back_list:
            if i in name.lower():
                name_ = new.join(name.lower().split(i))
                break

    return name_


def str_to_dict1(str_:str):
    """

    :param str_:
    :return:
    """
    if not isinstance(str_, str):
        log('Параметр не является строкой.', 2)
        return

    new = ''.join((''.join(''.join(str_.split('{')).split('}')).split("'")))
    new = [new.split(', ')[0].split(': '), new.split(', ')[1].split(': '), new.split(', ')[2].split(': ')]
    new = {new[0][0]: new[0][1], new[1][0]: new[1][1], new[2][0]: new[2][1]}
    return new


def str_to_dict(text:str):
    """

    :param text:
    :return:
    """

    if not isinstance(text, str):
        log('Параметр не является строкой.', 2)
        return

    new = ''.join((''.join(''.join(text.split('{')).split('}')).split("'")))
    new = new.split(', ')
    end = {}
    for i in new:
        data = i.split(': ')
        if len(data) == 2:
            end[data[0]] = data[1]
    return end


def str_to_list(text:str):
    """

    :param text:
    :return:
    """
    text = str(text)
    new = ''.join((''.join(''.join(text.split('[')).split(']')).split("'")))
    new = new.split(', ')
    end = {}
    for i in new:
        data = i.split(', ')
        if len(data) == 2:
            end[data[0]] = data[1]
    return end


def finder(text:str, items:list):
    """

    :param text:
    :param items:
    :return:
    """
    text = text.split(' ')
    finding_items = []
    first_word = True
    for word in text:
        if word != '':
            if first_word:
                for item in items:
                    if word.lower() in item['name'].lower():
                        finding_items.append(item)
                first_word = False
            else:
                finding_items_temp = []
                for item in finding_items:
                    if word.lower() in item['name'].lower():
                        finding_items_temp.append(item)
                finding_items = finding_items_temp

    return finding_items
