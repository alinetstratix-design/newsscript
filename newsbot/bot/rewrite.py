import os
import logging
import json
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_fixed
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Use the most stable available Gemini 1.5 model
# Use 'gemini-flash-latest' for the best combination of speed and availability
MODEL_NAME = 'gemini-flash-latest'

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
        
    prompt = f"""तुम एक अनुभवी हिंदी न्यूज़ एंकर और रिपोर्टर हो।
तुम्हारी शैली शांत, सवाल पूछने वाली और जमीन से जुड़ी हो (Ravish Kumar और Anjana Om Kashyap जैसी)।

नीचे दी गई खबर को ऐसे लिखो जैसे कोई असली पत्रकार लिखता है — भरोसेमंद, साफ और इंसानी अंदाज़ में।

========================
खबर:
Title: {item['title']}
Details: {item.get('description', item.get('summary', ''))}
Source: {item['source']}
Area: {item.get('category', 'Uttarakhand')}
========================

नियम:
- कोई emoji नहीं
- कोई AI जैसा formatting नहीं
- भाषा सरल, natural और conversational हो
- tone calm रहे, sensational नहीं
- जरूरी जगह पर सवाल पूछो (viewer connect के लिए)
- अगर हादसा है तो असर और सावधानी ज़रूर बताओ
- लोकल एंगल जोड़ो (हरिद्वार, रुड़की आदि)
- खबर believable लगे, script नहीं

OUTPUT FORMAT:

FACEBOOK POST:
[हेडलाइन]

[60–80 शब्दों में पूरी खबर, बीच में 1–2 सवाल naturally डालो]

[लोकल असर या ground situation]

[End में soft CTA — जैसे: 
"ऐसी ही खबरों के लिए हमारे पेज को फॉलो करें, आप क्या सोचते हैं हमें जरूर बताएं।"]

INSTAGRAM REEL SCRIPT:
Hook (Hinglish, calm but engaging)

Line 1  
Line 2  
Line 3  

CTA (short, natural): Follow for real local updates

Hashtags: 5 simple hashtags (no spam)

X POST:
Short breaking line (max 180 characters, neutral tone)

YOUTUBE COMMUNITY:
2 छोटे पैराग्राफ (calm + questioning tone)

Poll: Yes/No based question

End line:
"अगर आप अपने इलाके की सच्ची खबरें देखना चाहते हैं, तो जुड़े रहें।"

TAGS:
10 clean hashtags (local + topic based)"""

    try:
        ai_text = generate_ai_content(prompt)
        footer = "\n\n👉 ताज़ा ख़बरों के लिए Like, Follow और Subscribe करें!"
        return ai_text + footer
    except Exception as e:
        logger.exception(f"Gemini AI error during rewrite: {e}")
        return f"📢 {item['title']}\n\nSource: {item['source']}\n(AI Rewrite Failed)"
