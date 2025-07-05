from aiogram import Bot, Dispatcher
from handlers import user_handlers, other_handlers
from config import Config, load_conf
import asyncio

async def main():
    config: Config = load_conf()

    bot = Bot(token=config.tgbot.token)
    dp = Dispatcher()

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())