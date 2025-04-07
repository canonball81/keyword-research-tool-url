import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords

# Download NLTK stopwords if not already present
nltk.download('stopwords')

st.title("🔍 Website Keyword Extractor")

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

        # Tokenize and filter words
        words = re.findall(r'\b[a-z]{3,}\b', text)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word not in stop_words]

        # Count keyword frequency
        keyword_freq = Counter(filtered_words).most_common(20)

        st.subheader("📈 Top Keywords:")
        for word, freq in keyword_freq:
            st.write(f"{word}: {freq}")

    except Exception as e:
        st.error(f"Error fetching or processing the URL: {e}")
