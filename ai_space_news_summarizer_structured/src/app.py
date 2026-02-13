import os, time
from datetime import datetime, timezone
import streamlit as st

from settings import DEFAULT_FEEDS, OLLAMA_BASE_URL, OLLAMA_MODEL
from core.rss import fetch_feed, dedup, sort_desc
from core.html import clean_html
from ui.theme import inject_css
from llm.ollama_client import chat

st.set_page_config(page_title="AI Space News Summarizer", page_icon="🛰️", layout="wide")
inject_css()

st.title("🛰️ AI Space News Summarizer")
st.caption("Stream latest space headlines • Summarize locally with Ollama • Dark galaxy UI")

with st.sidebar:
    st.subheader("⚙️ Settings")
    base_url = st.text_input("Ollama Base URL", value=OLLAMA_BASE_URL)
    model = st.text_input("Model", value=OLLAMA_MODEL)
    temperature = st.slider("Temperature", 0.0, 1.2, 0.2, 0.05)
    stream_mode = st.toggle("Stream summaries", True)
    kids_mode = st.toggle("Kids Mode (simple language)", False)

    st.markdown("---")
    st.markdown("**News Sources**")
    selected = st.multiselect("Pick feeds", options=list(DEFAULT_FEEDS.keys()), default=list(DEFAULT_FEEDS.keys())[:4])
    custom = st.text_input("Add custom RSS URL (optional)")

    st.markdown("---")
    keywords = st.text_input("Include keywords (comma-separated)")
    exclude = st.text_input("Exclude keywords (comma-separated)")
    top_k = st.slider("Max articles", 1, 30, 12)
    fetch_full = st.toggle("Fetch article page (slower)", False)
    cache_ttl = st.slider("Cache time (minutes)", 1, 60, 10)

@st.cache_data(ttl=60, show_spinner=False)
def fetch_full_text(url: str):
    import requests
    from bs4 import BeautifulSoup
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent":"SpaceSummarizer/1.0"}); r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        nodes = [soup.select_one(sel) for sel in ['article','main','div#content','div.article','div.post','section']]
        nodes = [n for n in nodes if n] or [soup]
        best=''
        for n in nodes:
            txt = ' '.join([p.get_text(' ', strip=True) for p in n.find_all(['p','li'])])
            if len(txt)>len(best): best = txt
        return best
    except Exception:
        return ''

SYSTEM_PROMPT = (
    "You are a concise, accurate space news summarizer. Summarize into:\n"
    "• 3-5 key bullets with facts & numbers\n• A 1-2 line TL;DR\n• Why it matters (impact)\n"
    "Keep dates & missions correct. If info is missing, say so."
)


def to_list(s: str):
    return [x.strip().lower() for x in s.split(',') if x.strip()] if s else []

if st.button("🚀 Fetch & Summarize", type="primary"):
    feeds = {name: DEFAULT_FEEDS[name] for name in selected}
    if custom:
        feeds["Custom"] = custom

    all_items = []
    with st.spinner("Fetching feeds..."):
        for name, url in feeds.items():
            window = int(time.time() // (cache_ttl*60)) if cache_ttl else 0
            items = st.cache_data(show_spinner=False)(fetch_feed)(url)  # cache at function level
            for it in items:
                it['feed_name'] = name
            all_items.extend(items)

    inc, exc = to_list(keywords), to_list(exclude)
    def txt(it): return (it['title']+" "+it['summary']).lower()
    if inc:
        all_items = [it for it in all_items if any(k in txt(it) for k in inc)]
    if exc:
        all_items = [it for it in all_items if not any(k in txt(it) for k in exc)]

    all_items = dedup(sort_desc(all_items))[:top_k]
    st.success(f"Loaded {len(all_items)} articles from {len(feeds)} sources")

    for it in all_items:
        with st.container(border=True):
            title, link, src = it['title'], it['link'], it.get('feed_name','Source')
            st.markdown(f"### {title}")
            st.caption(link)
            context = it.get('summary','')
            if fetch_full:
                with st.spinner("Fetching full article text..."):
                    full = fetch_full_text(link)
                    if full and len(full) > len(context):
                        context = full

            user_prompt = (
                f"Source: {src}\nTitle: {title}\nURL: {link}\n\nCONTENT:\n{context[:5000]}\n\n"
                "Summarize now in markdown with sections: \n- **Key points** (3-5 bullets)\n- **TL;DR** (1-2 lines)\n- **Why it matters**\n"
            )
            if kids_mode:
                user_prompt += "\nUse simple words, 8th-grade level, friendly tone, short sentences."

            messages = [
                {"role":"system","content": SYSTEM_PROMPT},
                {"role":"user","content": user_prompt}
            ]

            ph = st.empty(); out=""
            try:
                for chunk in chat(base_url, model, messages, temperature=temperature, stream=stream_mode):
                    out += chunk
                    if stream_mode:
                        ph.markdown(out)
                if not stream_mode:
                    ph.markdown(out)
            except Exception as ex:
                st.error(f"LLM error: {ex}")
                fallback = []
                for line in context.split('.')[:5]:
                    if line.strip(): fallback.append('• '+line.strip())
                if fallback: ph.markdown('\n'.join(fallback)+"\n\n_Offline fallback (no Ollama)_")

            with st.expander("Show raw context (sanitized)"):
                st.write(context[:2000] + ("..." if len(context)>2000 else ""))
            st.markdown("---")
else:
    st.markdown("<div class='glass'><p class='small'><span class='badge'>Tip</span> Use the sidebar to pick feeds or add your own RSS URL. Click <b>Fetch & Summarize</b>.</p></div>", unsafe_allow_html=True)
