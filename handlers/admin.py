from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile

from config import Config
from database.db import Database
from services.openai_service import OpenAIService
from services.pdf_generator import PDFGenerator
from services.prompt_builder import build_full_prompt

router = Router()


@router.callback_query(F.data.startswith("approve:"))
async def approve_payment(
    callback: CallbackQuery,
    db: Database,
    config: Config,
    openai_service: OpenAIService,
    pdf_generator: PDFGenerator,
) -> None:
    if callback.from_user.id != config.admin_id:
        await callback.answer("Недостаточно прав.", show_alert=True)
        return

    telegram_id = int(callback.data.split(":", maxsplit=1)[1])
    user = await db.get_user(telegram_id)
    if user is None:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    await db.set_user_paid(telegram_id, True)
    await db.set_payment_pending(telegram_id, False)

    prompt = build_full_prompt(user)
    try:
        strategy = await openai_service.generate_text(prompt)
        pdf_path = await pdf_generator.create_strategy_pdf(telegram_id, strategy)
        await callback.bot.send_document(
            chat_id=telegram_id,
            document=FSInputFile(path=pdf_path),
            caption="Оплата подтверждена. Вот ваша полная стратегия 🚀",
        )
    except Exception:
        await callback.bot.send_message(
            chat_id=telegram_id,
            text="Оплата подтверждена, но при генерации стратегии произошла ошибка. Напишите администратору.",
        )
        await callback.bot.send_message(
            chat_id=config.admin_id,
            text=f"Ошибка генерации стратегии для пользователя {telegram_id}.",
        )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.bot.send_message(
        chat_id=config.admin_id,
        text=f"Пользователь {telegram_id} успешно одобрен.",
    )
    await callback.answer("Оплата одобрена")


@router.callback_query(F.data.startswith("reject:"))
async def reject_payment(callback: CallbackQuery, db: Database, config: Config) -> None:
    if callback.from_user.id != config.admin_id:
        await callback.answer("Недостаточно прав.", show_alert=True)
        return

    telegram_id = int(callback.data.split(":", maxsplit=1)[1])
    await db.set_payment_pending(telegram_id, False)

    await callback.bot.send_message(
        chat_id=telegram_id,
        text=(
            "Ваш платеж не подтвержден. Пожалуйста, проверьте перевод и отправьте корректный чек."
        ),
    )
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.bot.send_message(
        chat_id=config.admin_id,
        text=f"Платеж пользователя {telegram_id} отклонен.",
    )
    await callback.answer("Платеж отклонен")
