import os
import logging
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "YOUR_GEMINI_API_KEY":
    genai.configure(api_key=api_key)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def generate_ai_content(prompt):
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

def rewrite(item):
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return f"📢 {item['title']}\n\nSource: {item['source']}"
        
    prompt = f"""You are a professional Hindi news editor and viral content creator.

Your task is to process the following news and output a highly engaging, ready-to-publish Telegram message.

=== NEWS TO PROCESS ===
Title: {item['title']}
Description: {item.get('description', item.get('summary', ''))}
=======================

=== GENERATION RULES ===
1. FACT-CHECK: If the news appears to be fake or rumor, output ONLY: "UNVERIFIED/RISKY: Cannot process." Assuming it's safe (factual tone), proceed.
2. CATEGORY: Detect category (Haridwar / Dehradun / Uttarakhand / National / International).
3. POST CONTENT: Simple Hindi, fast-paced, 50-80 words, 2-3 short paragraphs. NO emojis in the text. Clear and factual. 
4. ENGAGEMENT: First line must be a strong hook. Last line must be a highly relatable local engagement question for the Uttarakhand audience.
5. HEADLINE: Short, bold, and powerful breaking news text (max 6-8 words).
6. REEL HOOK: 1-line script for the first 2 seconds of a reel (shocking or curiosity trigger).
7. TAGS: 6 keyword hashtags (lowercase).

Output EXACTLY in the following format (do not add any extra text outside this format):

📍 [Category]

📰 [Headline]

📝 [Post Content]

🎬 Reel Hook:
[Reel Hook Line]

[#hashtags]"""
    try:
        ai_text = generate_ai_content(prompt)
        cta = "\n\n👉 ताज़ा ख़बरों के लिए पेज/चैनल को Like, Subscribe, Comment और Follow जरूर करें!"
        return ai_text + cta
    except Exception as e:
        logger.error(f"Gemini AI error after retries: {e}")
        return f"📢 {item['title']}\n\nSource: {item['source']}"
