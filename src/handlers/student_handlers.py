import asyncio

from aiogram import Router, Bot, F, BaseMiddleware
from aiogram.exceptions import TelegramUnauthorizedError
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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.keyboards import keyboards_ru
from src.lexicon import lexicon_ru
from src.states.bot_states import ReportStates
from typing import Callable, Dict, Awaitable, Any
from src.backend.users_controller import BackendUsersController

ADMIN_GROUP_ID = -4904031171


class StudentAccessMiddleware(BaseMiddleware):
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
        if user_from_api and user_from_api.role == 'student':
            # Если пользователь - студент, обогащаем данные и передаем управление дальше
            data['user'] = user_from_api
            return await handler(event, data)

        # Если пользователь не студент или не найден в API,
        # обработка на этом роутере прекращается.
        # Мы НЕ вызываем handler.
        # Опционально: можно ответить пользователю.
        if isinstance(event, Message):
            await event.answer("К сожалению, доступ к этому разделу есть только у студентов.")
        elif isinstance(event, CallbackQuery):
            await event.answer("Доступ запрещен", show_alert=True)

        # Так как мы не вызвали await handler(...), aiogram не будет
        # искать обработчики для этого события в данном роутере.
        return


router = Router()
router.message.middleware(StudentAccessMiddleware())
router.callback_query.middleware(StudentAccessMiddleware())


@router.callback_query(F.data == "coworking")
async def process_coworking_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.COWORKING_TEXT,
                                     reply_markup=keyboards_ru.gen_coworking_keyboard())


@router.callback_query(F.data == "nvk_links")
async def process_nvk_links_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.NVK_LINKS_TEXT,
                                     reply_markup=keyboards_ru.gen_nvk_links_keyboard())


@router.callback_query(F.data == "check_in")
async def process_check_in_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.CHECK_IN_TEXT,
                                     reply_markup=keyboards_ru.gen_check_in_keyboard())


@router.callback_query(F.data == "report")
async def process_report_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReportStates.wait_message_with_photo)
    await callback.message.edit_text(text=lexicon_ru.REPORT_TEXT,
                                     reply_markup=keyboards_ru.gen_report_keyboard())


@router.message(F.photo, StateFilter(ReportStates.wait_message_with_photo))
async def process_report_photo(message: Message):
    await message.send_copy(chat_id=ADMIN_GROUP_ID) # Тут можно добавить функцию обработки(то есть админ нажимает, что репорт обработан и пользователю приходит уведомление.)
    await message.answer(text="Успешно, твоя заявка отправлена!", reply_markup=keyboards_ru.menu_keyboard)


@router.callback_query(F.data == "FAQ")
async def process_faq_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.FAQ_TEXT,
                                     reply_markup=keyboards_ru.gen_faq_keyboard())
