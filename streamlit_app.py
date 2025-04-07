import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams
import matplotlib.pyplot as plt

nltk.download('stopwords')

st.title("📝 Long-Tail Keyword Extractor from Multiple URLs")

# Input for URLs
url_input = st.text_area("Paste one or more URLs (one per line):", height=200)

def extract_visible_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ')
        return re.sub(r'\s+', ' ', text).strip().lower()
    except Exception as e:
        return f"__ERROR__::{str(e)}"

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
        logs = []
        log_box = st.empty()
        progress = st.progress(0)

        for i, url in enumerate(urls):
            text = extract_visible_text(url)
            if text.startswith("__ERROR__::"):
                logs.append(f"❌ {url} — Error: {text.replace('__ERROR__::', '')}")
            else:
                char_count = len(text)
                preview = text[:250] + "..." if char_count > 250 else text
                logs.append(f"✅ {url} — {char_count} chars\n\n{preview}")

                if char_count > 30:
                    phrases = extract_ngrams(text, stop_words)
                    all_phrases += phrases
                else:
                    logs.append(f"⚠️ {url} — Skipped: Not enough text")

            # Display the last 5 logs in a scrollable text area
            log_box.text_area("🪵 Live Log (Last 5)", "\n\n---\n\n".join(logs[-5:]), height=160)

            progress.progress((i + 1) / len(urls))

        if all_phrases:
            st.subheader("📈 Top Long-Tail Keywords:")
            top_keywords = Counter(all_phrases).most_common(50)
            for phrase, freq in top_keywords:
                st.write(f"{phrase} — {freq} times")

            # Bar Chart for top 20 keywords
            st.subheader("📊 Keyword Frequency Chart")
            top_20 = top_keywords[:20]
            phrases = [x[0] for x in top_20]
            freqs = [x[1] for x in top_20]

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(phrases[::-1], freqs[::-1])  # reverse for descending
            ax.set_xlabel("Frequency")
            ax.set_ylabel("Keyword Phrase")
            ax.set_title("Top 20 Long-Tail Keywords")
            st.pyplot(fig)
        else:
            st.warning("No long-tail keywords found.")
