"""
Точка входа проекта.

Здесь мы:
1. Создаём бота и диспетчер (dispatcher).
2. Подключаем роутеры с обработчиками команд.
3. Запускаем получение сообщений из Telegram.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.database.db import init_db
from bot.handlers import routers
from config import BOT_TOKEN, PROXY_URL

# Если Telegram недоступен, ждём столько секунд и пробуем снова.
RETRY_DELAY_SECONDS = 10


async def set_commands(bot: Bot) -> None:
    """Добавляем команды в меню Telegram (кнопка «/» рядом с полем ввода)."""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="add", description="Добавить задачу"),
        BotCommand(command="list", description="Показать все задачи"),
        BotCommand(command="edit", description="Изменить категорию или статус"),
        BotCommand(command="list_csv", description="Скачать задачи в CSV"),
        BotCommand(command="cancel", description="Отменить добавление"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)


def create_session() -> AiohttpSession:
    """
    Создаёт HTTP-сессию для общения с Telegram.

    Если в .env указан PROXY_URL, все запросы пойдут через прокси.
    Это помогает, когда api.telegram.org недоступен напрямую.
    """
    if PROXY_URL:
        logging.info("Используется прокси из PROXY_URL.")
        return AiohttpSession(proxy=PROXY_URL)

    return AiohttpSession()


async def run_polling(bot: Bot, dp: Dispatcher) -> None:
    """
    Запускает получение сообщений.

    Если при старте нет связи с Telegram (нет интернета, нужен VPN/прокси),
    бот не падает с ошибкой, а пишет понятное сообщение в консоль
    и повторяет попытку каждые RETRY_DELAY_SECONDS секунд.
    """
    while True:
        try:
            # Проверяем связь и заодно убеждаемся, что токен верный.
            await bot.get_me()

            # Меню команд тоже требует связи с Telegram.
            await set_commands(bot)

            # close_bot_session=False: сессию закроем сами в main(),
            # чтобы её можно было использовать при повторных попытках.
            await dp.start_polling(bot, close_bot_session=False)
            return

        except TelegramNetworkError as error:
            logging.error("Нет связи с Telegram: %s", error)
            logging.error(
                "Проверьте интернет, VPN или прокси. "
                "Повторная попытка через %d секунд...",
                RETRY_DELAY_SECONDS,
            )
            await asyncio.sleep(RETRY_DELAY_SECONDS)


async def main() -> None:
    """Готовим базу данных, бота и запускаем его."""
    # Создаём таблицу tasks, если её ещё нет.
    await init_db()

    # parse_mode=HTML позволяет красиво оформлять текст (например, <b>жирный</b>).
    bot = Bot(
        token=BOT_TOKEN,
        session=create_session(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # MemoryStorage хранит состояния (FSM) в памяти.
    # После перезапуска бота незавершённые диалоги сбрасываются — для старта это нормально.
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем все роутеры из пакета bot/handlers.
    for router in routers:
        dp.include_router(router)

    try:
        logging.info("Бот запущен. Для остановки нажмите Ctrl+C.")
        await run_polling(bot, dp)
    finally:
        # Закрываем HTTP-соединение, чтобы не было предупреждения
        # «Unclosed client session».
        await bot.session.close()


if __name__ == "__main__":
    # Настраиваем логи, чтобы видеть ошибки и действия бота в консоли.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    try:
        asyncio.run(main())
    except TelegramUnauthorizedError:
        logging.error(
            "Telegram отклонил токен. Проверьте BOT_TOKEN в файле .env "
            "и получите актуальный токен у @BotFather."
        )
    except TelegramNetworkError as error:
        logging.error("Не удалось подключиться к Telegram: %s", error)
        logging.error(
            "Проверьте интернет, VPN или укажите прокси в .env:\n"
            "PROXY_URL=socks5://127.0.0.1:1080"
        )
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
