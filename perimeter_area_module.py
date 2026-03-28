import random
import re


# ------------------------------------
# 1️⃣ Square
# ------------------------------------

def square_perimeter():
    side = random.randint(2, 20)
    question = f"Find the perimeter of a square with side {side} cm."
    answer = str(4 * side)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Square"
    }


def square_area():
    side = random.randint(2, 20)
    question = f"Find the area of a square with side {side} cm."
    answer = str(side * side)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Square"
    }


# ------------------------------------
# 2️⃣ Rectangle
# ------------------------------------

def rectangle_perimeter():
    l = random.randint(3, 20)
    b = random.randint(2, 15)

    question = f"Find the perimeter of a rectangle with length {l} cm and breadth {b} cm."
    answer = str(2 * (l + b))

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Rectangle"
    }


def rectangle_area():
    l = random.randint(3, 20)
    b = random.randint(2, 15)

    question = f"Find the area of a rectangle with length {l} cm and breadth {b} cm."
    answer = str(l * b)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Rectangle"
    }


# ------------------------------------
# 3️⃣ Irregular Shape Perimeter
# ------------------------------------

def irregular_perimeter():
    sides = [random.randint(2, 15) for _ in range(5)]
    question = f"Find the perimeter of a shape with sides {', '.join(map(str, sides))} cm."
    answer = str(sum(sides))

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Irregular"
    }


# ------------------------------------
# 4️⃣ Area by Tiling
# ------------------------------------

def tiling_area():
    rows = random.randint(2, 6)
    cols = random.randint(2, 6)

    question = f"A rectangle has {rows} rows and {cols} columns of square tiles. Find the total area (in number of squares)."
    answer = str(rows * cols)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Tiling"
    }


# ------------------------------------
# 5️⃣ Shaded Area
# ------------------------------------

def shaded_area():
    total = random.randint(10, 25)
    shaded = random.randint(3, total - 2)

    question = f"A grid has {total} small squares. If {shaded} squares are shaded, what is the shaded area (in squares)?"
    answer = str(shaded)

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Shaded Area"
    }


# ------------------------------------
# Balanced Generator
# ------------------------------------

BALANCED_WORKSHEET_TYPES = [
    ("Square perimeter/area", [square_perimeter, square_area]),
    ("Rectangle perimeter/area", [rectangle_perimeter, rectangle_area]),
    ("Irregular perimeter", [irregular_perimeter]),
    ("Tiling area", [tiling_area]),
    ("Shaded area", [shaded_area]),
    (
        "Mixed practice",
        [
            square_perimeter,
            square_area,
            rectangle_perimeter,
            rectangle_area,
            irregular_perimeter,
            tiling_area,
            shaded_area,
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
        square_perimeter,
        square_area,
        rectangle_perimeter,
        rectangle_area,
        irregular_perimeter,
        tiling_area,
        shaded_area
    ]

    return random.choice(generators)()
