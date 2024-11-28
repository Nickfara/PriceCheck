import asyncio
import json

from kivymd.uix.snackbar import MDSnackbar



def str_to_dict(text):
    text = str(text)
    new = ''.join((''.join(''.join(text.split('{')).split('}')).split("'")))
    new = new.split(', ')
    end = {}
    for i in new:
        data = i.split(': ')
        if len(data) == 2:
            end[data[0]] = data[1]
    return end
def str_to_list(text):
    text = str(text)
    list_ = []
    new = ''.join((''.join(''.join(text.split('[')).split(']')).split("'")))
    new = new.split(', ')
    end = {}
    for i in new:
        data = i.split(', ')
        if len(data) == 2:
            end[data[0]] = data[1]
    return end

def finder(text, items):
    text = text.split(' ')
    finded_items = []
    first_word = True
    for word in text:
        if word != '':
            if first_word:
                for item in items:
                    if word.lower() in item['name'].lower():
                        finded_items.append(item)
                first_word = False
            else:
                finded_items_temp = []
                for item in finded_items:
                    if word.lower() in item['name'].lower():
                        finded_items_temp.append(item)
                finded_items = finded_items_temp


    return finded_items


active_bot = [False]

async def start_telegram(self, telegram):
    loop = asyncio.get_event_loop()
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor()
    def start():
        if active_bot[0] == False:
            self.send_files.text = 'Остановить бота'
            self.send_files.icon = 'stop_circle_outline'
            active_bot[0] = True
            print('Телеграм бот запущен!')
            telegram.start()
            print('Телеграм бот закончил свою работу!')
            self.send_files.text = 'Запустить бота'
            self.send_files.icon = 'download'
            active_bot[0] = False
        else:
            telegram.exit('Выход')
            self.send_files.text = 'Запустить бота'
            self.send_files.icon = 'download'

            active_bot[0] = False

    await loop.run_in_executor(executor, start)

async def background_load(self, parse_metro):
    loop = asyncio.get_event_loop()
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor()

    def start():
        print('Авторизация MSHOP началась!')
        parse_metro.auth_check()
        print('Авторизация MSHOP закончилась!')

        self.activate_enter_finder(self)
        print('Активация энтером включена!')

        print('Кэширование базы началось!')
        from read_doc import scanner
        self.base_price = scanner('')
        print('Кэширование базы закончилось!')


    await loop.run_in_executor(executor, start)


async def send_to_cart(item, parse_metro):
    loop = asyncio.get_event_loop()
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor()
    def start():
        print(f'Добавляем товар {item["name"]} в корзину!')
        parse_metro.add_cart(item)

    await loop.run_in_executor(executor, start)

async def remove_from_cart(item, parse_metro):
    loop = asyncio.get_event_loop()
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor()

    def start():
        print(f'Удаляем товар {item["name"]} из корзины!')
        parse_metro.remove_cart(item)

    await loop.run_in_executor(executor, start)


def get_cart():
    with open('cookies_mshop.json', 'r') as f:
        cart = json.load(f)
        return cart['cart']

def add_cart(item):
    cart = get_cart()
    cart.append(item)
    with open('cookies_mshop.json', 'w') as f:
        json.dump(cart, f)
        return True

def remove_cart(item):
    cart = get_cart()
    cart.remove(item)

    with open('cookies_mshop.json', 'w') as f:
        json.dump(cart, f)
        return True
