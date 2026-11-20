"""Работа с базой данных SQLite.

Все запросы к базе собраны в этом файле, чтобы обработчики (handlers)
не думали о SQL, а занимались только общением с пользователем.
"""

from datetime import datetime
from typing import Any

import aiosqlite

from bot.constants import DEFAULT_CATEGORY, DEFAULT_STATUS
from config import DB_PATH

# SQL-запрос создания таблицы.
# IF NOT EXISTS — создать таблицу, только если её ещё нет.
CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    text       TEXT NOT NULL,
    user       TEXT NOT NULL,
    created_at TEXT NOT NULL,
    category   TEXT NOT NULL DEFAULT 'Стандартная',
    status     TEXT NOT NULL DEFAULT 'Новая'
)
"""

# Названия колонок, которые появились в версии 2.
# Они нужны для миграции старой базы без потери задач.
NEW_COLUMNS = {
    "category": f"TEXT NOT NULL DEFAULT '{DEFAULT_CATEGORY}'",
    "status": f"TEXT NOT NULL DEFAULT '{DEFAULT_STATUS}'",
}


async def init_db() -> None:
    """
    Создаёт таблицу tasks при первом запуске бота.

    Если база уже существует со старой структурой (без category/status),
    добавляет недостающие колонки. Старые задачи получают значения по умолчанию.
    """
    # На всякий случай создаём папку для базы (например, data/).
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TASKS_TABLE)

        # PRAGMA table_info возвращает описание колонок таблицы.
        cursor = await db.execute("PRAGMA table_info(tasks)")
        existing_columns = {row[1] for row in await cursor.fetchall()}

        for column, definition in NEW_COLUMNS.items():
            if column not in existing_columns:
                # ALTER TABLE добавляет колонку в уже существующую таблицу.
                await db.execute(
                    f"ALTER TABLE tasks ADD COLUMN {column} {definition}"
                )

        await db.commit()


async def add_task(
    text: str,
    user: str,
    category: str = DEFAULT_CATEGORY,
    status: str = DEFAULT_STATUS,
) -> int:
    """
    Добавляет задачу в базу и возвращает её id.

    :param text: текст задачи
    :param user: кто добавил задачу (имя и/или username)
    :param category: категория (по умолчанию «Стандартная»)
    :param status: статус (по умолчанию «Новая»)
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async with aiosqlite.connect(DB_PATH) as db:
        # Знаки ? — это безопасная подстановка параметров (защита от SQL-инъекций).
        cursor = await db.execute(
            """
            INSERT INTO tasks (text, user, created_at, category, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (text, user, created_at, category, status),
        )
        await db.commit()
        return int(cursor.lastrowid or 0)


async def get_tasks() -> list[dict[str, Any]]:
    """Возвращает все задачи, сначала самые старые."""
    async with aiosqlite.connect(DB_PATH) as db:
        # row_factory позволяет обращаться к колонкам по имени: row["text"].
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT id, text, user, created_at, category, status
            FROM tasks
            ORDER BY id ASC
            """
        )
        rows = await cursor.fetchall()

        return [dict(row) for row in rows]


async def get_task(task_id: int) -> dict[str, Any] | None:
    """Возвращает одну задачу по номеру или None, если её нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT id, text, user, created_at, category, status
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )
        row = await cursor.fetchone()

        return dict(row) if row else None


async def update_task_category(task_id: int, category: str) -> bool:
    """Меняет категорию задачи. Возвращает True, если задача найдена."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "UPDATE tasks SET category = ? WHERE id = ?",
            (category, task_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def update_task_status(task_id: int, status: str) -> bool:
    """Меняет статус задачи. Возвращает True, если задача найдена."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def count_tasks() -> int:
    """Возвращает количество задач в базе."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM tasks")
        row = await cursor.fetchone()

        return int(row[0]) if row else 0
