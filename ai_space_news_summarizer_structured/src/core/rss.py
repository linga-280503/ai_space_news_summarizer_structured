import hashlib
from datetime import datetime, timezone
import feedparser, requests
from dateutil import parser as dateparser
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .html import clean_html

def make_session(timeout=12, retries=2, backoff=0.6):
    s = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff, status_forcelist=(500,502,503,504), allowed_methods=("GET","POST"), raise_on_status=False)
    ad = HTTPAdapter(max_retries=retry)
    s.mount('http://', ad); s.mount('https://', ad)
    s.request_timeout = timeout
    return s

SESSION = make_session()

def fetch_feed(url: str):
    resp = SESSION.get(url, timeout=SESSION.request_timeout, headers={"User-Agent":"SpaceSummarizer/1.0"})
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    items = []
    for e in parsed.entries:
        title = getattr(e,'title','')
        link = getattr(e,'link','')
        summary = clean_html(getattr(e,'summary','') or getattr(e,'description',''))
        published = None
        if hasattr(e,'published'):
            try: published = dateparser.parse(e.published)
            except Exception: published = None
        elif hasattr(e,'updated'):
            try: published = dateparser.parse(e.updated)
            except Exception: published = None
        items.append({'title':title,'link':link,'summary':summary,'published':published,'source':url})
    return items

def dedup(items):
    seen=set(); out=[]
    for it in items:
        h = hashlib.sha256((it.get('title','')+it.get('link','')).encode()).hexdigest()[:16]
        if h not in seen:
            seen.add(h); it['id']=h; out.append(it)
    return out

def sort_desc(items):
    def key(it): return it.get('published') or datetime.now(timezone.utc)
    return sorted(items, key=key, reverse=True)
