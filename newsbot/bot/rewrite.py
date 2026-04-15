import os
import logging
import json
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

# Use the most stable available Gemini 1.5 model
MODEL_NAME = 'gemini-1.5-flash'

api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "YOUR_GEMINI_API_KEY":
    genai.configure(api_key=api_key)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def generate_ai_content(prompt):
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    if not response.text:
        raise Exception("Empty response from Gemini")
    return response.text.strip()

def rewrite(item):
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return f"📢 {item['title']}\n\nSource: {item['source']}"
        
    prompt = f"""You are a senior Hindi news editor and growth expert for Uttarakhand's top digital news network.
Your goal is to reach 100k followers by providing hyper-local, factual, and neutral news.

=== NEWS TO PROCESS ===
Title: {item['title']}
Description: {item.get('description', item.get('summary', ''))}
Source: {item['source']}
Trending: {"YES" if item.get('trending') else "NO"}
Area: {item.get('category', 'Uttarakhand')}
=======================

=== GENERATION RULES ===
1. TONE: Neutral, objective, and factual. Do not take sides (Govt/Opposition). Use "Sarkari" terminology for official notes.
2. FORMATTING: Output content for 4 specific platforms.
3. LANGUAGE: Pure Hindi for main content; Hinglish mix for Hooks and Hashtags.
4. ACCIDENTS: If this is an accident (हादसा), prioritize safety warnings and traffic status.

Output EXACTLY in this structured format:

--- FACEBOOK (Engagement Heavy) ---
📍 [Neighborhood/Area] 
📰 [Powerful Headline]
📝 [50-word narrative summary including impact on locals]
❓ [Local engagement question, e.g., "क्या आपके इलाके में भी यही हाल है?"]

--- INSTAGRAM/YT REELS (Visual Hook) ---
🎬 0s-2s Hook: [Shocking or curiosity trigger line in Hinglish]
🎬 Script: [3 lines of punchy, fast-paced script for a 15-sec reel]
#️⃣ [5 Viral Reels Hashtags]

--- X (Breaking/Fast) ---
⚡ [Short Breaking News Text - Max 200 chars]
🔗 [Source Link if available]
#UttarakhandNews #Breaking

--- YT COMMUNITY ---
📊 [Formal Summary - 2 paragraphs]
🗳️ Community Poll Suggestion: [A binary poll question related to the news]

--- TAGS ---
[10 keyword hashtags, including specific areas like #Haridwar #Dehradun]"""

    try:
        ai_text = generate_ai_content(prompt)
        footer = "\n\n👉 ताज़ा ख़बरों के लिए Like, Follow और Subscribe करें!"
        return ai_text + footer
    except Exception as e:
        logger.error(f"Gemini AI error: {e}")
        return f"📢 {item['title']}\n\nSource: {item['source']}\n(AI Rewrite Failed)"
