"""
    Инициализация интерфейса приложения.
"""
import asyncio

from kivy.app import App

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
    def __init__(self):
        super(SettingsMain, self).__init__()
        self.data = {'shops': []}

    def add_shop(self, temp_main):
        """

        :param temp_main:
        """
        commands.Settings.add_shop(self, temp_main)

    def save_settings(self, temp_main):
        """

        :param temp_main:
        """
        commands.Settings.save(self, temp_main)

    def exit_settings(self, temp_main):
        """

        :param temp_main:
        """
        commands.Settings.exit(self, temp_main)


class SettingShop(MDBoxLayout):
    def one(self):
        """
            Пустая функция.
        """
        pass


class ItemObj(MDBoxLayout):
    def one(self):
        """
            Пустая функция.
        """
        pass


class CartMain(MDDialog):
    def one(self):
        """
            Пустая функция.
        """
        pass


class CartShop(MDBoxLayout):
    def one(self):
        """
            Пустая функция.
        """
        pass


class CartItem(MDBoxLayout):
    def one(self):
        """
            Пустая функция.
        """
        pass


class Plain(MDTooltip):
    def one(self):
        """
            Пустая функция.
        """
        pass


class Main(MDBoxLayout):
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

        :param instance:
        """
        commands.Cart.add_to_cart(self, instance)

    def add_to_cart_metro(self, instance):
        """

        :param instance:
        """
        commands.Cart.add_to_cart_metro(self, instance)

    def remove_from_cart(self, instance):
        """

        :param instance:
        """
        commands.Cart.remove_from_cart(self, instance)

    def remove_from_cart_metro(self, instance):
        """

        :param instance:
        """
        commands.Cart.remove_from_cart_metro(self, instance)

    @staticmethod
    def cart_open():
        """
            Открыть корзину
        """
        commands.Cart.open()

    def cart_edit(self, instance):
        """

        :param instance:
        """
        commands.Cart.edit(self, instance)

    @staticmethod
    def settings_open(add=False):
        """


        :param add:
        """
        commands.Settings.open(add)

    def func_dialog_save_enter(self, key):
        """

        :param key:
        """
        commands.Base.func_dialog_save_enter(self, key)

    def activate_enter_finder(self):
        """
            Активировать поиск по enter
        """
        commands.Base.activate_enter_finder(self)

    def on_focus_change(self, instance, text):
        """

        :param instance:
        :param text:
        """
        commands.Base.on_focus_change(self, instance, text)

    def notify(self, text):
        """

        :param text:
        """
        commands.Base.notify(self, text)

    def refresh(self):
        """
            Обновить базу данных
        """
        commands.Main.refresh(self)


class ToolsAJob(MDApp):
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
        Асинхронный запуск приложения
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
