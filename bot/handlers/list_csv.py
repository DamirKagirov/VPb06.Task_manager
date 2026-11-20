"""Экспорт задач в CSV: команда /list_csv и кнопка «Скачать CSV»."""

import csv
import io
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import BufferedInputFile, Message

from bot.database.db import get_tasks
from bot.keyboards.reply import BTN_CSV, main_menu

router = Router(name="list_csv")


def build_csv(tasks: list[dict]) -> bytes:
    """Собирает CSV-файл в памяти и возвращает его содержимое в байтах."""
    # StringIO — это «файл в памяти». Удобно, когда не нужно ничего писать на диск.
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)

    # Первая строка CSV — заголовки колонок.
    writer.writerow(["id", "text", "category", "status", "user", "created_at"])

    for task in tasks:
        writer.writerow(
            [
                task["id"],
                task["text"],
                task["category"],
                task["status"],
                task["user"],
                task["created_at"],
            ]
        )

    # utf-8-sig добавляет BOM — так Excel правильно открывает русский текст.
    return buffer.getvalue().encode("utf-8-sig")


@router.message(Command("list_csv"))
@router.message(F.text == BTN_CSV, StateFilter(None))
async def cmd_list_csv(message: Message) -> None:
    """Формирует CSV-файл со всеми задачами и отправляет его пользователю."""
    tasks = await get_tasks()

    file_bytes = build_csv(tasks)
    filename = f"tasks_{datetime.now():%Y-%m-%d_%H-%M}.csv"
    document = BufferedInputFile(file_bytes, filename=filename)

    if tasks:
        caption = f"📄 Задачи команды: <b>{len(tasks)}</b> шт."
    else:
        caption = "📄 Список пока пуст — в файле только заголовки."

    await message.answer_document(
        document,
        caption=caption,
        reply_markup=main_menu(),
    )
