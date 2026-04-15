import sys
import os
import json
import logging

# Setup basic logging for test
logging.basicConfig(level=logging.INFO)

# Add project root to path
sys.path.append(os.getcwd())

from newsbot.ingestion.rss import get_rss_news
from newsbot.ingestion.web import get_dipr_news
from newsbot.ingestion.social import get_social_news
from newsbot.bot.process import filter_and_rank_news

def test_news():
    print("--- Fetching RSS News ---")
    rss_news = get_rss_news()
    print(f"Total RSS items: {len(rss_news)}")
    
    print("\n--- Fetching Social News (FB/YT/X indexed) ---")
    social_news = get_social_news()
    print(f"Total Social items: {len(social_news)}")
    
    print("\n--- Fetching Web/DIPR News ---")
    web_news = get_dipr_news()
    print(f"Total Web items: {len(web_news)}")
    
    all_news = rss_news + web_news + social_news
    print("\n--- Ranking & Trending Detection ---")
    ranked = filter_and_rank_news(all_news)
    
    print(f"\nTop 15 Ranked items (including Viral Boosts):")
    for i, n in enumerate(ranked[:15]):
        trending_tag = "[TRENDING 🔥]" if n.get('trending') else ""
        print(f"{i+1}. [{n['score']}] {trending_tag} {n['source']} | {n['title']}")

if __name__ == "__main__":
    test_news()
