import asyncio
import mdlog
from copy import copy
from os import listdir
from os.path import isfile, join

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout as BoxLayout
from kivymd.uix.button import MDRectangleFlatButton as RFB, MDFlatButton as FB, MDRectangleFlatIconButton as RFIB
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import Screen
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.selectioncontrol import MDSwitch, MDCheckbox
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

import parse_metro
import command
import telegram
cart = []


class MC(MDApp):
    def __init__(self, **kwargs):
        super().__init__()
        color_bg = ''
        color_button = '#003fbd'
        self.text_find_names = MDTextField(text_color_focus='black', pos_hint={'center_x': .5, 'center_y': .5})

        self.find_butt = RFB(text='Поиск', halign="right", on_release=self.find, icon_color=color_button, line_color=color_button, text_color=color_button)
        self.cart = RFIB(text='Корзина', icon='cart', id='1', icon_color=color_button, line_color=color_button, text_color=color_button, on_release=self.open_cart)
        self.send_files = RFIB(text='Запустить бота', icon='download', icon_color=color_button, line_color=color_button, text_color=color_button, on_release=self.start_send_files)
        self.checkbox_parser_metro = MDCheckbox(size_hint_x=.1)
        self.base_price = [] # Кэширование прайсов
        self.TopAppBar = MDTopAppBar(type="top", spacing=0, padding=0, md_bg_color='#c9e5ff')  # Верхнее меню


        # Переменные диалоговых окон:
        self.dialog = False
        self.send_text = {}
        asyncio.ensure_future(command.background_load(self, parse_metro))

    def build(self):
        screen = Screen()
        layout_main = BoxLayout(orientation='vertical', md_bg_color='white')
        layout_top = BoxLayout(orientation='vertical', size_hint_y=None,  height=self.find_butt.height)
        layout_middle = BoxLayout(orientation='vertical')
        layout_find = BoxLayout(orientation='horizontal', spacing=10)


        self.scroll_layout = BoxLayout(orientation='vertical', spacing=0, padding=(0, 10, 0, 0), adaptive_height=True)
        self.scroll_layout.size_hint_y = None
        self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))
        scroll = ScrollView(do_scroll_x=False)

        layout_find.add_widget(self.send_files)
        layout_find.add_widget(self.checkbox_parser_metro)
        layout_find.add_widget(self.text_find_names)
        layout_find.add_widget(self.find_butt)
        layout_find.add_widget(self.cart)


        layout_top.add_widget(layout_find)
        self.TopAppBar.add_widget(layout_top)

        scroll.add_widget(self.scroll_layout)
        layout_middle.add_widget(scroll)

        layout_main.add_widget(self.TopAppBar)
        layout_main.add_widget(layout_middle)
        screen.add_widget(layout_main)
        return screen

    def find(self, instance):
        self.activate_enter_finder(self)
        name = self.text_find_names.text
        self.scroll_layout.clear_widgets()
        finder_items = command.finder(name, self.base_price) # Поиск товара

        result_mshop = []
        if self.checkbox_parser_metro.active == True:
            result_mshop = parse_metro.search(name)

        if type(result_mshop) is list:
            for item in result_mshop:
                finder_items.append({'seller': 'METRO', 'name': item['name'], 'cost': str(item['price']), 'bundleId': item['bundleId'], 'minOrderQuantity': item['minOrderQuantity']})

        for item in finder_items: # Добавление товаров в список на главный экран
            item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')

            seller = MDLabel(text='['+ item['seller'] + '] ', size_hint_x=None, width='110dp')
            text = item['name'] + '.'
            text = MDLabel(text=text)

            cost = MDLabel(text='Цена: ' + item['cost'], size_hint_x=None, width='110dp')
            if item in cart:
                if item['seller'] == 'METRO':
                    cart_plus = RFIB(text=' ', icon='cart-remove', id=str(item), on_release=self.remove_to_cart_metro, icon_color='red', line_color='white')
                else:
                    cart_plus = RFIB(text=' ', icon='cart-remove', id=str(item), on_release=self.remove_to_cart, icon_color = 'red', line_color='white')
            else:
                if item['seller'] == 'METRO':
                    cart_plus = RFIB(text=' ', icon='cart-plus', id=str(item), on_release=self.add_to_cart_metro, icon_color = 'blue', line_color='white')
                else:
                    cart_plus = RFIB(text=' ', icon='cart-plus', id=str(item), on_release=self.add_to_cart, icon_color = 'blue', line_color='white')

            item_layout.add_widget(seller)
            item_layout.add_widget(text)
            item_layout.add_widget(cost)
            item_layout.add_widget(cart_plus)
            self.scroll_layout.add_widget(item_layout)

    def add_to_cart(self, instance):
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=self.add_to_cart)
        instance.bind(on_release = self.remove_to_cart)
        item = instance.id
        item = command.str_to_dict(item) # Конвертация строки в словарь

        if item not in cart: # Если обьекта нет в корзине
            cart.append(dict(item)) # То обьект добавляется в корзину

    def remove_to_cart(self,instance):
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release = self.remove_to_cart)
        instance.bind(on_release=self.add_to_cart)
        item = instance.id
        item = command.str_to_dict1(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in cart: # Если обьект есть в корзине
            cart.remove(dict(item)) # То обьект удаляется из корзины
        if self.dialog:  # Закрыть диалоговое окно, если оно открыто
            self.dialog.dismiss()
            self.open_cart(self)

    def add_to_cart_metro(self, instance):
        instance.icon = 'cart-remove'
        instance.icon_color = 'red'
        instance.unbind(on_release=self.add_to_cart_metro)
        instance.bind(on_release=self.remove_to_cart_metro)
        item = instance.id

        item = command.str_to_dict(item) # Конвертация строки в словарь

        if item not in cart: # Если обьекта нет в корзине
            parse_metro.add_cart(item)
            cart.append(dict(item)) # То обьект добавляется в корзину

    def remove_to_cart_metro(self,instance):
        instance.icon = 'cart-plus'
        instance.icon_color = 'blue'
        instance.unbind(on_release = self.remove_to_cart_metro)
        instance.bind(on_release=self.add_to_cart_metro)
        item = instance.id
        item = command.str_to_dict(''.join(item.strip('cart')))  # Конвертация строки в словарь

        if item in cart: # Если обьект есть в корзине
            parse_metro.remove_cart(item)
            cart.remove(dict(item)) # То обьект удаляется из корзины

        if self.dialog:  # Закрыть диалоговое окно, если оно открыто
            self.dialog.dismiss()
            self.open_cart(self)

    def open_cart(self, instance): # Открытие корзины
        self.activate_enter_finder(self)
        if self.dialog:  # Закрыть диалоговое окно, если оно открыто
            self.dialog.dismiss()

        dialog_main_layout = BoxLayout(spacing="12dp", size_hint_y=None, height="400dp", orientation='vertical')

        def content():
            scroll_layout_dialog = BoxLayout(orientation='vertical', spacing=0, padding=(0, 10, 0, 0), adaptive_height=True)
            scroll_layout_dialog.size_hint_y = None
            scroll_layout_dialog.bind(minimum_height=self.scroll_layout.setter('height'))
            scroll = ScrollView(do_scroll_x=False, size_hint=(1,1))
            copy_cart = RFIB(text='Далее', icon='content-copy', on_release=self.copy_cart, icon_color='green',
                             line_color='green', text_color='green')
            dialog_main_layout.add_widget(copy_cart)

            for shop in ['Матушка', 'Алма', 'METRO']:
                items_list = []

                for item in cart: # Наполнение корзины товарами из массива
                    if shop.lower() == item['seller'].lower():
                        if item in cart:
                            if item['seller'] == 'METRO':
                                cart_plus = RFIB(text=' ', icon='cart-remove', id=str(item) + 'cart',
                                                 on_release=self.remove_to_cart_metro,
                                                 icon_color='red', line_color='white')
                            else:
                                cart_plus = RFIB(text=' ', icon='cart-remove', id=str(item) + 'cart', on_release=self.remove_to_cart,
                                             icon_color='red', line_color='white')
                        else:
                            if item['seller'] == 'METRO':
                                cart_plus = RFIB(text=' ', icon='cart-plus', id=str(item) + 'cart',
                                                 on_release=self.add_to_cart_metro,
                                                 icon_color='blue', line_color='white')
                            else:
                                cart_plus = RFIB(text=' ', icon='cart-plus', id=str(item) + 'cart', on_release=self.add_to_cart,
                                             icon_color='blue', line_color='white')
                        item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
                        text = MDLabel(text=str(item['name']))
                        item_layout.add_widget(text)
                        item_layout.add_widget(cart_plus)
                        items_list.append(item_layout)

                if len(items_list) > 0:
                    shop_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='40dp')
                    shop_layout.add_widget(MDLabel(text=str(shop) + ':'))
                    scroll_layout_dialog.add_widget(shop_layout)
                    for i in items_list:
                        scroll_layout_dialog.add_widget(i)
            scroll.add_widget(scroll_layout_dialog)

            dialog_main_layout.add_widget(scroll)
            return dialog_main_layout


        self.dialog = MDDialog(type="custom", content_cls = content())
        self.dialog.title = 'Корзина'

        self.dialog.open()

    def copy_cart(self, instance): # Открытие корзины
        if self.dialog:  # Закрыть диалоговое окно, если оно открыто
            self.dialog.dismiss()

        dialog_main_layout = BoxLayout(spacing="12dp", size_hint_y=None, height="400dp", orientation='vertical')

        def content():
            scroll_layout_dialog = BoxLayout(orientation='vertical', spacing=0, padding=(0, 10, 0, 0), adaptive_height=True)
            scroll_layout_dialog.size_hint_y = None
            scroll_layout_dialog.bind(minimum_height=self.scroll_layout.setter('height'))
            scroll = ScrollView(do_scroll_x=False, size_hint=(1,1))
            copy_cart_dismiss = RFIB(text='Вернуться', icon='keyboard-backspace', on_release=self.open_cart, icon_color='red',
                                     line_color='red', text_color='red')
            send_cart = RFIB(text='Отправить', icon='content-copy', on_release=self.send_cart, icon_color='green',
                             line_color='green', text_color='green')

            cart_layout = BoxLayout(orientation='horizontal', spacing=5)
            button_layout = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=copy_cart_dismiss.height)
            button_layout.add_widget(copy_cart_dismiss)
            button_layout.add_widget(send_cart)
            dialog_main_layout.add_widget(button_layout)
            scroll_layout_dialog.add_widget(cart_layout)

            for shop in ['Матушка', 'Алма', 'METRO']:
                text_cart = ''
                number = 1
                for item in cart: # Наполнение корзины товарами из массива
                    if shop.lower() == item['seller'].lower():
                        text_cart += str(number) + '. ' + str(item['name'] +' - \n')
                        number += 1

                if len(text_cart) > 0:
                    shop_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='40dp')
                    shop_layout.add_widget(MDLabel(text=str(shop) + ':'))
                    scroll_layout_dialog.add_widget(shop_layout)
                    items_cart = MDTextField(multiline=True, id=str(shop), )
                    items_cart.bind(text=self.on_focus_change)
                    items_cart.text = text_cart
                    scroll_layout_dialog.add_widget(items_cart)

            scroll.add_widget(scroll_layout_dialog)

            dialog_main_layout.add_widget(scroll)
            return dialog_main_layout


        self.dialog = MDDialog(type="custom", content_cls = content())
        self.dialog.title = 'Отправить'

        self.dialog.open()

    def on_focus_change(self, instance, text):
        shop = str(instance.id)
        self.send_text[shop] = str(text)
        print(self.send_text)

    def send_cart(self,instance):
        print(self.send_text)

        for shop in self.send_text:
            if len(self.send_text[shop]) > 1:
                text_cart = ((('Екатерина' if shop.lower() == 'матушка' else 'Ульяна' if shop.lower() == 'алма' else '') + ', добрый день!\nЗаявка на завтра:') if shop.lower() not in ('metro', 'купер') else 'METRO:') + '\n' + self.send_text[shop]

                telegram.send(text_cart)
        send_text = []

    def start_send_files(self, instance):
        self.activate_enter_finder(self)
        asyncio.ensure_future(command.start_telegram(self, telegram))


    def func_dialog_save_enter(self, window, key, i, r, x):
        if len(self.text_find_names.text) > 0:
            if key == 13:
                self.find(self)

    def activate_enter_finder(self, instance):
        self.root_window.bind(on_key_down=self.func_dialog_save_enter)


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