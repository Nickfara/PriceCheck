"""
    Инициализация классов интерфейса приложения из toolsajob.kv.
"""
import asyncio

from kivy.app import App

import PriceCheck.commands

import kivymd

print(kivymd.__version__)
MainApp = App.get_running_app()

from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.card import MDCard
from kivy.core.window import Window

from check_files import check_and_create as cac

cac()  # Проверка на наличие необходимых json файлов

from PriceCheck import commands
from functions import (background_load, refresh, find)

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


class ItemObj(MDBoxLayout):
    """
    Класс инициализации kv класса с одним товаром.
    Вызывается многократно, исходя из количества найденных товаров.
    todo реализовать выбор количества товара, по умолчанию должно стоять значение минимального количество для заказа
    """

    def one(self):
        """
            Пустая функция.
        """
        pass


class CartMain(MDDialog):
    """
                Класс инициализации kv класса диалогового окна с корзиной.
    """

    def confirm_checkout(self):
        """
            Пустая функция.
        """
        pass


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

    def update_name(self, new_name):
        """
        Обновить название товара.
        """
        self.item_name = new_name
        self.item_data['name'] = new_name
        if self.on_update:
            self.on_update(self.item_data)

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

    @staticmethod
    def build():
        """
        Реализация инициализации класса.
        :return:
        """
        return Main()

    def find(self):
        """
             Поиск среди продуктов
        """
        commands.Main.find(self, ItemObj)

    def add_to_cart(self, instance):
        """
        Добавление товара в корзину.
        :param instance:
        """
        commands.Cart.add_to_cart(self, instance)

    def add_to_cart_metro(self, instance):
        """
        Добавление товара в корзину.
        todo Реализовать при добавлении товара в корзину приложения, добавление так же, на сервере сайта.
        :param instance:
        """
        commands.Cart.add_to_cart_metro(self, instance)

    def remove_from_cart(self, instance):
        """
        Удаление товара из корзины.
        :param instance:
        """
        commands.Cart.remove_from_cart(self, instance)

    def remove_from_cart_metro(self, instance):
        """
        Удаление товара из корзины.
        todo Реализовать при удалении товара из корзины приложения, удаление так же, на сервере сайта.
        :param instance:
        """
        commands.Cart.remove_from_cart_metro(self, instance)

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


class ToolsAJob(MDApp):
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
        # todo self.theme_cls.themeStyle = "gray"
        # todo self.theme_cls.primaryPalette = "blue"
        # todo self.theme_cls.error_color = "red"

        print(self.theme_cls.backgroundColor)

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
    async_run = asyncio.ensure_future(asyncio.gather(ToolsAJob().async_run(async_lib='asyncio')))
    # Планируем остановку цикла, когда Kivy App закроется
    async_run.add_done_callback(lambda *args: loop.stop())

    # Запускаем цикл событий asyncio
    loop.run_forever()


if __name__ == "__main__":
    run_async()
