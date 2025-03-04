import requests

s = requests.Session()  # Создание сессии
s.headers.update({'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными

data = {"client_id": "digital-suite-web-app", "grant_type": "password", "username": '79920228848',
        "password": '649UPY',
        "password_type": "password", }  # Данные для авторизации

response = s.post('https://ekt.t2.ru/aufth/realms/tele2-b2c', data=data)

print(response)
print(dir(response))
print(response.json())