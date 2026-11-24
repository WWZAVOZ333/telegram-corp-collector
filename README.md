# Сборщик корпоративных переписок в Telegram

## Описание
Проект собирает сообщения из Telegram (текст, медиа, реакции) и сохраняет их в PostgreSQL. Бот-администратор позволяет выгружать историю в формате CSV.

## Установка
1. Установите зависимости: `pip install -r requirements.txt`
2. Установите PostgreSQL и создайте базу данных `telegram_collector`.

## Настройка .env файла
Создайте файл `.env` в корне проекта и заполните его:

| Переменная | Описание | Пример заполнения |
| :--- | :--- | :--- |
| `TELEGRAM_API_ID` | ID приложения с my.telegram.org | `12345678` |
| `TELEGRAM_API_HASH` | Хэш приложения с my.telegram.org | `abcdef1234567890abcdef1234567890` |
| `TELEGRAM_PHONE` | Номер телефона аккаунта-сборщика | `+79991234567` |
| `TELEGRAM_BOT_TOKEN` | Токен бота от BotFather | `123456:ABC-DEF...` |
| `ADMIN_IDS` | Telegram ID админов (через запятую) | `987654321` |
| `DATABASE_URL` | Строка подключения к PostgreSQL | `postgresql://postgres:pass@localhost:5432/telegram_collector` |