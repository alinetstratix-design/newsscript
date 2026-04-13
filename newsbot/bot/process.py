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
    for n in items:
        # Without checking keywords, simply pass top national and international news 
        # Score 4 ensures it is just below breaking local news (5) but above standard local (1)
        if n["source"] in ["National Top News", "World Top News"]:
            n["score"] = 4
            out.append(n)
        else:
            score = get_score(n["title"])
            if score > 0:
                n["score"] = score
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
