import os
from pathlib import Path
from dotenv import load_dotenv

DATA_DIR = Path.home() / ".email-brief"
DATA_DIR.mkdir(exist_ok=True)

ENV_FILE = DATA_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET", "")
AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL", "https://email-brief-eight.vercel.app")
BRIEFING_TIME = os.getenv("BRIEFING_TIME", "10:00")
EMAIL_COUNT = int(os.getenv("EMAIL_COUNT", "50"))

TOKEN_PATH = DATA_DIR / "token.json"
DB_PATH = DATA_DIR / "briefings.db"
