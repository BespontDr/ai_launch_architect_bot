import aiosqlite
from typing import Optional

from database.models import User


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    async def create_table(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    username TEXT,
                    full_name TEXT,
                    idea TEXT,
                    niche TEXT,
                    audience TEXT,
                    product TEXT,
                    is_paid BOOLEAN DEFAULT 0,
                    payment_pending BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.commit()

    async def create_user_if_not_exists(
        self,
        telegram_id: int,
        username: Optional[str],
        full_name: Optional[str],
    ) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR IGNORE INTO users (telegram_id, username, full_name)
                VALUES (?, ?, ?)
                """,
                (telegram_id, username, full_name),
            )
            await db.commit()

    async def get_user(self, telegram_id: int) -> Optional[User]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return User(**dict(row))

    async def update_user_field(self, telegram_id: int, field: str, value: Optional[str]) -> None:
        allowed_fields = {"idea", "niche", "audience", "product", "username", "full_name"}
        if field not in allowed_fields:
            raise ValueError(f"Unsupported field: {field}")

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"UPDATE users SET {field} = ? WHERE telegram_id = ?",
                (value, telegram_id),
            )
            await db.commit()

    async def set_user_paid(self, telegram_id: int, is_paid: bool = True) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_paid = ? WHERE telegram_id = ?",
                (1 if is_paid else 0, telegram_id),
            )
            await db.commit()

    async def set_payment_pending(self, telegram_id: int, pending: bool) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET payment_pending = ? WHERE telegram_id = ?",
                (1 if pending else 0, telegram_id),
            )
            await db.commit()
