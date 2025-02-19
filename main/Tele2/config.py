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
    number = config[0][0]
    password = config[0][1]
    return {'number': number, 'password': password}


def add_traffic():
    default = {
        "volume": {
            "value": config[1][1],
            "uom": config[1][0]
        },
        "cost": {
            "amount": config[1][2],
            "currency": "rub"
        },
        "trafficType": "data",
        'emojis': ['bomb', 'bomb', 'bomb'],
        'name': True
    }
    auto_check = [config[2][0], config[2][1], (True if config[2][2] == 'True' else False)]
    return default, auto_check
