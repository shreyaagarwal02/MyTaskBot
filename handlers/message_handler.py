from telegram import Update
from telegram.ext import ContextTypes
from config import TELEGRAM_USER_ID, GROQ_API_KEY
from groq import Groq
from task_manager import save_tasks, load_all_tasks, complete_task
import json
from datetime import datetime
from handlers.voice_handler import transcribe_voice

client = Groq(api_key=GROQ_API_KEY)

# Conversation memory - keeps last 6 messages (3 exchanges)
conversation_history = []

SYSTEM_PROMPT = """
You are a personal task manager assistant. Your job is to help the user manage their tasks via Telegram.

When the user sends a message, analyze it and respond with a JSON object in this exact format:
{
    "intent": "add_task" | "complete_task" | "list_tasks" | "delete_task" | "chat",
    "tasks": [
        {
            "title": "task title",
            "category": "work" | "personal" | "health" | "learning" | "admin",
            "urgency": "today" | "this_week" | "someday",
            "effort": "quick" | "medium" | "deep",
            "deadline": "YYYY-MM-DD or null"
        }
    ],
    "reply": "reply like your best friend who's keeping track of your life. super casual, warm, funny sometimes, use their exact words back at them, add a little personality. like 'vet visit for the kitty?? noted, tomorrow morning it is 🐱' or 'groceries before 6, got you 👍 don't forget the milk'. max 2 lines, no formal language ever."
}

Rules:
- Extract ALL tasks from a single message (user may mention multiple)
- If user says tomorrow, deadline is tomorrow's date and urgency is today since it is imminent
- Only use this_week if deadline is 3 or more days away
- If user says today, urgency is today
- Sound like a real person texting, not a bot confirming a transaction
- Vary your replies, don't always use the same structure
- Hinglish is fine if the user uses it
- Keep replies SHORT, max 2 lines
- Today's date is: {today}
- ALWAYS reply in English only, even if the user speaks in Hindi or Hinglish
- Never respond in Hindi or any other language, English only
- Use conversation history to understand context like "it", "that task", "the assignment" etc
- Only use intent complete_task if user EXPLICITLY mentions the task name AND says done/finished/completed. 
Example: 'done with groceries' or 'finished the assignment' = complete_task. 
But 'all done', 'okay done', 'done' alone = chat, ask them which task they completed"
- If user mentions a time like 'before 6', 'by evening', 'at 3pm', set urgency to today and 
mention the time in the task title like 'get groceries (before 6pm)'
- If user is correcting or updating an existing task (like adding a deadline or changing urgency), use intent 'update_task' not 'add_task'
- For update_task, use the same title as the existing task so it can be found
"""

async def process_message(user_message: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shared logic for both text and voice messages"""
    global conversation_history

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    today = datetime.now().strftime("%Y-%m-%d")
    system = SYSTEM_PROMPT.replace("{today}", today)

    # Add user message to history
    conversation_history.append({"role": "user", "content": user_message})

    # Build messages with history (last 6 = 3 exchanges)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system}
        ] + conversation_history[-6:],
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content
    print(f"Groq raw: {raw}")

    # Add bot response to history
    conversation_history.append({"role": "assistant", "content": raw})

    # Keep history from growing too large
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]

    try:
        data = json.loads(raw)
        intent = data.get("intent", "chat")
        tasks = data.get("tasks", [])
        reply = data.get("reply", "Done!")

        print(f"Intent: {intent} | New tasks from message: {len(tasks)}")

        if intent == "add_task" and tasks:
            save_tasks(tasks)

        elif intent == "update_task" and tasks:
            save_tasks(tasks)  # save_tasks will find and update existing file

        elif intent == "list_tasks":
            all_tasks = load_all_tasks()
            if all_tasks:
                tasks_text = "\n\n".join(all_tasks)
                summary_response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"""You are a chill helpful friend summarizing someone's task list.
Today's date is {today}.
Summarize these tasks casually like texting a friend.
IMPORTANT: Use the deadline date to describe when tasks are due, not the urgency field.
If deadline is today ({today}), say today.
If deadline is tomorrow, say tomorrow.
If deadline is this week, say this week.
No markdown, no **, just plain casual text with emojis. Keep it short."""},
                        {"role": "user", "content": f"Here are my tasks:\n{tasks_text}"}
                    ]
                )
                reply = summary_response.choices[0].message.content
            else:
                reply = "you're all clear! no pending tasks 🙌"

        elif intent == "complete_task":
            for task in tasks:
                complete_task(task.get("title", ""))
            reply = "✅ " + reply

        await update.message.reply_text(reply)

    except json.JSONDecodeError:
        await update.message.reply_text("Sorry I didn't understand that, try again!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != TELEGRAM_USER_ID:
        await update.message.reply_text("Sorry, this is a private bot.")
        return

    user_message = update.message.text
    print(f"Received: {user_message}")
    await process_message(user_message, update, context)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != TELEGRAM_USER_ID:
        await update.message.reply_text("Sorry, this is a private bot.")
        return

    file_id = update.message.voice.file_id
    transcribed_text = await transcribe_voice(context.bot, file_id)
    print(f"Transcribed: {transcribed_text}")
    await process_message(transcribed_text, update, context)