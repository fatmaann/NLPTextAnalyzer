import os
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymorphy2
import re

from collections import Counter
import logging
import nltk

from nltk.tokenize import word_tokenize
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

nltk.download('stopwords')
nltk.download('punkt_tab')
from nltk.corpus import stopwords


class TextAnalyzer:
    def __init__(self, text):
        self.text = text
        self.morph = pymorphy2.MorphAnalyzer()
        self.stop_words = set(stopwords.words('russian')).union(set(stopwords.words('english')))
        self.words = self._preprocess_text()
        logging.info("Text has been successfully loaded and processed")

    def _preprocess_text(self):
        words = word_tokenize(self.text.lower())
        filtered_words = [word for word in words if word.isalpha() and word not in self.stop_words]
        return filtered_words

    def analyze_sentiment(self):
        try:
            blob = TextBlob(self.text)
            sentiment = blob.sentiment.polarity
            if sentiment >= 0:
                return 'Positive'
            else:
                return 'Negative'
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {e}")
            return None

    def text_similarity(self, text2):
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([self.text, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return similarity[0][0]
        except Exception as e:
            logging.error(f"Error while comparing texts: {e}")
            return None

    def top_bigrams(self, ):
        try:
            bigram_measures = BigramAssocMeasures()
            freq_filter, top_n = 0, 0
            if len(self.words) < 500:
                freq_filter, top_n = [1, 5]
            elif 500 < len(self.words) < 2000:
                freq_filter, top_n = [2, 10]
            else:
                freq_filter, top_n = [3, 15]
            finder = BigramCollocationFinder.from_words(self.words)
            finder.apply_freq_filter(freq_filter)
            bigrams = finder.nbest(bigram_measures.pmi, top_n)
            return bigrams
        except Exception as e:
            logging.error(f"Error while searching for bigrams: {e}")
            return None

    def get_pos(self, word):
        p = self.morph.parse(word)[0]
        return p.tag.POS

    def basic_text_analysis(self):
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
                'Number of characters': char_count,
                'Number of words': word_count,
                'Number of sentences': sentence_count,
                'Average word length': avg_word_length,
                'Parts of speech': pos_counts
            }
        except Exception as e:
            logging.error(f"Basic text analysis error: {e}")
            return None
