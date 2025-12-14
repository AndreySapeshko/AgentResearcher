import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from app.config import TELEGRAM_BOT_TOKEN
from app.bot.handlers import router

dp = Dispatcher()
bot = Bot(TELEGRAM_BOT_TOKEN)


async def main():

    dp.include_router(router)
    print("🤖 Bot service started")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
