import streamlit as st
import logging
from sqlalchemy.orm import Session
from nlp import TextAnalyzer
from db_src import User, verify_password, get_db, create_user, save_user_text, save_button_click

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
st.set_page_config(page_title=' NLP Text Analyzer', page_icon='📄')


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


def login_page():
    st.title("Login")
    username_input = st.text_input("Username", key="login_username")
    password_input = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        db = get_db_session()
        if db:
            user = authenticate_user(db, username_input, password_input)
            if user:
                st.session_state['authenticated'] = True
                st.session_state['user_id'] = user.user_id
                st.session_state['page'] = 'nlp'
                save_button_click(db, st.session_state['user_id'], "login_button")
            else:
                st.error("Authentication Failed")

    if st.button("Register", key="register_button"):
        st.session_state['page'] = 'register'


def register_page():
    st.title("Register")
    username_input = st.text_input("Username", key="register_username")
    password_input = st.text_input("Password", type="password", key="register_password")
    confirm_password_input = st.text_input("Confirm Password", type="password", key="confirm_password")

    if st.button("Sign Up", key="signup_button"):
        if password_input == confirm_password_input:
            db = get_db_session()
            if db:
                user = create_user(db, username_input, password_input)
                if user:
                    st.success("Registration successful! You can now log in.")
                    st.session_state['user_id'] = user.user_id
                    save_button_click(db, st.session_state['user_id'], "signup_button")
                    st.session_state['page'] = 'login'
                else:
                    st.error("Username already exists")
            else:
                st.error("Error accessing the database")
        else:
            st.error("Passwords do not match")

    if st.button("Back to Login", key="back_to_login_button"):
        st.session_state['page'] = 'login'


def nlp_page():
    st.title("NLP Text Analyzer")
    text = st.text_area("Введите текст для анализа", key="text_area")

    if text:
        # Сохраняем текст в базу данных
        db = get_db_session()
        if db:
            save_user_text(db, st.session_state['user_id'], text)

        analyzer = TextAnalyzer(text)

        tab1, tab2, tab3, tab4 = st.tabs(
            ["Sentiment Analysis", "Text Similarity", "Top Bigrams", "Basic Text Analysis"])

        with tab1:
            st.header("Sentiment Analysis")
            sentiment = analyzer.analyze_sentiment()
            st.write(f"Тональность текста: {sentiment}")

            # Сохраняем нажатие на вкладку "Sentiment Analysis"
            if db:
                save_button_click(db, st.session_state['user_id'], "sentiment_an")

        with tab2:
            st.header("Text Similarity")
            comparison_text = st.text_area("Введите текст для сравнения", key="txt_compr")
            if comparison_text:
                similarity = analyzer.text_similarity(comparison_text)
                st.write(f"Схожесть текста: {similarity}")

            # Сохраняем нажатие на вкладку "Text Similarity"
            if db:
                save_button_click(db, st.session_state['user_id'], "txt_similar")

        with tab3:
            st.header("Tags")
            top_bigrams = analyzer.top_bigrams()
            st.write(f"Топ тэгов в тексте: {top_bigrams}")

            # Сохраняем нажатие на вкладку "Tags"
            if db:
                save_button_click(db, st.session_state['user_id'], "txt_tags")

        with tab4:
            st.header("Basic Text Analysis")
            analytics = analyzer.basic_text_analysis()
            st.write(analytics)

            # Сохраняем нажатие на вкладку "Basic Text Analysis"
            if db:
                save_button_click(db, st.session_state['user_id'], "txt_basic_an")


# Логика переключения страниц
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

if st.session_state['page'] == 'login':
    login_page()
elif st.session_state['page'] == 'register':
    register_page()
elif st.session_state['page'] == 'nlp':
    if st.session_state['authenticated']:
        nlp_page()
    else:
        st.error("You need to be logged in to access this page.")
