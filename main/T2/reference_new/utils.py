"""
Функции какие-то
"""
import asyncio
import os


def _print_version():
    print(f'tele2-profit v1.0.0 by M&D')


def run_main(main):
    """

    :param main:
    """
    try:
        _print_version()
        event_loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(main())
        event_loop.run_until_complete(future)
        if 'system' in dir(os):
            os.system('pause')
    except KeyboardInterrupt:
        pass
