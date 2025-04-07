import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams
import xml.etree.ElementTree as ET

nltk.download('stopwords')

st.title("🕸️ Sitemap-Based Long-Tail Keyword Extractor (with Live Diagnostics)")

sitemap_url = st.text_input("Enter sitemap.xml URL (e.g. https://www.affinda.com/sitemap.xml)")

def get_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        return [elem.text for elem in root.findall('.//ns:loc', namespace)]
    except Exception as e:
        st.error(f"Error reading sitemap: {e}")
        return []

def extract_visible_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(['script', 'style']):
            script.extract()
        text = soup.get_text(separator=' ')
        cleaned = re.sub(r'\s+', ' ', text).strip().lower()
        return cleaned
    except Exception as e:
        return f"__ERROR__::{e}"

def extract_ngrams(text, stop_words, n_range=(2, 5)):
    words = re.findall(r'\b[a-z]{3,}\b', text)
    filtered = [w for w in words if w not in stop_words]
    all_ngrams = []
    for n in range(n_range[0], n_range[1] + 1):
        all_ngrams += [' '.join(gram) for gram in ngrams(filtered, n)]
    return all_ngrams

if sitemap_url:
    urls = get_urls_from_sitemap(sitemap_url)
    
    if urls:
        st.success(f"✅ Found {len(urls)} URLs. Beginning analysis...")

        stop_words = set(stopwords.words('english'))
        all_phrases = []

        progress = st.progress(0)
        log = st.empty()
        logs = []

        for i, url in enumerate(urls):
            progress.progress((i + 1) / len(urls))
            log.markdown(f"**🔍 Checking:** `{url}`")

            text = extract_visible_text_from_url(url)

            if text.startswith("__ERROR__::"):
                logs.append(f"❌ `{url}` — Error: {text.replace('__ERROR__::', '')}")
                continue

            if len(text) < 100:
                logs.append(f"⚠️ `{url}` — Skipped: Not enough content ({len(text)} chars)")
                continue

            phrases = extract_ngrams(text, stop_words)

            if phrases:
                logs.append(f"✅ `{url}` — {len(phrases)} keywords found")
                all_phrases += phrases
            else:
                logs.append(f"🟡 `{url}` — No keywords found")

            log.markdown("  \n".join(logs[-10:]))  # Show last 10 entries live

        if all_phrases:
            phrase_counts = Counter(all_phrases).most_common(50)
            st.subheader("📈 Top Long-Tail Keywords (2–5 words):")
            for phrase, freq in phrase_counts:
                st.write(f"{phrase} — {freq} times")
        else:
            st.warning("😢 No long-tail keywords were extracted from the site.")
