from telethon import TelegramClient, events
from telethon.network.connection.tcpmtproxy import ConnectionTcpMTProxyRandomizedIntermediate
from config import API_ID, API_HASH, SESSION_NAME
from database import save_message, init_db, update_message_text
import asyncio
import os

# 👇 Настройка MTProto прокси
SECRET = "e84fd961332463d1be3a4f0f0be77717"

user_client = TelegramClient(
    SESSION_NAME,
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

async def start_collector():
    init_db()
    await user_client.start()
    print("[Collector] User session started")

    # Создаем папку для скачивания файлов, если её нет
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # 👇 ФУНКЦИЯ ДЛЯ СОХРАНЕНИЯ (чтобы не дублировать код)
    async def process_message(event, is_edited=False):
        msg = event.message
        chat = await event.get_chat()

        chat_type = "group" if hasattr(chat, "megagroup") else "channel"
        if hasattr(chat, "title"):
            chat_title = chat.title
        else:
            chat_title = getattr(chat, "username", str(chat.id))

        sender = await event.get_sender()
        sender_id = sender.id if sender else None
        sender_username = getattr(sender, "username", None) if sender else None
        sender_first = getattr(sender, "first_name", None) if sender else None
        sender_last = getattr(sender, "last_name", None) if sender else None

        # 👇 ПУНКТ 4: Скачивание медиафайлов
        media_type = None
        media_file_id = None
        media_path = None

        if msg.photo:
            media_type = "photo"
            media_file_id = msg.photo.id
        elif msg.document:
            media_type = "document"
            media_file_id = msg.document.id
        elif msg.video:
            media_type = "video"
            media_file_id = msg.video.id
        elif msg.voice:
            media_type = "voice"
            media_file_id = msg.voice.id

        if media_type:
            try:
                # Скачиваем файл в папку downloads
                media_path = await msg.download_media(file="downloads/")
                print(f"[Collector] Файл сохранен: {media_path}")
            except Exception as e:
                print(f"[Collector] Ошибка скачивания файла: {e}")

        reactions = None
        if hasattr(msg, "reactions") and msg.reactions:
            reactions = [{"emoji": r.reaction, "count": r.count}
                         for r in msg.reactions.results]

        # Если это редактирование — обновляем текст
        if is_edited:
            update_message_text(chat.id, msg.id, msg.text or "")
        else:
            # Обычное сохранение
            save_message(
                chat_id=chat.id,
                chat_title=chat_title,
                chat_type=chat_type,
                sender_id=sender_id,
                sender_username=sender_username,
                sender_first=sender_first,
                sender_last=sender_last,
                message_id=msg.id,
                date=msg.date,
                text=msg.text or "",
                media_type=media_type,
                media_file_id=media_file_id,
                media_path=media_path, # 👈 Передаем путь к файлу
                reactions=reactions,
                raw={"raw_text": msg.raw_text}
            )

    # Обработчик новых сообщений
    @user_client.on(events.NewMessage)
    async def handler_new(event):
        await process_message(event, is_edited=False)

    # 👇 ПУНКТ 6: Обработчик редактирования сообщений
    @user_client.on(events.MessageEdited)
    async def handler_edited(event):
        print(f"[Collector] Сообщение отредактировано: {event.message.id}")
        await process_message(event, is_edited=True)

    print("[Collector] Listening for new messages...")
    await user_client.run_until_disconnected()