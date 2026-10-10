import os
import re
from datetime import datetime

TASKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks")


def save_tasks(tasks: list):
    os.makedirs(TASKS_DIR, exist_ok=True)
    saved = []

    for task in tasks:
        title = task.get("title", "untitled")

        clean = re.sub(r'[^\x00-\x7F]+', '', title.lower())
        clean = clean.strip().replace(" ", "_")
        filename = clean + ".md" if clean else f"task_{datetime.now().strftime('%H%M%S')}.md"
        filepath = os.path.join(TASKS_DIR, filename)

        existing_file = None
        for f in os.listdir(TASKS_DIR):
            if f.endswith(".md"):
                key_words = [w for w in clean.split("_") if len(w) > 3]
                if any(word in f for word in key_words):
                    existing_file = os.path.join(TASKS_DIR, f)
                    break

        if existing_file:
            with open(existing_file, "r", encoding="utf-8") as f:
                content = f.read()
            new_deadline = task.get("deadline", "none")
            content = re.sub(r'\*\*Deadline:\*\* .*', f'**Deadline:** {new_deadline}', content)
            new_urgency = task.get("urgency", "someday")
            content = re.sub(r'\*\*Urgency:\*\* .*', f'**Urgency:** {new_urgency}', content)
            with open(existing_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated existing task: {existing_file}")
            saved.append(title)
            continue

        deadline = task.get("deadline", "none")
        urgency = task.get("urgency", "someday")
        category = task.get("category", "general")
        effort = task.get("effort", "medium")
        created = datetime.now().strftime("%Y-%m-%d %H:%M")

        content = "# " + title + "\n\n"
        content += "- **Category:** " + category + "\n"
        content += "- **Urgency:** " + urgency + "\n"
        content += "- **Effort:** " + effort + "\n"
        content += "- **Deadline:** " + str(deadline) + "\n"
        content += "- **Status:** pending\n"
        content += "- **Created:** " + created + "\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        saved.append(title)
        print(f"Saved task: {filepath}")

    return saved


def load_all_tasks():
    os.makedirs(TASKS_DIR, exist_ok=True)
    tasks = []

    for filename in os.listdir(TASKS_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(TASKS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            if "Status:** pending" in content:
                tasks.append(content)

    return tasks


def complete_task(task_title: str):
    for filename in os.listdir(TASKS_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(TASKS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            if task_title.lower() in content.lower():
                content = content.replace(
                    "- **Status:** pending",
                    "- **Status:** completed ✅"
                )
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Completed task: {filename}")
                return True
    return False


def complete_all_tasks():
    for filename in os.listdir(TASKS_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(TASKS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace(
                "- **Status:** pending",
                "- **Status:** completed ✅"
            )
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
    print("All tasks completed!")


def delete_all_tasks():
    for filename in os.listdir(TASKS_DIR):
        if filename.endswith(".md"):
            os.remove(os.path.join(TASKS_DIR, filename))
    print("All tasks deleted!")


def load_completed_today():
    today = datetime.now().strftime("%Y-%m-%d")
    completed = []

    for filename in os.listdir(TASKS_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(TASKS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            if "completed ✅" in content and today in content:
                completed.append(content)

    return completed