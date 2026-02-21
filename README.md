# ai_launch_architect_bot

Production-ready Telegram-бот на Python 3.11 для генерации стратегии запуска личного бренда или digital-проекта с бесплатной и платной версией, подтверждением оплаты администратором, SQLite и PDF.

## Что должно быть установлено

1. Python 3.11
2. pip
3. virtualenv
4. Telegram Bot Token (через @BotFather)
5. OpenAI API Key

## Установка

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Windows-инструкция

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
создать .env
python main.py
```

## Переменные окружения (.env)

```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
ADMIN_ID=123456789
PAYMENT_DETAILS=СБП +7XXXXXXXXXX
PRICE=1990 RUB
```

## Запуск

```bash
python main.py
```
