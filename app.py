import streamlit as st
import logging
from sqlalchemy.orm import Session
from analyzer.nlp import TextAnalyzer
from src.db_src import User, verify_password, get_db, create_user, save_user_text, save_button_click, get_user_texts
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
st.set_page_config(page_title='NLP Text Analyzer', page_icon='📄')


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def get_db_session():
    db = next(get_db())
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
    login_clicked = st.button("Login", key="login_button")
    if login_clicked:
        if (re.match(r'^[A-Za-z0-9_]+$', username_input)) and (len(username_input) > 4):
            db = get_db_session()
            if db and (len(password_input) > 5):
                user = authenticate_user(db, username_input.lower(), password_input)
                if user:
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = user.username.lower()
                    st.session_state['page'] = 'nlp'
                    save_button_click(db, st.session_state['user_id'], "login_button")
                    st.session_state.text_compr = False
                    st.session_state.proc_compr = False
                    st.rerun()
                else:
                    st.error("Authentication Failed")
            else:
                st.error("Authentication failed, try again later")
        else:
            st.error('Error: username must contain only Latin letters, numbers and "_"; Min. length 5 chars.')

    register_clicked = st.button("Register", key="register_button")
    if register_clicked:
        st.session_state['page'] = 'register'
        st.rerun()


def register_page():
    st.title("Register")
    username_input = st.text_input("Username", key="register_username")
    password_input = st.text_input("Password", type="password", key="register_password")
    confirm_password_input = st.text_input("Confirm Password", type="password", key="confirm_password")

    signup_clicked = st.button("Sign Up", key="signup_button")
    if signup_clicked:
        if (re.match(r'^[A-Za-z0-9_]+$', username_input)) and (len(username_input) > 4):
            if (len(password_input) > 5) and (password_input == confirm_password_input):
                db = get_db_session()
                if db:
                    user = create_user(db, username_input.lower(), password_input)
                    if user:
                        st.session_state['user_id'] = user.username.lower()
                        save_button_click(db, st.session_state['user_id'], "signup_button")
                        st.session_state['authenticated'] = True
                        st.session_state['page'] = 'nlp'
                        st.session_state.text_compr = False
                        st.session_state.proc_compr = False
                        st.rerun()
                    else:
                        st.error("Username already exists.")
                else:
                    st.error("Error accessing the database.")
            else:
                st.error("Passwords do not match or are less than 6 chars long.")
        else:
            st.error('Error: username must contain only Latin letters, numbers and "_"; Min. length 5 chars.')

    back_to_login_clicked = st.button("Back to Login", key="back_to_login_button")
    if back_to_login_clicked:
        st.session_state['page'] = 'login'
        st.rerun()


def nlp_page():
    st.title("NLP Text Analyzer")

    col_text, col_hist = st.columns([8, 2.5])
    with col_text:
        text = st.text_area("Enter text for analysis", key="text_area")

    with col_hist:
        st.markdown("<div style='margin-top: 29px;'></div>", unsafe_allow_html=True)
        with st.expander("History", expanded=False):
            db = get_db_session()
            if db:
                user_history = get_user_texts(db, st.session_state['user_id'])[:10]
                if len(user_history):
                    for user_text in user_history:
                        st.code(user_text.replace('\n', ' ').strip(), language="python")
                else:
                    st.write("No user data")

    if text:
        with col_text:

            db = get_db_session()
            if db:
                save_user_text(db, st.session_state['user_id'], text)

            analyzer = TextAnalyzer(text)
            col4, col1, col3, col2 = st.columns([4, 3, 4, 5], vertical_alignment="center")
            result_placeholder = st.empty()

            with col1:
                if st.button("Emotion"):
                    st.session_state.text_compr = False
                    st.session_state.proc_compr = False
                    with result_placeholder:
                        sentiment = analyzer.analyze_sentiment()
                        st.write(f"Analysis result: {sentiment}")
                        if db:
                            save_button_click(db, st.session_state['user_id'], "sentiment_an")

            with col3:
                if st.button("Top Bigrams"):
                    st.session_state.text_compr = False
                    st.session_state.proc_compr = False
                    with result_placeholder:
                        top_bigrams = analyzer.top_bigrams()
                        if len(top_bigrams):
                            for bigram in top_bigrams:
                                st.write(f"• {' '.join(list(bigram))}")
                        else:
                            st.write(f"The service was unable to highlight the top bigrams sets in the text")
                        if db:
                            save_button_click(db, st.session_state['user_id'], "txt_tags")

            with col4:
                if st.button("Basic Analysis"):
                    st.session_state.text_compr = False
                    st.session_state.proc_compr = False
                    with result_placeholder:
                        analytics = analyzer.basic_text_analysis()
                        st.write(analytics)
                        if db:
                            save_button_click(db, st.session_state['user_id'], "txt_basic_an")

            with col2:
                if st.button("Similarity Analysis"):
                    st.session_state.text_compr = True
                    st.session_state.proc_compr = False

            if st.session_state.text_compr:
                with result_placeholder:
                    comparison_text = st.text_area("Enter text to compare", key="txt_compr")
                    if comparison_text:
                        st.session_state.proc_compr = True

            if st.session_state.proc_compr:
                st.session_state.proc_compr = False
                similarity = analyzer.text_similarity(comparison_text)
                st.write(f"Analysis result - text similarity is {similarity} / 1.00")
                if db:
                    save_button_click(db, st.session_state['user_id'], "txt_similar")


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
