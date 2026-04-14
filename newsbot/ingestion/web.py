import json
import logging
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
SOURCES = config.get("web_sources", {})

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_html(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    return requests.get(url, headers=headers, timeout=15)

def get_dipr_news():
    news = []
    url = SOURCES.get("DIPR", "https://uttarainformation.gov.in/category/%e0%a4%aa%e0%a5%8d%e0%a4%b0%e0%a5%87%e0%a4%b8-%e0%a4%a8%e0%a5%8b%e0%a4%9f/")
    try:
        logger.info("Fetching Web Data from DIPR")
        resp = fetch_html(url)
        soup = BeautifulSoup(resp.content, "lxml")
        
        for h2 in soup.find_all(["h2", "h3"]):
            a_tag = h2.find("a")
            if a_tag and a_tag.text:
                news.append({
                    "title": a_tag.text.strip(),
                    "link": a_tag.get("href"),
                    "source": "DIPR",
                    "type": "web"
                })
                if len(news) >= 10: 
                    break
    except Exception as e:
        logger.error(f"Error fetching DIPR: {e}")
    return news
