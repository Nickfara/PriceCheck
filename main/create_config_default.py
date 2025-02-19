import json

data = {"shops": [
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
     "findtext": "\u0434\u043e\u0431\u043d\u044b\u0439 \u0434\u043e\u043c", "active": True}
]}

with open('data/config.json', 'w') as f:
    json.dump(data, f)
