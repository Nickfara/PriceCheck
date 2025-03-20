import json
import re
from colorama import Fore

from app.api import Tele2Api


def input_phone_number():
    while True:
        user_input = input(
            Fore.CYAN +
            f'Введите свой номер телефона Tele2 (оставьте пустое, чтобы отменить):'
        )
        if re.match(r'^7\d{10}?$', user_input):
            return user_input
        elif user_input == '':
            exit()
        else:
            print(Fore.RED + 'Неверный формат номера. Правильный - 7xxxxxxxxxx')


async def get_tokens(api: Tele2Api, phone_number: str):
    await api.send_sms_code()
    while True:
        try:
            sms_code = input(Fore.LIGHTCYAN_EX + 'SMS code: ')
            return await api.auth_with_code(phone_number, sms_code)
        except KeyError:
            print(Fore.RED + 'Неверный SMS-Код. Попробуйте еще раз')

async def get_tokens_s(api: Tele2Api, phone_number: str, password: str):
    await api.send_security_code()
    while True:
        try:
            sms_code = input(Fore.LIGHTCYAN_EX + 'SMS code: ')
            return await api.auth_with_password(phone_number, sms_code, password)
        except KeyError:
            print(Fore.RED + 'Неверный SMS-Код. Попробуйте еще раз')


def write_config_to_file(phone_number: str, access_token: str,
                         refresh_token: str):
    with open('config.json', 'w') as f:
        json.dump({
            'x-p': phone_number,
            'x-at': access_token,
            'x-rt': refresh_token,
        }, f, indent=2)
