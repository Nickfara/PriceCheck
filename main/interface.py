import asyncio

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout as BoxLayout
from kivymd.uix.button import MDIconButton as IconButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemTertiaryText
from kivymd.uix.screen import Screen
from kivymd.uix.scrollview import MDScrollView as ScrollView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText, MDSnackbarButtonContainer, MDSnackbarActionButton, \
    MDSnackbarActionButtonText, MDSnackbarCloseButton
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon

import commands
#import mdlog as print
import parse_metro
import telegram
import dialog_settings
import dialog_cart

cart = []


class MC(MDApp):
    def __init__(self, **kwargs):
        super().__init__()
        self.color_bg = '#f0faff'
        self.color_button = '#002538'
        self.color_top = '#c9e5ff'

        self.text_find = MDTextField(MDTextFieldLeadingIcon(icon="magnify", ), text_color_focus='black',
                                     pos_hint={'center_x': .5, 'center_y': .5}, hint_text='Найти товары')

        self.btn_find= IconButton(icon='store-search', icon_color=self.color_button,
                                    line_color=self.color_button, text_color=self.color_button,
                                    on_release=self.find)
        self.btn_cart = IconButton(icon='cart', id='1', icon_color=self.color_button,
                               line_color=self.color_button, text_color=self.color_button,
                               on_release=self.dialog_cart_open)
        self.btn_send_files = IconButton(icon='download', icon_color=self.color_button,
                                     line_color=self.color_button, text_color=self.color_button,
                                     on_release=self.start_send_files)
        self.btn_settings = IconButton(icon='settings', icon_color=self.color_button,
                                     line_color=self.color_button, text_color=self.color_button,
                                     on_release=self.dialog_settings)
        self.checkbox_parser_metro = MDCheckbox(size_hint_x=.1)
        self.base_price = []  # Кэширование прайсов
        self.text_find.text = ''
        self.text_find.focus = True

        # Переменные диалоговых окон:
        self.dialog = False
        self.send_text = {}

        asyncio.ensure_future(commands.background_load(self, parse_metro))

    def build(self):
        screen = Screen()
        layout_main = BoxLayout(orientation='vertical', md_bg_color=self.color_bg)
        layout_top = BoxLayout(orientation='horizontal', size_hint_y=None, height=self.text_find.height,
                               md_bg_color='#c9e5ff')
        layout_middle = BoxLayout(orientation='vertical', padding=(50, 0, 50, 0),)

        self.layout_scroll = BoxLayout(orientation='vertical', spacing=0, md_bg_color='gray', adaptive_height=True)
        self.layout_scroll.size_hint_y = None
        self.layout_scroll.bind(minimum_height=self.layout_scroll.setter('height'))
        scroll = ScrollView(do_scroll_x=False)

        layout_top.add_widget(self.btn_send_files)
        layout_top.add_widget(self.checkbox_parser_metro)
        layout_top.add_widget(self.text_find)
        layout_top.add_widget(self.btn_find)
        layout_top.add_widget(self.btn_cart)
        layout_top.add_widget(self.btn_settings)

        scroll.add_widget(self.layout_scroll)
        layout_middle.add_widget(scroll)

        layout_main.add_widget(layout_top)
        layout_main.add_widget(layout_middle)
        screen.add_widget(layout_main)
        return screen

    def find(self, instance):
        name = self.text_find.text
        self.layout_scroll.clear_widgets()
        finder_items = commands.finder(name, self.base_price)  # Поиск товара

        result_metro = []
        if self.checkbox_parser_metro.active:
            result_metro = parse_metro.search(name)

        if type(result_metro) is list:
            for item in result_metro:
                finder_items.append(
                    {'seller': 'METRO', 'name': item['name'], 'cost': str(item['price']), 'bundleId': item['bundleId'],
                     'minOrderQuantity': item['minOrderQuantity']})

        for item in finder_items:  # Добавление товаров в список на главный экран
            text = item['name'] + '.'
            item_layout = MDListItem(MDListItemSupportingText(text=item['seller']), MDListItemHeadlineText(text=text),
                                     MDListItemTertiaryText(text='Цена: ' + item['cost']),
                                     orientation='horizontal', size_hint_y=None, height='40dp',
                                     on_release=self.cart_list, id=str(item))

            cost = MDLabel(text='Цена: ' + item['cost'] + '₽', size_hint_x=None, width='110dp')
            if item in commands.get_cart():
                if item['seller'] == 'METRO':
                    cart_plus = IconButton(icon='cart-remove', id=str(item), on_release=self.remove_to_cart_metro,
                                           icon_color='red', line_color='white')
                else:
                    cart_plus = IconButton(icon='cart-remove', id=str(item), on_release=self.remove_to_cart,
                                           icon_color='red', line_color='white')
            else:
                if item['seller'] == 'METRO':
                    cart_plus = IconButton(icon='cart-plus', id=str(item), on_release=self.add_to_cart_metro,
                                           icon_color='blue', line_color='white')
                else:
                    cart_plus = IconButton(icon='cart-plus', id=str(item), on_release=self.add_to_cart,
                                           icon_color='blue', line_color='white')

            item_layout.add_widget(cart_plus)
            self.layout_scroll.add_widget(item_layout)

    def add_to_cart(self, instance):
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=self.add_to_cart)
        instance.bind(on_release=self.remove_to_cart)
        item = instance.id
        item = commands.str_to_dict(item)  # Конвертация строки в словарь

        if item not in cart:  # Если обьекта нет в корзине
            cart.append(dict(item))  # То обьект добавляется в корзину

    def remove_to_cart(self, instance):
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=self.remove_to_cart)
        instance.bind(on_release=self.add_to_cart)
        item = instance.id
        item = commands.str_to_dict1(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in cart:  # Если обьект есть в корзине
            cart.remove(dict(item))  # То обьект удаляется из корзины
        if self.dialog:  # Закрыть диалоговое окно, если оно открыто
            self.dialog.dismiss()
            self.dialog_cart_open(self)

    def add_to_cart_metro(self, instance):
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=self.add_to_cart_metro)
        instance.bind(on_release=self.remove_to_cart_metro)
        item = instance.id
        item = commands.str_to_dict(item)  # Конвертация строки в словарь

        if item not in cart:  # Если обьекта нет в корзине
            asyncio.ensure_future(commands.send_to_cart(item, parse_metro))  # Отправка в корзину на сервер
            cart.append(dict(item))  # То обьект добавляется в корзину

    def remove_to_cart_metro(self, instance):
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release=self.remove_to_cart_metro)
        instance.bind(on_release=self.add_to_cart_metro)
        item = instance.id
        item = commands.str_to_dict(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in cart:  # Если обьект есть в корзине
            asyncio.ensure_future(commands.remove_from_cart(item, parse_metro))  # Удаление из корзины на сервере
            cart.remove(dict(item))  # То обьект удаляется из корзины

        if self.dialog:  # Закрыть диалоговое окно, если оно открыто
            self.dialog.dismiss()
            self.dialog_cart_open(self)

    def cart_list(self,instance):
        dialog_cart.cart_list(self,instance)
    def dialog_cart_open(self, instance):  # Открытие корзины
        dialog_cart.dialog_cart_open(self, cart)

    def dialog_editCart_open(self, instance):
        dialog_cart.dialog_editCart_open(self, cart)
    def dialog_settings(self, instance):
        dialog_settings.dialog_settings_open(self)

    def start_send_files(self, instance):
        dialog_cart.start_send_files(self, instance)

    def func_dialog_save_enter(self, window, key, i, r, x):
        if len(self.text_find.text) > 0:
            if key == 13:
                self.find(self)

    def activate_enter_finder(self, instance):
        self.root_window.bind(on_key_down=self.func_dialog_save_enter)

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


def run_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Запускаем цикл событий Kivy
    async_run = asyncio.ensure_future(asyncio.gather(MC().async_run(async_lib='asyncio')))
    # Планируем остановку цикла, когда Kivy App закроется
    async_run.add_done_callback(lambda *args: loop.stop())

    # Запускаем цикл событий asyncio
    loop.run_forever()


if __name__ == "__main__":
    run_async()
