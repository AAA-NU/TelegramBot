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

from src.lexicon import lexicon_ru

router = Router()


@router.callback_query(F.data == "coworking")
async def process_coworking_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.COWORKING_TEXT)


@router.callback_query(F.data == "nvk_links")
async def process_nvk_links_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.NVK_LINKS_TEXT)


@router.callback_query(F.data == "check_in")
async def process_check_in_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.CHECK_IN_TEXT)


@router.callback_query(F.data == "report")
async def process_report_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.REPORT_TEXT)

