import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_try = [
    'gemini-1.5-flash',
    'gemini-pro',
    'gemini-1.0-pro',
    'models/gemini-1.5-flash',
    'models/gemini-pro'
]

for m_name in models_to_try:
    print(f"Trying model: {m_name}")
    try:
        model = genai.GenerativeModel(m_name)
        response = model.generate_content("Hi")
        print(f"✅ Success with {m_name}!")
        print(f"Response: {response.text[:50]}...")
        break
    except Exception as e:
        print(f"❌ Error for {m_name}: {e}")
