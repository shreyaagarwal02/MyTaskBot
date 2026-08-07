from telegram.ext import ApplicationBuilder, MessageHandler, filters
from handlers.message_handler import handle_message, handle_voice
from config import TELEGRAM_TOKEN
from scheduler import setup_scheduler

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Text messages
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Voice messages
app.add_handler(MessageHandler(filters.VOICE, handle_voice))

async def on_startup(application):
    setup_scheduler(application.bot)

app.post_init = on_startup

print("Bot is running...")
app.run_polling()