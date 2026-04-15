import json
import logging
import feedparser
import urllib.parse
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
SOCIAL_SOURCES = config.get("social_sources", {})

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_social_feed(query):
    # Google News search RSS URL
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=hi&gl=IN&ceid=IN:hi"
    return feedparser.parse(url)

def get_social_news():
    news = []
    for source_name, query in SOCIAL_SOURCES.items():
        try:
            logger.info(f"Searching Social Index: {source_name}")
            feed = fetch_social_feed(query)
            for e in feed.entries[:10]: # Top 10 social results per query
                news.append({
                    "title": e.title.strip(),
                    "link": e.link,
                    "summary": e.get("summary", ""),
                    "source": source_name,
                    "type": "social"
                })
        except Exception as ex:
            logger.error(f"Error fetching social for {source_name}: {ex}")
    return news
