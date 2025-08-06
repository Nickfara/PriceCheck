"""
    Команды для парсинга цен
"""

import asyncio
import json

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import (MDSnackbar,
                                 MDSnackbarSupportingText,
                                 MDSnackbarButtonContainer,
                                 MDSnackbarActionButton,
                                 MDSnackbarActionButtonText,
                                 MDSnackbarCloseButton)

from general_func import (finder,
                          add_cart,
                          get_cart,
                          send_cart,
                          send_to_cart,
                          filter_shops,
                          remove_cart,
                          remove_from_cart,
                          str_to_dict)
from log import log
from PriceCheck import parse_metro

ToolsAJob = App.get_running_app


class Base:
    """
    Класс с нейтральными методами.
    """

    @staticmethod
    def on_focus_change(main_app, instance, text):
        """
        Фокусирование на текстовом поле.
        
        :param main_app: Экземпляр интерфейса главного окна.
        :param instance: Объект фокусировки.
        :param text: Текст с объекта фокусировки.
        """
        shop = str(instance.id)
        main_app.send_text[shop] = str(text)

    # noinspection PyUnusedLocal
    @staticmethod
    def notify(text: str):
        """
        Уведомление.

        :param text: Текст
        """
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
    """
    Методы в главном окне приложения.
    """

    @staticmethod
    def find(main_app, item_obj_):
        """
        Поиск товаров и добавление их на главный экран.
        todo Добавить в обычный поиск количество товара по умолчанию.
        todo Добавить в карточку товара выбор количества товара.
        todo В метро добавить возможность минимального или кратного обязательного количества. Добавить это же и в корзину.

        :param main_app: Экземпляр интерфейса главного экрана.
        :param item_obj_: Класс интерфейса карточки товара.
        """

        name = main_app.ids.text_find.text  # текст из текстового поля для поиска

        main_app.ids.list_items_obj.clear_widgets()  # Очистка виджетов в списке товаров
        finder_items = finder(name, main_app.base_price)  # Поиск name в оперативке списка товаров из кэша

        result_metro = []  # Список с результатом поиска в metro cc
        with open('data/config.json') as f:
            data = json.load(f)
            if data['metro_active']:  # Если метро включено в настройках, запускает авторизацию
                result_metro = parse_metro.search(name)  # Поиск в metro cc

        if isinstance(result_metro, list):
            for id_item in result_metro:
                finder_items[id_item['bundleId']] = {'title': 'METRO',
                                             'product_name': id_item['name'],
                                             'price': str(id_item['price']),
                                             'bundleId': id_item['bundleId'],
                                             'minOrderQuantity': id_item['minOrderQuantity']
                                             }  # Наполнение основного списка найденных товаров, товарами из metro cc

        for id_item in finder_items:  # Добавление карточек товаров в список на главный экран
            item_obj = item_obj_()  # Генерация карточки товара.
            text = finder_items[id_item]['product_name'] + '.'
            cost_str = 'Цена: ' + finder_items[id_item]['price'] + '₽'

            if 'packaging' in finder_items[id_item]:
                if finder_items[id_item]['packaging'] != '':
                    cost = cost_str + ' за ' + finder_items[id_item]['packaging']
                else:
                    cost = cost_str
            else:
                cost = cost_str

            item_obj.ids.item_seller.text = finder_items[id_item['title']]  # Здесь надо присвоить ячейкам с товарами значения и ниже в двух также
            item_obj.ids.item_name.text = text.capitalize()
            item_obj.ids.item_cost.text = cost

            def btn_for_item(on_release, icon_color, oid=str(id_item)):
                """
                Генерация кнопки для карточки товара
                :param on_release: функция при нажатии
                :param icon_color: Цвет иконки
                :param oid: Объект (словарь в формате строки)
                """
                item_obj.bind(on_release=on_release)
                item_obj.shadow_color = icon_color
                item_obj.id = oid

            if id_item in get_cart():
                if id_item['title'] == 'METRO':
                    btn_for_item(item_obj.remove_from_cart_metro, 'green')
                else:
                    btn_for_item(item_obj.remove_from_cart, 'green')
            else:
                if id_item['title'] == 'METRO':
                    btn_for_item(item_obj.add_to_cart_metro, 'gray')
                else:
                    btn_for_item(item_obj.add_to_cart, 'gray')

            main_app.ids.list_items_obj.add_widget(item_obj)


class Settings:
    """
    todo Добавить настройки телеграм бота. Состояние включен или выключен. При сохранении включается или выключается.
    todo Добавить настройки (фильтр) поиска по metro. Количество найденных товаров итд.
    Функции в диалоговом окне настроек.
    """

    @staticmethod
    def open():
        """
        Вызов генерирования и открытия диалогового окна с настройками.
        """
        main_app = ToolsAJob().MainApp  # Ссылка на экземпляр главного меню.
        settings_main_app = ToolsAJob().SettingsMainApp  # Ссылка на экземпляр окна настроек
        settings_main_app.data['shops'] = []

        settings_main_app.ids.main.clear_widgets()

        if main_app.dialog:  # Закрытие диалогового окна, если открыто.
            if main_app.dialog._is_open:
                main_app.dialog.dismiss()

        with open('data/config.json', encoding='utf-8') as f:
            data = json.load(f)

        for shop in data["shops_params"]:
            settings_shop = ToolsAJob().SettingShopApp()  # Создание экземпляра строки магазина

            settings_shop.filename = shop["filename"]
            settings_shop.title = shop["title"]
            settings_shop.dist_h = str(shop["dist_h"])
            settings_shop.dist_w = str(shop["dist_w"])
            settings_shop.dist_text = shop["dist_text"]
            settings_shop.price_w = str(shop["price_w"])
            settings_shop.product_name_w = str(shop["product_name_w"])
            settings_shop.packaging_w = str(shop["packaging_w"])
            settings_shop.status = bool(shop["status"])

            settings_main_app.ids.main.add_widget(settings_shop)

        settings_main_app.ids.checkbox_parser_metro.active = data['metro_active']

        main_app.dialog = settings_main_app

        main_app.dialog.open()

    @staticmethod
    def save(settings_main_app, main_app):
        """
        Сохранение настроек.

        :param settings_main_app: Экземпляр интерфейса окна с настройками.
        :param main_app: Экземпляр интерфейса главного окна.
        """

        with open('data/config.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data["shops_params"] = []
            data['metro_active'] = settings_main_app.ids.checkbox_parser_metro.active

            for shop in reversed(settings_main_app.ids.main.children):
                data["shops_params"].append({
                    "filename": shop.ids.get("filename_field").text,
                    "title": shop.ids.get("title_field").text,
                    "dist_h": int(shop.ids.get("dist_h_field").text),
                    "dist_w": int(shop.ids.get("dist_w_field").text),
                    "dist_text": shop.ids.get("dist_text_field").text,
                    "price_w": int(shop.ids.get("price_w_field").text),
                    "product_name_w": int(shop.ids.get("product_name_w_field").text),
                    "packaging_w": int(shop.ids.get("packaging_w_field").text),
                    "status": bool(shop.ids.get("status_field").active)
                })

            # noinspection PyTypeChecker
            f.seek(0)  # Возвращение к началу файла для записи
            json.dump(data, f)
            f.truncate()  # Удаление остатка старого файла

        with open('data/cache_prices.json', encoding='utf-8') as f:
            result = json.load(f)
            result_filtered = filter_shops(result["cache"])
            main_app.base_price = result_filtered
            log('Прайс в оперативке обновлён!')

        if main_app.dialog:
            main_app.dialog.dismiss()

    # noinspection PyUnusedLocal
    @staticmethod
    def exit(MainApp):
        """
        Закрыть диалоговое окно, без сохранения настроек.

        :param main: Класс интерфейса главного окна.
        """

        if MainApp.dialog:
            MainApp.dialog.dismiss()


class Cart:
    """
    Функции в диалоговом окне корзины.
    """

    @staticmethod
    def open():
        """
        Открытие диалогового окна с корзиной.
        todo внедрить количество добавленного товара.
        todo реализовать изменение количества товара в корзине, с сохранением изменений в кэш сразу при редактировании.
        :return:
        """

        app = ToolsAJob()
        main_app = app.MainApp
        cart_main_app = app.CartMainApp

        cart_main_app.ids.cart_items_box.clear_widgets()

        if main_app.dialog:  # Закрытие диалогового окна, если открыто.
            if main_app.dialog._is_open:
                main_app.dialog.dismiss()

        shopname_list = []
        cart_get_fri = get_cart()
        for item in cart_get_fri:
            if item['title'] not in shopname_list:
                shopname_list.append(item['title'])

        # добавление товаров как раньше
        for shop in shopname_list:
            cart_shop = app.CartShopApp()
            items_list = []
            item_height = 0
            cart_get = get_cart()
            for item in cart_get:
                try:
                    if shop.lower() == item['title'].lower():
                        item["quantity"] = 1  # Временное жёсткое задавание количества
                        cart_item = app.CartItemsApp(item)

                        cart_item.ids.name_field.text = item['product_name_visible']

                        cart_item.ids.qty_field.text = "1"
                        cart_item.ids.buttonItem.id = str(item) + "/34c5v89ypu"
                        cart_item.ids.buttonItem.icon = 'cart-remove'
                        cart_item.ids.buttonItem.icon_color = 'blue'
                        cart_item.ids.buttonItem.on_release = cart_main_app.remove_from_cart
                        cart_item.add_product_card(item)
                        items_list.append(cart_item)
                        item_height = cart_item.height
                except:
                    pass

            if items_list:
                cart_shop.ids.CartName.text = f"{shop}:"
                for widget in items_list:
                    cart_shop.ids.listItems.add_widget(widget)
                cart_main_app.ids.cart_items_box.add_widget(cart_shop)

                adaptive_height = len(items_list) * (item_height) + dp(56)

                cart_shop.size_hint_y = None
                cart_shop.height = adaptive_height if adaptive_height < 300 else dp(300)

        main_app.dialog = cart_main_app

        main_app.dialog.open()

    @staticmethod
    def edit(instance):
        """
        Редактирование товара.
        :param main: Класс интерфейса главного окна.
        :param instance: Товар, который нужно отредактировать.
        """
        # item.disabled = False

    @staticmethod
    def send(main):
        """
        Отправить готовый список товаров в телеграм бот.
        :param main: Класс интерфейса главного окна.
        """
        from kivymd.uix.dialog.dialog import MDDialog

        with open('data/cache_cart.json') as f:
            cart = json.load(f)
            cart = cart['cart']
            shops = {}
            for item in cart:
                if item['title'] not in shops:
                    shops[item['title']] = []
                shops[item['title']].append({'product_name': item['product_name'], 'count': item['count']})

            for shop in shops:
                text = str(shop) + ':\n'
                shop_dict = shops[shop]
                i = 1
                for item in shop_dict:
                    text += f'\n{i}. {item["product_name"]} — {item["count"]}'
                    i += 1
                asyncio.ensure_future(send_cart(text))  # Отправка заказа в телеграм

        for widget in main.children:  # Перебор виджетов в основном окне
            if isinstance(widget, MDDialog):  # Если виджет является диалоговым окном, то:
                if widget._is_open:  # Если диалоговое окно открыто
                    widget.dismiss()


    @staticmethod
    def back():
        """
         Функция будет содержать возврат назад
        """

    @staticmethod
    def add_to_cart(ItemObj):
        """
        Добавить товар в корзину.
        todo внедрить добавление количества товара в корзину (В кэш)
        :param ItemObj: Объект карточки товара.
        """
        ItemObj.shadow_color = 'green'
        ItemObj.unbind(on_release=ItemObj.add_to_cart)
        ItemObj.bind(on_release=ItemObj.remove_from_cart)
        item = ItemObj.id

        item = str_to_dict(item)  # Конвертация строки в словарь
        item["product_name_visible"] = item["product_name"] # Создание отдельного имени для отображения и отправки

        if item not in get_cart():  # Если объекта нет в корзине
            add_cart(item)  # Отправка в корзину на сервер

    @staticmethod
    def remove_from_cart(ItemObj):
        """
        Удалить товар из корзины
        :param ItemObj: Товар, который необходимо удалить.
        """
        if "/34c5v89ypu" not in ItemObj.id:
            ItemObj.shadow_color = 'gray'
            ItemObj.unbind(on_release=ItemObj.remove_from_cart)
            ItemObj.bind(on_release=ItemObj.add_to_cart)

        item = ItemObj.id
        item = str_to_dict(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in get_cart():  # Если объект есть в корзине
            remove_cart(dict(item))  # То объект удаляется из корзины

    @staticmethod
    def add_to_cart_metro(ItemObj):
        """
        Добавить товар в корзину METRO SHOP.

        :param ItemObj: Товар, который необходимо добавить.
        """
        ItemObj.shadow_color = 'green'
        ItemObj.unbind(on_release=ItemObj.add_to_cart_metro)
        ItemObj.bind(on_release=ItemObj.remove_from_cart_metro)
        item = ItemObj.id
        item = str_to_dict(item)  # Конвертация строки в словарь

        if item not in get_cart():  # Если объекта нет в корзине
            asyncio.ensure_future(send_to_cart(item, parse_metro))  # Отправка в корзину на сервер
            add_cart(dict(item))  # То объект добавляется в корзину

    @staticmethod
    def remove_from_cart_metro(ItemObj):
        """
        Удалить товар из корзины METRO SHOP.

        :param ItemObj: Товар, который необходимо удалить.
        """
        ItemObj.shadow_color = 'gray'
        ItemObj.unbind(on_release=ItemObj.remove_from_cart_metro)
        ItemObj.bind(on_release=ItemObj.add_to_cart_metro)
        item = ItemObj.id
        item = str_to_dict(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in get_cart():  # Если объект есть в корзине
            asyncio.ensure_future(remove_from_cart(item, parse_metro))  # Удаление из корзины на сервере
            remove_cart(dict(item))  # То объект удаляется из корзины