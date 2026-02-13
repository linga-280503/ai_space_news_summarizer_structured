import json, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_session(timeout=12, retries=2, backoff=0.6):
    s = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff, status_forcelist=(500,502,503,504), allowed_methods=("GET","POST"), raise_on_status=False)
    ad = HTTPAdapter(max_retries=retry)
    s.mount('http://', ad); s.mount('https://', ad)
    s.request_timeout = timeout
    return s

SESSION = make_session()

def chat(base_url: str, model: str, messages: list, temperature: float=0.2, stream: bool=True):
    url = base_url.rstrip('/') + '/api/chat'
    payload = {"model": model, "messages": messages, "stream": stream, "options": {"temperature": temperature}}
    headers = {"Content-Type":"application/json"}

    if stream:
        with SESSION.post(url, data=json.dumps(payload), headers=headers, timeout=SESSION.request_timeout) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line: continue
                if line.startswith('data:'):
                    try:
                        data = json.loads(line[len('data:'):].strip())
                        delta = data.get('message',{}).get('content','')
                        if delta: yield delta
                    except Exception:
                        continue
    else:
        r = SESSION.post(url, data=json.dumps(payload), headers=headers, timeout=SESSION.request_timeout)
        r.raise_for_status(); data = r.json()
        yield data.get('message',{}).get('content','')
