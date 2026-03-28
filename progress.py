import json
import os
from datetime import datetime

DATA_FILE = "progress.json"


def load_progress():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_progress(module, score, total, time_taken, attempts=None):
    data = load_progress()
    data.append({
        "module": module,
        "score": score,
        "total": total,
        "time_taken": time_taken,
        "attempts": attempts or [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def reset_progress():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)


def calculate_badges(data):
    badges = []

    total_attempts = len(data)

    if total_attempts >= 5:
        badges.append("⚽ Practice Player")

    if total_attempts >= 15:
        badges.append("🥅 Goal Scorer")

    if total_attempts >= 30:
        badges.append("🏆 Champion")

    if data:
        total_correct = sum(d["score"] for d in data)
        total_questions = sum(d["total"] for d in data)
        percentage = (total_correct / total_questions) * 100

        if percentage >= 90:
            badges.append("🔥 Ronaldo Level")
        elif percentage >= 75:
            badges.append("⚡ Messi Mode")

    return badges
