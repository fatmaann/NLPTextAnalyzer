import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import bcrypt

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    hashed_password = Column(String)

    texts = relationship("UserText", back_populates="user")
    button_clicks = relationship("ButtonClick", back_populates="user")


class UserText(Base):
    __tablename__ = "user_texts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.username"), nullable=False)
    text = Column(String, nullable=False)

    user = relationship("User", back_populates="texts")


class ButtonClick(Base):
    __tablename__ = "button_clicks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.username"), nullable=False)
    button_name = Column(String, nullable=False)
    click_timestamp = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="button_clicks")


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_user(db, username: str, password: str):
    existing_user = db.query(User).filter_by(username=username).first()
    if existing_user:
        return False

    hashed_password = hash_password(password)
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_user_text(db, user_id: str, text: str):
    last_text = db.query(UserText).filter(UserText.user_id == user_id).order_by(UserText.id.desc()).first()
    if last_text and last_text.text == text:
        return None
    user_text = UserText(user_id=user_id, text=text)
    db.add(user_text)
    db.commit()
    db.refresh(user_text)
    return user_text


def save_button_click(db, username: str, button_name: str):
    button_click = ButtonClick(user_id=username, button_name=button_name)
    db.add(button_click)
    db.commit()
    db.refresh(button_click)
    return button_click


def get_user_texts(db, username: str):
    user_texts = db.query(UserText).filter(UserText.user_id == username).order_by(UserText.id.desc()).all()
    for text in user_texts[5:]:
        db.delete(text)
    db.commit()
    return [text.text for text in user_texts[:5]]
