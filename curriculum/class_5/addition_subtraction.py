"""Class 5: Addition, Subtraction and Their Applications.

Whole-number calculations use 7–9 digit operands and nonnegative answers.
Estimates round each operand first. Subtraction has a right identity (zero),
not a two-sided identity, and is neither commutative nor associative.
"""

import random

from .large_numbers import format_number, question, round_half_up


CHAPTER_NAME = "Addition, Subtraction and Their Applications"
PROPERTY_OPTIONS = ["Commutative property", "Associative property", "Identity property"]


def number():
    digits = random.choice([7, 8, 9])
    return random.randint(10 ** (digits - 1), 10 ** digits - 1)


def display(value):
    return format_number(value, "Indian")


def numeric_question(text, answer, topic, **extra):
    return question(text, display(answer), topic,
                    hint="Enter a number, with or without commas.", **extra)


def choice_question(text, answer, options, topic):
    options = list(options)
    random.shuffle(options)
    return question(text, answer, topic, type="mcq", options=options)


def addition():
    a, b, c = number(), number(), number()
    operands = [a, b] if random.choice([True, False]) else [a, b, c]
    return numeric_question("Add: " + " + ".join(map(display, operands)) + " = ?",
                            sum(operands), "Addition of large numbers")


def addition_parts():
    a, b = random.sample(range(1_000_000, 100_000_000), 2)
    values = {"augend": a, "addend": b, "sum": a + b}
    part = random.choice(list(values))
    return choice_question(
        f"In {display(a)} + {display(b)} = {display(a + b)}, what is the {part}? "
        "Use the labels: augend + addend = sum.",
        display(values[part]), [display(value) for value in values.values()],
        "Parts of addition",
    )


def addition_property(kind):
    a, b, c = number(), number(), number()
    if kind == "Commutative":
        equation = f"{display(a)} + {display(b)} = {display(b)} + {display(a)}"
    elif kind == "Associative":
        equation = (f"({display(a)} + {display(b)}) + {display(c)} = "
                    f"{display(a)} + ({display(b)} + {display(c)})")
    else:
        equation = random.choice([f"{display(a)} + 0 = {display(a)}",
                                  f"0 + {display(a)} = {display(a)}"])
    return choice_question(f"Which property of addition is shown? {equation}",
                           f"{kind} property", PROPERTY_OPTIONS,
                           f"Addition: {kind.lower()} property")


def estimation(subtract=False):
    a, b = number(), number()
    if subtract:
        a, b = max(a, b), min(a, b)
    unit = 10 ** random.randint(1, 7)
    rounded_a, rounded_b = round_half_up(a, unit), round_half_up(b, unit)
    answer = rounded_a - rounded_b if subtract else rounded_a + rounded_b
    operation = "difference" if subtract else "sum"
    symbol = "−" if subtract else "+"
    return question(
        f"Estimate the {operation}: {display(a)} {symbol} {display(b)}. "
        f"Round EACH number to the nearest {display(unit)} first, then "
        f"{'subtract' if subtract else 'add'}.",
        display(answer), f"Estimating {operation}s",
        hint="Halfway values round up. Enter the estimated answer, not the exact answer.",
    )


def subtraction():
    a, b = number(), number()
    a, b = max(a, b), min(a, b)
    return numeric_question(f"Subtract: {display(a)} − {display(b)} = ?",
                            a - b, "Subtraction of large numbers")


def subtraction_parts():
    b = number()
    # Distinct values keep each option unambiguous.
    difference = b + random.randint(1, 9999)
    a = b + difference
    values = {"minuend": a, "subtrahend": b, "difference": difference}
    part = random.choice(list(values))
    return choice_question(
        f"In {display(a)} − {display(b)} = {display(difference)}, what is the {part}?",
        display(values[part]), [display(value) for value in values.values()],
        "Parts of subtraction",
    )


def subtraction_commutative():
    statement, answer = random.choice([
        ("Subtraction is commutative: changing the order always gives the same difference.", False),
        ("Subtraction is not commutative: changing the order can change the difference.", True),
    ])
    return question("True or False: " + statement, answer,
                    "Subtraction: commutative property", type="true_false")


def subtraction_associative():
    b, c = number(), number()
    b, c = max(b, c), min(b, c)
    a = b + c + number()
    equal = random.choice([True, False])
    comparison = "=" if equal else "≠"
    return question(
        f"True or False: ({display(a)} − {display(b)}) − {display(c)} "
        f"{comparison} {display(a)} − ({display(b)} − {display(c)}).",
        not equal, "Subtraction: associative property", type="true_false",
        hint="Calculate inside parentheses first. Does regrouping change the result?",
    )


def subtraction_zero():
    a = number()
    statement, answer = random.choice([
        (f"{display(a)} − 0 = {display(a)}.", True),
        (f"0 − {display(a)} = {display(a)}.", False),
        ("Subtracting zero from a number leaves that number unchanged.", True),
        ("Subtracting a positive number from zero leaves that positive number unchanged.", False),
    ])
    return question("True or False: " + statement, answer,
                    "Subtraction: zero", type="true_false")


def mixed_operations():
    a, b = number(), number()
    c = random.randint(1, a + b)
    if random.choice([True, False]):
        text = f"Calculate: ({display(a)} + {display(b)}) − {display(c)} = ?"
        hint = "Add the numbers in parentheses first, then subtract."
    else:
        # This also equals a + b - c, but the ungrouped expression is evaluated
        # left to right; addition does not have priority over subtraction.
        c = random.randint(1, a)
        text = f"Calculate: {display(a)} − {display(c)} + {display(b)} = ?"
        hint = "Addition and subtraction have equal priority. Work from left to right."
    return question(text, display(a + b - c), "Addition and subtraction together", hint=hint)


def word_problem(subtract=False):
    a, b = number(), number()
    if subtract:
        a, b = max(a, b), min(a, b)
        text = (f"A warehouse had {display(a)} notebooks and sent {display(b)} notebooks "
                "to schools. How many notebooks remain?")
        return numeric_question(text, a - b, "Subtraction applications")
    if random.choice([True, False]):
        text = (f"A city library programme distributed {display(a)} books last year and "
                f"{display(b)} books this year. How many books were distributed in all?")
        return numeric_question(text, a + b, "Addition applications")
    c = random.randint(1, a + b)
    text = (f"A relief fund received Rs {display(a)} in one month and Rs {display(b)} "
            f"the next month. It spent Rs {display(c)} on supplies. How many rupees remain?")
    return numeric_question(text, a + b - c, "Addition applications")


WORKSHEET_GENERATORS = [
    addition,
    addition_parts,
    lambda: addition_property("Associative"),
    lambda: addition_property("Identity"),
    lambda: addition_property("Commutative"),
    estimation,
    subtraction,
    subtraction_parts,
    subtraction_commutative,
    subtraction_associative,
    subtraction_zero,
    lambda: estimation(subtract=True),
    mixed_operations,
    word_problem,
    lambda: word_problem(subtract=True),
]


def generate_balanced_worksheet(total_questions=15):
    if not isinstance(total_questions, int) or total_questions < 0:
        raise ValueError("total_questions must be a nonnegative integer")
    questions = []
    while len(questions) < total_questions:
        generators = list(WORKSHEET_GENERATORS)
        random.shuffle(generators)
        for generator in generators[:total_questions - len(questions)]:
            item = generator()
            item["worksheet_type"] = item["topic"]
            questions.append(item)
    random.shuffle(questions)
    return questions
