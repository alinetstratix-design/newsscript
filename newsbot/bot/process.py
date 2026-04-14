import json
import os
import logging

logger = logging.getLogger(__name__)

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

HIGH_WEIGHT = [k.lower() for k in config.get("keywords", {}).get("high_weight", [])]
STD_WEIGHT = [k.lower() for k in config.get("keywords", {}).get("standard_weight", [])]

HISTORY_FILE = "history.json"

def get_score(title):
    score = 0
    title_lower = title.lower()
    for kw in HIGH_WEIGHT:
        if kw in title_lower:
            score += 5
    for kw in STD_WEIGHT:
        if kw in title_lower:
            score += 1
    return score

def filter_and_rank_news(items):
    out = []
    # Sources that should have a baseline to compete
    regional_sources = ["Haridwar News", "Dehradun News", "Uttarakhand", "Local Search", "DIPR"]
    
    for n in items:
        base_score = 0
        if n["source"] in regional_sources:
            base_score = 2 # Regional sources start with 2
            
        keyword_score = get_score(n["title"])
        total_score = base_score + keyword_score
        
        if n["source"] in ["National Top News", "World Top News"]:
            # National news stays at score 3 (fixed) so high-weight local news (2+5=7) wins
            # and standard local news (2+1=3) ties or wins if multiple keywords exist
            n["score"] = 3
            out.append(n)
        elif total_score > 0:
            n["score"] = total_score
            out.append(n)
            
    # Sort descending by score for ranking engine
    out.sort(key=lambda x: x["score"], reverse=True)
    return out

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(hist):
    with open(HISTORY_FILE, "w") as f:
        json.dump(hist[-300:], f) # Keep 300 to be safe in production

def deduplicate(items):
    hist = load_history()
    new_items = []
    for item in items:
        if item["link"] not in hist:
            new_items.append(item)
            hist.append(item["link"])
    save_history(hist)
    return new_items
