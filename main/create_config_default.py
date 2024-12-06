import json

data = {
  "shops": ({'filename': 'Матушка.xlsx', "sid": (0, 12), "seller": "Матушка", "findname": (0, 0), "findtext": "Прайс-лист на ", 'active': True},
         {'filename': 'Алма.xls', "sid": (0, 2, 1), "seller": "Алма", "findname": (3, 0), "findtext": "Алма", 'active': True}
)}

with open('config.json', 'w') as f:
    json.dump(data, f)