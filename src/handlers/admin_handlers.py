import asyncio

from aiogram import Router, Bot, F, BaseMiddleware
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.exceptions import TelegramUnauthorizedError, TelegramForbiddenError
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, TelegramObject
from aiogram.types import ChatMemberUpdated, Chat, CallbackQuery
from aiogram.filters import ChatMemberUpdatedFilter, Command, StateFilter, CommandStart
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters.chat_member_updated import IS_NOT_MEMBER, ADMINISTRATOR
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.token import TokenValidationError
from requests import HTTPError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.callbacks.callback_data import FAQCallback, CoworkingCallback, DateCallback, TimeCallback, RoomsCallback, \
    EndRoomCallback, GroupReportCallback
from src.keyboards import keyboards_ru
from src.lexicon import lexicon_ru
from src.states.bot_states import ReportStates, AdminMailingState
from typing import Callable, Dict, Awaitable, Any
from src.backend.users_controller import BackendUsersController
from src.backend.spaces_controller import SpacesApiController


class AdminAccessMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Получаем объект пользователя aiogram из данных события
        event_user = data.get('event_from_user')
        if not event_user:
            # Событие без пользователя (например, опрос в канале), пропускаем
            return await handler(event, data)

        # Запрашиваем пользователя из нашего API
        user_from_api = BackendUsersController.get_user_by_tg_id(event_user.id)

        # ГЛАВНАЯ ЛОГИКА ФИЛЬТРАЦИИ
        if user_from_api and user_from_api.role == 'admin':
            # Если пользователь - студент, обогащаем данные и передаем управление дальше
            data['user'] = user_from_api
            return await handler(event, data)

        raise CancelHandler()


# filters.py

from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


# Предположим, ваш контроллер находится здесь
# from a_folder.controllers import BackendUsersController

class RoleFilter(BaseFilter):
    def __init__(self, allowed_role: str):
        self.allowed_role = allowed_role

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        # Проверяем, есть ли вообще пользователь в событии
        if not event.from_user:
            return False
        try:
            # Делаем запрос в наше API прямо внутри фильтра
            user_from_api = BackendUsersController.get_user_by_tg_id(str(event.from_user.id))
        except HTTPError:
            return False
        print(user_from_api)
        # Если пользователь найден и его роль совпадает с разрешенной - фильтр пройден
        if user_from_api and user_from_api.role == self.allowed_role:
            return True

        # Во всех остальных случаях - не пропускаем
        return False


router = Router()
router.message.filter(RoleFilter("admin"))
router.callback_query.filter(RoleFilter("admin"))


@router.message(CommandStart())
async def process_start_for_admin(message: Message):
    await message.answer(text=lexicon_ru.START_ADMIN_MESSAGE_TEXT,
                         reply_markup=keyboards_ru.gen_start_admin_keyboard())


@router.callback_query(F.data == "mailing")
async def process_mailing_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminMailingState.wait_message)
    await callback.message.edit_text(text=lexicon_ru.MAILING_TEXT, reply_markup=keyboards_ru.menu_keyboard)


@router.message(StateFilter(AdminMailingState.wait_message))
async def process_mailing_message(message: Message):
    users = BackendUsersController.get_users()
    for user_model in users:
        try:
            await message.send_copy(chat_id=user_model.tgID)
        except TelegramForbiddenError:
            pass

    await message.answer(text=lexicon_ru.SUCCESS_MAILING, reply_markup=keyboards_ru.menu_keyboard)


@router.callback_query(F.data == "booking_room")
async def process_booking_room_callback(callback: CallbackQuery):
    rooms = SpacesApiController.get_rooms()
    await callback.message.edit_text(text=lexicon_ru.BOOKING_ROOM_TEXT,
                                     reply_markup=keyboards_ru.gen_rooms_keyboard(rooms=rooms))


@router.callback_query(RoomsCallback.filter())
async def process_rooms_callback(callback: CallbackQuery, callback_data: RoomsCallback):
    SpacesApiController.update_room_booking(room_id=callback_data.room_id, is_booked=True,
                                            booked_by=str(callback.from_user.id))
    await callback.message.edit_text(text=lexicon_ru.SUCCESS_BOOKING_ROOM.format(id=callback_data.room_id),
                                     reply_markup=keyboards_ru.gen_booking_end_keyboard(room_id=callback_data.room_id))


@router.callback_query(EndRoomCallback.filter())
async def process_end_room_callback(callback: CallbackQuery, callback_data: EndRoomCallback):
    SpacesApiController.update_room_booking(room_id=callback_data.room_id,
                                            is_booked=False, booked_by="")
    await callback.message.edit_text(text=lexicon_ru.END_ROOM_BOOKING_TEXT, reply_markup=keyboards_ru.menu_keyboard)


@router.callback_query(F.data == "admin_check_in")
async def process_admin_check_in_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.CHECK_IN_ADMIN_TEXT, reply_markup=keyboards_ru.menu_keyboard)


@router.callback_query(F.data == "menu")
async def process_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=lexicon_ru.START_ADMIN_MESSAGE_TEXT,
                                     reply_markup=keyboards_ru.gen_start_admin_keyboard())


@router.callback_query(GroupReportCallback.filter())
async def process_group_report_callback(callback: CallbackQuery, callback_data: GroupReportCallback, bot: Bot):
    await bot.send_message(chat_id=callback_data.user_id, text=lexicon_ru.REPORT_GROUP_PROCESSED_TEXT,
                           reply_markup=keyboards_ru.menu_keyboard)
    await callback.message.edit_text(text=lexicon_ru.SUCCESS_REPORT)
