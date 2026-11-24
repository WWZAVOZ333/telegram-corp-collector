import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем .env (с указанием кодировки, чтобы избежать ошибки 0xc2)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, encoding="utf-8")

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]

SESSION_NAME = "collector_session"

DB_USER = "postgres"
DB_PASS = "qwerty"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "corp_messages"

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"