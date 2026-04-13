import json
import logging
import feedparser
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
SOURCES = config.get("rss_sources", {})

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_feed(url):
    return feedparser.parse(url)

def get_rss_news():
    news = []
    for source_name, url in SOURCES.items():
        try:
            logger.info(f"Fetching RSS from {source_name}")
            feed = fetch_feed(url)
            for e in feed.entries[:5]: 
                image_url = ""
                # Attempt to extract image from RSS enclosures or media content
                if 'media_content' in e and len(e.media_content) > 0:
                    image_url = e.media_content[0].get('url', '')
                elif 'enclosures' in e and len(e.enclosures) > 0:
                    for enc in e.enclosures:
                        if 'image' in enc.get('type', ''):
                            image_url = enc.get('href', '')
                            break
                            
                news.append({
                    "title": e.title.strip(),
                    "link": e.link,
                    "summary": e.get("summary", ""),
                    "image": image_url,
                    "source": source_name,
                    "type": "rss"
                })
        except Exception as ex:
            logger.error(f"Error fetching from {source_name}: {ex}")
    return news
