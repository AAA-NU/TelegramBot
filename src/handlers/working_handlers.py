import asyncio

from aiogram import Router, Bot, F
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
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


ADMIN_GROUP_ID = -4904031171

router = Router()


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
async def process_report_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.REPORT_TEXT,
                                     reply_markup=keyboards_ru.gen_report_keyboard())


@router.message(F.photo)
async def process_report_photo(message: Message):
    await message.send_copy(chat_id=ADMIN_GROUP_ID) # Тут можно добавить функцию обработки(то есть админ нажимает, что репорт обработан и пользователю приходит уведомление.)
    await message.answer(text="Успешно, твоя заявка отправлена!", reply_markup=keyboards_ru.menu_keyboard)
