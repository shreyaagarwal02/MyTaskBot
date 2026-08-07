import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TASKS_DIR = "tasks/"