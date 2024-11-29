import asyncio

from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDIconButton as IconButton
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.boxlayout import MDBoxLayout as BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

import telegram
import commands
import parse_metro



def dialog_cart_open(self):  # Открытие корзины
    if self.dialog:  # Закрыть диалоговое окно, если оно открыто
        self.dialog.dismiss()



    def content():
        dialog_main_layout = BoxLayout(spacing="12dp", size_hint_y=None, height="400dp", orientation='vertical',
                                       md_bg_color=self.color_bg)
        scroll_global = ScrollView(do_scroll_x=False, size_hint=(1, 1))
        scroll_global_layout = BoxLayout(orientation='vertical', spacing=0, padding=(0, 10, 0, 0),
                                         adaptive_height=True)
        for shop in ['Матушка', 'Алма', 'METRO']:
            scroll_layout_dialog = BoxLayout(orientation='vertical', spacing=0, padding=(0, 10, 0, 0),
                                             adaptive_height=True)
            scroll_layout_dialog.size_hint_y = None
            scroll_layout_dialog.bind(minimum_height=self.layout_scroll.setter('height'))
            scroll = ScrollView(do_scroll_x=False, size_hint=(1, 1))
            items_list = []

            cart_get = commands.get_cart()
            for item in cart_get:  # Наполнение корзины товарами из массива
                if shop.lower() == item['seller'].lower():
                    if item in cart_get:
                        if item['seller'] == 'METRO':
                            cart_plus = IconButton(text=' ', icon='cart-remove', id=str(item) + 'cart',
                                                   on_release=self.remove_to_cart_metro,
                                                   icon_color='red', line_color='white')
                        else:
                            cart_plus = IconButton(text=' ', icon='cart-remove', id=str(item) + 'cart',
                                                   on_release=self.remove_to_cart,
                                                   icon_color='red', line_color='white')
                    else:
                        if item['seller'] == 'METRO':
                            cart_plus = IconButton(text=' ', icon='cart-plus', id=str(item) + 'cart',
                                                   on_release=self.add_to_cart_metro,
                                                   icon_color='blue', line_color='white')
                        else:
                            cart_plus = IconButton(text=' ', icon='cart-plus', id=str(item) + 'cart',
                                                   on_release=self.add_to_cart,
                                                   icon_color='blue', line_color='white')
                    item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
                    text = MDLabel(text=str(item['name']))
                    item_layout.add_widget(text)
                    item_layout.add_widget(cart_plus)
                    items_list.append(item_layout)

            if len(items_list) > 0:
                print(shop)
                print('Длина:')
                print(len(items_list))
                shop_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='40dp')
                shop_layout.add_widget(MDLabel(text=str(shop) + ':'))
                scroll_global_layout.add_widget(shop_layout)
                for i in items_list:
                    scroll_layout_dialog.add_widget(i)

                scroll.add_widget(л)
                scroll_global_layout.add_widget(scroll)
        scroll_global.add_widget(scroll_global_layout)
        dialog_main_layout.add_widget(scroll_global)
        return dialog_main_layout

    copy_cart = IconButton(icon='page-next', on_release=self.dialog_editCart_open, icon_color='green',
                           line_color='green', text_color='green')

    self.dialog = MDDialog(size_hint_y=None, size_hint_max_y=.9, size_hint_min_y=.1)
    self.dialog.add_widget(MDDialogHeadlineText(text='Корзина', halign='left'))
    self.dialog.add_widget(MDDialogContentContainer(content()))
    self.dialog.add_widget(MDDialogButtonContainer(BoxLayout(), copy_cart))

    self.dialog.open()


def dialog_editCart_open(self):  # Открытие корзины
    if self.dialog:  # Закрыть диалоговое окно, если оно открыто
        self.dialog.dismiss()

    dialog_main_layout = BoxLayout(spacing="12dp", size_hint_y=None, height="400dp", orientation='vertical',
                                   md_bg_color=self.color_bg)

    def send_cart(self, instance):
        print(self.send_text)

        for shop in self.send_text:
            if len(self.send_text[shop]) > 1:
                text_cart = (((
                                  'Екатерина' if shop.lower() == 'матушка' else 'Ульяна' if shop.lower() == 'алма' else '') + ', добрый день!\nЗаявка на завтра:') if shop.lower() not in (
                    'metro', 'купер') else 'METRO:') + '\n' + self.send_text[shop]

                telegram.send(text_cart)
        send_text = []

    def content():
        scroll_layout_dialog = BoxLayout(orientation='vertical', spacing=0, padding=(0, 10, 0, 0),
                                         adaptive_height=True)
        scroll_layout_dialog.size_hint_y = None
        scroll_layout_dialog.bind(minimum_height=self.layout_scroll.setter('height'))
        scroll = ScrollView(do_scroll_x=False, size_hint=(1, 1))

        for shop in ['Матушка', 'Алма', 'METRO']:
            text_cart = ''
            number = 1
            for item in commands.get_cart():  # Наполнение корзины товарами из массива
                if shop.lower() == item['seller'].lower():
                    text_cart += str(number) + '. ' + str(item['name'] + ' - \n')
                    number += 1

            if len(text_cart) > 0:
                shop_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='40dp')
                shop_layout.add_widget(MDLabel(text=str(shop) + ':'))
                dialog_main_layout.add_widget(shop_layout)
                items_cart = MDTextField(multiline=True, id=str(shop), )
                items_cart.bind(text=self.on_focus_change)
                items_cart.text = text_cart
                scroll_layout_dialog.add_widget(items_cart)

                scroll.add_widget(scroll_layout_dialog)

                dialog_main_layout.add_widget(scroll)
        return dialog_main_layout

    copy_cart_dismiss = IconButton(icon='backburger', on_release=dialog_cart_open,
                                   icon_color='red',
                                   line_color='red', text_color='red')
    send_cart = IconButton(text='Отправить', icon='content-copy', on_release=send_cart, icon_color='green',
                           line_color='green', text_color='green')

    self.dialog = MDDialog(size_hint_y=None, size_hint_max_y=.9, size_hint_min_y=.1)
    self.dialog.add_widget(MDDialogHeadlineText(text='Отправить', halign='left'))
    self.dialog.add_widget(MDDialogContentContainer(content()))
    self.dialog.add_widget(MDDialogButtonContainer(BoxLayout(), copy_cart_dismiss, send_cart))

    self.dialog.open()




def start_send_files(self, instance):
    asyncio.ensure_future(commands.start_telegram(self, telegram))

def cart_list(self, instance):  # Нажатие на кнопку корзины
    item = commands.str_to_dict(instance.id)
    id = instance.id
    btn = None

    for widget in instance.children:
        if widget.id == id:
            btn = widget
            break

    if btn != None:
        if item in commands.get_cart():
            if item['seller'] == 'METRO':
                self.remove_to_cart_metro(btn)
            else:
                self.remove_to_cart(btn)
        else:
            if item['seller'] == 'METRO':
                self.add_to_cart_metro(btn)
            else:
                self.add_to_cart(btn)