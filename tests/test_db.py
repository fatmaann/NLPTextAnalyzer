import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db_src import Base, User, UserText, ButtonClick, create_user, save_user_text, save_button_click

# Создаем базу данных в памяти для тестирования
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope='module')
def db():
    # Создаем тестовую базу данных
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_user(db):
    user = create_user(db, username="testuser", password="testpass")
    assert user is not None
    assert user.username == "testuser"

    # Проверяем, что пользователь сохранен в базе данных
    saved_user = db.query(User).filter_by(username="testuser").first()
    assert saved_user is not None
    assert saved_user.hashed_password != "testpass"  # Пароль должен быть зашифрован


def test_create_duplicate_user(db):
    # Попробуем создать пользователя с тем же именем
    user = create_user(db, username="testuser", password="testpass")
    assert user is False  # Второй пользователь с таким же именем не должен быть создан


def test_save_user_text(db):
    # Сохраняем текст для пользователя
    user_text = save_user_text(db, user_id="testuser", text="Hello World")
    assert user_text is not None
    assert user_text.text == "Hello World"

    # Проверяем, что текст сохранен в базе данных
    saved_text = db.query(UserText).filter_by(user_id="testuser").first()
    assert saved_text is not None
    assert saved_text.text == "Hello World"


def test_save_button_click(db):
    # Сохраняем клик по кнопке
    button_click = save_button_click(db, username="testuser", button_name="Submit")
    assert button_click is not None
    assert button_click.button_name == "Submit"

    # Проверяем, что клик сохранен в базе данных
    saved_click = db.query(ButtonClick).filter_by(user_id="testuser").first()
    assert saved_click is not None
    assert saved_click.button_name == "Submit"