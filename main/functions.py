
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText, MDSnackbarButtonContainer, MDSnackbarActionButton, \
    MDSnackbarActionButtonText, MDSnackbarCloseButton
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout as BoxLayout
from kivymd.uix.button import MDIconButton as IconButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField

from log import log
import asyncio
import json
import commands
import parse_metro


class Base:
    @staticmethod
    def func_dialog_save_enter(self, key):
        if len(self.ids.text_find.text) > 0:
            if key == 13:
                self.find(key)

    @staticmethod
    def activate_enter_finder(self):
        Window.bind(on_key_down=self.func_dialog_save_enter)

    @staticmethod
    def on_focus_change(self, instance, text):
        shop = str(instance.id)
        self.send_text[shop] = str(text)

    @staticmethod
    def notify(self, text):
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
    @staticmethod
    def find(Main, ItemObjs):
        name = Main.ids.text_find.text

        Main.ids.list_items_obj.clear_widgets()
        finder_items = commands.finder(name, Main.base_price)  # Поиск товара
        result_metro = []
        if Main.checkbox_parser_metro.active:
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

            ItemObj.ids.item_seller.text = item['seller']  # Здесь надо присвоить ячейкам с товарам значения и ниже в двух также
            ItemObj.ids.item_name.text = text.capitalize()
            ItemObj.ids.item_cost.text = cost

            def btnForItem(icon, on_release, icon_color, id=str(item)):
                ItemObj.ids.idItem.icon = icon
                ItemObj.ids.idItem.bind(on_release=on_release)
                #ItemObj.ids.item_object.bind(on_release=on_release)
                ItemObj.ids.idItem.icon_color = icon_color
                ItemObj.ids.idItem.id = id

            if item in commands.get_cart():
                if item['seller'] == 'METRO':
                    btnForItem('cart-remove', Main.remove_from_cart_metro, 'red')
                else:
                    btnForItem('cart-remove', Main.remove_from_cart, 'red')
            else:
                if item['seller'] == 'METRO':
                    btnForItem('cart-plus', Main.add_to_cart_metro, 'blue')
                else:
                    btnForItem('cart-plus', Main.add_to_cart, 'blue')

            Main.ids.list_items_obj.add_widget(ItemObj)

    def refresh(self):
        asyncio.ensure_future(commands.refresh(self))

    def start_jobBot(self):
        asyncio.ensure_future(commands.start_telegram(self))

    def start_t2Market(self):
        asyncio.ensure_future(commands.start_t2Market(self))

    def start_taxiParser(self):
        asyncio.ensure_future(commands.start_taxiParser(self))


class Settings:
    @staticmethod
    def open(Main, Settings, SettingsShop):
        if Main.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main.dialog.dismiss()

        def content():
            Main.data = {}
            Main.data['shops'] = []

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
                Main.data['shops'].append(temp)

            for shop in Main.data['shops']:
                SettingShop = SettingsShop()

                for obj in shop:
                    SettingShop.ids.shop.add_widget(shop[obj])

                Settings.ids.main.add_widget(SettingShop)


            Settings.ids.checkbox_parser_metro.active = data['metro_active']
            return Settings


        btn_dismiss = IconButton(icon='close', on_release=Main.exit_settings,
                                 icon_color='red',
                                 line_color='red', text_color='red')
        btn_save = IconButton(icon='check', on_release=Main.save_settings, icon_color='green',
                              line_color='green', text_color='green')

        Main.dialog = MDDialog(size_hint_y=None, size_hint_max_y=.9, size_hint_min_y=.1)
        add_shop = IconButton(icon='plus', on_release=Main.add_shop)
        Main.dialog.add_widget(MDDialogHeadlineText(text='Настройки'))
        Main.dialog.add_widget(MDDialogContentContainer(content()))

        Main.dialog.add_widget(MDDialogButtonContainer(add_shop, BoxLayout(), btn_dismiss, btn_save))

        Main.dialog.open()

    @staticmethod
    def add_shop(Main):
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

        Main.data['shops'].append(new_shop)

        for i in Main.scroll_global_layout.children:
            i.clear_widgets()
        Main.scroll_global_layout.clear_widgets()

        for shop in Main.data['shops']:
            layout_items = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=2,
                                     md_bg_color='white')

            for obj in shop:
                layout_items.add_widget(shop[obj])

            Main.scroll_global_layout.add_widget(layout_items)

    @staticmethod
    def save(Main):

        with open('data/config.json') as f:
            data = json.load(f)
        with open('data/config.json', 'w') as f:
            data["shops"] = []
            data['metro_active'] = Main.checkbox_parser_metro.active
            for shop in Main.data['shops']:
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
            Main.base_price = result_filtered
            log('Кэш прайса обновлён!', 1)

        if Main.dialog:
            Main.dialog.dismiss()

    @staticmethod
    def exit(Main):
        if Main.dialog:
            Main.dialog.dismiss()


class Cart:
    @staticmethod
    def open(Main, CartMain, CartShops, CartItems):
        # Открытие корзины
        if Main.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main.dialog.dismiss()

        def content():
            for shop in ['Матушка', 'Алма', 'METRO']:
                CartShop = CartShops()
                items_list = []

                cart_get = commands.get_cart()
                for item in cart_get:  # Наполнение корзины товарами из
                    CartItem = CartItems()
                    if shop.lower() == item['seller'].lower():
                        if item in cart_get:
                            CartItem.ids.buttonItem.icon = 'cart-remove'
                            CartItem.ids.buttonItem.icon_color = 'blue'
                            if item['seller'] == 'METRO':
                                pass
                                CartItem.ids.buttonItem.on_release = Main.remove_from_cart_metro
                            else:
                                pass
                                CartItem.ids.buttonItem.on_release = Main.remove_from_cart
                        else:
                            CartItem.ids.buttonItem.icon = 'cart-plus'
                            CartItem.ids.buttonItem.icon_color = 'blue'
                            if item['seller'] == 'METRO':
                                pass
                                CartItem.ids.buttonItem.on_release = Main.add_to_cart_metro
                            else:
                                CartItem.ids.buttonItem.on_release = Main.add_to_cart
                        CartItem.ids.buttonItem.id = str(item) + 'cart'
                                
                        
                        CartItem.ids.textItem = str(item['name'])
                        items_list.append(CartItem)

                if len(items_list) > 0:
                    CartShop.ids.CartName.text = str(shop) + ':'
                    
                    for i in items_list:
                        CartShop.ids.listItems.add_widget(i)

                    CartMain.ids.listShops.add_widget(CartShop)
            return Cart

        copy_cart = IconButton(icon='page-next', on_release=Main.edit, icon_color='green',
                               line_color='green', text_color='green')

        Main.dialog = MDDialog(size_hint_y=None, size_hint_max_y=.9, size_hint_min_y=.1)

        Main.dialog.add_widget(MDDialogHeadlineText(text='Корзина', halign='left'))
        Main.dialog.add_widget(MDDialogContentContainer(content()))
        Main.dialog.add_widget(MDDialogButtonContainer(BoxLayout(), copy_cart))

        Main.dialog.open()

    @staticmethod
    def edit(Main):
        # Открытие корзины
        if Main.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main.dialog.dismiss()

        def send_cart(instance):
            commands.start_taxiParser(Main)

        def content():
            dialog_main_layout = BoxLayout(spacing="12dp", size_hint_y=None, height="400dp", orientation='vertical')
            scroll_global = ScrollView(do_scroll_x=False, size_hint=(1, 1))
            scroll_global_layout = BoxLayout(orientation='vertical', spacing=0, padding=(0, 10, 0, 0),
                                             adaptive_height=True)
            for shop in ['Матушка', 'Алма', 'METRO']:
                scroll_layout_dialog = BoxLayout(orientation='vertical', spacing=0, padding=(0, 10, 0, 0),
                                                 adaptive_height=True)
                items_main_layout = BoxLayout(spacing="12dp", size_hint_y=None, height="150dp", orientation='vertical')
                scroll_layout_dialog.size_hint_y = None
                scroll_layout_dialog.bind(minimum_height=Main.layout_scroll.setter('height'))
                scroll = ScrollView(do_scroll_x=False, size_hint=(1, 1))
                text_cart = ''
                number = 1
                for item in commands.get_cart():  # Наполнение корзины товарами из массива
                    if shop.lower() == item['seller'].lower():
                        text_cart += str(number) + '. ' + str(item['name'] + ' - \n')
                        number += 1

                if len(text_cart) > 0:
                    shop_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='40dp')
                    shop_layout.add_widget(MDLabel(text=str(shop) + ':'))
                    scroll_global_layout.add_widget(shop_layout)
                    items_cart = MDTextField(multiline=True, id=str(shop), )
                    items_cart.bind(text=Main.on_focus_change)
                    items_cart.text = text_cart
                    scroll_layout_dialog.add_widget(items_cart)
                    scroll.add_widget(scroll_layout_dialog)
                    items_main_layout.add_widget(scroll)
                    scroll_global_layout.add_widget(items_main_layout)

            scroll_global.add_widget(scroll_global_layout)
            dialog_main_layout.add_widget(scroll_global)
            return dialog_main_layout

        copy_cart_dismiss = IconButton(icon='backburger', on_release=Main.dialog_cart_open, icon_color='red',
                                       line_color='red', text_color='red')
        send_cart = IconButton(icon='content-copy', on_release=send_cart, icon_color='green',
                               line_color='green', text_color='green')

        Main.dialog = MDDialog(size_hint_y=None, size_hint_max_y=.9, size_hint_min_y=.1)
        Main.dialog.theme_bg_color = 'Custom'
        Main.dialog.md_bg_color = Main.color_bg
        Main.dialog.add_widget(MDDialogHeadlineText(text='Отправить', halign='left'))
        Main.dialog.add_widget(MDDialogContentContainer(content()))
        Main.dialog.add_widget(MDDialogButtonContainer(BoxLayout(), copy_cart_dismiss, send_cart))

        Main.dialog.open()

    @staticmethod
    def send(Main):
        asyncio.ensure_future(commands.start_telegram(Main))
        if Main.dialog:
            Main.dialog.dismiss()

    @staticmethod
    def back(self):
        pass

    @staticmethod
    def add_to_cart(Main, instance):
        print(instance)
        print('Разделитель')
        print(instance.icon)
        print(instance.icon_color)
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=Main.add_to_cart)
        instance.bind(on_release=Main.remove_from_cart)
        item = instance.id
        item = commands.str_to_dict(item)  # Конвертация строки в словарь

        if item not in commands.get_cart():  # Если обьекта нет в корзине
            commands.add_cart(dict(item))  # Отправка в корзину на сервер


    @staticmethod
    def remove_from_cart(Main, instance):
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=Main.remove_from_cart)
        instance.bind(on_release=Main.add_to_cart)
        item = instance.id
        item = commands.str_to_dict(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in commands.get_cart():  # Если обьект есть в корзине
            commands.remove_cart(dict(item))  # То обьект удаляется из корзины

        if Main.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main.dialog.dismiss()
            Main.dialog_cart_open(Main)

    @staticmethod
    def add_to_cart_metro(Main, instance):
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=Main.add_to_cart_metro)
        instance.bind(on_release=Main.remove_from_cart_metro)
        item = instance.id
        item = commands.str_to_dict1(item)  # Конвертация строки в словарь

        if item not in commands.get_cart():  # Если обьекта нет в корзине
            asyncio.ensure_future(commands.send_to_cart(item, parse_metro))  # Отправка в корзину на сервер
            commands.add_cart(dict(item))  # То обьект добавляется в корзину

    @staticmethod
    def remove_from_cart_metro(Main, instance):
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=Main.remove_from_cart_metro)
        instance.bind(on_release=Main.add_to_cart_metro)
        item = instance.id
        item = commands.str_to_dict(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in commands.get_cart():  # Если обьект есть в корзине
            asyncio.ensure_future(commands.remove_from_cart(item, parse_metro))  # Удаление из корзины на сервере
            commands.remove_cart(dict(item))  # То обьект удаляется из корзины

        if Main.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main.dialog.dismiss()
            Main.dialog_cart_open(Main)

