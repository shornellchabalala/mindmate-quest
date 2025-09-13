import json
from pathlib import Path
from datetime import datetime, timedelta

DATA_FILE = Path("data/data.json")

def init_data_file():
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        default_data = {
            "tasks": [],
            "xp": 0,
            "level": 1,
            "streak": 0,
            "last_login": None,
            "badges": []
        }
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(default_data, f, indent=2)

def get_data():
    init_data_file()
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    
    # Update streak if last login was yesterday
    today = datetime.now().date()
    last_login_str = data.get("last_login")
    if last_login_str:
        last_login = datetime.strptime(last_login_str, "%Y-%m-%d").date()
        if last_login == today - timedelta(days=1):
            data["streak"] += 1
        elif last_login != today:
            data["streak"] = 1
    else:
        data["streak"] = 1
    
    data["last_login"] = str(today)
    
    # Award badges based on XP
    badges = []
    if data["xp"] >= 50:
        badges.append("Bronze Learner")
    if data["xp"] >= 100:
        badges.append("Silver Scholar")
    if data["xp"] >= 200:
        badges.append("Gold Master")
    data["badges"] = badges
    
    # Save changes
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    return data

def save_task(task_name):
    data = get_data()
    data["tasks"].append({"task": task_name, "done": False})
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def complete_task(task_index):
    data = get_data()
    if 0 <= task_index < len(data["tasks"]):
        data["tasks"][task_index]["done"] = True
        # Gain XP
        data["xp"] += 10
        # Level up every 50 XP
        data["level"] = data["xp"] // 50 + 1
        # Save changes
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
