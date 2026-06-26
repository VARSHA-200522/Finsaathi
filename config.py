import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

PROJECT_NAME = "FinSaathi"
VERSION = "1.0.0"
LANGUAGE = "en"
MAX_TOKENS = 1000
MODEL_NAME = "gemini-2.5-flash"
DB_PATH = "data/finsaathi.db"