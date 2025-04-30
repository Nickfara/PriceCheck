"""
    Инициализация классов интерфейса приложения из toolsajob.kv.
"""
import asyncio

from kivy.app import App

import PriceCheck.commands

MainApp = App.get_running_app()

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.tooltip import MDTooltip

from check_files import check_and_create as cac

cac()  # Проверка на наличие необходимых json файлов

from PriceCheck import commands
import handler

cart = []


# !/usr/bin/env python # -* - coding: utf-8-* -

class SettingsMain(MDDialog):
    """
    Класс инициализации kv класса диалогового окна с настройками.
    """
    def __init__(self):
        super(SettingsMain, self).__init__()
        self.data = {'shops': []}

    def add_shop(self, temp_main):
        """

        :param temp_main:
        """
        commands.Settings.add_shop(temp_main)

    def save_settings(self, temp_main):
        """

        :param temp_main:
        """
        commands.Settings.save(self, temp_main)

    def exit_settings(self, temp_main):
        """

        :param temp_main:
        """
        commands.Settings.exit(temp_main)

    @staticmethod
    def refresh(main):
        PriceCheck.commands.Settings.refresh(main)


class SettingShop(MDBoxLayout):
    """
        Класс инициализации kv класса c строкой конфига магазина.
    """
    def one(self):
        """
            Пустая функция.
        """
        pass


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
    def one(self):
        """
            Пустая функция.
        """
        pass


class CartShop(MDBoxLayout):
    """
                Класс инициализации kv класса одного магазина.
                Вызывается многократно, исходя из количества магазинов.
    """
    def one(self):
        """
            Пустая функция.
        """
        pass


class CartItem(MDBoxLayout):
    """
                Класс инициализации kv класса с одним товаром, для одного магазина.
                Вызывается многократно, для одного товара для каждых магазинов.
    """
    def one(self):
        """
            Пустая функция.
        """
        pass


class Plain(MDTooltip):
    """
                Класс инициализации kv класса для всплывающих уведомлений.
    """
    def one(self):
        """
            Пустая функция.
        """
        pass


class Main(MDBoxLayout):
    """
                Класс инициализации kv класса главного окна.
    """
    def __init__(self):
        super(Main, self).__init__()
        self.base_price = []  # Кэш прайсов
        asyncio.ensure_future(handler.background_load(self))  # Загрузка кэша

        self.theme_cls.bgColor = '#f0faff'
        self.theme_cls.btnColor = '#002538'
        self.theme_cls.topColor = '#c9e5ff'

        self.checkbox_parser_metro = MDCheckbox(size_hint_x=.1)

        # Переменные диалоговых окон:
        self.dialog = False
        self.send_text = {}
        self.data = {}

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
    def settings_open(add=False):
        """
        Открыть диалоговое окно с настройками.
        :param add:
        """
        commands.Settings.open(add)

    def func_dialog_save_enter(self, key, *args, **kwargs):
        """
        todo Доделать функцию сохранения настроек по нажатию клавиши enter.
        :param key:
        """
        commands.Base.func_dialog_save_enter(self, key)

    def activate_enter_finder(self):
        """
            Активировация поиска товаров по нажатию клавиши enter.
        """
        commands.Base.activate_enter_finder(self)

    def on_focus_change(self, instance, text):
        """
        Что-то связаное с фокусом, насколько помню в тектовом поле. Хотя могу ошибаться.
        :param instance:
        :param text:
        """
        commands.Base.on_focus_change(self, instance, text)

    def notify(self, text):
        """
        Вроде как реализованные всплывающие уведомления. Но не помню, реализовал или нет.
        :param text:
        """
        commands.Base.notify(text)

    def refresh(self):
        """
            Обновить кэш с прайс-листами.
        """

        asyncio.ensure_future(handler.refresh(self))


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
        self.MainApp = Main()

        self.SettingsMainApp = SettingsMain

        self.CartMainApp = CartMain

        self.SettingShopApp = SettingShop

        self.ItemObjApp = ItemObj

        self.CartShopApp = CartShop

        self.CartItemsApp = CartItem

        # self.PlainApp = Plain()

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
