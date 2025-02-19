import sqlite3
from log import log


def connect():
    """
    Осуществление подключения к базе данных.

    :return: Открытая база данных
    """
    conn = sqlite3.connect('data/taxi_prices.db')
    conn.row_factory = sqlite3.Row
    return conn


def create():
    """
    Создание таблицы.
    :return:
    """
    connection = connect()
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Prices (
        ts TEXT,
        to_price TEXT,
        from_price TEXT,
        to_wait TEXT,
        from_wait TEXT,
        to_duration TEXT,
        from_duration TEXT
        )
        ''')
    connection.commit()
    connection.close()


def clear():
    """
    Полная очистка базы от всех данных.
    :return: Отсутствует.
    """
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Prices")
    connection.commit()
    connection.close()


def add(cost):
    """
    Добавление строки с новыми данными о цене.

    :param cost: Словарь содержащий в себе данные (Время, цена, ожидание водителя, длительность поездки) о поездке из дома до работы и обратно.
    :return: Возвращение логического значения об исходе операции.
    """
    result = False
    conn = connect()

    if isinstance(cost, dict) and len(cost) == 7:
        conn.execute(
            'INSERT INTO Prices (ts, to_price, from_price, to_wait, from_wait, to_duration, from_duration) VALUES (?, ?, ?, ?, ?, ?, ?)',
            ([*cost.values()]))
        conn.commit()
        conn.close()
        result = True
    return result


def get():
    """
    Получение списка всех поездок из базы данных

    :return: Возвращение списка данных о всех поездках из базы
    """
    conn = connect()
    item_row = conn.execute('SELECT * FROM Prices')  # Получение из базы row списка строк в форматах row
    item_get = item_row.fetchall()
    item_return = []
    for cost in item_get:
        res_item = {
            "ts": cost['ts'],
            "to_price": int(float(cost['to_price'])),
            "from_price": int(float(cost['from_price'])),
            "to_wait": int(float(cost['to_wait'])),
            "from_wait": int(float(cost['from_wait'])),
            "to_duration": int(float(cost['to_duration'])),
            "from_duration": int(float(cost['from_duration'])),
        }  # Трансформирование row объекта в словарь
        item_return.append(res_item)  # Пополнение списка готовым объектом из базы
    conn.close()
    return item_return
