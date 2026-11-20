"""Inline-клавиатуры (кнопки внутри сообщений)."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.constants import (
    CATEGORY_STANDARD,
    CATEGORY_URGENT,
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    STATUS_NEW,
)
from bot.formatters import category_of, status_of


def _mark(is_current: bool) -> str:
    """Пометка текущего выбранного значения на кнопке."""
    return "• " if is_current else ""


def task_actions_keyboard(task: dict) -> InlineKeyboardMarkup:
    """
    Кнопки изменения категории и статуса одной задачи.

    callback_data имеет вид:
    • cat:<id>:<ключ>     — смена категории;
    • status:<id>:<ключ>  — смена статуса;
    • edit:close          — закрыть карточку.
    """
    task_id = task["id"]
    category = category_of(task)
    status = status_of(task)

    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{_mark(category == CATEGORY_STANDARD)}🏷 Стандартная",
                callback_data=f"cat:{task_id}:standard",
            ),
            InlineKeyboardButton(
                text=f"{_mark(category == CATEGORY_URGENT)}🚨 Срочная",
                callback_data=f"cat:{task_id}:urgent",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"{_mark(status == STATUS_NEW)}🆕 Новая",
                callback_data=f"status:{task_id}:new",
            ),
            InlineKeyboardButton(
                text=f"{_mark(status == STATUS_IN_PROGRESS)}⏳ В работе",
                callback_data=f"status:{task_id}:in_progress",
            ),
            InlineKeyboardButton(
                text=f"{_mark(status == STATUS_DONE)}✅ Выполнена",
                callback_data=f"status:{task_id}:done",
            ),
        ],
        [
            InlineKeyboardButton(text="✖️ Закрыть", callback_data="edit:close"),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
