import streamlit as st
import logging
from sqlalchemy.orm import Session
from nlp import TextAnalyzer
from db_src import User, verify_password, get_db, create_user  # Импортируйте функцию создания пользователя

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Функция аутентификации пользователя
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


# Получение сессии для работы с базой данных
def get_db_session():
    db = next(get_db())  # Извлекаем сессию из генератора
    try:
        return db
    except Exception as e:
        logging.error(f"Error accessing DB: {e}")
        return None
    finally:
        db.close()


# Страница аутентификации
def login_page():
    st.title("Login")
    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")

    if st.button("Login"):
        db = get_db_session()  # Получаем сессию для работы с базой данных
        if db:
            user = authenticate_user(db, username_input, password_input)

            if user:
                st.success(f"Authenticated Successfully. Welcome, {user.username}!")
                st.session_state['authenticated'] = True
            else:
                st.error("Authentication Failed")
        else:
            st.error("Could not connect to the database")

    if st.button("Register"):
        st.session_state['page'] = 'register'


# Страница регистрации
def register_page():
    st.title("Register")
    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")
    confirm_password_input = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password_input == confirm_password_input:
            db = get_db_session()  # Получаем сессию для работы с базой данных
            if db:
                if db.query(User).filter(User.username == username_input).first():
                    st.error("Username already exists")
                else:
                    create_user(db, username_input, password_input)
                    st.success("Registration successful! You can now log in.")
                    st.session_state['page'] = 'login'
            else:
                st.error("Could not connect to the database")
        else:
            st.error("Passwords do not match")

    if st.button("Back to Login"):
        st.session_state['page'] = 'login'


# Проверка сессии аутентификации и страницы
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# Показываем соответствующую страницу
if st.session_state['page'] == 'login':
    login_page()
elif st.session_state['page'] == 'register':
    register_page()

# Основная страница
if st.session_state['authenticated']:
    st.title("NLP Text Analyzer")

    text = st.text_area("Введите текст для анализа", "")

    if text:
        analyzer = TextAnalyzer(text)

        tab1, tab2, tab3, tab4 = st.tabs(
            ["Sentiment Analysis", "Text Similarity", "Top Bigrams", "Basic Text Analysis"])

        with tab1:
            st.header("Sentiment Analysis")
            sentiment = analyzer.analyze_sentiment()
            st.write(f"Тональность текста: {sentiment}")

        with tab2:
            st.header("Text Similarity")
            comparison_text = st.text_area("Введите текст для сравнения")
            if comparison_text:
                similarity = analyzer.text_similarity(comparison_text)
                st.write(f"Схожесть текста: {similarity}")

        with tab3:
            st.header("Tags")
            top_bigrams = analyzer.top_bigrams()
            st.write(f"Топ тэгов в тексте: {top_bigrams}")

        with tab4:
            st.header("Basic Text Analysis")
            analytics = analyzer.basic_text_analysis()
            st.write(analytics)
