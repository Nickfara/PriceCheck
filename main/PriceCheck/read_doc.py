"""
    Чтение документов EXEL
"""
import json
import os

from openpyxl import load_workbook as open_xlsx
from xlrd import open_workbook as open_xls

from log import log

# !/usr/bin/env python # -* - coding: utf-8-* -

with open('data/config.json', encoding='utf-8') as f:
    data = json.load(f)

h = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
     "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE",
     "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR",
     "AS", "AT", "AU", "AV", "AW", "AX", "AY", "AZ"]


def read(filename):  # Чтение таблицы
    """
    Открытие документа.

    :param filename: Имя файла.
    :return: Список прочитанных товаров
    [{'name': 'Наименование', 'cost': 'Цена', 'type': 'Вид фасовки', 'seller': 'Название поставщика'}, ...]
    """

    file_formate = filename.split('.')[1]
    path = 'data/prices/' + str(filename)

    try:
        with open(path, encoding='utf-8'):
            log(f'Файл "{filename}" найден!')
    except FileNotFoundError:
        response = False
        log(f'Файл "{filename}" не найден!', 2)
    else:
        if file_formate == 'xls':  # Чтение xls
            workbook = open_xls(path)
            log(f'Начало сканирования файла: {filename}')
            response = xls(workbook)
        elif file_formate == 'xlsx':  # Чтение xlsx
            workbook = open_xlsx(path)
            log(f'Начало сканирования файла: {filename}')
            response = xlsx(workbook)
        else:
            response = False  # Формат файла неверный
            error_text = 'Неверный формат файла.'
            log(error_text, 3)

    return response


def xls(workbook):
    """
    Сканирование документа в формате: .xls

    :param workbook: Лист excel
    :return: Список прочитанных товаров
    [{'name': 'Наименование', 'cost': 'Цена', 'type': 'Вид фасовки', 'seller': 'Название поставщика'}, ...]
    """
    items = []
    price_w = False
    product_name_w = False
    packaging_w = False
    title = False
    end_time = 0

    for shop in data['shops_params']:
        for param in workbook.sheets():
            worksheet = workbook.sheet_by_index(workbook.sheets().index(param))
            dist_text = str(worksheet.cell_value(shop['dist_w'], shop['dist_h'])).lower()
            if shop['dist_text'].lower() in dist_text:
                price_w = shop['price_w']
                product_name_w = shop['product_name_w']
                packaging_w = shop['packaging_w']
                title = shop['title']
                break

    if title:
        for sheet in workbook.sheets():
            worksheet = workbook.sheet_by_index(workbook.sheets().index(sheet))
            for line in range(0, worksheet.utter_max_rows):  # Чтение строк
                item = {}
                try:
                    # Проверка наличия индексов
                    str(worksheet.cell_value(line, price_w))
                    str(worksheet.cell_value(line, product_name_w))
                    str(worksheet.cell_value(line, packaging_w))
                except IndexError:
                    if end_time == 5:
                        log(f'Конец документа. Страница: {sheet}')
                        break
                    end_time += 1
                else:
                    item['product_name'] = str(worksheet.cell_value(line, product_name_w))
                    item['title'] = title

                    if item['product_name'] != 'None':
                        end_time = 0

                    item['product_name'] = ''.join(item['product_name'].split(','))  # Удаление запятых из названия
                    item['price'] = str(worksheet.cell_value(line, price_w))
                    if packaging_w != -1:
                        item['packaging'] = str(worksheet.cell_value(line, packaging_w))
                    else:
                        item['packaging'] = ''

                    if item['price'] == '' or item['price'] is None:
                        item['price'] = 'категория'
                    else:
                        items.append(item)
    else:
        log('Не найдено имя поставщика в таблице!', 3)

    return items


# noinspection PyBroadException
def xlsx(workbook):
    """
    Сканирование документа в формате: .xlsx

    :param workbook: Лист excel
    :return: Список прочитанных товаров
    [{'name': 'Наименование', 'cost': 'Цена', 'type': 'Вид фасовки', 'seller': 'Название поставщика'}, ...]
    """

    sheet_names = workbook.sheetnames
    items = []
    price_w = False
    product_name_w = False
    packaging_w = False
    title = False
    end_time = 0

    for shop in data['shops_params']:
        for sheet in sheet_names:
            worksheet = workbook[sheet]
            print(f'Shop БЛЯДЬ:   {shop}')
            try:
                dist_text = str(worksheet[h[shop['dist_w']]][shop['dist_h']].value).lower()
                if shop['dist_text'].lower() in dist_text:
                    price_w = shop['price_w']
                    product_name_w = shop['product_name_w']
                    packaging_w = shop['packaging_w']
                    title = shop['title']
                    break
            except IndexError as e:
                log(e, 2)
                log(shop, 2)

    if title:
        for sheet in sheet_names:
            worksheet = workbook[sheet]
            for line in range(0, 1000):  # Чтение строк
                item = {}
                try:
                    # Проверка наличия индексов
                    str(worksheet[f'{price_w}'][line].value)
                    str(worksheet[f'{product_name_w}'][line].value)
                    str(worksheet[f'{packaging_w}'][line].value)
                except IndexError:
                    if end_time == 5:
                        item['title'] = title
                        break
                    end_time += 1
                else:
                    product_name = str(worksheet[f'{product_name_w}'][line].value)
                    price = str(worksheet[f'{price_w}'][line].value)

                    if 'мороженое' in str(product_name).lower():
                        break

                    item['title'] = title
                    item['product_name'] = str(product_name)

                    if item['product_name'] != 'None':
                        end_time = 0

                    item['product_name'] = ''.join(item['product_name'].split(','))  # Удаление запятых из названия

                    try:
                        item['price'] = price
                    except:
                        item['price'] = ''

                    if packaging_w != -1:
                        try:
                            item['packaging'] = str(worksheet[f'{packaging_w}'][line].value)
                        except:
                            item['packaging'] = 'хз'
                    else:
                        item['packaging'] = ''

                    if item['price'] == '':
                        item['price'] = 'категория'

                    items.append(item)
    else:
        items = False
        error_text = '\033[31m\033[1mНе найдено имя поставщика в таблице!'
        log(error_text, 3)
    return items


def filter_names(name: str = ''):
    """
    Фильтрация наименований, с целью приведения отличающихся имён одинаковых товаров к единому формату.
    :param name: Наименование товара.
    :return:
    """
    name = str(name).lower()
    base = {
        'куриное': ('цб', 'цыпленка-бройлеров', 'цыпленка бройлера', 'цыпленка'),
        'филе грудки': ('филе  грудки',),
        'грудки куриное': ('кур.грудки',)
    }

    all_check = {}
    find_type = None
    name_ = name

    for i in base:
        for i2 in base.keys():
            all_check[i2] = i  # Наполнение всех вариантов замен

    for i in all_check:
        if i in name:
            find_type = all_check[i]
            break

    if find_type:
        back_list = base[find_type]
        new = find_type

        if type(back_list) not in (list, tuple):
            return name.capitalize()

        for i in back_list:
            if i in name:
                name_ = new.join(name.split(i))
                name_ = name_.capitalize()
                break

    return name_


def scanner():
    """
    Сканирование документов excel.

    :return: Словарь {'cache': [Список товаров]}
    """

    items = []
    result = {'cache': []}
    for file in data['shops_params']:  # Итерация по поставщикам
        print(f'Файл типа того: {file}')
        if file['filename'] in os.listdir('data/prices'):  # Проверка наличия документа с прайс-листом.
            table = read(file['filename'])  # Сканирование документа.

            if table:  # Проверка на успешность сканирования.
                for i in table:  # Итерация по строкам в документе
                    items.append(i)  # Пополнение списка с товарами.

    for item in items:  # Итерация по списку товаров.
        item["product_name"] = filter_names(item["product_name"])  # Фильтр названий

        if item['product_name']:  # Проверка успешности фильтрации
            result['cache'].append(item)  # Пополнение итогового списка.

    def key(price):
        """
        Конвертирование прайса в тип float.

        :param price: Либо конвертированная цена в тип float, либо 0
        :return:
        """
        try:
            return float(price['price'])
        except TypeError:
            return 0
        except KeyError:
            return 0
        except ValueError:
            return 0

    result['cache'].sort(key=key)

    with open('data/cache_prices.json', 'w', encoding='utf-8') as file:
        # noinspection PyTypeChecker
        json.dump(result, file)
        log('Сохранение прайса в кэш.')

    print(f'Сканирование документов завершено успешно вроде как, сам смотри: {result}')
    return result
