# 🛰️ AI Space News Summarizer (Structured)

A fast, smooth, reliable **space news aggregator** with local **Ollama** summaries.

## Folder layout
```
ai_space_news_summarizer_structured/
├── README.md
├── requirements.txt
├── .env.example
├── feeds.yaml
├── .streamlit/
│   └── config.toml
└── src/
    ├── app.py                # Streamlit entry
    ├── settings.py           # Settings + feed loading
    ├── core/
    │   ├── rss.py            # Feed fetching, parsing, dedup, sanitize
    │   └── html.py           # HTML cleaners & extractors
    ├── llm/
    │   └── ollama_client.py  # Ollama chat wrapper (stream/non-stream)
    └── ui/
        └── theme.py          # CSS + UI helpers
```

## Quickstart
```bash
# 1) Run Ollama
ollama pull llama3.1:8b
ollama serve

# 2) Install deps
pip install -r requirements.txt

# 3) Run
streamlit run src/app.py
```

- Configure sources in `feeds.yaml` or via sidebar.
- Change Ollama base URL / model from the sidebar or `.env`.
