"""
Главный файл бота
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import config
from database import db
from handlers import user_router, games_router, admin_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Инициализация БД
    await db.init()
    logger.info("Database initialized")

    # Регистрация роутеров
    dp.include_router(user_router)
    dp.include_router(games_router)
    dp.include_router(admin_router)

    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
