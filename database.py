from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from config import DB_URL

Base = declarative_base()

# Настройка кодировки для PostgreSQL
engine = create_engine(
    DB_URL,
    connect_args={"client_encoding": "utf8"}
)
SessionLocal = sessionmaker(bind=engine)


class Chat(Base):
    __tablename__ = "chats"
    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=True)
    type = Column(String)
    messages = relationship("Message", back_populates="chat")


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    messages = relationship("Message", back_populates="sender")


class Message(Base):
    __tablename__ = "messages"
    id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey("chats.id"), primary_key=True)
    sender_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    text = Column(Text, nullable=True)
    media_type = Column(String, nullable=True)
    media_file_id = Column(String, nullable=True)
    media_path = Column(String, nullable=True)  # 👈 ДОБАВЛЕНО: путь к скачанному файлу (Пункт 4)
    reactions = Column(JSON, nullable=True)
    raw_json = Column(JSON, nullable=True)

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()


def save_message(chat_id, chat_title, chat_type, sender_id, sender_username,
                 sender_first, sender_last, message_id, date, text,
                 media_type=None, media_file_id=None, media_path=None, reactions=None, raw=None):
    session = get_session()
    try:
        chat = session.get(Chat, chat_id)
        if not chat:
            chat = Chat(id=chat_id, title=chat_title, type=chat_type)
            session.add(chat)

        sender = session.get(User, sender_id) if sender_id else None
        if sender_id and not sender:
            sender = User(id=sender_id, username=sender_username,
                          first_name=sender_first, last_name=sender_last)
            session.add(sender)

        msg = session.get(Message, (message_id, chat_id))
        if msg:
            return

        msg = Message(
            id=message_id, chat_id=chat_id, sender_id=sender_id,
            date=date, text=text, media_type=media_type,
            media_file_id=media_file_id, media_path=media_path,  # 👈 ДОБАВЛЕНО media_path
            reactions=reactions, raw_json=raw
        )
        session.add(msg)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"DB error: {e}")
    finally:
        session.close()


# 👇 ОБНОВЛЕНО: limit=None по умолчанию, чтобы выгружать все сообщения (Пункт 5)
def get_messages(chat_id, date_from=None, date_to=None, limit=None):
    session = get_session()
    q = session.query(Message).filter(Message.chat_id == chat_id)
    if date_from:
        q = q.filter(Message.date >= date_from)
    if date_to:
        q = q.filter(Message.date <= date_to)

    if limit:
        result = q.order_by(Message.date.desc()).limit(limit).all()
    else:
        result = q.order_by(Message.date.desc()).all()

    session.close()
    return result


def get_all_chats():
    session = get_session()
    chats = session.query(Chat).all()
    session.close()
    return chats


# 👇 НОВАЯ ФУНКЦИЯ: обновление текста при редактировании (Пункт 6)
def update_message_text(chat_id, message_id, new_text):
    session = get_session()
    try:
        msg = session.get(Message, (message_id, chat_id))
        if msg:
            msg.text = new_text
            session.commit()
            print(f"[DB] Сообщение {message_id} обновлено")
    except Exception as e:
        session.rollback()
        print(f"DB error update: {e}")
    finally:
        session.close()