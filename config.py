import os
from dotenv import load_dotenv

load_dotenv()

# Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")

# Admins
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

# APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot.db")

# OpenAI model
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Rate limiting
RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "10"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

# Default language
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ar")

# Max notes per user
MAX_NOTES = int(os.getenv("MAX_NOTES", "50"))

# Max reminders per user
MAX_REMINDERS = int(os.getenv("MAX_REMINDERS", "10"))

# AI conversation history length
AI_HISTORY_LENGTH = int(os.getenv("AI_HISTORY_LENGTH", "20"))
