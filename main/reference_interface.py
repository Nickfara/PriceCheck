import asyncio
import mdlog
from copy import copy
from os import listdir
from os.path import isfile, join

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout as BoxLayout, MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton as RFB, MDFlatButton as FB, MDRectangleFlatIconButton as RFIB
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import Screen
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.selectioncontrol import MDSwitch, MDCheckbox
from kivymd.uix.textfield import MDTextField

import Database_connections as dc
import Database_functions
import Wildberries_parser as WB_Pars
import autoclick


items_warning = []
log = True
dc.update_item('АВТОКЛИКЕР', '0')

async def async_autoclick(a, b, c, d, e, f):
    check = copy(dc.get_item('АВТОКЛИКЕР'))['names']
    if check != '0' and check != '1':
        dc.update_item('АВТОКЛИКЕР', '0')
    if check == '0':
        loop = asyncio.get_event_loop()
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor()

        def start_clicker():
            result = autoclick.start(a, b, c, e, f, check_data=d)
            items_warning.append(result) # Запуск автокликера и добавление предупреждений если есть

        await loop.run_in_executor(executor, start_clicker)

    else:
        print('Остановка автокликера!')
        dc.update_item('АВТОКЛИКЕР', '0')



def base_get():
    logging.info('ИНТЕРФЕЙС: base_get')
    with open('Wildberries_database.txt', 'r') as f:
        data = f.read()
        if data.find('|') != -1:
            data = data.split('|')
            return data
        else:
            return None


def base_push(string):
    logging.info('ИНТЕРФЕЙС: base_push')
    with open('Wildberries_database.txt', 'w') as f:
        if log: print('Чтение файла базы WB...')
        if log: print(string)
        f.write(string)
        f.close()


class BotiIko(MDApp):
    def __init__(self):  # Переменные класса
        super().__init__()
        # Оформление
        self.teafiles = []
        self.onlyfiles = [] # Файлы документов
        self.color_acent_1 = '#fefefe'
        self.color_acent_2 = '#fe433e'
        self.color_panel = '#272a2f'
        self.color_background_start = '#212529'
        self.color_background_top = '#1E2125'
        self.color_list = '#5F646D'

        self.tea_checks = None  # Массив чеков с ВБ на чай
        self.scroll_layout = None
        self.shops = None  # Названия поставщиков
        self.btn_select_shop = None  # Выбранный поставщик
        self.doc = None  # Накладная в словаре
        self.dialog = None  # Диалоговое окно
        self.item_name = None  # Выбранный из списка товар
        self.name_ = None  # Наименование товара
        self.items = None  # Список товаров из iIko
        self.end_docList = None  # Готовая накладная, готовая к заведению
        self.drop = None
        self.menu_select_item = None  # Хранит в себе название товара если он один в поиске
        self.enter_for_save = False
        self.temp = None  # Временные данные с накладной (Используется для получения шапки чека, при запуске кликера)
        self.shops = ['Чек', 'Коф', 'КофП', 'Метро', 'Матушка',
                      'Хозы', 'Юнит', 'Выпечка', 'Айсберри', 'Десан', 'Виста', 'Кофе', 'Арома']  # Названия поставщиков
        self.shops = sorted(self.shops)  # Сортировка
        self.dialog_wb = None

    def check_warnings(self, instance):
        def check2():
            if len(items_warning) > 0:
                print(items_warning[0])
                if len(items_warning[0]) > 0:
                    text = 'Цена у товаров с id ниже отличается более чем в 1.7 раз:'
                    for i in items_warning[0]:
                        print('ПОП2')
                        text += f'\n{i}'
                    text_ = MDLabel(text=text)
                    self.scroll_layout.clear_widgets()
                    self.scroll_layout.add_widget(text_)
                    print('ПОПОПОПОПО')
    def scan_file(self):
        logging.info('ИНТЕРФЕЙС: scan_file')
        self.onlyfiles = [f for f in listdir('documents') if isfile(join('documents', f))]

        for i in self.teafiles:
            self.onlyfiles.append(i)
        menu_items = []
        for doc_name in self.onlyfiles:
            if '.' in doc_name:
                if doc_name.split('.')[1] in ['json', 'xls', 'xlsx', 'WB']:
                    menu_items.append({
                        "text": f"{doc_name}",
                        "on_release": lambda x=f"{doc_name}": self.func_select_doc_active(x),
                        'theme_text_color': 'Custom',
                        "text_color": self.color_acent_1,
                        "md_bg_color": self.color_background_start
                    })
        return menu_items

    def build(self):
        logging.info('ИНТЕРФЕЙС: build')

        # ______________________________Выбор поставщика
        def add_button_shops():
            self.btn_select_shop = RFB(text='Поставщик', size_hint=(0.5, None), icon='plus',
                                       text_color=self.color_acent_1, line_color=self.color_acent_2)
            menu_items = []
            for shop in self.shops:
                menu_items.append({
                    "text": f"{shop}",
                    "on_release": lambda x=f"{shop}": self.func_select_shop_active(x),
                    'theme_text_color': 'Custom',
                    "text_color": self.color_acent_1,
                    "md_bg_color": self.color_background_start
                })
            self.dropdown = MDDropdownMenu()
            self.dropdown.items = menu_items
            self.dropdown.caller = self.btn_select_shop
            self.btn_select_shop.bind(on_release=self.func_select_shop)
            self.dropdown.bind(on_select=lambda instance, x: setattr(self.btn_select_shop, 'text', x))

        # _______________________________Выбор накладной
        def add_button_doc():
            self.dropdown2 = MDDropdownMenu()
            self.dropdown2.caller = self.btn_input_doc_name
            self.btn_input_doc_name.bind(on_release=self.func_select_doc)
            self.dropdown2.bind(on_select=lambda instance, x: setattr(self.btn_input_doc_name, 'text', x))

        # _______________________________Переключатели
        def switched():
            # ______________________________Переключатели
            self.switch_name = MDSwitch(width='64', track_color_active=self.color_acent_2,
                                        thumb_color_inactive=self.color_acent_2,
                                        thumb_color_active=self.color_background_start) # Переключатель наименования
            self.switch_name.active = True
            self.switch_header = MDSwitch(width='64', track_color_active=self.color_acent_2,
                                          thumb_color_inactive=self.color_acent_2,
                                          thumb_color_active=self.color_background_start, pos=(.8, .5))
            self.checkbox_header = MDCheckbox(size_hint=(None, None), size=(24, 24)) # Переключатель шапки
            self.checkbox_header.pos_hint = {'x': .5, 'y': 0.3}
            self.switch_header.active = True
            self.switch_type = MDSwitch(size_hint=(None, None), width='10dp', track_color_active=self.color_acent_2,
                                        thumb_color_inactive=self.color_acent_2,
                                        thumb_color_active=self.color_background_start) # Переключатель типа
            self.switch_type.active = True
            self.checkbox_type = MDCheckbox(size_hint=(None, None), size=(24, 24)) # Чекбокс детального ввода типа
            self.checkbox_type.pos_hint = {'x': .5, 'y': 0.3}

            self.switch_count = MDSwitch(size_hint=(None, None), width='10dp', track_color_active=self.color_acent_2,
                                         thumb_color_inactive=self.color_acent_2,
                                         thumb_color_active=self.color_background_start) # Переключатель количества
            self.switch_cost = MDSwitch(size_hint=(None, None), width='10dp', track_color_active=self.color_acent_2,
                                        thumb_color_inactive=self.color_acent_2,
                                        thumb_color_active=self.color_background_start) # Переключатель цены
            self.switch_version = RFB(text='Режим', size_hint=(None, None), width='10dp', icon='plus',
                                       text_color=self.color_acent_1, line_color=self.color_acent_2, on_release=self.func_switch_version) # Переключатель режимов
            # _________________________Текст_Переключателей
            switch_header_text = MDLabel(text='Шапка:', valign="center", halign="right", theme_text_color='Custom',
                                         text_color=self.color_acent_1)
            switch_name_text = MDLabel(text='Название:', valign="center", halign="right", theme_text_color='Custom',
                                       text_color=self.color_acent_1)
            switch_type_text = MDLabel(text='Тип товара:', valign="center", halign="right", theme_text_color='Custom',
                                       text_color=self.color_acent_1)
            switch_count_text = MDLabel(text='Количество:', valign="center", halign="right", theme_text_color='Custom',
                                        text_color=self.color_acent_1)
            switch_cost_text = MDLabel(text='Цена:', valign="center", halign="right", theme_text_color='Custom',
                                       text_color=self.color_acent_1)
            switch_version_text = MDLabel(text='Режим:', theme_text_color='Custom',
                                          text_color=self.color_acent_1)

            # Структура лэйаутов
            switch_layouts = {BoxLayout(orientation='horizontal'): (switch_name_text, self.switch_name),
                              BoxLayout(orientation='horizontal'): (self.checkbox_type, switch_type_text, self.switch_type),
                              BoxLayout(orientation='horizontal'): (self.checkbox_header, switch_header_text, self.switch_header),
                              BoxLayout(orientation='horizontal'): (switch_count_text, self.switch_count),
                              BoxLayout(orientation='horizontal'): (switch_cost_text, self.switch_cost),
                              BoxLayout(orientation='horizontal'): (switch_version_text, self.switch_version)}

            switch_left_layout = BoxLayout(orientation='vertical', padding=(0, 0, 40, 0), size_hint_x=None, width=185,
                                           md_bg_color=self.color_panel)
            switch_right_layout = BoxLayout(orientation='vertical', padding=(0, 0, 35, 0), size_hint_x=None, width=180,
                                            md_bg_color=self.color_panel)
            switch_all_layout = BoxLayout(orientation='horizontal', padding=(0, 0, 50, 0), size_hint_x=None,
                                          width=(switch_left_layout.width + switch_right_layout.width),
                                          md_bg_color=self.color_panel)

            # Сортировка лэйаутов
            n = 0
            for i in switch_layouts:
                i.add_widget(switch_layouts[i][0])
                i.add_widget(switch_layouts[i][1])
                if len(switch_layouts[i]) >= 3:
                    i.add_widget(switch_layouts[i][2])
                if n < 3:
                    switch_left_layout.add_widget(i)
                else:
                    switch_right_layout.add_widget(i)
                n += 1

            switch_all_layout.add_widget(switch_left_layout)
            switch_all_layout.add_widget(switch_right_layout)
            return switch_all_layout

        # _______________________________Остальные кнопки__________________________________________________
        btn_launch_autoclick = RFB(text="Запустить автокликер", on_release=self.func_launch_autoclick, size_hint=(1, 1),
                                   text_color=self.color_acent_1, line_color=self.color_acent_2,
                                   md_bg_color=self.color_background_start)
        btn_check_warnings = RFB(text="Проверить предупреждения", on_release=self.check_warnings, size_hint=(1, 1),
                                   text_color=self.color_acent_1, line_color=self.color_acent_2,
                                   md_bg_color=self.color_background_start)
        btn_menu_item = RFIB(icon='pencil-outline', text="Редактировать товар", on_release=self.func_dialog_open,
                             size_hint=(.2, .5), text_color=self.color_acent_2, icon_color=self.color_acent_2,
                             line_color=self.color_panel, font_size=14)
        btn_wb = RFIB(icon='cart-arrow-down', text="Wildberries", on_release=self.wb_parse,
                      size_hint=(.2, .5), text_color='#8D297F', icon_color='#8D297F',
                      line_color=self.color_panel, font_size=14)

        # ______________________________Кнопки
        self.btn_doc_read = RFB(text="Считать", on_release=self.func_doc_read, size_hint=(0.5, None),
                                text_color=self.color_acent_1, line_color=self.color_acent_2)
        self.btn_doc_convert = RFB(text="Конвертировать", on_release=self.func_doc_convert_new, size_hint=(0.5, None),
                                   text_color=self.color_acent_1, line_color=self.color_acent_2)

        self.btn_input_doc_name = RFB(text='Накладная', size_hint=(0.5, None), text_color=self.color_acent_1,
                                      line_color=self.color_acent_2)

        def sort_layouts():
            add_button_doc()
            add_button_shops()

            # Лэйаут с кнопками-меню
            btn_select_layout = BoxLayout(orientation='horizontal', size_hint_y=None,
                                          height=self.btn_select_shop.height)
            # Лэйаут с кнопками-конвертации
            btn_read_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=self.btn_select_shop.height)
            # Лэйаут с доп кнопками
            btn_edit_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=18)
            # Лэйаут с кнопками
            btn_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=350, padding=10, spacing=10,
                                   md_bg_color=self.color_panel)
            # Лэйаут - верхнее меню, с лэйаутами выше
            top_layout = BoxLayout(orientation='horizontal', padding=(0, 0, 0, 0,), size_hint_y=None, height='240dp',
                                   md_bg_color=self.color_background_top)

            # Лэйаут под листающий список
            self.scroll_layout = BoxLayout(orientation='vertical', spacing=0, padding=(0, 10, 0, 0))
            self.scroll_layout.size_hint_y = None
            self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))
            scroll = ScrollView(do_scroll_x=False)

            # Главный лэйаут
            layout = BoxLayout(orientation='vertical', md_bg_color=self.color_list)
            top_layout_card = MDCard(orientation='horizontal', elevation=2, radius=[0, ], size_hint_y=None,
                                     height=top_layout.height, )

            # Структура лэйаутов
            layout_dict = {top_layout_card:
                               {top_layout:
                                    {btn_layout:
                                         {btn_select_layout: {self.btn_select_shop: {}, self.btn_input_doc_name: {}},
                                          btn_read_layout: {self.btn_doc_read: {}, self.btn_doc_convert: {}},
                                          btn_edit_layout: {BoxLayout(): {}, btn_wb: {}, btn_menu_item: {}},
                                          BoxLayout(): {},
                                          btn_launch_autoclick: {},
                                          btn_check_warnings: {}
                                          },
                                     BoxLayout(): {},
                                     switched(): {}
                                     }},
                           scroll: {self.scroll_layout: {}}}

            # Процесс сортировки лэйаутов
            for i in layout_dict:
                if len(layout_dict[i]) > 0:
                    for i2 in layout_dict[i]:
                        if len(layout_dict[i][i2]) > 0:
                            for i3 in layout_dict[i][i2]:
                                if len(layout_dict[i][i2][i3]) > 0:
                                    for i4 in layout_dict[i][i2][i3]:
                                        if len(layout_dict[i][i2][i3][i4]) > 0:
                                            for i5 in layout_dict[i][i2][i3][i4]:
                                                i4.add_widget(i5)
                                        i3.add_widget(i4)
                                i2.add_widget(i3)
                        i.add_widget(i2)
                layout.add_widget(i)

            screen = Screen()
            screen.add_widget(layout)
            return screen

        self.items = copy(Database_functions.take_items())
        if log: print('ДОКУМЕНТЫ: ' + str(self.onlyfiles))
        return sort_layouts()

    # Считать накладную
    def func_doc_read(self, instance):
        logging.info('ИНТЕРФЕЙС: func_doc_read')
        from Scanning_documents import doc
        self.scroll_layout.clear_widgets()
        if self.btn_select_shop != 'Выбрать поставщика':
            if self.btn_select_shop.text == 'Чек':
                if self.btn_input_doc_name.text.split('.')[1] in ('json'):
                    self.temp = doc(self.btn_select_shop.text, f"documents/{self.btn_input_doc_name.text}")
                    self.doc = self.temp['items']

            else:
                self.temp = doc(self.btn_select_shop.text, f"documents/{self.btn_input_doc_name.text}")
                print(self.temp)
                if type(self.temp) == dict:
                    self.doc = self.temp['items']
                else:
                    self.doc = self.temp
                    self.temp = None

            if log: print('Считанная накладная:')
            if log: print(self.temp if self.temp != None else self.doc)

            if self.doc:
                return
            text = MDLabel(text='Поставщик введён неверно!')
            self.scroll_layout.clear_widgets()
            self.doc = None
        else:
            text = MDLabel(text='Поставщик не выбран!')
            self.scroll_layout.clear_widgets(text)

    # Первое выполнение конвертации
    def func_doc_convert_new(self, obj):
        logging.info('ИНТЕРФЕЙС: func_doc_convert_new')
        self.end_docList = []
        self.func_doc_convert_repeat(obj)

    # Продолжение конвертации после не найденого товара
    def func_doc_convert_repeat(self, obj):
        logging.info('ИНТЕРФЕЙС: func_doc_convert_repeat')
        if log: logging.info('ИНТЕРФЕЙС: func_doc_convert_repeat')
        self.end_docList = []
        if log: print('SELF.DOC:')
        if log: print(self.doc)
        if log: print('SELF.TEMP:')
        if log: print(self.temp)
        if self.doc is None:
            self.scroll_layout.clear_widgets()
            self.scroll_layout.add_widget(MDLabel(text='Накладная не считана'))
        else:
            self.ind_convert_item = 0
            for i in self.doc:
                response = Database_functions.get_item(i)
                self.name_ = i
                if not response:
                    self.func_dialog_open(obj)
                    break
                else:
                    temp = copy(i)
                    temp['name'] = response['item']
                    temp['original'] = i['name']
                    self.end_docList.append(temp)
                self.ind_convert_item += 1
                self.scroll_layout.clear_widgets()
                if self.btn_select_shop.text == 'Чек' or (self.checkbox_header.active and type(self.temp) == dict):
                    list_items_text3 = MDLabel(text=f'Дата: {self.temp["date"]}\n', theme_text_color='Custom',
                                               text_color=self.color_acent_1)
                    if self.btn_select_shop.text == 'Чек':
                        list_items_text3.text += f'\nЧек: {self.temp["check"]}\n\n'
                    else:
                        list_items_text3.text += f'\n{self.temp["check"]}\n\n'
                    data_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='120dp')
                    data_layout.add_widget(list_items_text3)
                    self.scroll_layout.add_widget(data_layout)
            for i1 in self.end_docList:
                list_items_text1 = MDLabel(text='\n' + f"{i1['id']}. {i1['original']} ||||| {i1['name']} |||||",
                                           theme_text_color='Custom', text_color=self.color_acent_1)
                list_items_text2 = MDLabel(
                    text='\n' + f"{i1['count']} X {i1['cost']} = {i1['sum'] if self.btn_select_shop == 'Чек' else ''}",
                    halign="right", size_hint_x=None, width='190dp', theme_text_color='Custom',
                    text_color=self.color_acent_1)
                text_item_Layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='60dp')
                text_item_Layout.add_widget(list_items_text1)
                text_item_Layout.add_widget(list_items_text2)
                self.scroll_layout.add_widget(text_item_Layout)

    # Добавить товар
    def func_add_item(self, instance):
        logging.info('ИНТЕРФЕЙС: func_add_item')
        if log: print(self.list_.text)
        Database_functions.add_item(item=self.list_.text)
        self.items = copy(Database_functions.take_items())

    # Очистить товар
    def func_clear_item(self, instance):
        logging.info('ИНТЕРФЕЙС: func_clear_item')
        if log: print(self.list_.text)
        Database_functions.clear_item(item=self.list_.text)
        self.items = copy(Database_functions.take_items())

    # Удалить товар
    def func_delete_item(self, instance):
        logging.info('ИНТЕРФЕЙС: func_delete_item')
        if log: print(self.list_.text)
        Database_functions.delete_item(item=self.list_.text)
        self.items = copy(Database_functions.take_items())

    # Запуск автокликера
    def func_launch_autoclick(self, instance):
        logging.info('ИНТЕРФЕЙС: func_launch_autoclick')
        try:
            if log: print(self.switch_name.active)
            checkboxs = {'name': self.switch_name.active, 'type': self.switch_type.active,
                         'count': self.switch_count.active, 'cost': self.switch_cost.active,
                         'header': self.switch_header.active}
            if self.temp != None and (self.btn_select_shop.text == 'Чек' or (self.checkbox_header.active and type(self.temp) == dict)):
                number = self.temp["check"] if self.btn_input_doc_name.text.split('.')[
                                                   1] == 'WB' else (f'\nЧек: {self.temp["check"]}' if self.btn_select_shop.text == 'Чек' else self.temp["check"])
                info = {'date': self.temp["date"], 'number': number}
            else:
                info = None
            asyncio.ensure_future(async_autoclick(self.end_docList, self.btn_select_shop, checkboxs, info,
                                                  self.btn_input_doc_name.text.split('.')[1],
                                                  self.checkbox_type.active))
            #Autoclick.start(self.end_docList, self.btn_select_shop, checkboxs, check_data=info)
        except Exception as e:
            self.scroll_layout.clear_widgets()
            if log: print(e)
            self.scroll_layout.add_widget(MDLabel(text=str(e)))


    # Диалоговое окно - Открытие
    def func_dialog_open(self, obj):
        logging.info('ИНТЕРФЕЙС: func_dialog_open')
        self.enter_for_save = False
        self.item_name = None
        btn_item_add = RFB(text="Добавить товар", text_color=self.color_acent_1, line_color=self.color_acent_2,
                           pos_hint={
                               'center_x': 0.5, 'center_y': 0.6}, on_release=self.func_add_item)
        btn_item_delete = RFB(text="Удалить товар", pos_hint={
            'center_x': 0.5, 'center_y': 0.6}, text_color=self.color_acent_1, line_color=self.color_acent_2,
                              on_release=self.func_delete_item)
        btn_item_clear = RFB(text="Очистить товар", pos_hint={
            'center_x': 0.5, 'center_y': 0.6}, text_color=self.color_acent_1, line_color=self.color_acent_2,
                             on_release=self.func_clear_item)
        name = self.name_['name'] if type(self.name_) == dict else 'none'
        text = f"'{name}' - наименование не найдено, выберите товар из списка ниже, что бы связать их! "
        if type(obj) is not int:
            if obj.text == 'Редактировать товар':
                text = 'Выберите товар из списка, для редактирования!'
        btn_skip = FB(text="Пропустить", theme_text_color='Custom', text_color=self.color_acent_1,
                      on_release=self.func_dialog_close)
        btn_save = RFB(text="Сохранить", text_color=self.color_acent_1,
                       on_release=self.func_dialog_save, line_color=self.color_acent_2)
        self.list_ = MDTextField(hint_text="Поиск товара", on_text_validate=self.func_dialog_enter,
                                 text_color_focus=self.color_acent_1, line_color_focus=self.color_acent_2,
                                 hint_text_color_focus=self.color_acent_2)
        self.list_.bind(text=self.func_dialog_load)
        self.dialog_layout = BoxLayout(spacing="12dp", size_hint_y=None, height="220dp", orientation='vertical')

        def sort_():
            btn_layout = BoxLayout(orientation='horizontal')
            btn_layout.add_widget(btn_skip)
            btn_layout.add_widget(btn_save)

            btn_item_layout = BoxLayout(orientation='horizontal')
            btn_item_layout.add_widget(btn_item_delete)
            btn_item_layout.add_widget(btn_item_clear)
            btn_item_layout.add_widget(btn_item_add)

            self.dialog_layout.add_widget(MDLabel(text=text, theme_text_color='Custom', text_color=self.color_acent_1))
            self.dialog_layout.add_widget(self.list_)

            if type(obj) is not int:
                if obj.text == 'Редактировать товар':
                    btn_layout.remove_widget(btn_skip)
                    btn_layout.remove_widget(btn_save)
                    btn_layout.add_widget(FB(text="Закрыть", theme_text_color='Custom', text_color=self.color_acent_1,
                                             on_release=self.func_dialog_close))
            self.dialog_layout.add_widget(btn_item_layout)
            self.dialog_layout.add_widget(btn_layout)

            return self.dialog_layout

        title_text = f"[color={self.color_acent_1}]Товар не найден![/color]"
        if type(obj) is not int:
            if obj.text == 'Редактировать товар':
                title_text = 'Настройки товаров!'

        self.dialog = MDDialog(title=title_text, type="custom", content_cls=sort_(),
                               md_bg_color=self.color_background_start)
        #self.list_.text = ''
        #self.list_.focus = True
        self.dialog.open()

    # Диалоговое окно - Закрытие
    def func_dialog_close(self, obj):
        logging.info('ИНТЕРФЕЙС: func_dialog_close')
        if obj.text == 'Закрыть':
            self.dialog.dismiss()
            self.enter_for_save = False
        else:
            self.doc.pop(self.ind_convert_item)
            self.dialog.dismiss()
            self.func_doc_convert_repeat(obj)
            self.enter_for_save = False

    # Диалоговое окно - Кнопка сохранить
    def func_dialog_save(self, obj):
        logging.info('ИНТЕРФЕЙС: func_dialog_save')
        item = {self.item_name: self.items[self.item_name]}
        response = Database_functions.update_items(item, self.name_, self.items)
        self.enter_for_save = False
        if response != False:
            Database_functions.get_item(self.name_)
            self.dialog.dismiss()
            self.func_doc_convert_repeat(obj)

    # Диалоговое окно - Сохранить на ентер
    def func_dialog_save_enter(self, window, key, i, r, x):
        logging.info('ИНТЕРФЕЙС: func_dialog_save_enter')
        print(self.dialog)
        print(self.dialog_wb)
        if self.dialog:
            if self.enter_for_save:
                if log: print('Сработала функция нажатия Enter')
                if key == 13:
                    self.func_dialog_save(key)
        if self.dialog_wb:
            self.wb_save(self)

    # Диалоговое окно - Кнопка-название товара
    def func_dialog_select(self, obj):
        logging.info('ИНТЕРФЕЙС: func_dialog_select')
        if log: print('Выбран: ', str(obj))
        self.list_.text = str(obj)
        self.item_name = str(obj)
        self.drop.dismiss()
        self.root_window.bind(on_key_down=self.func_dialog_save_enter)
        if obj != '':
            self.enter_for_save = True
        else:
            self.enter_for_save = False

    # Диалоговое окно - Кнопка-название товара (Активация через ентер)
    def func_dialog_enter(self, instance):
        logging.info('ИНТЕРФЕЙС: func_dialog_enter')
        if self.dialog:
            obj = self.menu_select_item
            self.func_dialog_select(obj=obj)

    # Загрузка, поиск и отображение товаров в выпадающем списке
    def func_dialog_load(self,instance, item=None):
        logging.info('ИНТЕРФЕЙС: func_dialog_load')
        if self.drop:
            self.drop.dismiss()
        self.drop = MDDropdownMenu()
        text = self.list_.text.split(' ')
        menu_items = []
        for i in self.items:
            check = True
            for find_obj in text:
                if find_obj.lower() in i.lower():
                    pass
                else:
                    check = False

            if check:
                menu_items.append({
                    "text": f"{i}",
                    "on_release": lambda x=f"{i}": self.func_dialog_select(x),
                    'theme_text_color': 'Custom',
                    "text_color": self.color_acent_1,
                    "md_bg_color": self.color_background_start
                })

        if len(menu_items) > 0:
            self.menu_select_item = menu_items[0]['text']
        self.drop.items = menu_items
        self.drop.caller = self.list_
        self.drop.open()

    # Кнопка выбора поставщика - Открытие диалогового окна
    def func_select_shop(self, instance):
        logging.info('ИНТЕРФЕЙС: func_select_shop')

        self.dropdown.open()

    # Кнопка-название поставщика - выбор поставщика и закрытие диалогового окна
    def func_select_shop_active(self, shop):
        logging.info('ИНТЕРФЕЙС: func_select_shop_active')
        self.dropdown.dismiss()
        self.btn_select_shop.text = shop
        if shop in ['Виста', 'Кофе', 'Айсберри']:
            if log: print(shop)
            self.btn_doc_read.disabled = True
            self.btn_doc_convert.disabled = True
            self.switch_header.active = True
            self.switch_header.disabled = True
            self.switch_name.disabled = True
            self.switch_name.active = True
            self.switch_type.disabled = True
            self.switch_type.active = True
            self.switch_count.disabled = True
            self.switch_count.active = True
            self.switch_cost.disabled = True
            self.switch_cost.active = True
            self.switch_version.disabled = True
            self.btn_input_doc_name.disabled = True
        else:
            self.btn_doc_read.disabled = False
            self.btn_doc_convert.disabled = False
            self.switch_header.disabled = False
            self.switch_name.disabled = False
            self.switch_type.disabled = False
            self.switch_count.disabled = False
            self.switch_cost.disabled = False
            self.switch_version.disabled = False
            self.btn_input_doc_name.disabled = False

            # Кнопка выбора документа

    # Кнопка выбора документа
    def func_select_doc(self, instance):
        logging.info('ИНТЕРФЕЙС: func_select_doc')
        self.dropdown2.items = self.scan_file()
        self.dropdown2.open()

    # Кнопка-название документа
    def func_select_doc_active(self, name):
        logging.info('ИНТЕРФЕЙС: func_select_doc_active')
        self.switch_header.active = True
        self.switch_name.active = True
        self.switch_type.active = True
        self.switch_count.active = False
        self.switch_cost.active = False
        self.doc = None
        self.dropdown2.dismiss()
        self.btn_input_doc_name.text = name
        doc_name = ''.join(c for c in name.split('.')[0] if c.isalpha())
        if log: print(doc_name)
        if doc_name.capitalize() in self.shops:
            self.btn_select_shop.text = doc_name
        elif 'check' in doc_name or 'WB' in ''.join(c for c in name.split('.')[1] if c.isalpha()):
            self.btn_select_shop.text = 'Чек'
        if self.btn_input_doc_name.text.split('.')[1] == 'WB':
            if log: print(self.tea_checks)
            self.temp = self.tea_checks[int(name.split('.')[0])]
            self.doc = self.tea_checks[int(name.split('.')[0])]['items']

    # Пустая функция
    def pass_(self, window, key, *args):
        logging.info('ИНТЕРФЕЙС: pass_')
        pass

    # Переключатель режима автокликера
    def func_switch_version(self, instance):
        logging.info('ИНТЕРФЕЙС: func_switch_version')
        if ((self.switch_name.active and self.switch_type.active and self.switch_count.active == False and self.switch_cost.active == False) or
                (self.switch_count.active and self.switch_cost.active and self.switch_name.active == False and self.switch_type.active == False)):
            self.switch_name.active = (False if self.switch_name.active else True)
            self.switch_header.active = False
            self.switch_type.active = (False if self.switch_type.active else True)
            self.switch_count.active = (False if self.switch_count.active else True)
            self.switch_cost.active = (False if self.switch_cost.active else True)
        else:
            self.switch_name.active = True
            self.switch_header.active = True
            self.switch_type.active = True
            self.switch_count.active = False
            self.switch_cost.active = False

    # Запуск парсера чеков Wildberries
    def wb_parse(self, instance):
        logging.info('ИНТЕРФЕЙС: wb_parse')
        def sort_():
            self.date = MDTextField(hint_text="Дата",
                                    helper_text_mode="on_focus", helper_text="Последний чек, в формате: 31.01.2024",
                                    size_hint_x=None, width='120dp',
                                    halign='left',
                                    on_text_validate=self.func_dialog_enter,
                                    text_color_focus=self.color_acent_1, line_color_focus=self.color_acent_2,
                                    hint_text_color_focus=self.color_acent_2)

            self.token = MDTextField(text=base_get()[0] if base_get() is not None else '',
                                     hint_text="Токен",
                                     helper_text_mode="on_focus", helper_text="Просто вставь сюда токен",
                                     size_hint_x=None, width=240,
                                     halign='left',
                                     on_text_validate=self.func_dialog_enter, text_color_focus=self.color_acent_1,
                                     line_color_focus=self.color_acent_2, hint_text_color_focus=self.color_acent_2)

            self.token_btn = RFIB(icon='key', text="Авторизоваться",
                                  on_release=lambda x: self.wb_replace_widget(new_widget=self.token),
                                  size_hint_y=None, height='160dp', text_color='#8D297F', icon_color='#8D297F',
                                  line_color=self.color_acent_2, font_size=18)

            self.get_item = RFB(text="Получить чеки",
                                on_release=self.wb_get,
                                halign="right",
                                text_color=self.color_acent_1, line_color=self.color_acent_2)

            self.save = RFB(text="Сохранить",
                            on_release=self.wb_save,
                            halign="left",
                            text_color=self.color_acent_1, line_color=self.color_acent_2)

            self.verify = MDLabel(halign="center", size_hint_x=None,
                                  theme_text_color='Custom', text_color=self.color_acent_1)
            # Наполнение верхнего меню
            with open('Wildberries_database.txt', 'r'):
                if base_get() is None:
                    self.verify.text = 'Введите данные в форму ниже!'
                else:
                    self.verify.text = 'Подключено!'

            date_text = base_get()[1].split('T')[0].split('-') if base_get() is not None else ''
            date_text = date_text[2] + '.' + date_text[1] + '.' + date_text[0] if base_get() is not None else ''
            self.date.text = date_text
            self.token.bind(focus=self.wb_on_focus)
            self.date.bind(focus=self.wb_on_focus2)

            if WB_Pars.auth(self.token.text).ok:
                self.token_btn.text = 'Подключено!'
            else:
                self.token_btn.text = 'Авторизоваться!'

            # Верхнее меню - Лэйауты
            self.layout_top_wb = MDBoxLayout(orientation='vertical')
            for i in (self.token_btn, self.date, self.save):
                self.layout_top_wb.add_widget(i)
            self.layout_top_wb.size_hint_y = None
            self.layout_top_wb.bind(minimum_height=self.layout_top_wb.setter('height'))

            # Общее наполнение лэйаутов
            layout_buttons = MDBoxLayout(orientation='horizontal', )
            layout_buttons.add_widget(MDLabel())
            layout_buttons.add_widget(self.get_item)
            layout_buttons.size_hint_y = None
            layout_buttons.bind(minimum_height=layout_buttons.setter('height'))

            layout_main = MDBoxLayout(orientation='vertical', md_bg_color=self.color_background_start)
            layout_verify = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=20)
            layout_verify.add_widget(MDLabel())

            for i in (layout_verify, self.layout_top_wb, layout_buttons):
                layout_main.add_widget(i)

            layout_main.size_hint_y = None
            layout_main.bind(minimum_height=layout_main.setter('height'))
            self.layout_menu = MDBoxLayout(orientation='vertical', size_hint_y=None, height=500)
            self.layout_menu.add_widget(layout_main)
            self.layout_middle = ScrollView(size_hint=(1, 1), pos_hint={'center_x': .5, 'center_y': .5},
                                            do_scroll_x=False)
            self.layout_menu.add_widget(self.layout_middle)
            return self.layout_menu

        self.dialog_wb = MDDialog(title='Чеки WildBerries', type="custom", content_cls=sort_(),
                                  md_bg_color=self.color_background_start)
        self.dialog_wb.open()

    def wb_on_focus(self, value, instance):
        logging.info('ИНТЕРФЕЙС: wb_on_focus')
        print('Значение вали')
        print(value.hint_text)
        print(instance)
        if not self.token.focus:  # Если фокус потерян
            self.wb_replace_widget(new_widget=self.token_btn)

    def wb_on_focus2(self, value, instance):
        pass

    def wb_replace_widget(self, new_widget):
        logging.info('ИНТЕРФЕЙС: wb_replace_widget')
        if new_widget.text not in ('Авторизоваться!', 'Подключено!'):
            if self.token.focus == False:
                self.token.focus = True
        else:
            if self.token.focus == True:
                self.token.focus = False

        self.layout_top_wb.clear_widgets()
        for i in (new_widget, self.date, self.save):
            self.layout_top_wb.add_widget(i)

    def wb_save(self, instance):
        logging.info('ИНТЕРФЕЙС: wb_save')
        date = self.date.text
        if len(date) == 10:
            if date[2] == '.' and date[5] == '.':
                date = date.split('.')
                if len(date[0]) == 2 and len(date[1]) == 2 and len(date[2]) == 4:
                    try:
                        if 32 > int(date[0]) > 0 and 13 > int(date[1]) > 0 and 2050 > int(date[2]) > 2023:
                            string = str(self.token.text) + '|' + f'{date[2]}-{date[1]}-{date[0]}T21:58:00.000'
                            if WB_Pars.auth(self.token.text).ok:
                                base_push(string)
                                self.verify.text = ''
                            else:
                                self.verify.text = 'Ошибка авторизации! Токен недействителен!'
                                if log: print(self.token.text)
                                if log: print(WB_Pars.auth(self.token.text).ok)
                                if log: print(WB_Pars.auth(self.token.text))
                        else:
                            self.verify.text = 'Указана несуществующая дата!'
                    except Exception as e:
                        self.verify.text = 'Указаны не только цифры в дате!'
                        if log: print(date)
                        if log: print(e)
                else:
                    self.verify.text = 'Длинна одного параметра даты не правильная!'
            else:
                self.verify.text = 'Не найдены точки!'
        else:
            self.verify.text = 'Длинна даты не правильная!'
        self.wb_replace_widget(new_widget=self.token_btn)

    def wb_get(self, instance):
        logging.info('ИНТЕРФЕЙС: wb_get')
        layout_receipts = MDBoxLayout(orientation='vertical', padding=20)
        layout_receipts.size_hint_y = None
        layout_receipts.bind(minimum_height=layout_receipts.setter('height'))
        if base_get() is not None:
            checks = WB_Pars.get_info(base_get()[0], base_get()[1])
            self.tea_checks = []

            if len(checks) > 0:
                ind_check = 0
                index_check_WB = 0
                remove_mass = []
                self.teafiles = []  # Удаление добавленых чеков
                for check in checks:  # Создание чеков
                    line = MDBoxLayout(md_bg_color=self.color_background_start, size_hint_y=None, height=30)
                    layout_receipt = MDBoxLayout(orientation='vertical', md_bg_color=self.color_list)
                    layout_info = MDBoxLayout(orientation='vertical', size_hint_y=None, height=60)
                    layout_itog = MDBoxLayout(orientation='horizontal')
                    layout_texts = MDBoxLayout(orientation='horizontal')

                    pos = 0
                    all_count = 0
                    all_price = 0
                    # Конвертация чая
                    for i in check['check']:
                        pos += 1
                        all_price += float(i['cтоимость'])
                        if i['название'].find('200') != -1:
                            name_tea = 'Чай 200шт.'
                            all_count += 200 * int(i['количество'])
                        elif i['название'].find('100') != -1:
                            name_tea = 'Чай 100шт.'
                            all_count += 100 * int(i['количество'])
                        else:
                            name_tea = str(i['название'].strip('                                            '))

                        one_receipt = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                        strings1 = {str(pos) + '. ': 'right', name_tea: 'left',
                                    '     ' + str(i['цена за шт']) + ' Х ' + str(i['количество']) + ' = ': 'right',
                                    str(''.join(i['cтоимость'].split(' '))): 'left'}
                        for i2 in strings1:
                            one_receipt.add_widget(MDLabel(text=i2, halign="right", size_hint_x=None))
                        layout_receipt.add_widget(one_receipt)

                    strings_texts = {'': 'left', 'Название:': 'left', 'Цена:': "right", 'Количество:': "center",
                                     'Сумма:': "left"}
                    strings_itog = {'Всего: ': 'right', (str(all_count) + 'шт.'): 'left', '': 'right',
                                    'Итого: ': 'right', str(all_price) + '₽': 'left'}

                    for i2 in (str(check['date']) + '    ', str(check['number']) + '    '):
                        layout_info.add_widget(MDLabel(text=i2, halign="right", ))

                    for i2 in strings_texts:
                        layout_texts.add_widget(MDLabel(text=i2, halign=strings_texts[i2], size_hint_x=None))

                    for i2 in strings_itog:
                        layout_itog.add_widget(MDLabel(text=i2, halign=strings_itog[i2], size_hint_x=None))

                    layout_receipt.add_widget(layout_info)
                    layout_receipt.add_widget(layout_texts)

                    self.tea_checks.append(
                        {'date': 'T'.join(check['date'].strip('                        ').split(' ')),
                         'check': check['number'].strip('                        '),
                         'items': [{'id': 0, 'name': 'Чай пакетированный', 'cost': all_price,
                                    'count': all_count, 'sum': all_price, 'type': 'шт'}]})
                    self.teafiles.append(f'{ind_check}.WB')

                    # Нормализация размеров лайаутов
                    layout_receipt.size_hint_y = None
                    layout_receipt.bind(minimum_height=layout_receipt.setter('height'))
                    layout_texts.size_hint_y = None
                    layout_texts.bind(minimum_height=layout_receipt.setter('height'))
                    layout_itog.size_hint_y = None
                    layout_itog.bind(minimum_height=layout_receipt.setter('height'))

                    layout_receipt.add_widget(layout_itog)
                    layout_receipts.add_widget(layout_receipt)
                    layout_receipts.add_widget(line)
                    ind_check += 1
            else:
                layout_receipts.clear_widgets()
                layout_receipts.add_widget(MDLabel(text='Незаведёных чеков нет!'))
        else:
            layout_receipts.clear_widgets()
            layout_receipts.add_widget(MDLabel(text='Сначала вам нужно указать токен и дату!'))

        self.layout_middle.clear_widgets()
        self.layout_middle.add_widget(layout_receipts)
        self.layout_menu.remove_widget(self.layout_middle)
        self.layout_menu.add_widget(self.layout_middle)


# Используем эту функцию для запуска цикла событий Kivy с интеграцией asyncio
def run_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Запускаем цикл событий Kivy
    async_run = asyncio.ensure_future(asyncio.gather(BotiIko().async_run(async_lib='asyncio')))
    # Планируем остановку цикла, когда Kivy App закроется
    async_run.add_done_callback(lambda *args: loop.stop())

    # Запускаем цикл событий asyncio
    loop.run_forever()


if __name__ == "__main__":
    run_async()
