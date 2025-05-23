"""
    Команды для парсинга цен
"""

import asyncio
import json

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import (MDSnackbar,
                                 MDSnackbarSupportingText,
                                 MDSnackbarButtonContainer,
                                 MDSnackbarActionButton,
                                 MDSnackbarActionButtonText,
                                 MDSnackbarCloseButton)

from functions import (finder,
                       add_cart,
                       get_cart,
                       send_cart,
                       send_to_cart,
                       filter_shops,
                       remove_cart,
                       remove_from_cart,
                       str_to_dict1,
                       str_to_dict2)
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
        Сохранение по нажатию клавиши enter.

        :param main:
        :param key:
        """
        if len(main.ids.text_find.text) > 0 and key == 13:
            main.find(key)

    @staticmethod
    def activate_enter_finder(main):
        """
        Поиск по нажатию клавиши enter.

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
    def notify(text: str):
        """
        Уведомление.

        :param text: Текст
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
    Функции в главном окне приложения.
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
        finder_items = finder(name, main.base_price)  # Поиск товара

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

            if item in get_cart():
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
    Функции в диалоговом окне настроек.
    """

    @staticmethod
    def open():
        """
        Вызов генерирования и открытия диалогового окна с настройками.
        :param add: True - Создаёт новую строку для интеграции нового поставщика. По умолчанию - False.
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


            for shop in data["shops_params"]:
                settings_shop = ToolsAJob().SettingShopApp()

                settings_shop.filename = shop["filename"]
                settings_shop.title = shop["title"]
                settings_shop.dist_h = str(shop["dist_h"])
                settings_shop.dist_w = str(shop["dist_w"])
                settings_shop.dist_text = shop["dist_text"]
                settings_shop.price_w = str(shop["price_w"])
                settings_shop.product_name_w = str(shop["product_name_w"])
                settings_shop.packaging_w = str(shop["packaging_w"])
                settings_shop.status = bool(shop["status"])

                settings_main.ids.main.add_widget(settings_shop)

            settings_main.ids.checkbox_parser_metro.active = data['metro_active']
            return settings_main

        main.dialog = content()

        main.dialog.open()

    @staticmethod
    def save(settings_main, main):
        """
        Сохранение настроек.

        :param settings_main: Класс интерфейса окна с настройками.
        :param main: Класс интерфейса главного окна.
        """

        with open('data/config.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data["shops_params"] = []
            data['metro_active'] = main.checkbox_parser_metro.active

            print(f'Итерация по списку: {settings_main.ids.main.children}')
            for shop in reversed(settings_main.ids.main.children):

                data["shops_params"].append({
                    "filename": shop.ids.get("filename_field").text,
                    "title": shop.ids.get("title_field").text,
                    "dist_h": int(shop.ids.get("dist_h_field").text),
                    "dist_w": int(shop.ids.get("dist_w_field").text),
                    "dist_text": shop.ids.get("dist_text_field").text,
                    "price_w": int(shop.ids.get("price_w_field").text),
                    "product_name_w": int(shop.ids.get("product_name_w_field").text),
                    "packaging_w": int(shop.ids.get("packaging_w_field").text),
                    "status": bool(shop.ids.get("status_field").active)
                })

            # noinspection PyTypeChecker
            f.seek(0)  # Возвращение к началу файла для записи
            json.dump(data, f)
            f.truncate()  # Удаление остатка старого файла

        with open('data/cache_prices.json', encoding='utf-8') as f:
            result = json.load(f)
            result_filtered = filter_shops(result["cache"])
            main.base_price = result_filtered
            log('Кэш прайса обновлён!')

        if main.dialog:
            main.dialog.dismiss()

    # noinspection PyUnusedLocal
    @staticmethod
    def exit(main):
        """
        Закрыть диалоговое окно, без сохранения настроек.

        :param main: Класс интерфейса главного окна.
        """

        if main.dialog:
            main.dialog.dismiss()


class Cart:
    """
    Функции в диалоговом окне корзины.
    """

    @staticmethod
    def open():
        app = ToolsAJob()
        main = app.MainApp
        cart_main_layout = app.CartMainApp()

        if main.dialog:
            main.dialog.dismiss()

        # добавление товаров как раньше
        for shop in ['Матушка', 'Алма', 'METRO']:
            cart_shop = app.CartShopApp()
            items_list = []

            cart_get = get_cart()
            for item in cart_get:
                if shop.lower() == item['seller'].lower():
                    item["quantity"] = 1  # Временное жёсткое задавание количества
                    cart_item = app.CartItemsApp(item)
                    cart_item.ids.name_field.text = item['name']
                    cart_item.ids.qty_field.text = "1"
                    cart_item.ids.buttonItem.icon = 'cart-remove'
                    cart_item.ids.buttonItem.icon_color = 'blue'
                    cart_item.ids.buttonItem.on_release = main.remove_from_cart
                    cart_item.add_product_card(item)
                    items_list.append(cart_item)

            if items_list:
                cart_shop.ids.CartName.text = f"{shop}:"
                for widget in items_list:
                    cart_shop.ids.listItems.add_widget(widget)
                cart_main_layout.ids.cart_items_box.add_widget(cart_shop)

        main.dialog = cart_main_layout

        main.dialog.open()

    # noinspection PyUnusedLocal
    @staticmethod
    def edit(main, instance):
        """
        Редактирование товара.
        :param main: Класс интерфейса главного окна.
        :param instance: Товар, который нужно отредактировать.
        """

    @staticmethod
    def send(main):
        """
        Отправить готовый список товаров в телеграм бот.
        :param main: Класс интерфейса главного окна.
        """
        asyncio.ensure_future(send_cart(main))
        if main.dialog:
            main.dialog.dismiss()

    @staticmethod
    def back():
        """
         Функция будет содержать возврат назад
        """

    @staticmethod
    def add_to_cart(name, instance):
        """
        Добавить товар в корзину.
        :param main: Класс интерфейса главного окна.
        :param instance: Товар, который необходимо добавить.
        """

        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=Cart.add_to_cart)
        instance.bind(on_release=Cart.remove_from_cart)
        item = instance.id

        item = str_to_dict2(item)  # Конвертация строки в словарь

        if item not in get_cart():  # Если объекта нет в корзине
            add_cart(item)  # Отправка в корзину на сервер

    @staticmethod
    def remove_from_cart(main, instance):
        """
        Удалить товар из корзины
        :param main: Класс интерфейса главного окна.
        :param instance: Товар, который необходимо удалить.
        """
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=Cart.remove_from_cart)
        instance.bind(on_release=Cart.add_to_cart)
        item = instance.id
        item = str_to_dict2(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in get_cart():  # Если объект есть в корзине
            remove_cart(dict(item))  # То объект удаляется из корзины

    @staticmethod
    def add_to_cart_metro(main, instance):
        """
        Добавить товар в корзину METRO SHOP.

        :param main: Класс интерфейса главного окна.
        :param instance: Товар, который необходимо добавить.
        """
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=Cart.add_to_cart_metro)
        instance.bind(on_release=Cart.remove_from_cart_metro)
        item = instance.id
        item = str_to_dict1(item)  # Конвертация строки в словарь

        if item not in get_cart():  # Если объекта нет в корзине
            asyncio.ensure_future(send_to_cart(item, parse_metro))  # Отправка в корзину на сервер
            add_cart(dict(item))  # То объект добавляется в корзину

    @staticmethod
    def remove_from_cart_metro(main, instance):
        """
        Удалить товар из корзины METRO SHOP.

        :param main: Класс интерфейса главного окна.
        :param instance: Товар, который необходимо удалить.
        """
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=Cart.remove_from_cart_metro)
        instance.bind(on_release=Cart.add_to_cart_metro)
        item = instance.id
        item = str_to_dict2(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in get_cart():  # Если объект есть в корзине
            asyncio.ensure_future(remove_from_cart(item, parse_metro))  # Удаление из корзины на сервере
            remove_cart(dict(item))  # То объект удаляется из корзины

        if main.dialog:  # Закрыть диалоговое окно, если оно открыто
            main.dialog.dismiss()
            main.dialog_cart_open(main)
