"""
    Команды для парсинга цен
"""

import asyncio
import json

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import (MDSnackbar,
                                 MDSnackbarSupportingText,
                                 MDSnackbarButtonContainer,
                                 MDSnackbarActionButton,
                                 MDSnackbarActionButtonText,
                                 MDSnackbarCloseButton)

import handler
from log import log
from PriceCheck import parse_metro

ToolsAJob = App.get_running_app


class Base:
    """
        Базовый класс
    """

    @staticmethod
    def func_dialog_save_enter(main, key):
        """

        :param main:
        :param key:
        """
        if len(main.ids.text_find.text) > 0 and key == 13:
            main.find(key)

    @staticmethod
    def activate_enter_finder(main):
        """

        :param main:
        """
        Window.bind(on_key_down=main.func_dialog_save_enter)

    @staticmethod
    def on_focus_change(main, instance, text):
        """

        :param main:
        :param instance:
        :param text:
        """
        shop = str(instance.id)
        main.send_text[shop] = str(text)

    # noinspection PyUnusedLocal
    @staticmethod
    def notify(text):
        """

        :param text:
        """
        MDSnackbar(
            MDSnackbarSupportingText(text=text, ),
            MDSnackbarButtonContainer(
                MDSnackbarActionButton(
                    MDSnackbarActionButtonText(
                        text="Action button"
                    ),
                ),
                MDSnackbarCloseButton(
                    icon="close",
                ),
                pos_hint={"center_y": 0.5}
            ),
            y=dp(24),
            orientation="horizontal",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
        ).open()


class Main:
    """
        Приложение
    """

    @staticmethod
    def find(main, item_objs):
        """
        Поиск товаров.
        :param main:
        :param item_objs:
        """

        name = main.ids.text_find.text

        main.ids.list_items_obj.clear_widgets()
        finder_items = handler.finder(name, main.base_price)  # Поиск товара

        result_metro = []
        if main.checkbox_parser_metro.active:
            result_metro = parse_metro.search(name)

        if isinstance(result_metro, list):
            for item in result_metro:
                finder_items.append(
                    {'seller': 'METRO',
                     'name': item['name'],
                     'cost': str(item['price']),
                     'bundleId': item['bundleId'],
                     'minOrderQuantity': item['minOrderQuantity']
                     })

        for item in finder_items:  # Добавление товаров в список на главный экран

            item_obj = item_objs()
            text = item['name'] + '.'
            cost_str = 'Цена: ' + item['cost'] + '₽'

            if 'type' in item:
                if item['type'] != '':
                    cost = cost_str + ' за ' + item['type']
                else:
                    cost = cost_str
            else:
                cost = cost_str

            item_obj.ids.item_seller.text = item[
                'seller']  # Здесь надо присвоить ячейкам с товарами значения и ниже в двух также
            item_obj.ids.item_name.text = text.capitalize()
            item_obj.ids.item_cost.text = cost

            def btn_for_item(icon, on_release, icon_color, oid=str(item)):
                """

                :param icon:
                :param on_release:
                :param icon_color:
                :param oid:
                """
                item_obj.ids.idItem.icon = icon
                item_obj.ids.idItem.bind(on_release=on_release)
                item_obj.ids.idItem.icon_color = icon_color
                item_obj.ids.idItem.id = oid

            if item in handler.get_cart():
                if item['seller'] == 'METRO':
                    btn_for_item('cart-remove', main.remove_from_cart_metro, 'red')
                else:
                    btn_for_item('cart-remove', main.remove_from_cart, 'red')
            else:
                if item['seller'] == 'METRO':
                    btn_for_item('cart-plus', main.add_to_cart_metro, 'blue')
                else:
                    btn_for_item('cart-plus', main.add_to_cart, 'blue')

            main.ids.list_items_obj.add_widget(item_obj)


class Settings:
    """
        Настройки
    """

    @staticmethod
    def preset_shop(shop):
        """

        :param shop:
        :return:
        """
        temp = {'filename': TextInput(text=str(shop['filename']),
                                      size_hint_y=None,
                                      height="30dp"),

                'sid_w': TextInput(text=str(shop['sid'][0]),
                                   size_hint_x=None,
                                   width="22dp",
                                   size_hint_y=None,
                                   height="30dp"),

                'sid_h': TextInput(text=str(shop['sid'][1]),
                                   size_hint_x=None,
                                   width="22dp",
                                   size_hint_y=None,
                                   height="30dp"),

                'sid_t': TextInput(text=str(shop['sid'][2]),
                                   size_hint_x=None,
                                   width="22dp",
                                   size_hint_y=None,
                                   height="30dp"),

                'seller': TextInput(text=shop['seller'],
                                    size_hint_y=None,
                                    height="30dp"),

                'findname_w': TextInput(text=str(shop['findname'][0]),
                                        size_hint_x=None,
                                        width="22dp",
                                        size_hint_y=None,
                                        height="30dp"),

                'findname_h': TextInput(text=str(shop['findname'][1]),
                                        size_hint_x=None,
                                        width="22dp",
                                        size_hint_y=None,
                                        height="30dp"),

                'findtext': TextInput(text=shop['findtext'],
                                      size_hint_y=None,
                                      height="30dp"),

                'active': MDCheckbox(active=shop['active'],
                                     size_hint_x=None,
                                     width="25dp")}
        return temp

    @staticmethod
    def open(add):
        """

        :param add:
        :return:
        """
        main = ToolsAJob().MainApp
        if main.dialog:  # Закрыть диалоговое окно, если оно открыто
            main.dialog.clear_widgets()
            main.dialog.dismiss()

        settings_main = ToolsAJob().SettingsMainApp()

        def content():
            """

            :return:
            """
            settings_main.data['shops'] = []

            with open('data/config.json', encoding='utf-8') as f:
                data = json.load(f)

            if add:
                new_shop = {"filename": "Введите имя файла",
                            "sid": [0, 0, 0],
                            "seller": "Введите название поставщика",
                            "findname": [0, 0],
                            "findtext": "Введите слово для поиска",
                            "active": False}

                data["shops"].append(new_shop)

            for shop in data["shops"]:
                preset_shop = Settings.preset_shop(shop)
                settings_main.data['shops'].append(preset_shop)

            for shop in settings_main.data['shops']:
                settings_shop = ToolsAJob().SettingShopApp()

                for obj in shop:
                    settings_shop.ids.shop.add_widget(shop[obj])

                settings_main.ids.main.add_widget(settings_shop)

            settings_main.ids.checkbox_parser_metro.active = data['metro_active']
            return settings_main

        main.dialog = content()

        main.dialog.open()

    # noinspection PyUnusedLocal
    @staticmethod
    def add_shop(main):
        """

        :param main:
        """
        main.settings_open(None, add=True)

    @staticmethod
    def save(settings_main, main):
        """

        :param settings_main:
        :param main:
        """

        with open('data/config.json', 'a', encoding='utf-8') as f:
            data = json.load(f)
            data["shops"] = []
            data['metro_active'] = main.checkbox_parser_metro.active

            for shop in settings_main.data['shops']:
                sid_w = shop['sid_w'].text
                sid_h = shop['sid_h'].text
                sid_t = shop['sid_t'].text
                seller = shop['seller'].text
                findname_w = shop['findname_w'].text
                findname_h = shop['findname_h'].text
                findtext = shop['findtext'].text
                active = shop['active'].active

                data["shops"].append(
                    {'filename': shop['filename'].text,
                     'sid': (int(sid_w),
                             int(sid_h),
                             int(sid_t)),
                     'seller': seller,
                     'findname': (int(findname_w),
                                  int(findname_h)),
                     'findtext': findtext,
                     'active': active})
            # noinspection PyTypeChecker
            json.dump(data, f)

        with open('data/cache_prices.json', encoding='utf-8') as f:
            result = json.load(f)
            result_filtered = handler.filter_shops(result)
            main.base_price = result_filtered
            log('Кэш прайса обновлён!')

        if main.dialog:
            main.dialog.dismiss()

    # noinspection PyUnusedLocal
    @staticmethod
    def exit(main):
        """
        :param main:
        """

        if main.dialog:
            main.dialog.dismiss()


class Cart:
    """
        Корзина
    """

    @staticmethod
    def open():
        """

        :return:
        """
        main = ToolsAJob().MainApp
        # Открытие корзины

        if main.dialog:  # Закрыть диалоговое окно, если оно открыто
            main.dialog.dismiss()

        def content():
            """

            :return:
            """
            app = ToolsAJob()
            cart_main_app = app.CartMainApp()
            for shop in ['Матушка', 'Алма', 'METRO']:
                cart_shop = app.CartShopApp()
                items_list = []

                cart_get = handler.get_cart()
                for item in cart_get:  # Наполнение списка товарами из кэша
                    cart_item = app.CartItemsApp()
                    if shop.lower() == item['seller'].lower():
                        if item in cart_get:
                            cart_item.ids.buttonItem.icon = 'cart-remove'
                            cart_item.ids.buttonItem.icon_color = 'blue'
                            if item['seller'] == 'METRO':
                                cart_item.ids.buttonItem.on_release = main.remove_from_cart_metro
                            else:
                                cart_item.ids.buttonItem.on_release = main.remove_from_cart
                        else:
                            cart_item.ids.buttonItem.icon = 'cart-plus'
                            cart_item.ids.buttonItem.icon_color = 'blue'
                            if item['seller'] == 'METRO':
                                cart_item.ids.buttonItem.on_release = main.add_to_cart_metro
                            else:
                                cart_item.ids.buttonItem.on_release = main.add_to_cart
                        cart_item.ids.buttonItem.id = str(item) + 'cart'

                        cart_item.ids.textItem.text = str(item['name'])
                        items_list.append(cart_item)

                if len(items_list) > 0:  # Наполнение корзины товарами
                    cart_shop.ids.CartName.text = str(shop) + ':'

                    for i in items_list:
                        cart_shop.ids.listItems.add_widget(i)

                cart_main_app.ids.listShops.add_widget(cart_shop)
            return cart_main_app

        main.dialog = content()
        main.dialog.open()

    # noinspection PyUnusedLocal
    @staticmethod
    def edit(main, instance):
        """

        :param main: 
        :param instance: 
        """

    @staticmethod
    def send(main):
        """

        :param main: 
        """
        asyncio.ensure_future(handler.send_cart(main))
        if main.dialog:
            main.dialog.dismiss()

    @staticmethod
    def back():
        """
         Функция будет содержать возврат назад
        """

    @staticmethod
    def add_to_cart(main, instance):
        """

        :param main: 
        :param instance: 
        """

        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=main.add_to_cart)
        instance.bind(on_release=main.remove_from_cart)
        item = instance.id
        item = handler.str_to_dict2(item)  # Конвертация строки в словарь

        if item not in handler.get_cart():  # Если объекта нет в корзине
            handler.add_cart(item)  # Отправка в корзину на сервер

    @staticmethod
    def remove_from_cart(main, instance):
        """

        :param main: 
        :param instance: 
        """
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=main.remove_from_cart)
        instance.bind(on_release=main.add_to_cart)
        item = instance.id
        item = handler.str_to_dict2(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in handler.get_cart():  # Если объект есть в корзине
            handler.remove_cart(dict(item))  # То объект удаляется из корзины

    @staticmethod
    def add_to_cart_metro(main, instance):
        """

        :param main: 
        :param instance: 
        """
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=main.add_to_cart_metro)
        instance.bind(on_release=main.remove_from_cart_metro)
        item = instance.id
        item = handler.str_to_dict1(item)  # Конвертация строки в словарь

        if item not in handler.get_cart():  # Если объекта нет в корзине
            asyncio.ensure_future(handler.send_to_cart(item, parse_metro))  # Отправка в корзину на сервер
            handler.add_cart(dict(item))  # То объект добавляется в корзину

    @staticmethod
    def remove_from_cart_metro(main, instance):
        """

        :param main: 
        :param instance: 
        """
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=main.remove_from_cart_metro)
        instance.bind(on_release=main.add_to_cart_metro)
        item = instance.id
        item = handler.str_to_dict2(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in handler.get_cart():  # Если объект есть в корзине
            asyncio.ensure_future(handler.remove_from_cart(item, parse_metro))  # Удаление из корзины на сервере
            handler.remove_cart(dict(item))  # То объект удаляется из корзины

        if main.dialog:  # Закрыть диалоговое окно, если оно открыто
            main.dialog.dismiss()
            main.dialog_cart_open(main)
