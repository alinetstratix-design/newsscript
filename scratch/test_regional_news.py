import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from newsbot.ingestion.rss import get_rss_news
from newsbot.ingestion.web import get_dipr_news
from newsbot.bot.process import filter_and_rank_news

def test_news():
    print("--- Fetching RSS News ---")
    rss_news = get_rss_news()
    print(f"Total RSS items: {len(rss_news)}")
    
    print("\n--- Fetching Web/DIPR News ---")
    web_news = get_dipr_news()
    print(f"Total Web items: {len(web_news)}")
    
    all_news = rss_news + web_news
    print("\n--- Ranking News ---")
    ranked = filter_and_rank_news(all_news)
    
    print(f"\nTop 10 Ranked items:")
    for i, n in enumerate(ranked[:10]):
        print(f"{i+1}. [{n['score']}] {n['source']} | {n['title']}")

if __name__ == "__main__":
    test_news()
