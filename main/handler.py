import asyncio

import json

import ParserTaxi.taxi_parser as tp
from log import log
import tg_bot
from PriceCheck.read_doc import scanner

# !/usr/bin/env python # -* - coding: utf-8-* -

def str_to_dict1(str_):
    str_ = str(str_)
    new = ''.join((''.join(''.join(str_.split('{')).split('}')).split("'")))
    new = [new.split(', ')[0].split(': '), new.split(', ')[1].split(': '), new.split(', ')[2].split(': ')]
    new = {new[0][0]: new[0][1], new[1][0]: new[1][1], new[2][0]: new[2][1]}
    return new


def str_to_dict(text):
    text = str(text)
    new = ''.join((''.join(''.join(text.split('{')).split('}')).split("'")))
    new = new.split(', ')
    end = {}
    for i in new:
        data = i.split(': ')
        if len(data) == 2:
            end[data[0]] = data[1]
    return end


def str_to_list(text):
    text = str(text)
    list_ = []
    new = ''.join((''.join(''.join(text.split('[')).split(']')).split("'")))
    new = new.split(', ')
    end = {}
    for i in new:
        data = i.split(', ')
        if len(data) == 2:
            end[data[0]] = data[1]
    return end


def finder(text, items):
    text = text.split(' ')
    finded_items = []
    first_word = True
    for word in text:
        if word != '':
            if first_word:
                for item in items:
                    if word.lower() in item['name'].lower():
                        finded_items.append(item)
                first_word = False
            else:
                finded_items_temp = []
                for item in finded_items:
                    if word.lower() in item['name'].lower():
                        finded_items_temp.append(item)
                finded_items = finded_items_temp

    return finded_items


async def async_start(start):
    loop = asyncio.get_event_loop()
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor()
    await loop.run_in_executor(executor, start)


def filter_shops(items):
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


async def background_load(self):
    def start():
        tg_bot.start()
        log('TG бот включен!', 1)

        tp.run()
        log('Парсер такси включен!', 1)

        with open('data/cache_prices.json') as f:
            result = json.load(f)
            result_filtered = filter_shops(result)
            self.base_price = result_filtered
            log('Прайс загружен в кэш!', 1)

        try:
            with open('data/cache_cart.json', 'w') as f:
                json.dump({'cart': []}, f)
        except:
            with open('data/cache_cart.json', 'w') as f:
                json.dump({'cart': []}, f)

        self.activate_enter_finder(self)
        log('Поиск по нажатию "enter" включен!', 1)

    await async_start(start)


async def refresh(self):
    def start():
        imports()

        scanner('')
        log('Сканирование прайсов запущено!', 1)
        with open('data/cache_prices.json') as f:
            result = json.load(f)
            result_filtered = filter_shops(result)
            self.base_price = result_filtered
            log('Отсканированы файлы и обновлён кэш!', 1)

        with open('data/config.json') as f:
            data = json.load(f)
            if data['metro_active']:  # Если метро включено в настройках, запускает авторизацию
                import parse_metro
                parse_metro.auth_check()
                # self.checkbox_parser_metro.active = True
                log('MShop авторизован!', 1)

    await async_start(start)


async def send_to_cart(item, parse_metro):
    def start():
        parse_metro.add_cart(item)
        log(f'Товар: "{item["name"]}" добавлен в корзину!', 1)

    await async_start(start)


async def remove_from_cart(item, parse_metro):
    def start():
        parse_metro.remove_cart(item)
        log(f'Товар: "{item["name"]}" удалён из корзины!', 1)

    await async_start(start)


def get_cart():
    with open('data/cache_cart.json') as f:
        cart = json.load(f)
        return cart['cart']


def add_cart(item):
    cart = get_cart()
    cart.append(item)
    cart = {'cart': cart}
    with open('data/cache_cart.json', 'w') as f:
        json.dump(cart, f)
        return True


def send_cart(self):
    for shop in self.send_text:
        if len(self.send_text[shop]) > 1:
            text_cart = (((
                              'Екатерина' if shop.lower() == 'матушка' else 'Ульяна' if shop.lower() == 'алма' else '') + ', добрый день!\nЗаявка на завтра:') if shop.lower() not in (
                'metro', 'купер') else 'METRO:') + '\n' + self.send_text[shop]

            tg_bot.send(text_cart)


def remove_cart(item):
    cart = get_cart()
    cart.remove(item)
    cart = {'cart': cart}
    with open('data/cache_cart.json', 'w') as f:
        json.dump(cart, f)
        return True


def chablone(name, back_list, new):
    name_ = None
    if type(back_list) not in (list, tuple):
        return None

    for i in back_list:
        if i in name.lower():
            name_ = new.join(name.lower().split(i))
            break
    return name_


def filter_names(name):
    base = {
        'куриное': ('цб', 'цыпленка-бройлеров', 'цыпленка бройлера', 'кур.грудки', 'цыпленка'),
        'филе грудки': ('филе  грудки')
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


def t2b(uid, data:dict, type_='g'):
    if type_ == 'u':
        with open(f'data/t2b.json', 'w+') as f:
            file = json.load(f)
            for i in data:
                file[uid][i] = data[i]
            json.dump(file, f)
    elif type_ == 'g':
        with open('data/t2b.json') as f:
            if uid in json.load(f):
                return json.load(f)[uid]
            else:
                with open(f'data/t2b.json', 'w') as f:
                    file = json.load(f)
                    file[uid] = {'auth_login': '', 'auth_password': '', 'status_run_auto': 0, 'status_lagg': 0,
                                 'status_sms': 0, 'stage_autorize': 0, 'lvl_setting': 0, 'lvl_redactor': 0,
                                 'security_code': '',
                                 'security_code_token': ''}
                    json.dump(file, f)
                    return file[uid]
    elif type_ == 'd':
        with open(f'data/t2b.json', 'w+') as f:
            file = json.load(f)
            if data in file:
                del file[data]
                json.dump(file, f)