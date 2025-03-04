import matplotlib.pyplot as plt

from database import get


def render(group='all', filter='all', week='all'):
    """
    Рендеринг окна с графиком.

    :param group: Параметр группировки цен. (Если включен режим дня недели, работает только группировка по часам)
    :param filter: Параметр фильтра.
    :param week: Фильтр по дню недели. Если он включен, включается группировка цен в этот день.
    :return:
    """
    if week != 'all':
        filter = 'all'
        if group != 'hours':
            group = 'all'

    base = get()

    x = []
    to_y = []
    from_y = []
    days = {}
    weeks = {}
    for price in base:
        datetime = price['ts']
        if filter != 'all':
            if filter != datetime.split[' '][0]:
                continue

        cost_to = price['to_price']
        cost_from = price['from_price']

        if group == 'days':
            date = datetime.split(' ')[0]
        elif group == 'hours':
            date = datetime.split(':')[0]
            if week != 'all':
                time = datetime.split(' ')[1].split(':')
                time = f'{time[0]}:{time[1]}'
                if time not in weeks:
                    weeks[time] = {}
                    if 'cost_to' not in weeks[time] and 'cost_from' not in weeks[time]:
                        weeks[time]['cost_to'] = []
                        weeks[time]['cost_from'] = []
                weeks[time]['cost_to'].append(cost_to)
                weeks[time]['cost_from'].append(cost_to)
        elif group == 'week':
            date = datetime.split(' ')[2]
        else:
            date = datetime

        if group != 'all':
            if date not in days:
                days[date] = {}
                if 'cost_to' not in days[date] and 'cost_from' not in days[date]:
                    days[date]['cost_to'] = []
                    days[date]['cost_from'] = []
            days[date]['cost_to'].append(cost_to)
            days[date]['cost_from'].append(cost_from)
        else:
            if week != 'all':
                time = datetime.split(' ')[1].split(':')
                time = f'{time[0]}:{time[1]}'
                if time not in weeks:
                    weeks[time] = {}
                    if 'cost_to' not in weeks[time] and 'cost_from' not in weeks[time]:
                        weeks[time]['cost_to'] = []
                        weeks[time]['cost_from'] = []
                weeks[time]['cost_to'].append(cost_to)
                weeks[time]['cost_from'].append(cost_from)
            else:
                x.append(date)
                to_y.append(cost_to)
                from_y.append(cost_from)
    if group != 'all' and week == 'all':
        for day in days:
            x.append(day)
            cost_to = sum(days[day]['cost_to']) / len(days[day]['cost_to'])
            cost_from = sum(days[day]['cost_from']) / len(days[day]['cost_from'])
            to_y.append(cost_to)
            from_y.append(cost_from)

    if week != 'all':
        hours = {}
        for time in weeks:
            if group == 'hours':

                hour = time.split(':')[0]

                if hour not in hours:
                    hours[hour] = {}
                    if 'cost_to' not in hours[hour] and 'cost_from' not in hours[hour]:
                        hours[hour]['cost_to'] = []
                        hours[hour]['cost_from'] = []

                for cost_time in weeks[time]['cost_to']:
                    hours[hour]['cost_to'].append(cost_time)
                for cost_time in weeks[time]['cost_from']:
                    hours[hour]['cost_from'].append(cost_time)


            else:
                x.append(time)
                cost_to = sum(weeks[time]['cost_to']) / len(weeks[time]['cost_to'])
                cost_from = sum(weeks[time]['cost_from']) / len(weeks[time]['cost_from'])
                to_y.append(cost_to)
                from_y.append(cost_from)
        for hour in hours:
            cost_to = sum(hours[hour]['cost_to']) / len(hours[hour]['cost_to'])
            cost_from = sum(hours[hour]['cost_from']) / len(hours[hour]['cost_from'])
            x.append(hour)
            to_y.append(cost_to)
            from_y.append(cost_from)

    plt.plot(x, to_y, color='red', marker='o', markersize=7)
    plt.plot(x, from_y, color='green', marker='o', markersize=7)
    plt.xlabel('Время')  # Подпись для оси х
    plt.ylabel('Цена')  # Подпись для оси y
    plt.title('Цены на такси')  # Название
    plt.show()
