import os, yaml, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

DEFAULT_FEEDS = {
    "NASA Breaking News": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "NASA JPL News": "https://www.jpl.nasa.gov/feeds/news/",
    "ESA Top News": "https://www.esa.int/rssfeed/TopNews",
    "Space.com": "https://www.space.com/home/feed/site.xml",
    "SpaceNews": "https://spacenews.com/feed/",
    "Phys.org – Space": "https://phys.org/rss-feed/space-news/",
    "Spaceflight Now": "https://spaceflightnow.com/feed/",
}

# Load feeds.yaml if present
FEEDS_FILE = ROOT / 'feeds.yaml'
if FEEDS_FILE.exists():
    try:
        data = yaml.safe_load(FEEDS_FILE.read_text(encoding='utf-8')) or {}
        DEFAULT_FEEDS.update(data.get('feeds', {}))
    except Exception:
        pass

# Env defaults
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
