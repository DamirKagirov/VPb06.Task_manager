"""Изменение категории и статуса задачи: /edit и кнопка «Изменить задачу»."""

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.constants import CATEGORY_KEYS, STATUS_KEYS
from bot.database.db import get_task, update_task_category, update_task_status
from bot.formatters import task_card
from bot.keyboards.inline import task_actions_keyboard
from bot.keyboards.reply import BTN_EDIT, cancel_keyboard
from bot.states.task import EditTask

router = Router(name="edit_task")


async def show_task_card(message: Message, task_id: int) -> bool:
    """
    Показывает карточку задачи с кнопками изменения.

    Возвращает True, если задача найдена.
    """
    task = await get_task(task_id)

    if task is None:
        await message.answer(
            f"Задача <b>#{task_id}</b> не найдена.\n"
            "Посмотрите номера задач в /list и попробуйте снова.",
        )
        return False

    await message.answer(
        task_card(task),
        reply_markup=task_actions_keyboard(task),
    )
    return True


@router.message(Command("edit"))
async def cmd_edit(
    message: Message,
    command: CommandObject,
    state: FSMContext,
) -> None:
    """
    Команда /edit.

    • /edit 3 — сразу открыть карточку задачи №3;
    • /edit — бот попросит ввести номер.
    """
    # Если пользователь был в другом диалоге (например, добавлял задачу),
    # начинаем редактирование с чистого листа.
    await state.clear()

    task_id_text = (command.args or "").strip().lstrip("#")

    # Если номер передан сразу — показываем карточку.
    if task_id_text.isdigit():
        await show_task_card(message, int(task_id_text))
        return

    await state.set_state(EditTask.waiting_for_id)
    await message.answer(
        "🔢 Введите номер задачи, которую нужно изменить.\n"
        "Номер виден в списке: /list\n\n"
        "Например: <code>3</code>\n"
        "Чтобы отменить — нажмите «Отмена» или введите /cancel.",
        reply_markup=cancel_keyboard(),
    )


@router.message(F.text == BTN_EDIT, StateFilter(None))
async def button_edit(message: Message, state: FSMContext) -> None:
    """Нажатие на кнопку «Изменить задачу» в главном меню."""
    await state.set_state(EditTask.waiting_for_id)
    await message.answer(
        "🔢 Введите номер задачи из списка /list.\n"
        "Например: <code>3</code>",
        reply_markup=cancel_keyboard(),
    )


@router.message(EditTask.waiting_for_id, F.text, ~F.text.startswith("/"))
async def process_task_id(message: Message, state: FSMContext) -> None:
    """Пользователь ввёл номер задачи — открываем карточку."""
    task_id_text = message.text.strip().lstrip("#")

    if not task_id_text.isdigit():
        await message.answer(
            "Нужен номер задачи — только цифры. Например: <code>3</code>"
        )
        return

    found = await show_task_card(message, int(task_id_text))

    if found:
        await state.clear()


@router.message(EditTask.waiting_for_id, ~F.text)
async def process_not_text(message: Message) -> None:
    """Если прислали не текст, просим номер ещё раз."""
    await message.answer("Пожалуйста, пришлите номер задачи текстом, например: 3")


async def refresh_card(callback: CallbackQuery, task: dict, notice: str) -> None:
    """Обновляет карточку после изменения и отвечает на нажатие кнопки."""
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            task_card(task),
            reply_markup=task_actions_keyboard(task),
        )
    await callback.answer(notice)


@router.callback_query(F.data.startswith("cat:"))
async def change_category(callback: CallbackQuery) -> None:
    """Смена категории по кнопке «🏷 Стандартная» / «🚨 Срочная»."""
    try:
        _, task_id_text, key = callback.data.split(":", 2)
        task_id = int(task_id_text)
        category = CATEGORY_KEYS[key]
    except (ValueError, KeyError):
        await callback.answer("Некорректные данные кнопки", show_alert=True)
        return

    task = await get_task(task_id)
    if task is None:
        await callback.answer("Задача не найдена", show_alert=True)
        return

    if task["category"] == category:
        await callback.answer("Эта категория уже выбрана")
        return

    await update_task_category(task_id, category)
    task["category"] = category
    await refresh_card(callback, task, f"Категория: {category}")


@router.callback_query(F.data.startswith("status:"))
async def change_status(callback: CallbackQuery) -> None:
    """Смена статуса по кнопкам «Новая» / «В работе» / «Выполнена»."""
    try:
        _, task_id_text, key = callback.data.split(":", 2)
        task_id = int(task_id_text)
        status = STATUS_KEYS[key]
    except (ValueError, KeyError):
        await callback.answer("Некорректные данные кнопки", show_alert=True)
        return

    task = await get_task(task_id)
    if task is None:
        await callback.answer("Задача не найдена", show_alert=True)
        return

    if task["status"] == status:
        await callback.answer("Этот статус уже выбран")
        return

    await update_task_status(task_id, status)
    task["status"] = status
    await refresh_card(callback, task, f"Статус: {status}")


@router.callback_query(F.data == "edit:close")
async def close_task_card(callback: CallbackQuery) -> None:
    """Кнопка «Закрыть» убирает карточку и её кнопки."""
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "✖️ Карточка закрыта.\n"
            "Открыть снова: <code>/edit 3</code>",
        )
    await callback.answer()
