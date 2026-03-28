import random
import re
from datetime import datetime, timedelta


# ------------------------------------
# 1️⃣ 24 hr ↔ 12 hr Conversion
# ------------------------------------

def convert_24_to_12():
    hour = random.randint(0, 23)
    minute = random.choice([0, 15, 30, 45])

    time_24 = f"{hour:02}:{minute:02}"
    dt = datetime.strptime(time_24, "%H:%M")
    answer = dt.strftime("%I:%M %p")

    question = f"Convert {time_24} into 12-hour format."

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Clock Conversion"
    }


def convert_12_to_24():
    hour = random.randint(1, 12)
    minute = random.choice([0, 15, 30, 45])
    period = random.choice(["AM", "PM"])

    time_12 = f"{hour}:{minute:02} {period}"
    dt = datetime.strptime(time_12, "%I:%M %p")
    answer = dt.strftime("%H:%M")

    question = f"Convert {time_12} into 24-hour format."

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Clock Conversion"
    }


# ------------------------------------
# 2️⃣ Units Conversion
# ------------------------------------

def convert_hours_to_minutes():
    h = random.randint(1, 12)
    question = f"Convert {h} hours into minutes."
    answer = str(h * 60)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Time Conversion"
    }


def convert_days_to_hours():
    d = random.randint(1, 7)
    question = f"Convert {d} days into hours."
    answer = str(d * 24)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Time Conversion"
    }


# ------------------------------------
# 3️⃣ Addition of Time
# ------------------------------------

def add_time():
    h1 = random.randint(1, 5)
    m1 = random.choice([10, 20, 30, 40, 50])

    h2 = random.randint(1, 5)
    m2 = random.choice([10, 20, 30, 40, 50])

    total_minutes = (h1 * 60 + m1) + (h2 * 60 + m2)
    final_h = total_minutes // 60
    final_m = total_minutes % 60

    question = f"{h1} hr {m1} min + {h2} hr {m2} min = ?"
    answer = f"{final_h} hr {final_m} min"

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Addition"
    }


# ------------------------------------
# 4️⃣ Duration in Days
# ------------------------------------

def duration_in_days():
    start = random.randint(1, 20)
    end = start + random.randint(1, 10)

    question = f"Find the number of days from March {start} to March {end}."
    answer = str(end - start)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Duration"
    }


# ------------------------------------
# Balanced Generator
# ------------------------------------

BALANCED_WORKSHEET_TYPES = [
    ("Clock conversion", [convert_24_to_12, convert_12_to_24]),
    ("Time unit conversion", [convert_hours_to_minutes, convert_days_to_hours]),
    ("Add time", [add_time]),
    ("Duration", [duration_in_days]),
    (
        "Mixed practice",
        [
            convert_24_to_12,
            convert_12_to_24,
            convert_hours_to_minutes,
            convert_days_to_hours,
            add_time,
            duration_in_days,
        ],
    ),
]


def question_stem(question_text):
    normalized = question_text.lower()
    normalized = re.sub(r"\d+:\d+", "<time>", normalized)
    normalized = re.sub(r"\d+", "<num>", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def generate_balanced_worksheet(total_questions=15):
    questions = []
    used_stems = set()
    type_indices = list(range(len(BALANCED_WORKSHEET_TYPES)))
    random.shuffle(type_indices)
    base_count = total_questions // len(BALANCED_WORKSHEET_TYPES)
    remainder = total_questions % len(BALANCED_WORKSHEET_TYPES)

    for rank, idx in enumerate(type_indices):
        worksheet_type, generators = BALANCED_WORKSHEET_TYPES[idx]
        count = base_count + (1 if rank < remainder else 0)
        for _ in range(count):
            attempts = 0
            while True:
                q = random.choice(generators)()
                stem = question_stem(q["question"])
                if stem not in used_stems or attempts >= 20:
                    used_stems.add(stem)
                    break
                attempts += 1
            q["worksheet_type"] = worksheet_type
            questions.append(q)

    random.shuffle(questions)
    return questions


def generate_question():
    generators = [
        convert_24_to_12,
        convert_12_to_24,
        convert_hours_to_minutes,
        convert_days_to_hours,
        add_time,
        duration_in_days
    ]

    return random.choice(generators)()
