import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
WEB_SITE_URL = os.getenv('WEB_SITE_URL', 'http://localhost:5173')
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://127.0.0.1:8000/bot/auth/')

if not BOT_TOKEN:
    print("[OGOHLANTIRISH] BOT_TOKEN .env faylida ko'rsatilmagan!")

