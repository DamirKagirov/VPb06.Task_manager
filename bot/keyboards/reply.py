"""Клавиатуры, которые показываются пользователю в Telegram."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Тексты кнопок храним в константах, чтобы не опечататься в обработчиках.
BTN_ADD = "➕ Добавить задачу"
BTN_LIST = "📋 Список задач"
BTN_EDIT = "🛠 Изменить задачу"
BTN_CSV = "📄 Скачать CSV"
BTN_HELP = "❓ Помощь"
BTN_CANCEL = "❌ Отмена"


def main_menu() -> ReplyKeyboardMarkup:
    """Главное меню с кнопками под полем ввода."""
    keyboard = [
        [KeyboardButton(text=BTN_ADD), KeyboardButton(text=BTN_LIST)],
        [KeyboardButton(text=BTN_EDIT), KeyboardButton(text=BTN_CSV)],
        [KeyboardButton(text=BTN_HELP)],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,  # делаем кнопки компактными
        input_field_placeholder="Выберите действие или введите /add ...",
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура на время ввода текста задачи: только кнопка «Отмена»."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True,
        input_field_placeholder="Введите текст задачи...",
    )
