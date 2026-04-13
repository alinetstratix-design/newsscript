import os
import logging
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
PHOTO_URL = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def send_message(text):
    data = {"chat_id": CHAT_ID, "text": text}
    resp = requests.post(URL, data=data, timeout=10)
    resp.raise_for_status()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def send_photo(photo_url, caption):
    data = {"chat_id": CHAT_ID, "photo": photo_url, "caption": caption}
    resp = requests.post(PHOTO_URL, data=data, timeout=15)
    if resp.status_code != 200:
        logger.warning(f"Failed to send photo: {resp.text}. Falling back to text.")
        send_message(caption)
