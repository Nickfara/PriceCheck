def converting(file):
    data = ''

    print(file)
    for item in data:
        obj_str = f'{item["name"]};{item["cost"]},'
        data += obj_str
    with open('data/csv.csv', 'a') as f:
        f.write(data)