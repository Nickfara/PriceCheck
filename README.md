# Дерево проекта:

```
main\
  data\
    prices\
      Алма.xls
      Интерфиш.xls
      Матушка.csv
      Матушка.xlsx
      СдобныйДом.xlsx
      Юнит.xlsx
    cache_cart.json
    cache_prices.json
    config.json
    cookies_kuper.json
    cookies_mshop.json
    csv.csv
    db_taxi.json
    t2b.json
    taxi_prices.db
  ParserTaxi\
    config.py
    database.py
    graph.py
    taxi_parser.py
  PriceCheck\
    commands.py
    create_csv.py
    parse_kuper.py
    parse_metro.py
    read_doc.py
  T2\
    api.py
    commands.py
    config.py
    constants.py
    menu.py
  check_files.py
  constants.py
  crypt.py
  handler.py
  init_app.py
  log.py
  preset.py
  requirements.txt
  Start MC.ps1
  tg_bot.py
  toolsajob.kv

```

# Функционал приложения:

## T2: 
Работа с маркетом Т2 для автоматизации продажи трафика.

#### api.py: 
Реализует подключение к серверу Т2 через API.

#### commands.py:
Выполняет запросы на выполнение функционала.

#### constants.py
Содержит в себе пару ссылок и загаловок.

## PriceCheck: 
Сканирование excel документов с прайс-листами от поставщиков.

#### commands.py
Выполняет запросы на выполнение функционала.

#### create_csv.py


#### parse_kuper.py
Подключение по API к магазину KUPER.

#### parse_metro.py
Подключение по API к магазину METRO SHOP HORECA.

#### read_doc.py
Сканирование excel документов.

## ParserTaxi:
Делает запрос на стоимость поездки из точки A в точку B. И так же присылает уведомления, когда цена значительно снизилась.

#### config.py:
Даёт доступ к локальному конфигу.

#### database.py:
Команды для работы с базой данных.

#### graph.py:
Реализация интерфейса просморта графика по данным из базы.

#### taxi_parser.py:
Основной функционал по запросу на цены.
