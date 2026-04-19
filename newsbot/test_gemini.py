import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing with API Key: {api_key[:10]}...")

genai.configure(api_key=api_key)
# Using the updated model name
MODEL_NAME = 'gemini-flash-latest'

try:
    print(f"Attempting to generate content with {MODEL_NAME}...")
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content("Hello! This is a test from the news bot.")
    print("Success! Response:")
    print(response.text)
except Exception as e:
    print(f"Error occurred: {e}")
    # We expect 403 if the key hasn't been replaced yet
    if "403" in str(e):
        print("\n[!] WARNING: The API key is still blocked (403 Leaked Key).")
        print("Please replace the key in .env with a new one from https://aistudio.google.com/app/apikey")
