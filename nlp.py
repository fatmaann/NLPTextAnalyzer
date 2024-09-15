from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymorphy2
import re
import nltk

from nltk.tokenize import word_tokenize
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from collections import Counter
import logging

nltk.download('stopwords')
nltk.download('punkt_tab')

from nltk.corpus import stopwords


class TextAnalyzer:
    def __init__(self, text):
        self.text = text
        self.morph = pymorphy2.MorphAnalyzer()
        self.stop_words = set(stopwords.words('russian'))
        self.words = self._preprocess_text()
        logging.info("Текст успешно загружен и обработан.")

    def _preprocess_text(self):
        """Приведение текста к нижнему регистру и удаление стоп-слов."""
        words = word_tokenize(self.text.lower())
        filtered_words = [word for word in words if word.isalpha() and word not in self.stop_words]
        return filtered_words

    def analyze_sentiment(self):
        """Анализирует тональность текста (положительная или отрицательная)."""
        try:
            blob = TextBlob(self.text)
            sentiment = blob.sentiment.polarity
            if sentiment >= 0:
                return 'Позитивный'
            else:
                return 'Негативный'
        except Exception as e:
            logging.error(f"Ошибка при анализе тональности: {e}")
            return None

    def text_similarity(self, text2):
        """Сравнивает текущий текст с другим по косинусной схожести."""
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([self.text, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return similarity[0][0]
        except Exception as e:
            logging.error(f"Ошибка при сравнении текстов: {e}")
            return None

    def top_bigrams(self, freq_filter=3, top_n=3):
        """Находит топ-N биграмм с наибольшим PMI."""
        try:
            bigram_measures = BigramAssocMeasures()
            finder = BigramCollocationFinder.from_words(self.words)
            finder.apply_freq_filter(freq_filter)
            bigrams = finder.nbest(bigram_measures.pmi, top_n)
            return bigrams
        except Exception as e:
            logging.error(f"Ошибка при поиске биграмм: {e}")
            return None

    def get_pos(self, word):
        """Возвращает часть речи для заданного слова."""
        p = self.morph.parse(word)[0]
        return p.tag.POS

    def basic_text_analysis(self):
        """Выполняет базовый анализ текста: количество символов, слов, предложений, частей речи."""
        try:
            words = [word for word in word_tokenize(self.text.lower()) if word.isalpha()]
            sentences = re.split(r'[.!?]+', self.text)
            char_count = len(self.text)
            word_count = len(words)
            sentence_count = len(sentences)
            avg_word_length = sum(len(word) for word in words) / word_count if word_count != 0 else 0
            pos_counts = Counter([self.get_pos(word) for word in words])
            pos_counts = {k: v for k, v in pos_counts.items() if k}

            return {
                'Количество символов': char_count,
                'Количество слов': word_count,
                'Количество предложений': sentence_count,
                'Средняя длина слова': avg_word_length,
                'Части речи': pos_counts
            }
        except Exception as e:
            logging.error(f"Ошибка при базовом анализе текста: {e}")
            return None
