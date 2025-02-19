import sqlite3
from log import log

# Устанавливаем соединение с базой данных
connection = sqlite3.connect('data/t2.db')
cursor = connection.cursor()

# Создаем таблицу Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id TEXT,
auth_login TEXT,
auth_password TEXT,
username TEXT,
status_sms INTEGER,
stage_autorize INTEGER,
lvl_autorize INTEGER,
lvl_setting INTEGER,
lvl_redactor INTEGER,
config_type TEXT,
config_uom TEXT,
config_count TEXT,
config_price TEXT,
config_emojis TEXT,
config_autotime TEXT,
config_repit TEXT,
token TEXT,
list_lots TEXT,
security_code TEXT,
security_code_token TEXT
)
''')

# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()
