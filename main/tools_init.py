"""
    Инициализация классов интерфейса приложения из tools.kv.
"""
import json
import os

from kivymd.uix.button import MDIconButton

os.environ["KCFG_KIVY_LOG_LEVEL"] = "warning"  # уровни: 'trace', 'debug', 'info', 'warning', 'error', 'critical'

import asyncio

from kivy.app import App

MainApp = App.get_running_app()

from kivy.properties import StringProperty, BooleanProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.card import MDCard
from kivy.core.window import Window

from files_check import check_and_create as cac

cac()  # Проверка на наличие необходимых json файлов

from PriceCheck import commands
from general_func import (background_load, refresh, find)

cart = []


# !/usr/bin/env python # -* - coding: utf-8-* -

class SettingsMain(MDDialog):
    """
    Класс инициализации kv класса диалогового окна с настройками.
    """

    def __init__(self):
        super(SettingsMain, self).__init__()
        self.data = {'shops': []}

    def add_shop(self, setting_shop_app):
        """
        :param setting_shop_app:
        """

        self.ids.main.add_widget(setting_shop_app())

    def save_settings(self, main_app):
        """

        :param main_app: Экземпляр интерфейса главного меню.
        """
        commands.Settings.save(self, main_app)

    def exit_settings(self, main_app):
        """

        :param main_app: Экземпляр интерфейса главного меню.
        """
        commands.Settings.exit(main_app)

    def refresh(self):
        """
        Обновить кэш с прайс-листами.
        """

        asyncio.ensure_future(refresh(self))


class SettingShop(MDCard):
    """
    Класс инициализации kv класса c строкой конфига магазина.
    """

    filename = StringProperty("")
    title = StringProperty("")
    dist_h = StringProperty("")
    dist_w = StringProperty("")
    dist_text = StringProperty("")
    price_w = StringProperty("")
    product_name_w = StringProperty("")
    packaging_w = StringProperty("")
    status = BooleanProperty()

    def remove_self(self):
        """
        Удаление виджета с карточкой магазина.
        """
        if self.parent:
            self.parent.remove_widget(self)


class ItemObj(MDCard):
    """
    Класс инициализации kv класса с одним товаром.
    Вызывается многократно, исходя из количества найденных товаров.
    todo реализовать выбор количества товара, по умолчанию должно стоять значение минимального количество для заказа
    """

    def add_to_cart(self, instance):
        """
        Добавление товара в корзину.
        """
        commands.Cart.add_to_cart(self)

    def remove_from_cart(self, instance):
        """
        Удаление товара из корзины.
        """
        commands.Cart.remove_from_cart(self)

    def add_to_cart_metro(self, instance):
        """
        Добавление товара в корзину.
        todo Реализовать при добавлении товара в корзину приложения, добавление так же, на сервере сайта.
        """
        commands.Cart.add_to_cart_metro(self)

    def remove_from_cart_metro(self, instance):
        """
        Удаление товара из корзины.
        todo Реализовать при удалении товара из корзины приложения, удаление так же, на сервере сайта.
        """
        commands.Cart.remove_from_cart_metro(self)


class CartMain(MDDialog):
    """
                Класс инициализации kv класса диалогового окна с корзиной.
    """

    def confirm_checkout(self):
        """
            Пустая функция.
        """
        pass

    def send_orders(self, instance):
        commands.Cart.send(self.parent)

    def cart_main_app(self, instance):
        commands.Cart.remove_from_cart(instance)


class CartShop(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_items = []

    def add_product_card(self, item_data):
        """
        Добавить товар в корзину.
        :param item_data:
        """
        card = CartItem(
            item_data=item_data,
            on_update=self.update_item_data,
            on_remove=self.remove_item_card
        )
        self.ids.listItems.add_widget(card)
        self.cart_items.append(card)

    def update_item_data(self, updated_data):
        """
        Обновить название товара. todo
        """
        # Тут можно обновлять JSON-файл, словарь или отправить на сервер
        print("Обновлено:", updated_data)

    def remove_item_card(self, item_widget):
        """
        Удалить товар из корзины.
        :param item_widget: Объект удаления.
        """
        self.ids.listItems.remove_widget(item_widget)
        self.cart_items.remove(item_widget)


class CartItem(MDBoxLayout):
    def __init__(self, item_data, on_update=None, on_remove=None, **kwargs):
        super().__init__(**kwargs)
        self.item_name = item_data.get('name', '')
        self.item_quantity = item_data.get('quantity', 1)
        self.item_data = item_data
        self.on_update = on_update
        self.on_remove = on_remove
        self.tempname = None

    def update_name(self, name):
        """
        Активировать возможность редактирования названия товара.
        """
        name.readonly = False
        name.mode = "outlined"
        self.tempname = name.text

    def accept_name(self, name):
        """
        Принять изменённое название товара.
        """

        if not name.focus:
            if name.mode == "outlined":
                name.readonly = True
                name.mode = "filled"
                with open('data/cache_cart.json') as f:
                    cache_cart = json.load(f)
                    for item in cache_cart['cart']:
                        if item['product_name'] == self.tempname:
                            item['product_name_visible'] = name.text

    def update_quantity(self, new_qty):
        """
        Обновить количество товара.
        """
        try:
            self.item_quantity = int(new_qty)
            self.item_data['quantity'] = int(new_qty)
            if self.on_update:
                self.on_update(self.item_data)
        except ValueError:
            pass

    def remove_self(self):
        """
        Удалить товар из корзины.
        """
        if self.parent:
            self.parent.remove_widget(self)

    def add_product_card(self, item):
        """
        TODO Реализовать возвращение товара в корзину в течении 5 секунд после удаления.
        """
        pass


class Plain(MDTooltip):
    """
    Инициализация класса всплывающего уведомления.
    """

    def one(self):
        """
            Пустая функция.
        """
        pass


class Main(MDBoxLayout):
    """
    Инициализация класса главного окна.
    """

    def __init__(self):
        super(Main, self).__init__()
        self.base_price = []  # Кэш прайсов
        asyncio.ensure_future(background_load(self))  # Загрузка кэша

        self.theme_cls.bgColor = '#f0faff'
        self.theme_cls.btnColor = '#002538'
        self.theme_cls.topColor = '#c9e5ff'

        self.checkbox_parser_metro = MDCheckbox(size_hint_x=.1)

        # Переменные диалоговых окон:
        self.dialog = False
        self.send_text = {}
        self.data = {}
        Window.bind(on_key_down=self.on_enter_find)

        child = self.ids.asdasd.width
        print(self.ids.asdasd.children)
        print(child)


    @staticmethod
    def build():
        """
        Реализация инициализации класса.
        todo реализовать добавление товара в избранное из карточки товара на главном экране.
        :return:
        """
        return Main()

    def find(self):
        """
             Поиск среди продуктов
        """
        commands.Main.find(self, ItemObj)

    @staticmethod
    def cart_open():
        """
            Открыть диалоговое окно с корзиной.
        """
        commands.Cart.open()

    def cart_edit(self, instance):
        """
        todo Реализовать возможность редактирования названий товаров и редактирования количества.
        :param instance:
        """
        commands.Cart.edit(self, instance)

    @staticmethod
    def settings_open():
        """
        Открыть диалоговое окно с настройками.
        """
        commands.Settings.open()

    def on_enter_find(self, window, key, *args, **kwargs):
        """
        Сохранение по нажатию клавиши enter.

        :param key: Объект нажатой кнопки.
        """

        if len(self.ids.text_find.text) > 0 and key == 13:
            self.find()

    def on_focus_change(self, instance, text):
        """
        При фокусировании на текстовом поле.

        :param instance: Объект фокусировки.
        :param text: Текст с объекта фокусировки.
        """
        commands.Base.on_focus_change(self, instance, text)

    @staticmethod
    def notify(text):
        """
        Вроде как реализованные всплывающие уведомления. Но не помню, реализовал или нет.
        :param text:
        """
        commands.Base.notify(text)

    @staticmethod
    def graph():
        from ParserTaxi.graph import render
        render()


class Tools(MDApp):
    """
    Класс запуска самого приложения и подрузка всех классов интерфейса.
    todo Оптимизировать логику работы.
    """

    def __init__(self):
        super().__init__()
        self.CartItemsApp = None
        self.CartShopApp = None
        self.ItemObjApp = None
        self.SettingShopApp = None
        self.CartMainApp = None
        self.SettingsMainApp = None
        self.MainApp = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.rippleColor = "green"  # Цвет анимации нажатия кнопки
        # self.theme_cls.transparentColor = "pink" # цвет фона виджетов
        self.theme_cls.backgroundColor = "#232633"
        self.theme_cls.topBgColor = "#1e2129"
        self.theme_cls.secondaryColor = "#8c93a3"
        self.theme_cls.accentColor = "#77ed8c"
        self.theme_cls.accentTextColor = "#062926"
        self.theme_cls.buttonColor = "#8c93a3"
        self.theme_cls.textColor = "white"
        self.theme_cls.primaryColor

        self.MainApp = Main()

        self.SettingsMainApp = SettingsMain()

        self.SettingShopApp = SettingShop

        self.CartMainApp = CartMain()

        self.CartShopApp = CartShop

        self.CartItemsApp = CartItem

        self.ItemObjApp = ItemObj

        return self.MainApp


def run_async():
    """
        Запуск приложения с интеграцией возможности асинхронных действий.
    """

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Запускаем цикл событий Kivy
    async_run = asyncio.ensure_future(asyncio.gather(Tools().async_run(async_lib='asyncio')))
    # Планируем остановку цикла, когда Kivy App закроется
    async_run.add_done_callback(lambda *args: loop.stop())

    # Запускаем цикл событий asyncio
    loop.run_forever()


if __name__ == "__main__":
    run_async()
