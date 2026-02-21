from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from config import Config
from database.db import Database
from keyboards.inline import admin_payment_keyboard

router = Router()


@router.callback_query(F.data == "buy_full_strategy")
async def buy_full_strategy(callback: CallbackQuery, config: Config) -> None:
    text = (
        "Для получения полной стратегии оплатите доступ.\n\n"
        f"Стоимость: {config.price}\n"
        f"Реквизиты: {config.payment_details}\n\n"
        "После оплаты отправьте фото чека в этот чат."
    )
    await callback.message.answer(text)
    await callback.answer()


@router.message(F.photo)
async def payment_receipt_handler(message: Message, db: Database, config: Config) -> None:
    user = await db.get_user(message.from_user.id)
    if user is None:
        await message.answer("Пожалуйста, сначала нажмите /start.")
        return

    if user.is_paid:
        await message.answer("Ваша оплата уже подтверждена.")
        return

    await db.set_payment_pending(message.from_user.id, True)

    photo = message.photo[-1].file_id
    caption = (
        "Новая заявка на подтверждение оплаты\n\n"
        f"User ID: {message.from_user.id}\n"
        f"Username: @{message.from_user.username if message.from_user.username else '-'}\n"
        f"Full name: {message.from_user.full_name or '-'}"
    )

    await message.bot.send_photo(
        chat_id=config.admin_id,
        photo=photo,
        caption=caption,
        reply_markup=admin_payment_keyboard(message.from_user.id),
    )
    await message.answer("Чек получен и отправлен администратору на проверку.")
