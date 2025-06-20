"""
Временный конфиг для работы с Т2
"""
# 79923415301:868BNQ-gigabyte:1:90:bomb,bomb,bomb:Светлана=15:False
# 79018555731:UKt842-gigabyte:1:90:bomb,bomb,bomb:Светлана=15:False

config = []
data = ':-gb:6:90:bomb,bomb,bomb:��������=35:20:True'
main = data.split('-')
data1 = main[0].split(':')
data_temp = main[1].split('=')
data2 = data_temp[0].split(':')
data3 = data_temp[1].split(':')
config.append(data1)
config.append(data2)
config.append(data3)


def account():
    """

    :return:
    """
    number = config[0][0]
    password = config[0][1]
    return {'number': number, 'password': password}


def add_traffic():
    """

    :return:
    """
    default = {
        "volume": {
            "value": '6',
            "uom": 'gb'
        },
        "cost": {
            "amount": '90',
            "currency": "rub"
        },
        "trafficType": "data",
        'emojis': ['bomb', 'bomb', 'bomb'],
        'name': True
    }
    auto_check = ["35", "20", "True"]
    return default, auto_check
