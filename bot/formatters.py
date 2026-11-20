"""Форматирование задач для сообщений Telegram."""

import html

from bot.constants import (
    CATEGORY_EMOJI,
    CATEGORY_STANDARD,
    DEFAULT_CATEGORY,
    DEFAULT_STATUS,
    STATUS_EMOJI,
)


def category_of(task: dict) -> str:
    """Возвращает категорию задачи (для старых записей — «Стандартная»)."""
    return str(task.get("category") or DEFAULT_CATEGORY)


def status_of(task: dict) -> str:
    """Возвращает статус задачи (для старых записей — «Новая»)."""
    return str(task.get("status") or DEFAULT_STATUS)


def task_card(task: dict) -> str:
    """Подробная карточка одной задачи (используется при редактировании)."""
    category = category_of(task)
    status = status_of(task)

    return (
        f"<b>Задача #{task['id']}</b>\n\n"
        f"📝 {html.escape(str(task['text']))}\n\n"
        f"🏷 Категория: {CATEGORY_EMOJI.get(category, '🏷')} <b>{category}</b>\n"
        f"🔄 Статус: {STATUS_EMOJI.get(status, '🔄')} <b>{status}</b>\n"
        f"👤 {html.escape(str(task['user']))}\n"
        f"🕒 {html.escape(str(task['created_at']))}"
    )


def task_list_item(task: dict) -> str:
    """Одна задача в общем списке /list."""
    category = category_of(task)
    status = status_of(task)

    return (
        f"<b>#{task['id']}</b> "
        f"{CATEGORY_EMOJI.get(category, '🏷')} {category} · "
        f"{STATUS_EMOJI.get(status, '🔄')} {status}\n"
        f"{html.escape(str(task['text']))}\n"
        f"   👤 {html.escape(str(task['user']))} · "
        f"🕒 {html.escape(str(task['created_at']))}"
    )
