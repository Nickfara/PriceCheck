import asyncio

from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout as BoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import MDListItem, MDListItemSupportingText, MDListItemHeadlineText, MDListItemTertiaryText
from kivymd.uix.screen import Screen
from kivymd.uix.scrollview import MDScrollView as ScrollView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText, MDSnackbarButtonContainer, MDSnackbarActionButton, \
    MDSnackbarActionButtonText, MDSnackbarCloseButton

import functions
import commands
from log import log

import parse_metro
from dialog_settings import dialog_settings
from dialog_cart import Carts

cart = []


# !/usr/bin/env python # -* - coding: utf-8-* -

class Settings(BoxLayout):
    def one(self):
        pass


class SettingShop(BoxLayout):
    def one(self):
        pass


class ItemObj(BoxLayout):
    def one(self):
        pass


class CartMain(BoxLayout):
    def one(self):
        pass

class CartShop(BoxLayout):
    def one(self):
        pass

class CartItem(BoxLayout):
    def one(self):
        pass


class Main(BoxLayout, Carts):
    def __init__(self, **kwargs):
        super(Main, self).__init__()
        self.base_price = [] # Кэш прайсов
        asyncio.ensure_future(commands.background_load(self))  # Прогрузка кэша
        self.layout_scroll = None
        self.color_bg = '#f0faff'
        self.color_button = '#002538'
        self.theme_cls.btnColor = '#002538'
        self.color_top = '#c9e5ff'

        self.checkbox_parser_metro = MDCheckbox(size_hint_x=.1)

        # Переменные диалоговых окон:
        self.dialog = False
        self.send_text = {}

        asyncio.ensure_future(commands.background_load(self))

    def build(self):

        return Main()
    def find(self, instance):functions.Main.find(self, ItemObj)
    def add_to_cart(self, instance):functions.Cart.add_to_cart(self, instance)
    def add_to_cart_metro(self, instance):functions.Cart.add_to_cart_metro(self, instance)
    def remove_from_cart(self, instance):functions.Cart.remove_from_cart(self, instance)
    def remove_from_cart_metro(self, instance):functions.Cart.remove_from_cart_metro(self, instance)
    def cart_open(self, instance):functions.Cart.open(self, CartMain(), CartShop, CartItem)
    def dialog_editCart_open(self, instance):functions.Cart.edit(self)
    def settings_open(self, instance):functions.Settings.open(self, Settings(), SettingShop)
    def add_shop(self, instance):functions.Settings.add_shop(self)
    def save_settings(self, instance):functions.Settings.save(self)
    def exit_settings(self, instance):functions.Settings.exit(self)
    def start_jobBot(self, instance):functions.Main.start_jobBot(self)
    def start_t2Market(self, instance):functions.Main.start_t2Market(self)
    def start_taxiParser(self, instance):functions.Main.start_taxiParser(self)
    def func_dialog_save_enter(self, window, key, i, r, x):functions.Base.func_dialog_save_enter(self, key)
    def activate_enter_finder(self, instance):functions.Base.activate_enter_finder(self)
    def on_focus_change(self, instance, text):functions.Base.on_focus_change(self, instance, text)
    def notify(self, text):functions.Base.notify(self, text)
    def refresh(self, instance):functions.Main.refresh(self)


class ToolsAJob(MDApp):
    def build(self):
        return Main()



def run_async():
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
