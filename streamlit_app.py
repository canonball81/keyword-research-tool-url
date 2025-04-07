import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams

nltk.download('stopwords')

st.title("📝 Long-Tail Keyword Extractor from Multiple URLs (with Real-Time Logging)")

# Input for URLs
url_input = st.text_area("Paste one or more URLs (one per line):", height=200)

def extract_visible_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ')
        cleaned_text = re.sub(r'\s+', ' ', text).strip().lower()
        return cleaned_text
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
        log_box = st.empty()
        progress = st.progress(0)
        logs = []

        for i, url in enumerate(urls):
            text = extract_visible_text(url)
            if text.startswith("__ERROR__::"):
                logs.append(f"❌ `{url}` — Error: {text.replace('__ERROR__::', '')}")
            else:
                char_count = len(text)
                preview = text[:250] + "..." if char_count > 250 else text
                logs.append(f"✅ `{url}` — {char_count} chars\n\n**Preview:**\n```\n{preview}\n```")

                if char_count > 30:
                    phrases = extract_ngrams(text, stop_words)
                    all_phrases += phrases
                else:
                    logs.append(f"⚠️ `{url}` — Skipped: Not enough text")

            # Real-time log viewer (only show last 10 logs to keep it clean)
            log_box.markdown("___\n\n".join(logs[-10:]))
            progress.progress((i + 1) / len(urls))

        if all_phrases:
            st.subheader("📈 Top Long-Tail Keywords:")
            top_keywords = Counter(all_phrases).most_common(50)
            for phrase, freq in top_keywords:
                st.write(f"{phrase} — {freq} times")
        else:
            st.warning("No long-tail keywords found.")
