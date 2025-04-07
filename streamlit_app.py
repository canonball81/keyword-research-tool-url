import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams

nltk.download('stopwords')

st.title("📝 Long-Tail Keyword Extractor from Multiple URLs")

# Text area for multiple URLs
url_input = st.text_area("Paste one or more URLs (one per line):", height=200)

def extract_visible_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ')
        return re.sub(r'\s+', ' ', text).strip().lower()
    except Exception:
        return ""

def extract_ngrams(text, stop_words, n_range=(2, 5)):
    words = re.findall(r'\b[a-z]{3,}\b', text)
    filtered = [w for w in words if w not in stop_words]
    all_ngrams = []
    for n in range(n_range[0], n_range[1]+1):
        all_ngrams += [' '.join(gram) for gram in ngrams(filtered, n)]
    return all_ngrams

if st.button("🔍 Extract Keywords"):
    urls = [u.strip() for u in url_input.splitlines() if u.strip()]
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        stop_words = set(stopwords.words('english'))
        all_phrases = []
        progress = st.progress(0)
        log = st.empty()

        for i, url in enumerate(urls):
            log.markdown(f"Processing: `{url}`")
            text = extract_visible_text(url)
            if len(text) > 100:
                phrases = extract_ngrams(text, stop_words)
                all_phrases += phrases
            else:
                st.info(f"⚠️ Skipped {url} — too little content.")
            progress.progress((i+1) / len(urls))

        if all_phrases:
            st.subheader("📈 Top Long-Tail Keywords:")
            top_keywords = Counter(all_phrases).most_common(50)
            for phrase, freq in top_keywords:
                st.write(f"{phrase} — {freq} times")
        else:
            st.warning("No long-tail keywords found.")
