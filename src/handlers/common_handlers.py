from typing import Callable, Dict, Awaitable, Any

from aiogram import Router, Bot, F, BaseMiddleware
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, TelegramObject
from aiogram.types import ChatMemberUpdated, Chat, CallbackQuery
from aiogram.filters import ChatMemberUpdatedFilter, Command, StateFilter, CommandStart, CommandObject
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters.chat_member_updated import IS_NOT_MEMBER, ADMINISTRATOR
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.backend.users_controller import BackendUsersController
from src.backend.qr_controller import VerifyApiController

from src.keyboards import keyboards_ru
from src.lexicon import lexicon_ru

router = Router()


@router.message(CommandStart(deep_link=True, magic=F.args))
async def process_start_with_deeplink(message: Message, command: CommandObject):
    deeplink_param = command.args
    verify_result = VerifyApiController.verify_uuid(uuid=deeplink_param)
    if verify_result.valid:
        await message.answer(text=lexicon_ru.SUCCESS_CHECK_IN)
    else:
        await message.answer(text=lexicon_ru.UNSUCCESS_CHECK_IN)


@router.message(CommandStart())
async def show_menu(message: Message, state: FSMContext):
    BackendUsersController.create_user(
        tgID=str(message.from_user.id), language="ru")
    await state.clear()
    await message.answer(text=lexicon_ru.START_MESSAGE_TEXT,
                         reply_markup=keyboards_ru.gen_start_keyboard())


@router.message(Command(commands='help'))
async def process_help(message: Message):
    await message.answer(text=lexicon_ru.HELP_MESSAGE_TEXT)


@router.callback_query(F.data == "menu")
async def process_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=lexicon_ru.START_MESSAGE_TEXT,
                                     reply_markup=keyboards_ru.gen_start_keyboard())
    await callback.answer()
