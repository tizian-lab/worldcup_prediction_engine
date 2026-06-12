import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
WORLD_CUP_LEAGUE_ID = int(os.getenv("WORLD_CUP_LEAGUE_ID", 1))
WORLD_CUP_SEASON = int(os.getenv("WORLD_CUP_SEASON", 2026))

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN fehlt in der .env-Datei.")

if not API_FOOTBALL_KEY:
    raise ValueError("API_FOOTBALL_KEY fehlt in der .env-Datei.")