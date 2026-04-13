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
        
    prompt = f"""
    Please write a comprehensive, detailed, and engaging news article in Hindi based on the following news.
    
    Requirements:
    - Length: Minimum 200 words, Maximum 600 words.
    - Style: Professional, informative, and complete. Suitable for a Facebook news post or YouTube script.
    - Formatting: Write in clear paragraphs. NO emojis or icons whatsoever. Absolutely zero icons/emojis.
    - Language: 100% in pure Hindi (Devanagari script), Hinglish.
    - Constraints: Do not include any URLs or source links.
    
    News Headline: {item['title']}
    News Summary/Context: {item.get('summary', 'Context not provided, please expand based on the headline.')}
    Source: {item['source']}
    """
    try:
        return generate_ai_content(prompt)
    except Exception as e:
        logger.error(f"Gemini AI error after retries: {e}")
        return f"📢 {item['title']}\n\nSource: {item['source']}"
