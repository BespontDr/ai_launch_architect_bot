from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.db import Database
from keyboards.inline import start_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, db: Database) -> None:
    user = message.from_user
    await db.create_user_if_not_exists(user.id, user.username, user.full_name)

    await message.answer(
        "Привет! Я помогу создать стратегию запуска личного бренда или digital-проекта.\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=start_keyboard(),
    )
