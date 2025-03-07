import asyncio

from kivy.app import App

MainApp = App.get_running_app()

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.tooltip import MDTooltip
import check_files
from PriceCheck import functions
import handler

cart = []


# !/usr/bin/env python # -* - coding: utf-8-* -

class SettingsMain(MDDialog):
    def __init__(self, **kwargs):
        super(SettingsMain, self).__init__()
        self.data = {'shops': []}

    def add_shop(self, temp_main): functions.Settings.add_shop(self, temp_main)

    def save_settings(self, temp_main): functions.Settings.save(self, temp_main)

    def exit_settings(self, temp_main): functions.Settings.exit(self, temp_main)


class SettingShop(MDBoxLayout):
    def one(self):
        pass


class ItemObj(MDBoxLayout):
    def one(self):
        pass


class CartMain(MDDialog):
    def one(self):
        pass


class CartShop(MDBoxLayout):
    def one(self):
        pass


class CartItem(MDBoxLayout):
    def one(self):
        pass


class Plain(MDTooltip):
    def one(self):
        pass


class Main(MDBoxLayout):
    def __init__(self, **kwargs):
        super(Main, self).__init__()
        self.base_price = []  # Кэш прайсов
        asyncio.ensure_future(handler.background_load(self))  # Прогрузка кэша

        self.theme_cls.bgColor = '#f0faff'
        self.theme_cls.btnColor = '#002538'
        self.theme_cls.topColor = '#c9e5ff'

        self.checkbox_parser_metro = MDCheckbox(size_hint_x=.1)

        # Переменные диалоговых окон:
        self.dialog = False
        self.send_text = {}
        self.data = {}

    def build(self):
        return Main()

    def find(self, instance): functions.Main.find(self, ItemObj)

    def add_to_cart(self, instance): functions.Cart.add_to_cart(self, instance)

    def add_to_cart_metro(self, instance): functions.Cart.add_to_cart_metro(self, instance)

    def remove_from_cart(self, instance): functions.Cart.remove_from_cart(self, instance)

    def remove_from_cart_metro(self, instance): functions.Cart.remove_from_cart_metro(self, instance)

    def cart_open(self, instance): functions.Cart.open()

    def cart_edit(self, instance): functions.Cart.edit(self, instance)

    def settings_open(self, instance=None, add=False): functions.Settings.open(add)

    def start_jobBot(self): functions.Main.start_jobBot(self)

    def start_t2Market(self): functions.Main.start_t2Market(self)

    def start_taxiParser(self): functions.Main.start_taxiParser(self)

    def func_dialog_save_enter(self, window, key, i, r, x): functions.Base.func_dialog_save_enter(self, key)

    def activate_enter_finder(self, instance): functions.Base.activate_enter_finder(self)

    def on_focus_change(self, instance, text): functions.Base.on_focus_change(self, instance, text)

    def notify(self, text): functions.Base.notify(self, text)

    def refresh(self): functions.Main.refresh(self)

    def plaiN(self, instance):
        print('СОБАКА')
        plain = Plain()
        plain.ids.plain.text = 'Куку'


class ToolsAJob(MDApp):
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
    check_files.check_and_create()  # Проверка на наличие необходимых json файлов

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
