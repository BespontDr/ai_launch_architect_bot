import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    openai_api_key: str
    admin_id: int
    payment_details: str
    price: str
    db_path: str = "database.db"



def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    admin_id_raw = os.getenv("ADMIN_ID", "0")
    payment_details = os.getenv("PAYMENT_DETAILS", "Реквизиты не указаны")
    price = os.getenv("PRICE", "1000 RUB")

    if not bot_token:
        raise ValueError("BOT_TOKEN is not set")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    try:
        admin_id = int(admin_id_raw)
    except ValueError as exc:
        raise ValueError("ADMIN_ID must be an integer") from exc

    if admin_id <= 0:
        raise ValueError("ADMIN_ID must be set and greater than 0")

    return Config(
        bot_token=bot_token,
        openai_api_key=openai_api_key,
        admin_id=admin_id,
        payment_details=payment_details,
        price=price,
    )
