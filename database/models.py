from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    telegram_id: int
    username: Optional[str]
    full_name: Optional[str]
    idea: Optional[str]
    niche: Optional[str]
    audience: Optional[str]
    product: Optional[str]
    is_paid: int
    payment_pending: int
    created_at: str
