from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config, load_conf
import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.handlers import common_handlers, student_handlers, other_handlers
from src import handlers
from src.middleware.middleware import ThrottlingMiddleware, DBMiddleware
from src.database.database import async_session_maker
from src.database.database import engine, Base
from src.database import models



async def main():
    storage = MemoryStorage()

    config: Config = load_conf()

    bot = Bot(token=config.tgbot.token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)

    db_middleware = DBMiddleware(session_maker=async_session_maker)
    dp.update.middleware(db_middleware)

    throttling_middleware = ThrottlingMiddleware()
    dp.update.middleware(throttling_middleware)

    dp.include_router(common_handlers.router)
    dp.include_router(student_handlers.router)
    dp.include_router(other_handlers.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
