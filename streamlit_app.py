import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams

nltk.download('stopwords')

st.title("🔍 Long-Tail Keyword Extractor (2–5 words)")

# Input URL
url = st.text_input("Enter a website URL (e.g. https://example.com)")

if url:
    try:
        # Fetch page content
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Get visible text
        text = soup.get_text(separator=' ')
        text = re.sub(r'\s+', ' ', text).strip().lower()

        # Tokenize and filter stopwords
        words = re.findall(r'\b[a-z]{3,}\b', text)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word not in stop_words]

        # Create 2- to 5-word n-grams
        all_ngrams = []
        for n in range(2, 6):
            all_ngrams += [' '.join(gram) for gram in ngrams(filtered_words, n)]

        # Count and display most common n-grams
        ngram_freq = Counter(all_ngrams).most_common(25)

        st.subheader("🧠 Top Long-Tail Keywords (2–5 words):")
        for phrase, freq in ngram_freq:
            st.write(f"{phrase} — {freq} times")

    except Exception as e:
        st.error(f"Error: {e}")
