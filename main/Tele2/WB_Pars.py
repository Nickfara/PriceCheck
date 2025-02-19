link_receipts = 'https://www.wildberries.ru/webapi/lk/receipts/data?count=80'
last_date_g = '2024-1-30T21:58:00.000'
token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDY3ODE3OTIsInZlcnNpb24iOjIsInVzZXIiOiIxNDM2NzY0MyIsInNoYXJkX2tleSI6IjEyIiwiY2xpZW50X2lkIjoid2IiLCJzZXNzaW9uX2lkIjoiNGRjMThhMWEzMGJkNDZmYThmNTQyZWIzOWM3MTk3ZDUiLCJ1c2VyX3JlZ2lzdHJhdGlvbl9kdCI6MTY3NDIxNzc0MiwidmFsaWRhdGlvbl9rZXkiOiI2NTYwMzU3OTYxYzY1MWY0NjEyZmQwY2EwMDIzZTE3ZjEwMWRkMWQ3YmYzMjY4MDZlN2Q0OTk2OTQzYzcyNjQ2IiwicGhvbmUiOiJzS0xlMXBEcTJJZDZBWW4vYjl1aW1RPT0ifQ.k2TTVOgllzbx_uJc7TfyhntmfHsjD4-L5bn_Affj4CVzG1XwUUWOQg2cG59k09B6v_HLEL1YYFECoVfJ-bqaY7e78YRE6VjLzNvoZWKtgj7lEKbuquOtmZ-tKtI5jO-8hUak3-rMh0jSHvjYoVamg7ymwB-llDbjoqd5Uu0E6ubmXAmXmYkCu68Nud3tuxXFsCB63q9163HvawgEyrbfLnpvT_3oAanJHkO2RTA58RddYqD-7YKIVxnpytK4pShw8ga_plvH-eN1IkrTfyH9mgBqtXK_d29PT9q28FgneslIw66LMde9Oog8idc1b0ygvb9g2Ff61siMw8vsqcDTPA'
from log import log


def get_info():
    print('Ожидайте примерно 15 секунд!')
    import requests
    import datetime
    from bs4 import BeautifulSoup

    last_date = datetime.datetime.strptime(last_date_g, '%Y-%m-%dT%H:%M:%S.%f')

    def errors(response):
        if response.status_code == 200:
            return {'status': True, 'text': 'Успешно', 'response': response}
        elif response.status_code == 404:
            return {'status': False, 'text': 'Ошибка в ссылке api', 'response': response}
        elif response.status_code == 403:
            return {'status': False, 'text': 'Ошибка запроса', 'response': response}
        elif response.status_code == 401:
            return {'status': False, 'text': 'Ошибка авторизации', 'response': response}
        else:
            return {'status': False, 'text': response.json()['meta']['message'], 'response': response}

    def api(link, get_status):
        s = requests.Session()  # Создание сессии
        s.headers.update(
            {'User-Agent': 'okhttp/5.3.1'})  # Заголовок с данными
        s.headers.update({'Authorization': 'Bearer {}'.format(token)})
        if get_status == 1:
            response = s.get(link)
        else:
            response = s.post(link)

        # response = errors(response)
        try:
            return response.json()
        except:
            return response

    receipts = api(link_receipts, 0)['value']['data']['receipts']

    new_receipts = []
    for i in receipts:
        date = datetime.datetime.strptime(i['operationDateTime'], '%Y-%m-%dT%H:%M:%S.%f')
        if date > last_date:
            new_receipts.append(i['link'])

    def html_to_dict(response):
        base = []
        soup = BeautifulSoup(response.text, "html.parser")
        c_number = 'products-cell products-cell_number'
        c_name = 'products-prop-value'
        c_price = 'products-cell products-cell_price'
        c_price_all = 'products-cell products-cell_cost'
        c_count = 'products-cell products-cell_count'

        name = soup.findAll('div', class_=c_name)
        filtered_name = []
        for data in name:
            if data.find('div', class_='products-prop-value') is not None:
                filtered_name.append(data.text.split('\n')[1])

        price = soup.findAll('div', class_=c_price)
        filtered_price = []
        for data in price:
            if data.find('div', class_='products-prop-value') is not None:
                filtered_price.append(data.text.split('\n')[1])

        price_all = soup.findAll('div', class_=c_price_all)
        filtered_price_all = []
        for data in price_all:
            if data.find('div', class_='products-prop-value') is not None:
                filtered_price_all.append(data.text.split('\n')[1])

        count = soup.findAll('div', class_=c_count)
        filtered_count = []
        for data in count:
            if data.find('div', class_='products-prop-value') is not None:
                filtered_count.append(data.text.split('\n')[1])

        i = 0
        last = len(filtered_name)
        while i < last:
            if filtered_name[i].lower().find('чай') != -1:
                base.append(
                    {'название': filtered_name[i], 'цена за шт': filtered_price[i], 'количество': filtered_count[i],
                     'cтоимость': filtered_price_all[i], })
            i += 1
        date = str(soup.findAll('div', class_='check-header-column gray')).split('\n')
        tea_info.append(date[1])
        tea_info.append(date[4])
        return base

    tea_receipts = []
    for i in new_receipts:
        response = api(i, 1)
        tea_check = response.text.lower().find('чай')

        if tea_check != -1:
            tea_info = []
            check = html_to_dict(response)
            tea_receipts.append({'check': check, 'date': tea_info[0].split('<')[0], 'number': tea_info[1]})
    return tea_receipts


checks = get_info()
if len(checks) > 0:
    for check in checks:
        print(
            '\n\n______________________________________________________________________________________________________')
        print('_______________________________________________________________________________________________________')
        print(check['number'])
        print(check['date'])
        pos = 0
        for i in check['check']:
            if True:
                pos += 1
                print('Позиция: ' + str(pos))
                print('Название: ' + str(i['название'].strip('                                            ')))
                print('Цена за шт: ' + str(i['цена за шт']))
                print('Количество: ' + str(i['количество']))
                print('Стоимость: ' + str(i['cтоимость']))
                print('\n_________________')
else:
    print('Незаведёных чеков нет!')
