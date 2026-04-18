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

def get_web_news():
    all_news = []
    
    # 1. Official Press Notes (DIPR)
    dipr_sources = ["DIPR", "DIPR_English"]
    for src_key in dipr_sources:
        url = SOURCES.get(src_key)
        if not url: continue
        
        try:
            logger.info(f"Fetching Web Data from {src_key}")
            resp = fetch_html(url)
            soup = BeautifulSoup(resp.content, "lxml")
            
            for h2 in soup.find_all(["h2", "h3"]):
                a_tag = h2.find("a")
                if a_tag and a_tag.text:
                    all_news.append({
                        "title": a_tag.text.strip(),
                        "link": a_tag.get("href"),
                        "source": src_key,
                        "type": "web"
                    })
                    if len(all_news) >= 20: break
        except Exception as e:
            logger.error(f"Error fetching {src_key}: {e}")

    # 2. District Portals (NIC S3WaaS)
    nic_sources = ["Dehradun_NIC", "Haridwar_NIC"]
    for src_key in nic_sources:
        url = SOURCES.get(src_key)
        if not url: continue
        
        try:
            logger.info(f"Fetching NIC Data from {src_key}")
            resp = fetch_html(url)
            soup = BeautifulSoup(resp.content, "lxml")
            
            # NIC S3WaaS typically uses tables for press releases
            rows = soup.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    a_tag = cols[0].find("a") or cols[1].find("a")
                    if a_tag and a_tag.text:
                        all_news.append({
                            "title": a_tag.text.strip(),
                            "link": a_tag.get("href") if a_tag.get("href").startswith("http") else url + a_tag.get("href"),
                            "source": src_key,
                            "type": "web"
                        })
                    if len(all_news) >= 30: break
        except Exception as e:
            logger.error(f"Error fetching {src_key}: {e}")
            
    return all_news
