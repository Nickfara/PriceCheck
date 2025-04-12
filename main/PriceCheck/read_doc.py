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

    :param filename:
    :return:
    """
    file_formate = filename.split('.')[1]
    path = 'data/prices/' + str(filename)

    try:
        with open(path, encoding='utf-8'):
            pass
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

    :return:
    :param workbook:
    :return:
    """
    items = []
    sid = False
    seller = False
    end_time = 0
    for i in data['shops']:
        for i2 in workbook.sheets():
            worksheet = workbook.sheet_by_index(workbook.sheets().index(i2))
            findname = str(worksheet.cell_value(i['findname'][0], i['findname'][1])).lower()
            if i['findtext'].lower() in findname:
                sid = i['sid']
                seller = i['seller']
                break

    if isinstance(sid, list):
        for i2 in workbook.sheets():
            worksheet = workbook.sheet_by_index(workbook.sheets().index(i2))
            for i in range(0, worksheet.utter_max_rows):  # Чтение строк
                item = {}
                try:
                    # Проверка наличия индексов
                    str(worksheet.cell_value(i, sid[0]))
                    str(worksheet.cell_value(i, sid[1]))
                    str(worksheet.cell_value(i, sid[2]))
                except IndexError:
                    if end_time == 5:
                        log(f'Конец документа. Страница: {i2}')
                        break
                    end_time += 1
                else:
                    item['name'] = str(worksheet.cell_value(i, sid[0]))
                    item['seller'] = seller
                    if item['name'] != 'None':
                        end_time = 0
                    item['name'] = ''.join(item['name'].split(','))  # Удаление запятых из названия
                    item['cost'] = str(worksheet.cell_value(i, sid[1]))
                    if sid[2] != -1:
                        item['type'] = str(worksheet.cell_value(i, sid[2]))
                    else:
                        item['type'] = ''

                    if item['cost'] == '' or item['cost'] is None:
                        item['cost'] = 'категория'
                    else:
                        items.append(item)
    else:
        items = False
        error_text = 'Не найдено имя поставщика в таблице!'
        log(error_text, 3)

    return items


# noinspection PyBroadException
def xlsx(workbook):
    """

    :param workbook:
    :return:
    """
    sheet_names = workbook.sheetnames
    items = []
    sid = False
    seller = False
    type_n = None

    end_time = 0
    for i in data['shops']:
        for i2 in sheet_names:
            worksheet = workbook[i2]
            try:
                findname = str(worksheet[h[i['findname'][0]]][i['findname'][1]].value).lower()
                if i['findtext'].lower() in findname:
                    sid = (h[i['sid'][0]], h[i['sid'][1]])
                    seller = i['seller']
                    type_n = i['sid'][2]
                    break
            except IndexError as e:
                log(e, 2)
                log(i, 2)

    if isinstance(sid, list):
        for i2 in sheet_names:
            worksheet = workbook[i2]
            for i in range(0, 1000):  # Чтение строк
                item = {}
                try:
                    # Проверка наличия индексов
                    str(worksheet[f'{sid[0]}'][i].value)
                    str(worksheet[f'{sid[1]}'][i].value)
                    str(worksheet[f'{sid[2]}'][i].value)
                except IndexError:
                    if end_time == 5:
                        item['seller'] = seller
                        break
                    end_time += 1
                else:
                    name = str(worksheet[f'{sid[0]}'][i].value)
                    cost = str(worksheet[f'{sid[1]}'][i].value)

                    if 'мороженое' in str(name).lower():
                        break

                    item['seller'] = seller
                    item['name'] = str(name)

                    if item['name'] != 'None':
                        end_time = 0

                    item['name'] = ''.join(item['name'].split(','))  # Удаление запятых из названия

                    try:
                        item['cost'] = cost
                    except:
                        item['cost'] = ''

                    if type_n != -1:
                        try:
                            item['type'] = str(worksheet[f'{sid[2]}'][i].value)
                        except:
                            item['type'] = 'хз'
                    else:
                        item['type'] = ''

                    if item['cost'] == '':
                        item['cost'] = 'категория'

                    items.append(item)
    else:
        items = False
        error_text = '\033[31m\033[1mНе найдено имя поставщика в таблице!'
        log(error_text, 3)
    return items


def filter_names(name:str = ''):
    """

    :param name:
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


def scanner(name: str = ''):
    """

    :param name:
    :return:
    """
    name = str(name)
    items = []
    result = {'cache': []}

    for file in data['shops']:
        if file['filename'] in os.listdir('data/prices'):
            table = read(file['filename'])
            from PriceCheck.create_csv import converting
            converting(table)
            if table:
                for i in table:
                    items.append(i)

    for i in items:
        if name.lower() in i['name'].lower():
            i["name"] = filter_names(i["name"])

            if i['name']:
                result['cache'].append(i)

    def key(price):
        """

        :param price:
        :return:
        """
        try:
            return float(price['cost'])
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

    return result

scanner()