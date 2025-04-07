import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

nltk.download('stopwords')

st.title("🕸️ Long-Tail Keyword Extractor from Sitemap.xml")

# Input for sitemap.xml
sitemap_url = st.text_input("Enter sitemap.xml URL (e.g. https://www.affinda.com/sitemap.xml)")

def get_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [elem.text for elem in root.findall('.//ns:loc', namespace)]
        return urls
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
        return re.sub(r'\s+', ' ', text).strip().lower()
    except Exception:
        return ""

def extract_ngrams(text, stop_words, n_range=(2,5)):
    words = re.findall(r'\b[a-z]{3,}\b', text)
    filtered = [w for w in words if w not in stop_words]
    all_ngrams = []
    for n in range(n_range[0], n_range[1]+1):
        all_ngrams += [' '.join(gram) for gram in ngrams(filtered, n)]
    return all_ngrams

if sitemap_url:
    urls = get_urls_from_sitemap(sitemap_url)
    
    if urls:
        st.write(f"✅ Found {len(urls)} URLs in the sitemap.")
        stop_words = set(stopwords.words('english'))
        all_phrases = []

        progress = st.progress(0)
        for i, url in enumerate(urls):
            text = extract_visible_text_from_url(url)
            all_phrases += extract_ngrams(text, stop_words)
            progress.progress((i+1)/len(urls))

        # Count long-tail keyword frequencies
        phrase_counts = Counter(all_phrases).most_common(50)
        st.subheader("📈 Top Long-Tail Keywords (2–5 words):")
        for phrase, freq in phrase_counts:
            st.write(f"{phrase} — {freq} times")
