from openpyxl import load_workbook as open_xlsx

from xlrd import open_workbook as open_xls

shops = {'Матушка.xlsx': {'sid': (0, 12), 'seller': 'Матушка', 'findname': (0, 0), 'findtext': 'Прайс-лист на '},
         'Алма.xls': {'sid': (0, 2, 1), 'seller': 'Алма', 'findname': (3, 0), 'findtext': 'Алма'}
         }
temp = {'Интерфиш.xls':{'sid': (0, 2, 1), 'seller': 'Интерфиш', 'findname': (0, 0)}}
h = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
     "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE",
     "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR",
     "AS", "AT", "AU", "AV", "AW", "AX", "AY", "AZ"]

def read(filename):  # Чтение таблицы
    print(filename)
    format = filename.split('.')[1]
    if True:
        if format == 'xls':  # Чтение xls
            workbook = open_xls('doc/' + str(filename))
            worksheet = workbook.sheet_by_index(0)
            response = xls(worksheet)
        elif format == 'xlsx':  # Чтение xlsx
            worksheet = open_xlsx('doc/' + str(filename))
            response = xlsx(worksheet)
        else:
            response = False  # Формат файла неверный
            error_text = 'Формат файла неверный'
            print(error_text)
    try:
        pass
    except Exception as e:
        response = False
        error_text = 'Сработало исключение:\n' + str(e)
        print(error_text)
    return response


def xls(worksheet):
    items = []
    sid = False
    seller = False
    for i in shops:
        if shops[i]['findtext'].lower() in str(worksheet.cell_value(shops[i]['findname'][0], shops[i]['findname'][1])).lower():
            sid = shops[i]['sid']
            seller = shops[i]['seller']
            break

    print(sid)
    if sid:
        for i in range(0, 200):  # Чтение строк
            item = {}
            try:
                item['seller'] = seller
                item['name'] = str(worksheet.cell_value(i, sid[0]))
                item['name'] = ''.join(item['name'].split(',')) # Удаление запятых из названия
                item['cost'] = str(worksheet.cell_value(i, sid[1]))
                if item['cost'] == '':
                    item['cost'] = 'категория'

                items.append(item)
            except Exception as e:
                error_text = 'Пустая строка!'
                print(error_text)
                print(e)
    else:
        items = False
        error_text = 'Не найдено имя поставщика в таблице!'
        print(error_text)
    return items


def xlsx(worksheet):
    items = []
    sid = False
    seller = False
    for i in shops:
        if shops[i]['findtext'].lower() in str(worksheet.active[h[shops[i]['findname'][0]]][shops[i]['findname'][1]].value).lower():
            sid = (h[shops[i]['sid'][0]], h[shops[i]['sid'][1]])
            seller = shops[i]['seller']
            break
    if sid:
        for i in range(0, 1000):  # Чтение строк
            item = {}
            try:
                if 'мороженое' in str(worksheet.active[f'{sid[0]}'][i].value).lower():
                    print('Дальше мороженое. Остановка чтения файла.')
                    break
                item['seller'] = seller
                item['name'] = str(worksheet.active[f'{sid[0]}'][i].value)
                item['name'] = ''.join(item['name'].split(',')) # Удаление запятых из названия
                item['cost'] = str(worksheet.active[f'{sid[1]}'][i].value)
                if item['cost'] == '':
                    item['cost'] = 'категория'
                items.append(item)
            except Exception as e:
                error_text = 'Пустая строка!'
                print(error_text)
                print(e)
    else:
        items = False
        error_text = 'Не найдено имя поставщика в таблице!'
        print(error_text)
    return items


def scanner(name):
    name = str(name)
    items = []
    result = []
    for filename in shops:
        table = read(filename)
        if table:
            for i in table:
                items.append(i)

    for i in items:
        if name.lower() in i['name'].lower():
            item = f'[{i["seller"]}] {i["name"]} - Цена: {i["cost"]}руб.'
            #print(item)
            result.append(i)

    def key(price):
        try:
            return float(price['cost'])
        except:
            return 0

    result.sort(key=key)
    return result


scanner('')