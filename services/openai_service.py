import asyncio
import logging

from openai import OpenAI


logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)

    async def generate_text(self, prompt: str) -> str:
        def _request() -> str:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по запуску digital-проектов и личного бренда.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("OpenAI returned empty content")
            return content.strip()

        try:
            return await asyncio.to_thread(_request)
        except Exception as exc:
            logger.exception("OpenAI generation failed")
            raise RuntimeError("Ошибка генерации ответа. Попробуйте позже.") from exc
