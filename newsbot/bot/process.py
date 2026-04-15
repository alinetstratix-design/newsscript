import json
import os
import logging
import re

logger = logging.getLogger(__name__)

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

HIGH_WEIGHT = [k.lower() for k in config.get("keywords", {}).get("high_weight", [])]
STD_WEIGHT = [k.lower() for k in config.get("keywords", {}).get("standard_weight", [])]

HISTORY_FILE = "history.json"

def get_tokens(text):
    """Normalize text and return meaningful tokens for similarity check."""
    text = text.lower()
    # Remove common words and punctuation
    text = re.sub(r'[^\w\s]', '', text)
    tokens = set(text.split())
    # Filter out very short tokens or generic news words
    stop_words = {'news', 'video', 'watch', 'breaking', 'update', 'latest'}
    return {t for t in tokens if len(t) > 2 and t not in stop_words}

def get_score(title):
    score = 0
    title_lower = title.lower()
    for kw in HIGH_WEIGHT:
        if kw in title_lower:
            score += 10 # Increased weight for high-priority local/accidents
    for kw in STD_WEIGHT:
        if kw in title_lower:
            score += 2
    return score

def detect_overlap(items):
    """Assign viral boost if multiple sources report similar news."""
    for i in range(len(items)):
        tokens_i = get_tokens(items[i]['title'])
        overlap_count = 1
        for j in range(len(items)):
            if i == j: continue
            tokens_j = get_tokens(items[j]['title'])
            
            # If 40% of unique tokens match, consider it same news
            common = tokens_i.intersection(tokens_j)
            if len(tokens_i) > 0 and (len(common) / len(tokens_i)) > 0.4:
                overlap_count += 1
        
        if overlap_count >= 2:
            logger.info(f"Viral Boost detected for: {items[i]['title']} (Found in {overlap_count} sources)")
            items[i]['score'] += (overlap_count * 5) # Significant boost for trending news
            items[i]['trending'] = True
    return items

def filter_and_rank_news(items):
    out = []
    # Sources that should have a baseline to compete
    regional_sources = ["Haridwar News", "Dehradun News", "Uttarakhand", "Local Search", "DIPR", "Facebook_Local", "YouTube_Trending", "X_Twitter_Alerts"]
    
    for n in items:
        base_score = 0
        if n["source"] in regional_sources:
            base_score = 5 # Regional/Social sources start with higher baseline
            
        keyword_score = get_score(n["title"])
        total_score = base_score + keyword_score
        
        if n["source"] in ["National Top News", "World Top News"]:
            n["score"] = 3 # National news at lower priority than local
            out.append(n)
        elif total_score > 0:
            n["score"] = total_score
            out.append(n)
            
    # Apply Overlap/Trending Detection
    out = detect_overlap(out)
            
    # Sort descending by score for ranking engine
    out.sort(key=lambda x: x["score"], reverse=True)
    return out

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_history(hist):
    with open(HISTORY_FILE, "w") as f:
        json.dump(hist[-500:], f) # Increased history limit

def deduplicate(items):
    hist = load_history()
    new_items = []
    for item in items:
        if item["link"] not in hist:
            new_items.append(item)
            hist.append(item["link"])
    save_history(hist)
    return new_items
