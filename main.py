import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Config, load_config
from database.db import Database
from handlers.admin import router as admin_router
from handlers.launch_flow import router as launch_flow_router
from handlers.payment import router as payment_router
from handlers.start import router as start_router
from services.openai_service import OpenAIService
from services.pdf_generator import PDFGenerator


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    config: Config = load_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    db = Database(config.db_path)
    await db.create_table()

    openai_service = OpenAIService(config.openai_api_key)
    pdf_generator = PDFGenerator()

    dp["config"] = config
    dp["db"] = db
    dp["openai_service"] = openai_service
    dp["pdf_generator"] = pdf_generator

    dp.include_router(start_router)
    dp.include_router(launch_flow_router)
    dp.include_router(payment_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
