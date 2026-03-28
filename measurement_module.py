import random
import re


# -----------------------------------
# 1️⃣ Units of Measurement (Concept)
# -----------------------------------

def unit_identification():
    questions = [
        ("What unit is used to measure the length of a road?", "Kilometre"),
        ("What unit is used to measure milk?", "Litre"),
        ("What unit is used to measure weight of rice?", "Kilogram"),
        ("What unit is used to measure height of a person?", "Metre"),
        ("What unit is used to measure medicine?", "Millilitre"),
    ]

    question, answer = random.choice(questions)

    option_pool = ["Kilometre", "Litre", "Kilogram", "Metre", "Millilitre", "Gram", "Centimetre"]
    wrong_options = [option for option in option_pool if option != answer]
    options = random.sample(wrong_options, 3) + [answer]
    random.shuffle(options)

    return {
        "question": question,
        "answer": answer,
        "options": options,
        "type": "mcq",
        "topic": "Units"
    }


# -----------------------------------
# 2️⃣ Conversion Questions
# -----------------------------------

def convert_length():
    value = random.randint(1, 9)

    if random.choice([True, False]):
        question = f"Convert {value} km into metres."
        answer = str(value * 1000)
    else:
        question = f"Convert {value} m into centimetres."
        answer = str(value * 100)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Conversion"
    }


def convert_mass():
    if random.choice([True, False]):
        value = random.randint(1, 9)
        question = f"Convert {value} kg into grams."
        answer = str(value * 1000)
    else:
        value = random.randint(1, 9) * 1000
        question = f"Convert {value} g into kilograms."
        answer = str(value // 1000)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Conversion"
    }


def convert_capacity():
    if random.choice([True, False]):
        value = random.randint(1, 9)
        question = f"Convert {value} L into millilitres."
        answer = str(value * 1000)
    else:
        value = random.randint(1, 9) * 1000
        question = f"Convert {value} ml into litres."
        answer = str(value // 1000)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Conversion"
    }


# -----------------------------------
# 3️⃣ Addition & Subtraction
# -----------------------------------

def add_length():
    m1 = random.randint(1, 9)
    cm1 = random.randint(10, 90)

    m2 = random.randint(1, 9)
    cm2 = random.randint(10, 90)

    total_cm = cm1 + cm2
    extra_m = total_cm // 100
    final_cm = total_cm % 100
    final_m = m1 + m2 + extra_m

    question = f"{m1} m {cm1} cm + {m2} m {cm2} cm = ?"
    answer = f"{final_m} m {final_cm} cm"

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Addition/Subtraction"
    }


def subtract_mass():
    kg1 = random.randint(5, 9)
    g1 = random.randint(100, 900)

    kg2 = random.randint(1, 4)
    g2 = random.randint(100, 900)

    total1 = kg1 * 1000 + g1
    total2 = kg2 * 1000 + g2

    diff = total1 - total2
    final_kg = diff // 1000
    final_g = diff % 1000

    question = f"{kg1} kg {g1} g - {kg2} kg {g2} g = ?"
    answer = f"{final_kg} kg {final_g} g"

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Addition/Subtraction"
    }


# -----------------------------------
# 4️⃣ Estimation
# -----------------------------------

def estimate_rounding():
    value = random.randint(100, 999)

    rounded = round(value, -2)

    question = f"Round {value} g to the nearest 100 g."
    answer = str(rounded)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Estimation"
    }


# -----------------------------------
# Balanced Generator
# -----------------------------------

BALANCED_WORKSHEET_TYPES = [
    ("Unit identification", [unit_identification]),
    ("Length conversion", [convert_length]),
    ("Mass conversion", [convert_mass]),
    ("Capacity conversion", [convert_capacity]),
    ("Add/Subtract measurements", [add_length, subtract_mass]),
    ("Estimation", [estimate_rounding]),
    (
        "Mixed practice",
        [
            unit_identification,
            convert_length,
            convert_mass,
            convert_capacity,
            add_length,
            subtract_mass,
            estimate_rounding,
        ],
    ),
]


def question_stem(question_text):
    normalized = question_text.lower()
    normalized = re.sub(r"\d+/\d+", "<frac>", normalized)
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
        unit_identification,
        convert_length,
        convert_mass,
        convert_capacity,
        add_length,
        subtract_mass,
        estimate_rounding
    ]

    return random.choice(generators)()
