from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Запустить проект", callback_data="start_launch")
    return builder.as_markup()


def skip_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Пропустить", callback_data="skip_step")
    return builder.as_markup()


def get_full_strategy_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Получить полную стратегию", callback_data="buy_full_strategy")
    return builder.as_markup()


def admin_payment_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Одобрить", callback_data=f"approve:{telegram_id}")
    builder.button(text="❌ Отказать", callback_data=f"reject:{telegram_id}")
    builder.adjust(2)
    return builder.as_markup()
