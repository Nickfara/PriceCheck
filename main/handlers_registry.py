def get_admin_commands(uid, t2b, menu, commands, log):
    return {
        'МТ2': lambda call: menu.admin_login(call),
        'ОСТ': lambda call: log('ОСТ команда получена', 2),
        'ПТ': lambda call: log('ПТ команда получена', 2),
        'ПРС': lambda call: log('ПРС команда получена', 2),
        'Войти админ': lambda call: (
            t2b(uid, data={'stage_authorize': 2}, type_='u')
            if commands.admin_auth(call)
            else log('Ошибка авторизации', 3)
        )
    }


def get_user_commands(uid, t2b, menu, commands, settings, log, stop):
    return {
        'Главное меню': lambda c: menu.home(c) if commands.home_menu(c) else log('Главное меню недоступно', 2),
        'Профиль': lambda c: menu.profile(c, commands.profile(c)),
        'Запуск': menu.bot_select,
        'Настройки': lambda c: (t2b(uid, data={'lvl_setting': 0}, type_='u'), settings(c)),
        'Назад': lambda c: (t2b(uid, data={'lvl_setting': 0}, type_='u'), settings(c)),
        'Авто-продажа': lambda c: commands.run_auto(c, 'sell'),
        'Авто-поднятие': lambda c: commands.run_auto(c, 'top'),
        'Поднять': lambda c: (
            menu.up(c) if commands.up(c)
            else (log('Лотов нет!', 2), menu.bot_active(c, 'Лотов нет!'), stop(c))
        ),
        'Отмена': lambda c: menu.home(c) if commands.home_menu(c) else log('Меню недоступно', 2),
        'Выйти из аккаунта': lambda c: log('Выход из аккаунта', 1),
        'Интервал': lambda c: (t2b(uid, data={'lvl_setting': 1}, type_='u'), settings(c)),
        'Количество': lambda c: (t2b(uid, data={'lvl_setting': 2}, type_='u'), settings(c)),
        'Повторы': lambda c: (t2b(uid, data={'lvl_setting': 3}, type_='u'), settings(c)),
        'Вид трафика': lambda c: (t2b(uid, data={'lvl_setting': 4}, type_='u'), settings(c)),
        'Минуты': lambda c: (settings(c), t2b(uid, data={'lvl_setting': 0}, type_='u')),
        'Гигабайты': lambda c: (settings(c), t2b(uid, data={'lvl_setting': 0}, type_='u')),
        'Остановить': stop,
        'Отозвать минуты': menu.remove_minutes_lots_confirm,
        'Подтверждение отзыва минут': commands.remove_minutes_lots,
        'Редактировать лоты': commands.edit_lots,
    }


def get_param_commands(commands):
    return {
        'del': commands.delete_confirm,
        'delconf': commands.delete_yes,
        'red': commands.redactor_lot,
        'top': commands.top,
        'emoji': commands.emoji,
        'name': commands.name,
        'save': commands.save,
    }



