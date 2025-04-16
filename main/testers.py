import requests

s = requests.Session()  # Создание сессии
s.headers.update({'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными



response = s.post('https://ekt.t2.ru/api/validation/number/79923415301', json={'sender': 'Tele2'})

print(response)
