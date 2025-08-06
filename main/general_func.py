"""
Функции сопутствующие всему проекту.
"""
import time

from log import log

import asyncio
import json

import threading

_t2b_lock = threading.Lock()

# !/usr/bin/env python # -* - coding: utf-8-* -

cache_cart = 'data/cache_cart.json'


async def async_start(start):
    """

    :param start:
    """
    loop = asyncio.get_event_loop()
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor()
    # noinspection PyTypeChecker
    await loop.run_in_executor(executor, start)


async def background_load(main_app):
    """
    Асинхронная прогрузка функций:
    1. Подрузка кэша.
    2. Активация события on_enter.
    3. Телеграм бот.
    4. Автоматическая отправка админ меню в ТГ бот.
    5. Парсинг такси.
    :param main_app: Экземпляр класса интерфейса главного меню.
    """

    # noinspection PyTypeChecker, PyBroadException
    def load_cache():
        """
        Загрузка кэша в оперативную память.
        """
        with open('data/cache_prices.json') as f:
            result = json.load(f)
            if result['cache']:
                result_filtered = filter_shops(result['cache'])

                main_app.base_price = result_filtered

                log('Прайс из кэша загружен в оперативку!')

    def activate_tg_bot():
        """
        Телеграм бот.
        """
        from bot import run, start
        result = run()
        if result == 7:
            return 7
        log('TG бот включен!')

    def send_first():
        """
        Автоматическая отправка админ меню в ТГ бот.
        """
        time.sleep(1)
        from T2.menu import admin_menu

        class Call(object):
            """
                Класс 'call'
            """
            data = 'Первоначальный запуск'

            class message: message_id = 0

            class from_user: id = 828853360

            def __init__(self):
                self.data = 'Первоначальный запуск'
                self.from_user.id = 828853360
                self.message.message_id = 0

        admin_menu(Call, 1)
        log('Админу было отправлено меню!')

    def activate_taxi_pars():
        """
        Парсинг такси.
        """
        import ParserTaxi.taxi_parser as tp

        tp.run()
        log('Парсер такси включен!')

    def check_metro():
        with open('data/config.json') as f:
            data = json.load(f)
            if data['metro_active']:  # Если метро включено в настройках, запускает авторизацию
                from PriceCheck import parse_metro
                result = parse_metro.get_valid_session()
                if result: log('MShop авторизован!')

    await async_start(load_cache)
    #await async_start(activate_taxi_pars) / Временно не работает из-за чего следующие функции не запускаются.
    await async_start(send_first)
    await async_start(check_metro)
    await async_start(activate_tg_bot)


async def refresh(self):
    """
    Асинхронный запуска обновления кэша.
    :param self:
    """

    def start():
        """
        Обновление кэша.
        """

        from PriceCheck.read_doc import scanner
        log('Сканирование кэша прайсов запущено!')
        scanner()
        log('Сканирование кэша прайсов завершено!')

        with open('data/cache_prices.json') as f:
            result = json.load(f)
            result_filtered = filter_shops(result['cache'])
            self.base_price = result_filtered
            log('Отсканирован кэш и подгружен в оперативку!')

        with open('data/config.json') as f:
            data = json.load(f)
            if data['metro_active']:  # Если метро включено в настройках, запускает авторизацию
                from PriceCheck import parse_metro
                result = parse_metro.get_valid_session()
                if result: log('MShop авторизован!')

    await async_start(start)


async def send_to_cart(item, parse_metro):
    """
    Асинхронный запуска отправки товара в корзину metro.
    :param item: Объект товара.
    :param parse_metro: Объект класса...
    """

    def start():
        """
        Отправка товара в корзину metro.
        """

        parse_metro.add_cart(item)
        log(f'Товар: "{item["product_name"]}" добавлен в корзину!')

    await async_start(start)


async def remove_from_cart(item, parse_metro):
    """
    Асинхронный запуск удаления из корзины metro.
    :param item: Объект товара.
    :param parse_metro: Объект класса...
    """

    def start():
        """
            Функция запуска
        """
        parse_metro.remove_cart(item)
        log(f'Товар: "{item["product_name"]}" удалён из корзины!')

    await async_start(start)


async def find(main_app, item_obj):
    """
    Асинхронный запуск поиска товара в прайс-листе.
    :param main_app: Объект интерфейса главного экрана.
    :param item_obj: Объект интерфейса карточки товара.
    """

    def start():
        """
        Поиск товара в прайс-листе.
        """
        from PriceCheck.commands import Main
        Main.find(main_app, item_obj)

    await async_start(start)


def filter_shops(items: dict):
    """
    Фильтр активных магазинов для кэша

    :param items: Кэшированные объекты
    :return:
    """
    shops = []
    items_filtered = []
    with open('data/config.json') as f:
        config = json.load(f)
        for shop in config['shops_params']:
            if shop['status']:
                shops.append(shop['title'])

    if shops:
        for item in items:
            if items[item]['title'] in shops:
                items_filtered.append(items[item])

    return items_filtered


def get_cart():
    """
    Получение корзины.
    :return:
    """
    with open(cache_cart) as f:
        cart = json.load(f)
        return cart['cart']


def add_cart(item: dict):
    """
    Добавление в корзину.
    :param item:
    :return:
    """

    cart = get_cart()
    cart.append(item)
    cart = {'cart': cart}

    with open(cache_cart, 'w') as f:
        # noinspection PyTypeChecker
        json.dump(cart, f)
        return True


async def send_cart(text: str):
    """
    Отправка корзины в телеграм бот.
    :param text: Готовый текст для отправки
    """

    # for shop in self.send_text:
    #     if len(self.send_text[shop]) > 1:
    #         name = ('Екатерина' if shop.lower() == 'матушка' else 'Ульяна' if shop.lower() == 'алма' else '')
    #         header_text = (
    #             (name + ', добрый день!\nЗаявка на завтра:') if shop.lower() not in ('metro', 'купер') else 'METRO:')
    #         text_cart = header_text + '\n' + self.send_text[shop]

    def start():
        from bot import just_send

        just_send(text)

    await async_start(start)


def remove_cart(item: dict):
    """
    Удаление из корзины
    :param item:
    :return:
    """
    cart = get_cart()
    cart.remove(item)
    cart = {'cart': cart}
    with open(cache_cart, 'w') as f:
        # noinspection PyTypeChecker
        json.dump(cart, f)
        return True


def filter_names(name):
    """
    Приведение разных обозначений продукта к единому формату.
    :param name: Исходное наименование товара.
    :return: Готовое наименование.
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


def str_to_dict(text: str):
    """
    Конвертация строки в json, потом в словарь.

    :param text: Строка. Соответствующая формату dict.
    :return: Готовый словарь.
    """

    end = json.loads('"'.join(text.split("'")))

    return end


def finder(text: str, items: dict):
    """
    Поиск объекта {text} в списке {items}.

    :param text: Имя объекта.
    :param items: Словарь объектов.
    :return:
    """
    text = text.split(' ')
    finding_items = {}
    first_word = True
    for word in text:
        if word != '':
            if first_word:
                for item in items:
                    if word.lower() in item[item]['product_name'].lower():
                        finding_items[item] = items[item]
                first_word = False
            else:
                finding_items_temp = []
                for item in finding_items:
                    if word.lower() in item['product_name'].lower():
                        finding_items_temp[item] = items[item]
                finding_items = finding_items_temp

    return finding_items


def text_lot(lots, i):
    """
    Подготовка текста для сообщения с данными о лоте.

    :param lots: Список всех лотов.
    :param i: Вероятно id нужного лота
    :return: Готовый текст
    """

    emoji_symbol = {'bomb': '💣', 'cat': '😸', 'cool': '😎', 'devil': '😈', 'rich': '🤑', 'scream': '😱', 'tongue': '😛',
                    'zipped': '🤐'}

    date_time_str = lots[i]['creationDate'].split('+')[0]
    date = date_time_str.split('T')[0]
    date = date.split('-')
    months = [r'янв\.', r'фев\.', r'мар\.', r'апр\.', r'мая\.', r'июня\.',
              r'июля', r'авг\.', r'сен\.', r'окт\.', r'ноя\.', r'дек\.']
    date = f'{date[2]} {months[int(date[1]) - 1]}'
    time_str = date_time_str.split('T')[1].split('.')[0].split(':')
    time_str = time_str[0] + ':' + time_str[1]
    emojis = ''
    for emoji_text in lots[i]['emojis']:
        print(emoji_text)
        emojis += emoji_symbol[emoji_text]
    cymbal_emoji = emojis if emojis != '' else r'пусто\!'
    answer = f'_{str(lots[i]["value"])}_' + (
        '_ГБ_ ' if lots[i]['type'] == 'gb' else (r' минут\(ы\) ' if lots[i]['type'] == 'min' else r' ед\.')) + \
             f'за _{str(int(lots[i]["price"]))}₽_'
    answer += f"\n\n*Эмодзи:* {cymbal_emoji}"
    answer += f'\n*Имя:* {lots[i]["name"] if lots[i]["name"] is not None else "Анонимно"}'
    answer += f"\n*Создан:* {date} {time_str}"
    answer += '\n*Статус:* ' + ('В топе ⬆️' if lots[i]['status'] else 'В жопе ⬇️')
    return answer


def t2b(uid, data: dict = True, type_='g'):
    """
    Обработчик базы пользователей

    :param uid: ID пользователя (Обязательно)
    :param data: Словарь с данными пользователя (При типе 'u')
    :param type_: Тип действия: ('g'- получить [default], 'u' - обновить, 'd' - сброс)
    :return: Набор данных о пользователе (При типе 'g')
    """
    uid = str(uid)
    default = {'auth_login': '', 'auth_password': '', 'status_run_auto': 0, 'status_lagg': 0,
               'status_sms': 0, 'stage_authorize': 0, 'lvl_setting': 0, 'lvl_redactor': 0,
               'security_code': '', 'security_code_token': '', "config_count": 6, "config_autotime": 35,
               "config_uom": "gb", "config_repeat": 20, "config_price": 90, "config_type": "data"}
    with _t2b_lock:
        with open(f'data/t2b.json') as f:
            if type_ == 'u':
                file = json.load(f)
                for i in data:
                    file[uid][i] = data[i]
                with open(f'data/t2b.json', 'w') as f2:
                    json.dump(file, f2)
            elif type_ == 'g':
                file = json.load(f)
                if uid in file:
                    return file[uid]
                else:
                    file[uid] = default

                    with open('data/t2b.json', 'w') as f2:
                        json.dump(file, f2)
                        return file[uid]
            elif type_ == 'd':
                file = json.load(f)
                if uid in file:
                    file[uid] = default
                    with open(f'data/t2b.json', 'w') as f2:
                        json.dump(file, f2)
