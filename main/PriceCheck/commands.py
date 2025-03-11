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
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText, MDSnackbarButtonContainer, MDSnackbarActionButton, \
    MDSnackbarActionButtonText, MDSnackbarCloseButton

import handler
from PriceCheck import parse_metro
from log import log

ToolsAJob = App.get_running_app


class Base:
    """
        Базовый класс
    """

    @staticmethod
    def func_dialog_save_enter(self, key):
        """

        :param self:
        :param key:
        """
        if len(self.ids.text_find.text) > 0:
            if key == 13:
                self.find(key)

    @staticmethod
    def activate_enter_finder(self):
        """

        :param self:
        """
        Window.bind(on_key_down=self.func_dialog_save_enter)

    @staticmethod
    def on_focus_change(self, instance, text):
        """

        :param self:
        :param instance:
        :param text:
        """
        shop = str(instance.id)
        self.send_text[shop] = str(text)

    # noinspection PyUnusedLocal
    @staticmethod
    def notify(self, text):
        """

        :param self:
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
    def find(Main_, ItemObjs):
        """

        :param Main_:
        :param ItemObjs:
        """
        name = Main_.ids.text_find.text

        Main_.ids.list_items_obj.clear_widgets()
        finder_items = handler.finder(name, Main_.base_price)  # Поиск товара
        result_metro = []
        if Main_.checkbox_parser_metro.active:
            result_metro = parse_metro.search(name)

        if type(result_metro) is list:
            for item in result_metro:
                finder_items.append(
                    {'seller': 'METRO', 'name': item['name'], 'cost': str(item['price']), 'bundleId': item['bundleId'],
                     'minOrderQuantity': item['minOrderQuantity']})

        for item in finder_items:  # Добавление товаров в список на главный экран
            ItemObj = ItemObjs()
            text = item['name'] + '.'

            if 'type' in item:
                if item['type'] != '':
                    cost = 'Цена: ' + item['cost'] + '₽' + ' за ' + item['type']
                else:
                    cost = 'Цена: ' + item['cost'] + '₽'
            else:
                cost = 'Цена: ' + item['cost'] + '₽'

            ItemObj.ids.item_seller.text = item[
                'seller']  # Здесь надо присвоить ячейкам с товарами значения и ниже в двух также
            ItemObj.ids.item_name.text = text.capitalize()
            ItemObj.ids.item_cost.text = cost

            def btn_for_item(icon, on_release, icon_color, oid=str(item)):
                """

                :param icon:
                :param on_release:
                :param icon_color:
                :param oid:
                """
                ItemObj.ids.idItem.icon = icon
                ItemObj.ids.idItem.bind(on_release=on_release)
                # ItemObj.ids.item_object.bind(on_release=on_release)
                ItemObj.ids.idItem.icon_color = icon_color
                ItemObj.ids.idItem.id = oid

            if item in handler.get_cart():
                if item['seller'] == 'METRO':
                    btn_for_item('cart-remove', Main_.remove_from_cart_metro, 'red')
                else:
                    btn_for_item('cart-remove', Main_.remove_from_cart, 'red')
            else:
                if item['seller'] == 'METRO':
                    btn_for_item('cart-plus', Main_.add_to_cart_metro, 'blue')
                else:
                    btn_for_item('cart-plus', Main_.add_to_cart, 'blue')

            Main_.ids.list_items_obj.add_widget(ItemObj)

    def refresh(self):
        """
            Обновление базы товаров
        """
        asyncio.ensure_future(handler.refresh(self))


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
        temp = {'filename': TextInput(text=str(shop['filename']), size_hint_y=None, height="30dp"),
                'sid_w': TextInput(text=str(shop['sid'][0]), size_hint_x=None, width="22dp", size_hint_y=None,
                                   height="30dp"),
                'sid_h': TextInput(text=str(shop['sid'][1]), size_hint_x=None, width="22dp", size_hint_y=None,
                                   height="30dp"),
                'sid_t': TextInput(text=str(shop['sid'][2]), size_hint_x=None, width="22dp", size_hint_y=None,
                                   height="30dp"),
                'seller': TextInput(text=shop['seller'], size_hint_y=None, height="30dp"),
                'findname_w': TextInput(text=str(shop['findname'][0]), size_hint_x=None, width="22dp", size_hint_y=None,
                                        height="30dp"),
                'findname_h': TextInput(text=str(shop['findname'][1]), size_hint_x=None, width="22dp", size_hint_y=None,
                                        height="30dp"),
                'findtext': TextInput(text=shop['findtext'], size_hint_y=None, height="30dp"),
                'active': MDCheckbox(active=shop['active'], size_hint_x=None, width="25dp")}
        return temp

    @staticmethod
    def open(add):
        """

        :param add:
        :return:
        """
        Main_ = ToolsAJob().MainApp
        if Main_.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main_.dialog.clear_widgets()
            Main_.dialog.dismiss()

        SettingsMain = ToolsAJob().SettingsMainApp()

        def content():
            """

            :return:
            """
            SettingsMain.data['shops'] = []

            with open('data/config.json') as f:
                data = json.load(f)

            if add:
                new_shop = {"filename": "Введите имя файла", "sid": [0, 0, 0], "seller": "Введите название поставщика",
                            "findname": [0, 0], "findtext": "Введите слово для поиска", "active": False}
                data["shops"].append(new_shop)

            for shop in data["shops"]:
                print(shop)
                preset_shop = Settings.preset_shop(shop)
                SettingsMain.data['shops'].append(preset_shop)

            for shop in SettingsMain.data['shops']:
                SettingShop = ToolsAJob().SettingShopApp()

                for obj in shop:
                    SettingShop.ids.shop.add_widget(shop[obj])

                SettingsMain.ids.main.add_widget(SettingShop)

            SettingsMain.ids.checkbox_parser_metro.active = data['metro_active']
            return SettingsMain

        Main_.dialog = content()

        Main_.dialog.open()

    # noinspection PyUnusedLocal
    @staticmethod
    def add_shop(self, Main_):
        """

        :param self:
        :param Main_:
        """
        Main_.settings_open(None, add=True)

    @staticmethod
    def save(self, Main_):
        """

        :param self:
        :param Main_:
        """
        with open('data/config.json') as f:
            data = json.load(f)
        with open('data/config.json', 'w') as f:
            data["shops"] = []
            data['metro_active'] = Main_.checkbox_parser_metro.active

            for shop in self.data['shops']:
                sid_w = shop['sid_w'].text
                sid_h = shop['sid_h'].text
                sid_t = shop['sid_t'].text
                seller = shop['seller'].text
                findname_w = shop['findname_w'].text
                findname_h = shop['findname_h'].text
                findtext = shop['findtext'].text
                active = shop['active'].active

                filename = shop['filename'].text

                data["shops"].append(
                    {'filename': filename, 'sid': (int(sid_w), int(sid_h), int(sid_t)), 'seller': seller,
                     'findname': (int(findname_w), int(findname_h)), 'findtext': findtext, 'active': active})
            # noinspection PyTypeChecker
            json.dump(data, f)

        with open('data/cache_prices.json') as f:
            result = json.load(f)
            result_filtered = handler.filter_shops(result)
            Main_.base_price = result_filtered
            log('Кэш прайса обновлён!')

        if Main_.dialog:
            Main_.dialog.dismiss()

    # noinspection PyUnusedLocal
    @staticmethod
    def exit(self, Main_):
        """

        :param self:
        :param Main_:
        """
        if Main_.dialog:
            Main_.dialog.dismiss()


class Cart:
    """
        Корзина
    """

    @staticmethod
    def open():
        """

        :return:
        """
        Main_ = ToolsAJob().MainApp
        # Открытие корзины

        if Main_.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main_.dialog.dismiss()

        def content():
            """

            :return:
            """
            app = ToolsAJob()
            CartMainApp = app.CartMainApp()
            for shop in ['Матушка', 'Алма', 'METRO']:
                CartShop = app.CartShopApp()
                items_list = []

                cart_get = handler.get_cart()
                for item in cart_get:  # Наполнение списка товарами из кэша
                    CartItem = app.CartItemsApp()
                    if shop.lower() == item['seller'].lower():
                        if item in cart_get:
                            CartItem.ids.buttonItem.icon = 'cart-remove'
                            CartItem.ids.buttonItem.icon_color = 'blue'
                            if item['seller'] == 'METRO':
                                pass
                                CartItem.ids.buttonItem.on_release = Main_.remove_from_cart_metro
                            else:
                                pass
                                CartItem.ids.buttonItem.on_release = Main_.remove_from_cart
                        else:
                            CartItem.ids.buttonItem.icon = 'cart-plus'
                            CartItem.ids.buttonItem.icon_color = 'blue'
                            if item['seller'] == 'METRO':
                                pass
                                CartItem.ids.buttonItem.on_release = Main_.add_to_cart_metro
                            else:
                                CartItem.ids.buttonItem.on_release = Main_.add_to_cart
                        CartItem.ids.buttonItem.id = str(item) + 'cart'

                        CartItem.ids.textItem.text = str(item['name'])
                        items_list.append(CartItem)

                if len(items_list) > 0:  # Наполнение корзины товарами
                    CartShop.ids.CartName.text = str(shop) + ':'

                    for i in items_list:
                        CartShop.ids.listItems.add_widget(i)

                CartMainApp.ids.listShops.add_widget(CartShop)
            return CartMainApp

        Main_.dialog = content()
        Main_.dialog.open()

    # noinspection PyUnusedLocal
    @staticmethod
    def edit(Main_, instance):
        """

        :param Main_: 
        :param instance: 
        """
        print(instance)

    @staticmethod
    def send(Main_):
        """

        :param Main_: 
        """
        asyncio.ensure_future(handler.send_cart(Main_))
        if Main_.dialog:
            Main_.dialog.dismiss()

    @staticmethod
    def back(self):
        """

        :param self:
        """
        pass

    @staticmethod
    def add_to_cart(Main_, instance):
        """

        :param Main_: 
        :param instance: 
        """
        # Main = MainApp().Main
        print(instance)
        print('Разделитель')
        print(instance.icon)
        print(instance.icon_color)
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=Main_.add_to_cart)
        instance.bind(on_release=Main_.remove_from_cart)
        item = instance.id
        item = handler.str_to_dict(item)  # Конвертация строки в словарь

        if item not in handler.get_cart():  # Если объекта нет в корзине
            handler.add_cart(item)  # Отправка в корзину на сервер

    @staticmethod
    def remove_from_cart(Main_, instance):
        """

        :param Main_: 
        :param instance: 
        """
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=Main_.remove_from_cart)
        instance.bind(on_release=Main_.add_to_cart)
        item = instance.id
        item = handler.str_to_dict(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in handler.get_cart():  # Если объект есть в корзине
            handler.remove_cart(dict(item))  # То объект удаляется из корзины

        if Main_.dialog:  # Закрыть диалоговое окно, если оно открыто
            print(Main_.dialog)
            # Main.dialog.dismiss()
            # Main.dialog = None
            # Main.cart_open(Main)

    @staticmethod
    def add_to_cart_metro(Main_, instance):
        """

        :param Main_: 
        :param instance: 
        """
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=Main_.add_to_cart_metro)
        instance.bind(on_release=Main_.remove_from_cart_metro)
        item = instance.id
        item = handler.str_to_dict1(item)  # Конвертация строки в словарь

        if item not in handler.get_cart():  # Если объекта нет в корзине
            asyncio.ensure_future(handler.send_to_cart(item, parse_metro))  # Отправка в корзину на сервер
            handler.add_cart(dict(item))  # То объект добавляется в корзину

    @staticmethod
    def remove_from_cart_metro(Main_, instance):
        """

        :param Main_: 
        :param instance: 
        """
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=Main_.remove_from_cart_metro)
        instance.bind(on_release=Main_.add_to_cart_metro)
        item = instance.id
        item = handler.str_to_dict(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in handler.get_cart():  # Если объект есть в корзине
            asyncio.ensure_future(handler.remove_from_cart(item, parse_metro))  # Удаление из корзины на сервере
            handler.remove_cart(dict(item))  # То объект удаляется из корзины

        if Main_.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main_.dialog.dismiss()
            Main_.dialog_cart_open(Main_)
