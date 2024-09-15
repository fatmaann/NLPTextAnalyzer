import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import bcrypt
from uuid import uuid4

# Получение URL базы данных из переменной окружения или использование SQLite как запасной вариант
DATABASE_URL = os.getenv("DATABASE_URL")

# Создание движка базы данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, unique=True)
    username = Column(String, index=True)
    hashed_password = Column(String)

    # Связь с таблицей текстов и таблицей нажатий
    texts = relationship("UserText", back_populates="user")
    button_clicks = relationship("ButtonClick", back_populates="user")


# Модель для хранения текстов пользователей
class UserText(Base):
    __tablename__ = "user_texts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    text = Column(String, nullable=False)

    # Связь с таблицей пользователей
    user = relationship("User", back_populates="texts")


# Модель для хранения статистики нажатий на кнопки
class ButtonClick(Base):
    __tablename__ = "button_clicks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    button_name = Column(String, nullable=False)

    # Связь с таблицей пользователей
    user = relationship("User", back_populates="button_clicks")


# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)


# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_id():
    return uuid4().hex


# Функция для хеширования паролей
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# Функция для проверки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# Функция для создания пользователя (используется один раз для добавления пользователей в базу)
def create_user(db, username: str, password: str):
    hashed_password = hash_password(password)
    user = User(user_id=get_user_id(), username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Функция для сохранения текста, отправленного пользователем
def save_user_text(db, user_id: str, text: str):
    user_text = UserText(user_id=user_id, text=text)
    db.add(user_text)
    db.commit()
    db.refresh(user_text)
    return user_text


# Функция для сохранения нажатия на кнопку
def save_button_click(db, user_id: str, button_name: str):
    button_click = ButtonClick(user_id=user_id, button_name=button_name)
    db.add(button_click)
    db.commit()
    db.refresh(button_click)
    return button_click
