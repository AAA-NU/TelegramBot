import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from sqlalchemy.ext.asyncio import async_sessionmaker
from cachetools import TTLCache


class DBMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker):
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        async with self.session_maker() as session:
            data['session'] = session

            result = await handler(event, data)

            return result


class ThrottlingMiddleware(BaseMiddleware):

    def __init__(self, rate_limit: float = 0.7):
        self.cache = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        user = data.get('event_from_user')
        if not user:
            return await handler(event, data)

        if user.id in self.cache:
            if event.callback_query:
                await event.callback_query.answer()
            return

        self.cache[user.id] = None
        return await handler(event, data)
