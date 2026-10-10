# MyTaskBot 🤖
> A personal AI chief of staff that lives in your Telegram — understands natural language, manages your tasks, and proactively keeps you on track.

## Demo
> Send a voice note or text message and watch it classify, save, and remind you — automatically.

```
You:  "yaar aaj gym jaana hai aur assignment bhi submit karni hai by Friday"
Bot:  "got it! gym added for today and assignment's on the list for Friday 💪"

You:  "what are my tasks"
Bot:  "hey, so you've got gym today 🏋️, assignment due Friday 📚,
       and don't forget to call the bank tomorrow 📞. you got this!"
```

---

## Why I Built This
Most task managers are rigid — you open an app, tap buttons, fill forms. I wanted something that works the way I actually think: messy, natural, sometimes in Hinglish, sometimes via voice note while walking. This bot understands all of it.

---

## Features
- 🗣️ **Natural language input** — no commands, just talk to it like a friend
- 🎤 **Voice note support** — send a voice note, Whisper transcribes it automatically
- 🌐 **Hinglish support** — works in English, Hindi, or mixed
- 🧠 **Smart classification** — extracts task title, category, urgency, effort, and deadline from one message
- 📁 **Obsidian-compatible storage** — tasks saved as markdown files, readable in Obsidian
- 💬 **Conversation memory** — remembers context across messages ("done with that", "the assignment")
- ☀️ **Morning briefing** — proactive message every day at 9am with your priorities
- 🌆 **Evening check-in** — 6pm nudge on pending tasks
- 🌙 **Night summary** — 10pm recap of what got done
- 🔒 **Private** — only responds to your Telegram ID

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Interface | Telegram Bot API | Conversational UI, no frontend needed |
| LLM | Groq + gpt-oss-120b | Fast inference, generous free tier |
| Speech-to-Text | Groq Whisper | Multilingual, runs via API, free |
| Orchestration | python-telegram-bot | Async handlers for text + voice |
| Scheduling | APScheduler | Cron-based proactive messages |
| Storage | Markdown files | Obsidian-compatible, human-readable |
| Language | Python 3.11 | Async support, clean ecosystem |

---

## Architecture

```
User (Telegram)
      │
      ├── Text message ──────────────────┐
      │                                  │
      └── Voice note ──► Groq Whisper ──┤
                         (transcribe)    │
                                         ▼
                              Groq LLM (gpt-oss-120b)
                              + System Prompt
                              + Conversation History
                                         │
                              ┌──────────┴──────────┐
                              │                     │
                         Parse Intent          Generate Reply
                    (add/complete/list/chat)   (friendly tone)
                              │
                    ┌─────────┴─────────┐
                    │                   │
               Save to              Read from
             tasks/*.md            tasks/*.md
                    │
              Obsidian Vault
                              
APScheduler (runs in background)
      ├── 9:00 AM  → Morning briefing
      ├── 6:00 PM  → Evening check-in  
      └── 10:00 PM → Night summary
```

---

## What Makes It Agentic

This isn't just a chatbot that calls an API. It:

1. **Reasons about intent** — understands the difference between "I need to call the bank" (add task) vs "called the bank" (complete task) vs "what do I have today" (list tasks)
2. **Extracts structured data** from unstructured input — one messy sentence becomes a classified task with category, urgency, effort, and deadline
3. **Acts proactively** — sends you messages without being asked, at scheduled times
4. **Maintains context** — remembers what you said earlier in the conversation so "done with that" makes sense
5. **Handles ambiguity** — asks clarifying questions when it's not sure what you mean

---

## Project Structure

```
MyTaskBot/
├── handlers/
│   ├── message_handler.py   # Text + voice processing, LLM calls
│   └── voice_handler.py     # Whisper transcription
├── tasks/                   # Markdown task files (Obsidian-compatible)
├── config.py                # Environment variables
├── main.py                  # Bot setup + handler registration
├── scheduler.py             # APScheduler cron jobs
├── task_manager.py          # CRUD operations for task files
└── requirements.txt
```

---

## How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/shreyaagarwal02/MyTaskBot.git
cd MyTaskBot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**

Create a `.env` file:
```
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_USER_ID=your_telegram_user_id
GROQ_API_KEY=your_groq_api_key
```

Get your keys:
- Telegram token → @BotFather on Telegram
- Telegram user ID → @userinfobot on Telegram  
- Groq API key → console.groq.com (free, no card needed)

**4. Run**
```bash
python main.py
```

---

## How the LLM is Prompted

The system prompt instructs the model to always respond in a structured JSON format:

```json
{
  "intent": "add_task | complete_task | list_tasks | delete_task | chat",
  "tasks": [
    {
      "title": "task title",
      "category": "work | personal | health | learning | admin",
      "urgency": "today | this_week | someday",
      "effort": "quick | medium | deep",
      "deadline": "YYYY-MM-DD or null"
    }
  ],
  "reply": "casual friendly reply"
}
```

This structured output makes the agent deterministic and reliable — it always knows what to do next based on the intent field.

---

## Example Task File (Obsidian-compatible)

```markdown
# finish resume

- **Category:** work
- **Urgency:** today
- **Effort:** deep
- **Deadline:** 2026-05-22
- **Status:** pending
- **Created:** 2026-05-22 10:07
```

---

## Challenges & Learnings

- **Hinglish transcription** — Whisper occasionally mistranscribes mixed Hindi-English. Solved by letting Whisper auto-detect language rather than forcing Hindi mode.
- **Conversation memory** — without history, "done with that" has no context. Solved by passing last 6 messages to every LLM call.
- **Duplicate tasks** — same task mentioned twice created two files. Solved with keyword-based similarity matching before saving.
- **Vague completion** — "all done" was marking tasks complete without knowing which one. Solved with stricter prompt rules requiring explicit task names for completion.

---

## What's Next (v2)

- [ ] Deploy to cloud (Railway / Fly.io)
- [ ] Multi-intent handling in one message
- [ ] Weekly productivity analytics
- [ ] Task priority scoring
- [ ] Integration with Google Calendar

---

## Built By

**Shreya Agarwal** — building in the agentic AI space

[GitHub](https://github.com/shreyaagarwal02) • [LinkedIn](https://linkedin.com/in/shreyaagarwal)
