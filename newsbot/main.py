import time
import os
import logging
import json

# Setup Production Logging
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/newsbot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("main")

from ingestion.rss import get_rss_news
from ingestion.web import get_dipr_news
from ingestion.social import get_social_news
from bot.process import filter_and_rank_news, deduplicate
from bot.rewrite import rewrite
from bot.telegram import send_message, send_photo

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def job():
    logger.info("Starting Senior-Level News Cycle (Multi-Platform)...")
    try:
        # Fetching from all sources
        rss_data = get_rss_news()
        web_data = get_dipr_news()
        social_data = get_social_news()
        
        raw_news = rss_data + web_data + social_data
        logger.info(f"Fetched | RSS: {len(rss_data)} | Web: {len(web_data)} | Social: {len(social_data)}")
        
        filtered_ranked = filter_and_rank_news(raw_news)
        new_news = deduplicate(filtered_ranked)
        
        if not new_news:
            logger.info("No fresh news requiring attention.")
            return

        logger.info(f"Processing Top {min(5, len(new_news))} items for multi-platform distribution.")

        for item in new_news[:5]:
            logger.info(f"AI Rewriting: {item['title'][:50]}... | Score: {item.get('score', 0)}")
            text = rewrite(item)
            
            if "image" in item and item["image"]:
                send_photo(item["image"], text)
            else:
                send_message(text)
                
            time.sleep(5) # Slow down for platform limits
        logger.info("Production Cycle Complete.")
    except Exception as e:
        logger.exception("Operational critical failure")

if __name__ == "__main__":
    logger.info("Uttarakhand AI News Intelligence Engine Active")
    job()
