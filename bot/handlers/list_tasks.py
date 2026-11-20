"""Вывод списка задач: команда /list и кнопка «Список задач»."""

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from bot.database.db import get_tasks
from bot.formatters import task_list_item
from bot.keyboards.reply import BTN_LIST, main_menu

router = Router(name="list_tasks")

# Telegram разрешает не больше 4096 символов в одном сообщении.
# Берём с запасом, чтобы точно не упереться в лимит.
MAX_MESSAGE_LENGTH = 3500


def build_messages(tasks: list[dict]) -> list[str]:
    """
    Собирает красивые сообщения со списком задач.

    Если задач много, они автоматически разбиваются на несколько сообщений.
    """
    header = f"📋 <b>Задачи команды</b> (всего: {len(tasks)})"

    # Каждая задача превращается в отдельный блок текста.
    blocks = [task_list_item(task) for task in tasks]

    messages: list[str] = []
    current = header

    for block in blocks:
        addition = ("\n\n" if current else "") + block

        if len(current) + len(addition) > MAX_MESSAGE_LENGTH:
            # Сообщение достигло лимита — сохраняем его и начинаем новое.
            messages.append(current)
            current = block
        else:
            current += addition

    if current:
        messages.append(current)

    # Подсказка, как изменить категорию или статус.
    if messages:
        messages[-1] += (
            "\n\n🛠 Изменить категорию или статус: <code>/edit 3</code>"
        )

    return messages


@router.message(Command("list"))
@router.message(F.text == BTN_LIST, StateFilter(None))
async def cmd_list(message: Message) -> None:
    """Показывает все задачи из базы."""
    tasks = await get_tasks()

    if not tasks:
        await message.answer(
            "📭 Пока задач нет.\n\n"
            "Добавьте первую: /add Купить молоко",
            reply_markup=main_menu(),
        )
        return

    for text in build_messages(tasks):
        await message.answer(text)

    # Отдельное сообщение с клавиатурой, чтобы меню оставалось под рукой.
    await message.answer("Готово 👍", reply_markup=main_menu())
