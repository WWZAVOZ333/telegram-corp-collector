from telethon import TelegramClient, events
from telethon.network.connection.tcpmtproxy import ConnectionTcpMTProxyRandomizedIntermediate
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS
from database import get_messages, get_all_chats
from datetime import datetime
from telethon.tl.types import DocumentAttributeFilename

# SECRET для MTProto прокси
SECRET = "e84fd961332463d1be3a4f0f0be77717"

bot_client = TelegramClient(
    "admin_bot_session",
    API_ID,
    API_HASH,
    connection=ConnectionTcpMTProxyRandomizedIntermediate,
    proxy=('127.0.0.1', 1443, SECRET),
    device_model="Desktop",
    system_version="Windows 11",
    app_version="1.0.0",
    lang_code="ru",
    system_lang_code="ru-RU"
)

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def start_admin_bot():
    await bot_client.start(bot_token=BOT_TOKEN)
    print("[AdminBot] Started")

    @bot_client.on(events.NewMessage(pattern="/start"))
    async def start(event):
        if not is_admin(event.sender_id):
            await event.reply("Доступ запрещён.")
            return
        await event.reply(
            "Команды:\n"
            "/chats — список чатов\n"
            "/export <chat_id> [YYYY-MM-DD] [YYYY-MM-DD]\n"
            "Пример: /export 123456789 2025-01-01 2025-03-01\n"
            "⚠️ Выгрузка доступна только в личных сообщениях."
        )

    @bot_client.on(events.NewMessage(pattern="/chats"))
    async def list_chats(event):
        if not is_admin(event.sender_id):
            return
        chats = get_all_chats()
        if not chats:
            await event.reply("Нет сохранённых чатов.")
            return
        lines = [f"{c.id} — {c.title} ({c.type})" for c in chats]
        await event.reply("\n".join(lines))

    @bot_client.on(events.NewMessage(pattern=r"/export (\S+)(?: (\S+))?(?: (\S+))?"))
    async def export(event):
        if not is_admin(event.sender_id):
            return

        # 👇 ПРОВЕРКА: ЗАПРЕТ ВЫГРУЗКИ В ГРУППАХ (Пункт 3)
        if not event.is_private:
            await event.reply("Выгрузку данных можно запрашивать только в личных сообщениях с ботом.")
            return

        parts = event.pattern_match.groups()
        chat_id = int(parts[0])
        date_from = datetime.strptime(parts[1], "%Y-%m-%d") if parts[1] else None
        date_to = datetime.strptime(parts[2], "%Y-%m-%d") if parts[2] else None

        await event.reply(f"Ищу сообщения для чата {chat_id}...")

        messages = get_messages(chat_id, date_from, date_to)
        if not messages:
            await event.reply("Сообщений за указанный период не найдено.")
            return

        import csv, io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "sender_id", "text", "media_type", "reactions"])
        for m in messages:
            writer.writerow([
                m.date.isoformat() if m.date else "",
                m.sender_id or "",
                (m.text or ""),  # 👈 УБРАНА ОБРЕЗКА ДО 500 СИМВОЛОВ (Пункт 5)
                m.media_type or "",
                str(m.reactions or "")
            ])

        csv_bytes = output.getvalue().encode("utf-8")

        await event.reply(
            f"Выгрузка: {len(messages)} сообщений.",
            file=csv_bytes,
            attributes=[DocumentAttributeFilename("export.csv")]
        )

    await bot_client.run_until_disconnected()