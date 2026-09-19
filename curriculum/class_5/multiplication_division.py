"""Class 5 multiplication, division, applications, and order of operations."""

import random

from .large_numbers import format_number, question, round_half_up

CHAPTER_NAME = "Multiplication, Division and Their Applications"


def display(number):
    return format_number(number, "Indian")


def numeric(text, answer, topic, **extra):
    return question(text, display(answer), topic, **extra)


def mcq(text, answer, options, topic):
    options = list(options)
    random.shuffle(options)
    return question(text, answer, topic, type="mcq", options=options)


def multiplication_tables():
    a, b = random.randint(2, 20), random.randint(1, 12)
    return numeric(f"{a} × {b} = ?", a * b, "Multiplication tables")


def multiplication_terms():
    a, b = random.randint(1000, 9999), random.randint(2, 99)
    values = {"multiplicand": a, "multiplier": b, "product": a * b}
    term = random.choice(list(values))
    return mcq(f"In {display(a)} × {b} = {display(a * b)}, identify the {term}. "
               "Use the labels: multiplicand × multiplier = product.",
               display(values[term]), [display(n) for n in values.values()], "Multiplication terms")


def multiplication_property(kind=None):
    kind = kind or random.choice(["identity", "zero", "commutative", "associative"])
    a, b, c = random.randint(100, 9999), random.randint(2, 30), random.randint(2, 20)
    if kind in ("identity", "zero"):
        factor = 1 if kind == "identity" else 0
        left, right = random.choice([(a, factor), (factor, a)])
        result = a if factor else 0
        return numeric(f"Use the {kind} property: {display(left)} × {display(right)} = ?",
                       result, "Multiplication properties")
    if kind == "commutative":
        equation = f"{a} × {b} = {b} × {a}"
    else:
        equation = f"({a} × {b}) × {c} = {a} × ({b} × {c})"
    return mcq(f"Which property is shown? {equation}", f"{kind.title()} property",
               ["Identity property", "Zero property", "Commutative property", "Associative property"],
               "Multiplication properties")


def distributive_property(subtract=None):
    subtract = random.choice([True, False]) if subtract is None else subtract
    a, c = random.randint(2, 30), random.randint(2, 50)
    b = c + random.randint(1, 50)
    symbol = "−" if subtract else "+"
    return numeric(f"Use the distributive property to calculate {a} × ({b} {symbol} {c}).",
                   a * (b - c if subtract else b + c), "Distributive property",
                   hint=f"Multiply each term: ({a} × {b}) {symbol} ({a} × {c}).")


def large_multiplication():
    digits = random.choice([4, 5])
    a = random.randint(10 ** (digits - 1), 10 ** digits - 1)
    b = random.randint(12, 999)
    return numeric(f"Multiply: {display(a)} × {display(b)} = ?", a * b,
                   "Large-number multiplication")


def lattice_svg(a, b):
    """A real diagonal lattice: tens above each diagonal, ones below it.

    All interpolated content comes from integer operands, never user HTML.
    """
    top, side = str(int(a)), str(int(b))
    size, margin = 56, 40
    width, height = len(top) * size + 2 * margin, len(side) * size + 2 * margin
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
             f'width="{width}" height="{height}" role="img" aria-label="Lattice for {a} times {b}">',
             f'<rect width="{width}" height="{height}" fill="white"/>',
             '<g font-family="sans-serif" font-size="18" text-anchor="middle" fill="#172554">']
    for col, digit in enumerate(top):
        parts.append(f'<text x="{margin + col * size + size // 2}" y="25">{digit}</text>')
    for row, digit in enumerate(side):
        y = margin + row * size
        parts.append(f'<text x="{margin + len(top) * size + 20}" y="{y + 34}">{digit}</text>')
        for col, other in enumerate(top):
            x = margin + col * size
            tens, ones = divmod(int(digit) * int(other), 10)
            parts.extend([
                f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="none" stroke="#334155"/>',
                f'<line x1="{x + size}" y1="{y}" x2="{x}" y2="{y + size}" stroke="#64748b"/>',
                f'<text x="{x + 15}" y="{y + 23}">{tens}</text>',
                f'<text x="{x + 41}" y="{y + 48}">{ones}</text>',
            ])
    parts.append('</g></svg>')
    return ''.join(parts)


def lattice_multiplication():
    a = random.randint(1000, 9999) if random.choice([True, False]) else random.randint(10000, 99999)
    b = random.randint(12, 99)
    return numeric(f"Use the lattice to find {display(a)} × {b}.", a * b,
                   "Lattice multiplication", diagram=lattice_svg(a, b),
                   hint="Each cell shows a digit product: tens above the diagonal, ones below. "
                        "Start at the bottom-right diagonal. Add along each diagonal, write its "
                        "ones digit, and carry its tens to the next diagonal towards the top-left.")


def multiplication_powers():
    a, factor = random.randint(100, 99999), random.choice([10, 100, 1000])
    return numeric(f"Multiply: {display(a)} × {display(factor)} = ?", a * factor,
                   "Multiplication by 10, 100 and 1000")


def estimating_products():
    a, b = random.randint(1000, 99999), random.randint(12, 99)
    unit = random.choice([100, 1000])
    return numeric(f"Estimate {display(a)} × {b}: round {display(a)} to the nearest "
                   f"{display(unit)} and {b} to the nearest 10, then multiply.",
                   round_half_up(a, unit) * round_half_up(b, 10), "Estimating products",
                   hint="Round each factor first. Halfway values round up.")


def multiplication_application():
    boxes, count = random.randint(1000, 99999), random.randint(12, 99)
    return numeric(f"A factory packs {count} pencils in each box. How many pencils are in "
                   f"{display(boxes)} boxes?", boxes * count, "Multiplication applications")


def division_terms():
    divisor, quotient = random.randint(12, 99), random.randint(101, 999)
    remainder = random.randint(0, divisor - 1)
    dividend = divisor * quotient + remainder
    values = {"dividend": dividend, "divisor": divisor, "quotient": quotient, "remainder": remainder}
    term = random.choice(list(values))
    return mcq(f"{display(dividend)} ÷ {divisor} = {quotient}, remainder {remainder}. "
               f"Which number is the {term}?", display(values[term]),
               [display(n) for n in values.values()], "Division terms")


def division_property(kind=None):
    kind = kind or random.choice(["one", "self", "zero_dividend", "zero_divisor", "identity", "remainder"])
    a = random.randint(10, 99999)
    if kind == "one":
        return numeric(f"{display(a)} ÷ 1 = ?", a, "Division properties")
    if kind == "self":
        return numeric(f"{display(a)} ÷ {display(a)} = ?", 1, "Division properties")
    if kind == "zero_dividend":
        return numeric(f"0 ÷ {display(a)} = ?", 0, "Division properties")
    if kind == "zero_divisor":
        dividend = random.choice([0, a])
        return mcq(f"What is {display(dividend)} ÷ 0?", "Undefined (division by zero is not allowed)",
                   ["0", display(a), "1", "Undefined (division by zero is not allowed)"], "Division properties")
    if kind == "identity":
        divisor, quotient = random.randint(12, 99), random.randint(100, 999)
        remainder = random.randint(0, divisor - 1)
        return numeric(f"Find the dividend when the divisor is {divisor}, the quotient is "
                       f"{quotient}, and the remainder is {remainder}.", divisor * quotient + remainder,
                       "Division properties", hint="Dividend = divisor × quotient + remainder.")
    divisor = random.randint(12, 99)
    remainder = random.choice([0, divisor - 1, divisor, divisor + 1])
    return question(f"True or False: {remainder} can be the remainder when a whole number "
                    f"is divided by {divisor}.", remainder < divisor, "Division properties",
                    type="true_false", hint="A remainder is nonnegative and strictly smaller than the divisor.")


def division_question(dividend, divisor, topic):
    quotient, remainder = divmod(dividend, divisor)
    return question(f"Divide {display(dividend)} by {display(divisor)}. Give the quotient and remainder.",
                    f"{display(quotient)} R {remainder}", topic, "quotient_remainder",
                    hint="Enter quotient R remainder, for example 125 R 3. Use R 0 for exact division.")


def division_powers():
    return division_question(random.randint(10000, 99999), random.choice([10, 100, 1000]),
                             "Division by 10, 100 and 1000")


def long_division():
    return division_question(random.randint(10000, 99999), random.randint(12, 99),
                             "Five-digit by two-digit division")


def unitary_method():
    units, price = random.randint(2, 20), random.randint(25, 999)
    target = random.choice([1, random.randint(21, 50)])
    return numeric(f"{units} identical notebooks cost Rs {display(units * price)}. "
                   f"At the same price per notebook, what is the cost in rupees of {target} "
                   f"{'notebook' if target == 1 else 'notebooks'}?", price * target,
                   "Division applications: unitary method",
                   hint="Find the cost of one notebook first, then the required number.")


def dmas(kind=None):
    kind = kind or random.choice(["mixed", "multiply_divide", "subtract_add"])
    a, b, c = random.randint(2, 20), random.randint(2, 20), random.randint(2, 20)
    if kind == "multiply_divide":
        expression, answer = f"{a * b} × {c} ÷ {b}", a * c
    elif kind == "subtract_add":
        expression, answer = f"{a + b} − {b} + {c}", a + c
    else:
        expression, answer = f"{a * b} ÷ {b} + {c} × {b} − {a}", c * b
    return numeric(f"Use DMAS: {expression} = ?", answer, "DMAS",
                   hint="Do division and multiplication first, from left to right. "
                        "Then do addition and subtraction, from left to right.")


WORKSHEET_GENERATORS = [
    multiplication_tables, multiplication_terms, multiplication_property,
    distributive_property, large_multiplication, lattice_multiplication,
    multiplication_powers, estimating_products, multiplication_application,
    division_terms, division_property, division_powers, long_division, unitary_method, dmas,
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
