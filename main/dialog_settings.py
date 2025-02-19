import json

from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout as BoxLayout
from kivymd.uix.button import MDIconButton as IconButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField

import commands
from log import log




# !/usr/bin/env python # -* - coding: utf-8-* -
class dialog_settings():
    def __init__(self):
        super().__init__()
        self.dialog_settings_open()

    def dialog_settings_open(self, Settings, SettingShop):
        if self.dialog:  # Закрыть диалоговое окно, если оно открыто
            self.dialog.dismiss()

        def content():
            dialog_main_layout = BoxLayout(spacing="12dp", size_hint_y=None, height="400dp", orientation='vertical')
            scroll_global = ScrollView(do_scroll_x=False, size_hint=(1, 1))
            self.scroll_global_layout = BoxLayout(orientation='vertical', spacing=20, padding=(0, 10, 0, 0),
                                                  adaptive_height=True)

            self.data = {}
            self.data['shops'] = []

            with open('data/config.json') as f:
                data = json.load(f)

            for shop in data["shops"]:
                temp = {}
                temp['filename'] = MDTextField(text=str(shop['filename']))
                temp['sid_w'] = MDTextField(text=str(shop['sid'][0]), size_hint_x=None, width="42dp")
                temp['sid_h'] = MDTextField(text=str(shop['sid'][1]), size_hint_x=None, width="42dp")
                temp['sid_t'] = MDTextField(text=str(shop['sid'][2]), size_hint_x=None, width="42dp")
                temp['seller'] = MDTextField(text=shop['seller'])
                temp['findname_w'] = MDTextField(text=str(shop['findname'][0]), size_hint_x=None, width="42dp")
                temp['findname_h'] = MDTextField(text=str(shop['findname'][1]), size_hint_x=None, width="42dp")
                temp['findtext'] = MDTextField(text=shop['findtext'])
                temp['active'] = MDCheckbox(active=shop['active'], size_hint_x=None, width="25dp")
                self.data['shops'].append(temp)

            for shop in self.data['shops']:
                layout_items = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=2,
                                         md_bg_color='white')
                for obj in shop:
                    layout_items.add_widget(shop[obj])
                self.scroll_global_layout.add_widget(layout_items)

            text_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=20)
            for i in ('Имя файла', 'Название', 'Цена', 'Тип', 'Поставщик', 'Горизонталь', 'Вертикаль', 'Поиск'):
                text_layout.add_widget(MDLabel(text=i))

            Settings.ids.checkbox_parser_metro.active = data['metro_active']
            metro_layout = BoxLayout(MDLabel(text='METRO: '), self.checkbox_parser_metro, size_hint_y=None,
                                     height=self.checkbox_parser_metro.height)
            dialog_main_layout.add_widget(metro_layout)
            scroll_global.add_widget(self.scroll_global_layout)
            dialog_main_layout.add_widget(text_layout)
            dialog_main_layout.add_widget(scroll_global)
            return dialog_main_layout

        btn_dismiss = IconButton(icon='close', on_release=self.exit_settings,
                                 icon_color='red',
                                 line_color='red', text_color='red')
        btn_save = IconButton(icon='check', on_release=self.save_settings, icon_color='green',
                              line_color='green', text_color='green')

        self.dialog = MDDialog(size_hint_min_x='800dp', size_hint_max_y=.9, size_hint_min_y=.1)
        add_shop = IconButton(icon='plus', on_release=self.add_shop)
        self.dialog.add_widget(MDDialogHeadlineText(text='Настройки'))
        self.dialog.add_widget(MDDialogContentContainer(content()))

        self.dialog.add_widget(MDDialogButtonContainer(add_shop, BoxLayout(), btn_dismiss, btn_save))

        self.dialog.open()

    def add_shop(self):
        new_shop = {}
        new_shop['filename'] = MDTextField()
        new_shop['sid_w'] = MDTextField()
        new_shop['sid_h'] = MDTextField()
        new_shop['sid_t'] = MDTextField()
        new_shop['seller'] = MDTextField()
        new_shop['findname_w'] = MDTextField()
        new_shop['findname_h'] = MDTextField()
        new_shop['findtext'] = MDTextField()
        new_shop['active'] = MDCheckbox()

        self.data['shops'].append(new_shop)

        for i in self.scroll_global_layout.children:
            i.clear_widgets()
        self.scroll_global_layout.clear_widgets()

        for shop in self.data['shops']:
            layout_items = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=2,
                                     md_bg_color='white')

            for obj in shop:
                layout_items.add_widget(shop[obj])

            self.scroll_global_layout.add_widget(layout_items)

    def save_settings(self):
        with open('data/config.json') as f:
            data = json.load(f)
        with open('data/config.json', 'w') as f:
            data["shops"] = []
            data['metro_active'] = self.checkbox_parser_metro.active
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
            json.dump(data, f)

        with open('data/cache_prices.json') as f:
            result = json.load(f)
            result_filtered = commands.filter_shops(result)
            self.base_price = result_filtered
            log('Кэш прайса обновлён!', 1)

        if self.dialog:
            self.dialog.dismiss()

    def exit_settings(self):
        if self.dialog:
            self.dialog.dismiss()
