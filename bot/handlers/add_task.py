"""Обработчики добавления задачи: /add и кнопка «Добавить задачу»."""

import html

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.constants import DEFAULT_CATEGORY, DEFAULT_STATUS
from bot.database.db import add_task
from bot.keyboards.reply import BTN_ADD, cancel_keyboard, main_menu
from bot.states.task import AddTask

router = Router(name="add_task")

# Максимальная длина текста задачи (чтобы не отправлять слишком большие файлы).
MAX_TASK_LENGTH = 1000


def get_user_title(message: Message) -> str:
    """Возвращает подпись автора задачи: «Имя (@username)» или просто имя."""
    user = message.from_user

    if user is None:
        return "неизвестный пользователь"

    if user.username:
        return f"{user.full_name} (@{user.username})"

    return user.full_name


async def ask_for_text(message: Message, state: FSMContext) -> None:
    """Просит пользователя прислать текст задачи и включает режим ожидания."""
    await state.set_state(AddTask.waiting_for_text)
    await message.answer(
        "✏️ Напишите текст задачи одним сообщением.\n"
        "Например: <i>Подготовить отчёт к пятнице</i>\n\n"
        "Чтобы отменить — нажмите «Отмена» или введите /cancel.",
        reply_markup=cancel_keyboard(),
    )


async def save_and_reply(message: Message, state: FSMContext, task_text: str) -> bool:
    """
    Проверяет текст, сохраняет задачу и отвечает пользователю.

    Возвращает True, если задача сохранена.
    """
    task_text = task_text.strip()

    # Пустой текст сохранять нельзя.
    if not task_text:
        await message.answer("Текст задачи пустой. Напишите что-нибудь 🙂")
        return False

    if len(task_text) > MAX_TASK_LENGTH:
        await message.answer(
            f"Слишком длинный текст: {len(task_text)} символов. "
            f"Максимум — {MAX_TASK_LENGTH}."
        )
        return False

    task_id = await add_task(text=task_text, user=get_user_title(message))
    await state.clear()

    await message.answer(
        f"✅ Задача <b>#{task_id}</b> добавлена:\n"
        f"<i>{html.escape(task_text)}</i>\n\n"
        f"🏷 Категория: {DEFAULT_CATEGORY} · 🔄 Статус: {DEFAULT_STATUS}\n"
        f"🛠 Изменить: <code>/edit {task_id}</code>",
        reply_markup=main_menu(),
    )
    return True


@router.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject, state: FSMContext) -> None:
    """
    Команда /add.

    Работает двумя способами:
    • /add Купить хлеб — сохраняет текст сразу;
    • /add — просит прислать текст следующим сообщением.
    """
    # command.args — это всё, что написано после команды /add.
    task_text = (command.args or "").strip()

    if task_text:
        await save_and_reply(message, state, task_text)
        return

    await ask_for_text(message, state)


@router.message(F.text == BTN_ADD, StateFilter(None))
async def button_add(message: Message, state: FSMContext) -> None:
    """Нажатие на кнопку «Добавить задачу» в главном меню."""
    await ask_for_text(message, state)


@router.message(AddTask.waiting_for_text, F.text, ~F.text.startswith("/"))
async def process_task_text(message: Message, state: FSMContext) -> None:
    """Пользователь прислал текст задачи — сохраняем его."""
    saved = await save_and_reply(message, state, message.text)

    # Если текст не подошёл (пустой или слишком длинный), остаёмся в режиме ожидания.
    if not saved:
        await state.set_state(AddTask.waiting_for_text)


@router.message(AddTask.waiting_for_text, ~F.text)
async def process_not_text(message: Message) -> None:
    """Если вместо текста прислали фото/стикер — вежливо просим текст."""
    await message.answer("Пожалуйста, пришлите задачу обычным текстом ✍️")
