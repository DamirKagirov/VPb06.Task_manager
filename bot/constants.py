"""
Справочники категорий и статусов задач.

Значения хранятся в базе как обычный текст (на русском),
а короткие ключи используются в callback_data кнопок Telegram.
"""

# Категории
CATEGORY_STANDARD = "Стандартная"
CATEGORY_URGENT = "Срочная"
CATEGORIES = (CATEGORY_STANDARD, CATEGORY_URGENT)
DEFAULT_CATEGORY = CATEGORY_STANDARD

# Статусы
STATUS_NEW = "Новая"
STATUS_IN_PROGRESS = "В работе"
STATUS_DONE = "Выполнена"
STATUSES = (STATUS_NEW, STATUS_IN_PROGRESS, STATUS_DONE)
DEFAULT_STATUS = STATUS_NEW

# Короткий ключ из кнопки -> значение в базе.
CATEGORY_KEYS = {
    "standard": CATEGORY_STANDARD,
    "urgent": CATEGORY_URGENT,
}
STATUS_KEYS = {
    "new": STATUS_NEW,
    "in_progress": STATUS_IN_PROGRESS,
    "done": STATUS_DONE,
}

# Эмодзи для красивого вывода.
CATEGORY_EMOJI = {
    CATEGORY_STANDARD: "🏷",
    CATEGORY_URGENT: "🚨",
}
STATUS_EMOJI = {
    STATUS_NEW: "🆕",
    STATUS_IN_PROGRESS: "⏳",
    STATUS_DONE: "✅",
}
