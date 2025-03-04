import sqlite3


# Функция для создания соединения с базой данных с row
def get_db_connection():
    conn = sqlite3.connect('data/t2.db')
    conn.row_factory = sqlite3.Row
    return conn


# Функция для создания соединения с базой данных без row
def get_db_connection2():
    conn = sqlite3.connect('data/t2.db')
    return conn


# Функция для получения пользователя по идентификатору
def get_user(user_id):
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM Users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    if user_row:
        # Преобразуем sqlite3.Row в словарь
        user_dict = dict(user_row)
        return user_dict
    else:
        return None


# Функция для создания нового пользователя
def create_user(user_id, auth_login='', auth_password='', status_autosell=0, status_autotop=0, status_lagg=0,
                status_sms=0, stage_autorize=0, lvl_autorize=0, lvl_setting=0, lvl_redactor=0, security_code='',
                security_code_token=''):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO Users (id, status_sms, stage_autorize, lvl_autorize, lvl_setting, lvl_redactor, security_code, security_code_token) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (user_id, status_sms, stage_autorize, lvl_autorize, lvl_setting, lvl_redactor, security_code,
         security_code_token))
    conn.commit()
    conn.close()


# Функция для обновления данных пользователя
def update_users(users):
    DB = get_user(users['id'])
    conn = get_db_connection2()
    cursor = conn.cursor()
    users = [users]
    for user in users:
        # Получаем текущие значения из базы данных
        # cursor.execute('SELECT * FROM Users WHERE id = ?', (str(user['id']),))
        # current_values = cursor.fetchone()
        current_values = DB
        # Обновляем только те значения, которые переданы в user
        update_values = {key: user.get(key, current_values[key]) for key in current_values.keys()}
        # Создаем строку с метками для параметров
        update_query = """
           UPDATE Users
           SET id = ?,
               auth_login = ?,
               auth_password = ?,
               username = ?,
               status_sms = ?,
               stage_autorize = ?,
               lvl_autorize = ?,
               lvl_setting = ?,
               lvl_redactor = ?, 
               config_type = ?,
               config_uom = ?,
               config_count = ?,
               config_price = ?,
               config_emojis = ?,
               config_autotime = ?,
               config_repit = ?,
               token = ?,
               list_lots = ?,
               security_code = ?,
               security_code_token = ?
           WHERE id = ?
        """

        # Создаем кортеж из значений параметров
        values = tuple(update_values[key] for key in update_values.keys()) + (user['id'],)
        # Выполняем запрос с параметрами
        cursor.execute(update_query, values)

    conn.commit()
    conn.close()


# Функция для удаления пользователя
def delete_user(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Users WHERE id = ?', (user_id,))
    conn.commit()  # Необходимо зафиксировать изменения
    conn.close()
