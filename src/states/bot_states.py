from aiogram.fsm.state import StatesGroup, State


class ReportStates(StatesGroup):
    wait_message_with_photo = State()


class AdminMailingState(StatesGroup):
    wait_message = State()

