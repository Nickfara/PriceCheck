import asyncio

from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout as BoxLayout
from kivymd.uix.button import MDIconButton as IconButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

import functions
import commands
from log import log


# !/usr/bin/env python # -* - coding: utf-8-* -
class Carts():
    def __init__(self):
        super().__init__()

    def open_(self):
        functions.Cart.edit(self)

    def edit(self, instance):  # Открытие корзины
        functions.Cart.edit(self)

    def send(self, instance):
        functions.Cart.edit(self)

