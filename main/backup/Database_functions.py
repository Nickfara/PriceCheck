import db_connect as db

log = True
# !/usr/bin/env python # -* - coding: utf-8-* -

try:
    with open('Database_iIko_items.db') as f:
        pass
except:
    db.create_base()
    if log: print('База данных отсутствовала, поэтому была создана. Приложение закрылось.')
    exit()


def take_items(item=None):
    logging.info('ФУНК: take_items')
    items = db.get_item(item)
    if items == None:
        return ('Ошибка')
    return items


def add_item(item=None):
    logging.info('ФУНК: add_items')
    if log: print(item)
    if type(item) is str:
        db.add_item(item)


def clear_item(item=None):
    logging.info('ФУНК: clear_item')
    if log: print(item)
    if type(item) is str:
        db.clear_item(item=item)


def delete_item(item=None):
    logging.info('ФУНК: delete_item')
    if log: print(item)
    if type(item) is str:
        db.delete_item(item)


def update_items(item=None, name=None, items=None):
    logging.info('ФУНК: update_items')
    if log: print(f'Потому что item={item}, \nname={name}')
    if type(item) == dict:
        for key in item:
            item_names = items[key]
            item_item = key
    if log: print(f'item_names = {item_names}')
    if log: print(f'item_item = {item_item}')
    if item != None:
        if None not in [item_names, item_item]:
            if name is not None:
                if log: print('ЗАПУСК АПДЕЙТ БАЗЫ')
                names_list = item_names.split('///')
                if name['name'] not in names_list:
                    item_names += '///' + name['name']
                db.update_item(item_item, item_names, items)
        else:
            if log: print('Товар не имеет наименований!')
            if type(name) == list:
                name = ''
                for i in name:
                    name += '///' + i
                db.update_item(item_item, name, items)
            else:
                db.update_item(item_item, name['name'], items)
    else:
        if log: print('Объекта "' + item + '" нет в базе!')
        return False


def get_item(name=None):
    logging.info('ФУНК: get_item')
    if name is not None:
        if log: print('NAME IS A:')
        if log: print(name)
        name = name['name']
        item = db.get_item_names(name)
        if log: print('ПОИСК ОШИБКИ!!!')
        if log: print(name)
        if log: print(item)
        if item != False:
            return item
        else:
            return False
