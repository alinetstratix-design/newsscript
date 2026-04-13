import time
import os
import logging
import schedule
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
from bot.process import filter_and_rank_news, deduplicate
from bot.rewrite import rewrite
from bot.telegram import send_message, send_photo

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def job():
    logger.info("Starting scheduled news fetch cycle...")
    try:
        raw_news = get_rss_news() + get_dipr_news()
        logger.info(f"Total raw items fetched: {len(raw_news)}")
        
        filtered_ranked = filter_and_rank_news(raw_news)
        new_news = deduplicate(filtered_ranked)
        
        if not new_news:
            logger.info("No new news found to send.")
            return

        logger.info(f"Processing top items out of {len(new_news)} fresh finds.")

        # Process top 5 items per cycle
        for item in new_news[:5]:
            # Print item safely without risking charmap failures
            logger.info(f"Applying AI Rewrite | Score: {item.get('score', 0)}")
            text = rewrite(item)
            
            if "image" in item and item["image"]:
                logger.info("Sending photo to Telegram...")
                send_photo(item["image"], text)
            else:
                logger.info("Sending text to Telegram...")
                send_message(text)
                
            time.sleep(3)
        logger.info("Cycle complete.")
    except Exception as e:
        logger.exception("Critical error in job execution")

if __name__ == "__main__":
    logger.info("Uttarakhand Production AI News Intelligence System Started")
    
    # Run once immediately on start
    job()
    
    interval = config.get("schedule_minutes", 30)
    logger.info(f"Scheduler configured for everyday {interval} minutes.")
    schedule.every(interval).minutes.do(job)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("System shutting down...")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)
