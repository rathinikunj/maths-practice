import random
import re
from math import gcd

# -----------------------------
# Utility Helpers
# -----------------------------

def simplify(n, d):
    g = gcd(n, d)
    return n // g, d // g

def improper_to_mixed(n, d):
    whole = n // d
    remainder = n % d
    return whole, remainder, d


# -----------------------------
# 1. TYPES OF FRACTIONS
# -----------------------------

def type_of_fraction():
    numerator = random.randint(1, 9)
    denominator = random.randint(2, 9)

    question = f"What type of fraction is {numerator}/{denominator}?"

    if numerator == 1:
        answer = "Unit"
    elif numerator < denominator:
        answer = "Proper"
    else:
        answer = "Improper"

    options = ["Unit", "Proper", "Improper", "Mixed"]
    random.shuffle(options)

    return {
        "question": question,
        "answer": answer,
        "options": options,
        "type": "mcq",
        "topic": "Types"
    }


def identify_like_unlike():
    d1 = random.randint(2, 9)
    d2 = random.randint(2, 9)

    question = f"Are {1}/{d1} and {2}/{d2} like fractions?"
    answer = "True" if d1 == d2 else "False"

    return {
        "question": question,
        "answer": answer,
        "type": "true_false",
        "topic": "Types"
    }


# -----------------------------
# 2. CONVERSIONS
# -----------------------------

def mixed_to_improper():
    whole = random.randint(1, 5)
    denominator = random.randint(2, 9)
    numerator = random.randint(1, denominator - 1)

    improper = whole * denominator + numerator

    question = f"Convert {whole} {numerator}/{denominator} into improper fraction."
    answer = f"{improper}/{denominator}"

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Conversion"
    }


def improper_to_mixed_q():
    denominator = random.randint(2, 9)
    whole = random.randint(1, 5)
    numerator = random.randint(1, denominator - 1)

    improper = whole * denominator + numerator

    question = f"Convert {improper}/{denominator} into mixed fraction."
    answer = f"{whole} {numerator}/{denominator}"

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Conversion"
    }


# -----------------------------
# 3. EQUIVALENT FRACTIONS
# -----------------------------

def equivalent_fraction_mcq():
    n = random.randint(1, 5)
    d = random.randint(2, 9)

    multiplier = random.randint(2, 5)
    correct_n = n * multiplier
    correct_d = d * multiplier

    options = [
        f"{correct_n}/{correct_d}",
        f"{n+1}/{d}",
        f"{n}/{d+1}",
        f"{n*2}/{d*3}"
    ]
    random.shuffle(options)

    return {
        "question": f"Which is equivalent to {n}/{d}?",
        "answer": f"{correct_n}/{correct_d}",
        "options": options,
        "type": "mcq",
        "topic": "Equivalent"
    }


def check_equivalent_true_false():
    n = random.randint(1, 5)
    d = random.randint(2, 9)

    multiplier = random.randint(2, 4)

    correct = random.choice([True, False])

    if correct:
        n2 = n * multiplier
        d2 = d * multiplier
    else:
        n2 = n * multiplier
        d2 = d * multiplier + 1

    question = f"True or False: {n}/{d} = {n2}/{d2}"
    answer = "True" if correct else "False"

    return {
        "question": question,
        "answer": answer,
        "type": "true_false",
        "topic": "Equivalent"
    }


# -----------------------------
# 4. COMPARISON
# -----------------------------

def compare_like():
    d = random.randint(2, 12)
    n1 = random.randint(1, d - 1)
    n2 = random.randint(1, d - 1)

    answer = ">" if n1 > n2 else "<" if n1 < n2 else "="

    question = f"Fill in the blank: {n1}/{d} ___ {n2}/{d}"

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Comparison"
    }


def compare_unlike():
    n1 = random.randint(1, 9)
    d1 = random.randint(2, 9)

    n2 = random.randint(1, 9)
    d2 = random.randint(2, 9)

    val1 = n1 / d1
    val2 = n2 / d2

    answer = ">" if val1 > val2 else "<" if val1 < val2 else "="

    question = f"Fill in the blank: {n1}/{d1} ___ {n2}/{d2}"

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Comparison"
    }


# -----------------------------
# 5. ADDITION & SUBTRACTION (LIKE)
# -----------------------------

def addition_like():
    d = random.randint(3, 12)
    n1 = random.randint(1, d - 2)
    n2 = random.randint(1, d - n1 - 1)

    result_n = n1 + n2

    question = f"{n1}/{d} + {n2}/{d} = ?"
    answer = f"{result_n}/{d}"

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Addition/Subtraction"
    }


def subtraction_like():
    d = random.randint(3, 12)
    n1 = random.randint(2, d - 1)
    n2 = random.randint(1, n1)

    result_n = n1 - n2

    question = f"{n1}/{d} - {n2}/{d} = ?"
    answer = f"{result_n}/{d}"

    return {
        "question": question,
        "answer": answer,
        "type": "fill",
        "topic": "Addition/Subtraction"
    }


# -----------------------------
# 6. WORD PROBLEMS
# -----------------------------

def fraction_word_problem():
    denominator = random.randint(3, 12)
    n1 = random.randint(1, denominator - 1)
    n2 = random.randint(1, denominator - 1)
    operation = random.choice(["add", "subtract"])

    if operation == "add":
        # Keep result a proper fraction for Class 4 practice.
        while n1 + n2 >= denominator:
            n1 = random.randint(1, denominator - 1)
            n2 = random.randint(1, denominator - 1)
        result_n = n1 + n2
        question = (
            f"Riya ate {n1}/{denominator} of a pizza at lunch and "
            f"{n2}/{denominator} at dinner. How much pizza did she eat in total?"
        )
    else:
        if n2 > n1:
            n1, n2 = n2, n1
        result_n = n1 - n2
        question = (
            f"Arjun filled {n1}/{denominator} of a water bottle in the morning "
            f"and used {n2}/{denominator} by afternoon. How much water is left?"
        )

    simplified_n, simplified_d = simplify(result_n, denominator)

    return {
        "question": question,
        "answer": f"{simplified_n}/{simplified_d}",
        "type": "fill",
        "topic": "Word Problems"
    }


# -----------------------------
# Balanced Worksheet Generator
# -----------------------------

BALANCED_WORKSHEET_TYPES = [
    ("Identify types", [type_of_fraction]),
    ("Convert mixed/improper", [mixed_to_improper, improper_to_mixed_q]),
    ("Equivalent fractions", [equivalent_fraction_mcq]),
    ("Compare fractions", [compare_like, compare_unlike]),
    ("Add/Subtract like fractions", [addition_like, subtraction_like]),
    ("Word problems", [fraction_word_problem]),
    ("True/False", [identify_like_unlike, check_equivalent_true_false]),
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
        type_of_fraction,
        identify_like_unlike,
        mixed_to_improper,
        improper_to_mixed_q,
        equivalent_fraction_mcq,
        check_equivalent_true_false,
        compare_like,
        compare_unlike,
        addition_like,
        subtraction_like,
        fraction_word_problem
    ]

    return random.choice(generators)()
