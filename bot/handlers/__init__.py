"""
Все роутеры бота собраны здесь.

В main.py мы просто перебираем список routers и подключаем их к диспетчеру.
Порядок важен: если два обработчика подходят под одно сообщение,
сработает тот, который зарегистрирован раньше.
"""

from aiogram import Router

from bot.handlers import add_task, list_csv, list_tasks, start

routers: list[Router] = [
    start.router,
    add_task.router,
    list_tasks.router,
    list_csv.router,
]

__all__ = ["routers"]
