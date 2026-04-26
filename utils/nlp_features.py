"""
NLP Feature Extraction Module
Provides TF-IDF keyword extraction and VADER sentiment analysis
for resume text and video transcripts.
"""

import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon (one-time, silent)
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)


def extract_keywords_tfidf(text, top_n=10):
    """Extract top keywords from text using TF-IDF.

    Splits text into sentence-level documents for TF-IDF to work on,
    then ranks terms by their TF-IDF score.

    Args:
        text: The resume or transcript text
        top_n: Number of top keywords to return

    Returns:
        list: Top keywords sorted by importance, e.g. ["Python", "React", "ML"]
    """
    if not text or len(text.strip()) < 20:
        return []

    # Split into sentences as "documents" for TF-IDF
    sentences = nltk.sent_tokenize(text)
    if len(sentences) < 2:
        # If only one sentence, split by newlines or periods
        sentences = [s.strip() for s in re.split(r'[.\n]', text) if s.strip()]

    if not sentences:
        return []

    try:
        vectorizer = TfidfVectorizer(
            max_features=50,
            stop_words="english",
            token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z+#.]{1,}\b',  # Words 2+ chars, allow C++, C#
            lowercase=True
        )
        tfidf_matrix = vectorizer.fit_transform(sentences)

        # Sum TF-IDF scores across all sentences
        scores = tfidf_matrix.sum(axis=0).A1
        feature_names = vectorizer.get_feature_names_out()

        # Sort by score descending
        ranked = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)

        return [word.title() for word, score in ranked[:top_n]]

    except ValueError:
        # Not enough text for TF-IDF
        return []


def analyze_sentiment(text):
    """Analyze sentiment of text using NLTK VADER.

    VADER is specifically designed for short texts and social media,
    making it suitable for interview transcripts.

    Args:
        text: Video transcript text

    Returns:
        dict: Sentiment scores
            - positive (0-1): Positive sentiment ratio
            - negative (0-1): Negative sentiment ratio
            - neutral (0-1): Neutral sentiment ratio
            - compound (-1 to 1): Overall sentiment (-1 = very negative, +1 = very positive)
            - label: "Positive" / "Neutral" / "Negative"
    """
    if not text or len(text.strip()) < 5:
        return {
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 1.0,
            "compound": 0.0,
            "label": "No Data"
        }

    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)

    # Determine label based on compound score
    compound = scores["compound"]
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "positive": round(scores["pos"], 3),
        "negative": round(scores["neg"], 3),
        "neutral": round(scores["neu"], 3),
        "compound": round(compound, 3),
        "label": label
    }
