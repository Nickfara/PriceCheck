import sqlite3
log = False

# !/usr/bin/env python # -* - coding: utf-8-* -
# Соединение с row
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Соединение без row
def get_db_connection2():
    conn = sqlite3.connect('database.db')
    return conn


# Получения товара по названию
def get_item(item=None):
    conn = get_db_connection()
    if type(item) is str:
        user_row = conn.execute('SELECT * FROM Items WHERE item = ?', (item.lower(),)).fetchone()
        conn.close()
        if user_row:
            # Преобразуем sqlite3.Row в словарь
            user_dict = dict(user_row)
            return user_dict
        else:
            return False
    else:
        item_row = conn.execute('SELECT * FROM Items')
        item_get = item_row.fetchall()
        item_return = {}
        for x in item_get:
            item_return[dict(x)['item']] = dict(x)['names']
        conn.close()
        return item_return


# Получения товара по наименованию
def get_item_names(name=None):
    conn = get_db_connection()
    if type(name) is str:
        name = name.lower()
        user_row = conn.execute("SELECT * FROM Items WHERE names LIKE ? OR names LIKE ? OR names LIKE ? OR names LIKE ?", (f'{name}', f'{name}///%', f'%///{name}', f'%///{name}///%')).fetchone()
        if log: print(user_row)
        conn.close()
        if user_row:
            # Преобразуем sqlite3.Row в словарь
            user_dict = dict(user_row)
            if log: print(user_dict)
            return user_dict
        else:
            return False
    else:
        return False


# Добавление товара
def add_item(item=None):
    if log: print('\033[44m')
    if log: print(f'Товар: {item}, добавляется!')
    items = get_item()
    if item not in items:
        if item != None:
            conn = get_db_connection()
            conn.execute('INSERT INTO Items (item) VALUES (?)', (item.lower(),))
            conn.commit()
            conn.close()
            return True
        else:
            return False
    else:
        return False
    if log: print('Запрос к базе завершен')
    if log: print('\033[0m')


# Обновления данных
def update_item(item=None, names=None, items=None):
    if type(item) is str and names is not None:
        conn = get_db_connection()
        conn.execute('UPDATE Items SET item = ?, names = ? WHERE item = ?', (item.lower(), names.lower(), item.lower()))
        conn.commit()
        conn.close()
        return True
    else:
        return False


# Удаление товара
def delete_item(item=None):
    if log: print('\033[44m')
    if item != None:
        conn = get_db_connection()
        conn.execute('DELETE FROM Items WHERE item = ?', (item.lower(),))
        conn.commit()
        conn.close()
        return True
    else:
        return False


# Удаление названий из товара
def clear_item(item=None, names=None):
    if log: print('\033[44m')
    if item != None:
        conn = get_db_connection()
        conn.execute('UPDATE Items SET item = ?, names = ? WHERE item = ?', (str(item).lower(), str(names).lower(), str(item).lower()))
        conn.commit()
        conn.close()
        return True
    else:
        return False


# Создание базы данных
def create_base():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Создаем таблицу Items
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Items (
    item TEXT,
    names TEXT
    )
    ''')

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()


# Устрочнение базы данных
def lowered_base():
    connection = get_db_connection()
    item_row = connection.execute('SELECT * FROM Items')
    item_get = item_row.fetchall()
    item_return = {}
    for x in item_get:
        item_return[dict(x)['item']] = dict(x)['names']
        item = dict(x)['item']
        names = dict(x)['names']
        if names != None:
            connection.execute('UPDATE Items SET names = ? WHERE item = ?', (names.lower(), item))
        if item != None:
            connection.execute('UPDATE Items SET item = ? WHERE item = ?', (item.lower(), item))
    connection.commit()
    connection.close()


lowered_base()

