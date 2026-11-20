"""Обработчики команд /start, /help и /cancel."""

import html

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.reply import BTN_CANCEL, BTN_HELP, main_menu

# Роутер — это набор обработчиков. В main.py все роутеры подключаются к диспетчеру.
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Приветствие по команде /start."""
    await state.clear()  # сбрасываем незавершённый диалог, если он был

    # Экранируем имя: в имени пользователя могут быть символы < > &.
    user_name = html.escape(message.from_user.full_name)

    await message.answer(
        f"Привет, <b>{user_name}</b>! 👋\n\n"
        "Я бот для командной работы. Вместе мы можем вести общий список задач.\n\n"
        "<b>Что я умею:</b>\n"
        "➕ /add — добавить задачу\n"
        "📋 /list — показать все задачи\n"
        "📄 /list_csv — скачать список файлом CSV\n\n"
        "Выберите действие на клавиатуре ниже или введите команду.",
        reply_markup=main_menu(),
    )


@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def cmd_help(message: Message) -> None:
    """Краткая справка по командам."""
    await message.answer(
        "<b>Как пользоваться ботом</b>\n\n"
        "• <code>/add Купить молоко</code> — добавить задачу одной строкой\n"
        "• <code>/add</code> — бот попросит текст задачи отдельным сообщением\n"
        "• <code>/list</code> — показать все задачи команды\n"
        "• <code>/list_csv</code> — получить CSV-файл со всеми задачами\n"
        "• <code>/cancel</code> — отменить добавление задачи\n\n"
        "Задачи хранятся в общей базе, поэтому их видят все участники.",
        reply_markup=main_menu(),
    )


@router.message(Command("cancel"))
@router.message(F.text == BTN_CANCEL)
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """Отмена текущего действия (например, добавления задачи)."""
    await state.clear()
    await message.answer(
        "Отменено. Возвращаемся в главное меню.",
        reply_markup=main_menu(),
    )
