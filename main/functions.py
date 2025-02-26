
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
from kivy.uix.textinput import TextInput

from log import log
import asyncio
import json
import handler
import parse_metro

from kivy.app import App
ToolsAJob = App.get_running_app


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
        finder_items = handler.finder(name, Main.base_price)  # Поиск товара
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

            if item in handler.get_cart():
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
        asyncio.ensure_future(handler.refresh(self))

    def start_jobBot(self):
        asyncio.ensure_future(handler.start_telegram(self))

    def start_t2Market(self):
        asyncio.ensure_future(handler.start_t2Market(self))

    def start_taxiParser(self):
        asyncio.ensure_future(handler.start_taxiParser(self))


class Settings:
    @staticmethod
    def preset_shop(shop):
        temp = {}
        temp['filename'] = TextInput(text=str(shop['filename']), size_hint_y=None, height="30dp")
        temp['sid_w'] = TextInput(text=str(shop['sid'][0]), size_hint_x=None, width="22dp", size_hint_y=None,
                                  height="30dp")
        temp['sid_h'] = TextInput(text=str(shop['sid'][1]), size_hint_x=None, width="22dp", size_hint_y=None,
                                  height="30dp")
        temp['sid_t'] = TextInput(text=str(shop['sid'][2]), size_hint_x=None, width="22dp", size_hint_y=None,
                                  height="30dp")
        temp['seller'] = TextInput(text=shop['seller'], size_hint_y=None, height="30dp")
        temp['findname_w'] = TextInput(text=str(shop['findname'][0]), size_hint_x=None, width="22dp", size_hint_y=None,
                                       height="30dp")
        temp['findname_h'] = TextInput(text=str(shop['findname'][1]), size_hint_x=None, width="22dp", size_hint_y=None,
                                       height="30dp")
        temp['findtext'] = TextInput(text=shop['findtext'], size_hint_y=None, height="30dp")
        temp['active'] = MDCheckbox(active=shop['active'], size_hint_x=None, width="25dp")
        return temp
    @staticmethod
    def open(add):
        Main = ToolsAJob().MainApp
        if Main.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main.dialog.clear_widgets()
            Main.dialog.dismiss()

        SettingsMain = ToolsAJob().SettingsMainApp()

        def content():
            SettingsMain.data['shops'] = []

            with open('data/config.json') as f:
                data = json.load(f)

            if add:
                new_shop = {"filename": "Введите имя файла", "sid": [0, 0, 0], "seller": "Введите название поставщика",
                            "findname": [0, 0], "findtext": "Введите слово для поиска", "active": False}
                data["shops"].append(new_shop)

            for shop in data["shops"]:
                print(shop)
                preset_shop = Settings.preset_shop(shop)
                SettingsMain.data['shops'].append(preset_shop)


            for shop in SettingsMain.data['shops']:
                SettingShop = ToolsAJob().SettingShopApp()

                for obj in shop:
                    SettingShop.ids.shop.add_widget(shop[obj])

                SettingsMain.ids.main.add_widget(SettingShop)

            SettingsMain.ids.checkbox_parser_metro.active = data['metro_active']
            return SettingsMain

        Main.dialog = content()

        Main.dialog.open()

    @staticmethod
    def add_shop(self, Main):
        Main.settings_open(None, add=True)

    @staticmethod
    def save(self, Main):

        with open('data/config.json') as f:
            data = json.load(f)
        with open('data/config.json', 'w') as f:
            data["shops"] = []
            data['metro_active'] = Main.checkbox_parser_metro.active

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
            result_filtered = handler.filter_shops(result)
            Main.base_price = result_filtered
            log('Кэш прайса обновлён!', 1)

        if Main.dialog:
            Main.dialog.dismiss()

    @staticmethod
    def exit(self, Main):
        if Main.dialog:
            Main.dialog.dismiss()


class Cart:
    @staticmethod
    def open():
        Main = ToolsAJob().MainApp
        # Открытие корзины

        if Main.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main.dialog.dismiss()

        def content():
            app = ToolsAJob()
            CartMainApp = app.CartMainApp()
            for shop in ['Матушка', 'Алма', 'METRO']:
                CartShop = app.CartShopApp()
                items_list = []

                cart_get = handler.get_cart()
                for item in cart_get:  # Наполнение списка товарами из кэша
                    CartItem = app.CartItemsApp()
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
                                
                        
                        CartItem.ids.textItem.text = str(item['name'])
                        items_list.append(CartItem)

                if len(items_list) > 0: # Наполнение корзины товарами
                    CartShop.ids.CartName.text = str(shop) + ':'

                    for i in items_list:
                        CartShop.ids.listItems.add_widget(i)


                CartMainApp.ids.listShops.add_widget(CartShop)
            return CartMainApp

        Main.dialog = content()
        Main.dialog.open()

    @staticmethod
    def edit(Main, instance):
        print(instance)

    @staticmethod
    def send(Main):
        asyncio.ensure_future(handler.start_telegram(Main))
        if Main.dialog:
            Main.dialog.dismiss()

    @staticmethod
    def back(self):
        pass

    @staticmethod
    def add_to_cart(Main, instance):
        #Main = MainApp().Main
        print(instance)
        print('Разделитель')
        print(instance.icon)
        print(instance.icon_color)
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=Main.add_to_cart)
        instance.bind(on_release=Main.remove_from_cart)
        item = instance.id
        item = handler.str_to_dict(item)  # Конвертация строки в словарь

        if item not in handler.get_cart():  # Если обьекта нет в корзине
            handler.add_cart(dict(item))  # Отправка в корзину на сервер


    @staticmethod
    def remove_from_cart(Main, instance):
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=Main.remove_from_cart)
        instance.bind(on_release=Main.add_to_cart)
        item = instance.id
        item = handler.str_to_dict(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in handler.get_cart():  # Если обьект есть в корзине
            handler.remove_cart(dict(item))  # То обьект удаляется из корзины

        if Main.dialog:  # Закрыть диалоговое окно, если оно открыто
            print(Main.dialog)
            #Main.dialog.dismiss()
            #Main.dialog = None
            #Main.cart_open(Main)

    @staticmethod
    def add_to_cart_metro(Main, instance):
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=Main.add_to_cart_metro)
        instance.bind(on_release=Main.remove_from_cart_metro)
        item = instance.id
        item = handler.str_to_dict1(item)  # Конвертация строки в словарь

        if item not in handler.get_cart():  # Если обьекта нет в корзине
            asyncio.ensure_future(handler.send_to_cart(item, parse_metro))  # Отправка в корзину на сервер
            handler.add_cart(dict(item))  # То обьект добавляется в корзину

    @staticmethod
    def remove_from_cart_metro(Main, instance):
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=Main.remove_from_cart_metro)
        instance.bind(on_release=Main.add_to_cart_metro)
        item = instance.id
        item = handler.str_to_dict(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in handler.get_cart():  # Если обьект есть в корзине
            asyncio.ensure_future(handler.remove_from_cart(item, parse_metro))  # Удаление из корзины на сервере
            handler.remove_cart(dict(item))  # То обьект удаляется из корзины

        if Main.dialog:  # Закрыть диалоговое окно, если оно открыто
            Main.dialog.dismiss()
            Main.dialog_cart_open(Main)

