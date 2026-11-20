"""Состояния (FSM) — «память» бота о том, что сейчас делает пользователь."""

from aiogram.fsm.state import State, StatesGroup


class AddTask(StatesGroup):
    """Сценарий добавления задачи."""

    # Бот ждёт, пока пользователь пришлёт текст задачи.
    waiting_for_text = State()


class EditTask(StatesGroup):
    """Сценарий изменения категории или статуса задачи."""

    # Бот ждёт номер задачи, которую нужно открыть.
    waiting_for_id = State()
