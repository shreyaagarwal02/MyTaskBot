import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from groq import Groq
from task_manager import load_all_tasks, load_completed_today
from config import GROQ_API_KEY, TELEGRAM_USER_ID
from datetime import datetime, timedelta

client = Groq(api_key=GROQ_API_KEY)

def generate_message(prompt: str, tasks_text: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""You are a chill helpful friend. Today is {today}.
You're texting your friend their task update. Be casual, warm, motivating.
No markdown, no **, just plain text with emojis. Keep it short and natural."""},
            {"role": "user", "content": prompt + "\n\nTasks:\n" + tasks_text}
        ]
    )
    return response.choices[0].message.content


async def morning_briefing(bot):
    tasks = load_all_tasks()
    if tasks:
        tasks_text = "\n\n".join(tasks)
        prompt = "Give a good morning message and summarize what your friend needs to do today. Be motivating and friendly."
    else:
        tasks_text = "no tasks"
        prompt = "Give a good morning message. Tell them they have nothing on the list today, maybe suggest they enjoy the day."

    message = generate_message(prompt, tasks_text)
    await bot.send_message(chat_id=TELEGRAM_USER_ID, text=message)
    print("Morning briefing sent!")


async def evening_checkin(bot):
    tasks = load_all_tasks()
    if tasks:
        tasks_text = "\n\n".join(tasks)
        prompt = "It's evening. Check in with your friend about their pending tasks. Ask how it's going, remind them what's still pending without being annoying."
    else:
        tasks_text = "no tasks"
        prompt = "It's evening and your friend has no pending tasks. Send a chill evening message."

    message = generate_message(prompt, tasks_text)
    await bot.send_message(chat_id=TELEGRAM_USER_ID, text=message)
    print("Evening check-in sent!")


async def night_summary(bot):
    all_tasks = load_all_tasks()
    tasks_text = "\n\n".join(all_tasks) if all_tasks else "no pending tasks"
    prompt = "It's night time. Give a brief summary of what's still pending. Tell your friend to rest well and that tomorrow is a new day. Keep it warm and short."

    message = generate_message(prompt, tasks_text)
    await bot.send_message(chat_id=TELEGRAM_USER_ID, text=message)
    print("Night summary sent!")


def setup_scheduler(bot):
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        morning_briefing,
        trigger="cron",
        hour=9, minute=0,
        args=[bot]
    )

    scheduler.add_job(
        evening_checkin,
        trigger="cron",
        hour=18, minute=0,
        args=[bot]
    )

    scheduler.add_job(
        night_summary,
        trigger="cron",
        hour=22, minute=0,
        args=[bot]
    )

    scheduler.start()
    print("Scheduler started! Morning 9am, Evening 6pm, Night 10pm")
    return scheduler


