from bs4 import BeautifulSoup

def clean_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(["script","style","noscript"]):
        tag.extract()
    text = soup.get_text(" ", strip=True)
    return ' '.join(text.split())
