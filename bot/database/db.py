"""
Работа с базой данных SQLite.

Все запросы к базе собраны в этом файле, чтобы обработчики (handlers)
не думали о SQL, а занимались только общением с пользователем.
"""

from datetime import datetime
from typing import Any

import aiosqlite

from config import DB_PATH

# SQL-запрос создания таблицы.
# IF NOT EXISTS — создать таблицу, только если её ещё нет.
CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    text       TEXT NOT NULL,
    user       TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


async def init_db() -> None:
    """Создаёт таблицу tasks при первом запуске бота."""
    # На всякий случай создаём папку для базы (например, data/).
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TASKS_TABLE)
        await db.commit()


async def add_task(text: str, user: str) -> int:
    """
    Добавляет задачу в базу и возвращает её id.

    :param text: текст задачи
    :param user: кто добавил задачу (имя и/или username)
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with aiosqlite.connect(DB_PATH) as db:
        # Знаки ? — это безопасная подстановка параметров (защита от SQL-инъекций).
        cursor = await db.execute(
            "INSERT INTO tasks (text, user, created_at) VALUES (?, ?, ?)",
            (text, user, created_at),
        )
        await db.commit()
        return int(cursor.lastrowid or 0)


async def get_tasks() -> list[dict[str, Any]]:
    """Возвращает все задачи, сначала самые старые."""
    async with aiosqlite.connect(DB_PATH) as db:
        # row_factory позволяет обращаться к колонкам по имени: row["text"].
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, text, user, created_at FROM tasks ORDER BY id ASC"
        )
        rows = await cursor.fetchall()

        return [dict(row) for row in rows]


async def count_tasks() -> int:
    """Возвращает количество задач в базе."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM tasks")
        row = await cursor.fetchone()

        return int(row[0]) if row else 0
