import requests

s = requests.Session()  # Создание сессии
s.headers.update({'Tele2-User-Agent': 'mytele2-app/5.11.0', 'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными


#s.headers.update(SECURITY_BYPASS_HEADERS)

#response = s.get('https://ekt.t2.ru/api/cart?siteId=siteEKT')

#print(response)

response = s.post('https://ekt.t2.ru/api/validation/number/79923415301', json={'sender': 'Tele2'})

print(response)
