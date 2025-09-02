from aiogram import Router, Bot, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.types import ChatMemberUpdated, Chat, CallbackQuery
from aiogram.filters import ChatMemberUpdatedFilter, Command, StateFilter, CommandStart
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters.chat_member_updated import IS_NOT_MEMBER, ADMINISTRATOR
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.lexicon import lexicon_ru

router = Router()


@router.message(F.text)
async def process_some_message(message: Message):
    await message.answer(text=lexicon_ru.SOME_MESSAGE_TEXT)


