"""
    Проверка на наличие обязательных файлов.
"""
import json
import os

from log import log

# noinspection SpellCheckingInspection
preset_config = {"shops": [
    {"filename": "\u041c\u0430\u0442\u0443\u0448\u043a\u0430.xlsx", "sid": [0, 12, -1],
     "seller": "\u041c\u0430\u0442\u0443\u0448\u043a\u0430", "findname": [0, 0],
     "findtext": "\u041f\u0440\u0430\u0439\u0441-\u043b\u0438\u0441\u0442 \u043d\u0430 ", "active": False},
    {"filename": "\u0410\u043b\u043c\u0430.xls", "sid": [0, 2, 1], "seller": "\u0410\u043b\u043c\u0430",
     "findname": [3, 0], "findtext": "\u0410\u043b\u043c\u0430", "active": False},
    {"filename": "\u0418\u043d\u0442\u0435\u0440\u0444\u0438\u0448.xls", "sid": [0, 2, 1],
     "seller": "\u0418\u043d\u0442\u0435\u0440\u0444\u0438\u0448", "findname": [0, 0],
     "findtext": "\u0418\u043d\u0442\u0435\u0440\u0444\u0438\u0448", "active": False},
    {"filename": "\u0421\u0434\u043e\u0431\u043d\u044b\u0439\u0414\u043e\u043c.xlsx", "sid": [0, 3, 2],
     "seller": "\u0421\u0434\u043e\u0431\u043d\u044b\u0439 \u0414\u043e\u043c", "findname": [0, 1],
     "findtext": "\u0434\u043e\u0431\u043d\u044b\u0439 \u0434\u043e\u043c", "active": True},
    {
        "filename": "\u042e\u043d\u0438\u0442.xlsx",
        "sid": [
            0,
            5,
            6
        ],
        "seller": "\u042e\u043d\u0438\u0442",
        "findname": [
            0,
            1
        ],
        "findtext": "\u041e\u041e\u041e \"\u042e\u043d\u0438\u0442\"",
        "active": False
    },
    {
        "filename": "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0438\u043c\u044f \u0444\u0430\u0439\u043b\u0430",
        "sid": [
            0,
            0,
            0
        ],
        "seller": "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u043e\u0441\u0442\u0430\u0432\u0449\u0438\u043a\u0430",
        "findname": [
            0,
            0
        ],
        "findtext": "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0441\u043b\u043e\u0432\u043e \u0434\u043b\u044f \u043f\u043e\u0438\u0441\u043a\u0430",
        "active": False
    },
    {
        "filename": "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0438\u043c\u044f \u0444\u0430\u0439\u043b\u0430",
        "sid": [
            0,
            0,
            0
        ],
        "seller": "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u043e\u0441\u0442\u0430\u0432\u0449\u0438\u043a\u0430",
        "findname": [
            0,
            0
        ],
        "findtext": "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0441\u043b\u043e\u0432\u043e \u0434\u043b\u044f \u043f\u043e\u0438\u0441\u043a\u0430",
        "active": False
    }

],
    "metro_active": False,
    "taxi": {
        "clid": "ak241111",
        "apikey": "YwgMXudjrASZaLAXpMqoNjTJjlDjrVKaMlrgBPN",
        "point1": "60.65829040252862,56.86060471272871",
        "point2": "60.6116408898243,56.839601819813524",
        "token": "bd1f236eb2a72a8e3cd4e2c748d5c00b"
    }
}

apply = [0]


# noinspection PyTypeChecker
def check_and_create():
    """
        Функция проверки
    """
    data_dir = os.listdir('data/')

    # noinspection SpellCheckingInspection
    files = {'config': preset_config,
             'cache_cart': {"cart": {}},
             'cache_prices': {"cache": {}},
             'db_taxi': {"price": []},
             'cookies_kuper': {"shops": {}},
             'cookies_mshop': {"shops": {}, 'time': ""},
             't2b': {}
             }

    # noinspection SpellCheckingInspection
    temp = {'cache_prices': ('cache', dict),
            'db_taxi': ('price', list),
            'cookies_kuper': ('shops', dict),
            'cookies_mshop': ('shops', dict),
            }

    for name in files:

        if f'{name}.json' not in data_dir:
            with open(f'data/{name}.json', 'w') as f:
                # noinspection PyTypeChecker
                json.dump(files[name], f)

                apply[0] = 1
        else:
            with open(f'data/{name}.json') as f:
                try:
                    obje = json.load(f)
                    if name in temp:
                        if temp[name][0] in obje:
                            if type(obje[temp[name][0]]) != temp[name][1]:
                                # noinspection PyTypeChecker
                                with open(f'data/{name}.json', 'w') as fw:
                                    json.dump(files[name], fw)
                                    apply[0] = 1
                        else:
                            with open(f'data/{name}.json', 'w') as fw:
                                json.dump(files[name], fw)
                                apply[0] = 1
                    if name == 't2b':
                        if type(obje) != dict:
                            # noinspection PyTypeChecker
                            with open(f'data/{name}.json', 'w') as fw:
                                json.dump({'3714856134875': {}}, fw)
                except ValueError:
                    with open(f'data/{name}.json', 'w') as fw:
                        json.dump(files[name], fw)
                        apply[0] = 1




    if apply[0] == 0:
        log("Все необходимые файлы присутствуют!")
    elif apply[0] == 1:
        # noinspection SpellCheckingInspection
        log("Найдены отсутствущие файлы, но были успешно созданы!")
    else:
        log("По каким то причинам, не удалось  проверить наличие файлов и создать их при отсутствии.", 3)
