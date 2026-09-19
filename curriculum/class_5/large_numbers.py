"""Class 5: Large Numbers, following the supplied chapter outline."""

import random

PLACE_NAMES = {
    "Indian": ["Ones", "Tens", "Hundreds", "Thousands", "Ten thousands",
               "Lakhs", "Ten lakhs", "Crores", "Ten crores"],
    "International": ["Ones", "Tens", "Hundreds", "Thousands", "Ten thousands",
                      "Hundred thousands", "Millions", "Ten millions", "Hundred millions"],
}
SMALL = ("zero one two three four five six seven eight nine ten eleven twelve "
         "thirteen fourteen fifteen sixteen seventeen eighteen nineteen").split()
TENS = "zero ten twenty thirty forty fifty sixty seventy eighty ninety".split()
ROMAN_VALUES = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
                (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
                (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
ROMAN_SYMBOLS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
ROMAN_RULES = [
    ("V, L and D may be repeated in a standard Roman numeral.", False),
    ("I, X, C and M may each be repeated up to three times in a row.", True),
    ("I can be subtracted from V and X.", True),
    ("X can be subtracted from L and C.", True),
    ("C can be subtracted from D and M.", True),
    ("V, L and D are used as subtractive symbols.", False),
    ("IL is the standard Roman numeral for 49.", False),
    ("When a smaller symbol follows a larger one, its value is added.", True),
    ("Zero has one of the seven basic Roman numeral symbols.", False),
    ("In IV, I is subtracted from V to make 4.", True),
]


def large_number(digits=None):
    digits = digits or random.choice([8, 9])
    return random.randint(10 ** (digits - 1), 10 ** digits - 1)


def format_number(number, system="International"):
    if system == "International":
        return f"{number:,}"
    digits = str(number)
    groups = [digits[-3:]]
    digits = digits[:-3]
    while digits:
        groups.append(digits[-2:])
        digits = digits[:-2]
    return ",".join(reversed(groups))


def below_thousand(number):
    words = []
    if number >= 100:
        words.extend([SMALL[number // 100], "hundred"])
        number %= 100
    if number >= 20:
        words.append(TENS[number // 10])
        number %= 10
    if number:
        words.append(SMALL[number])
    return " ".join(words)


def number_name(number, system):
    if number == 0:
        return "zero"
    scales = ([(10**7, "crore"), (10**5, "lakh"), (1000, "thousand")]
              if system == "Indian" else [(10**6, "million"), (1000, "thousand")])
    words = []
    for divisor, label in scales:
        count, number = divmod(number, divisor)
        if count:
            words.extend([below_thousand(count), label])
    if number:
        words.append(below_thousand(number))
    return " ".join(words)


def round_half_up(number, unit):
    return ((number + unit // 2) // unit) * unit


def to_roman(number):
    if not 1 <= number <= 3999:
        raise ValueError("Standard Roman numerals are supported from 1 to 3999.")
    result = []
    for value, symbol in ROMAN_VALUES:
        count, number = divmod(number, value)
        result.append(symbol * count)
    return "".join(result)


def question(text, answer, topic, answer_format="integer", **extra):
    return {"question": text, "answer": str(answer), "type": "fill",
            "topic": topic, "answer_format": answer_format, **extra}


def place_chart(system):
    number = large_number()
    exponent = random.randrange(len(str(number)))
    names = PLACE_NAMES[system]
    chart = {names[i]: [str(number // 10**i % 10) if i != exponent else "?"]
             for i in range(len(str(number)) - 1, -1, -1)}
    return question(
        f"Complete the {system} place value chart for {format_number(number, system)}. "
        f"Which digit belongs in the {names[exponent].lower()} column?",
        number // 10**exponent % 10, f"{system} place value chart", chart=chart,
    )


def names_question(system, in_words):
    number = large_number()
    if in_words:
        return question(
            f"Write {format_number(number, system)} in words using the {system} system.",
            number_name(number, system), f"{system} number names", "number_words",
            hint="Hyphens and the word 'and' are optional.",
        )
    return question(
        f"Write this {system} number name in figures: {number_name(number, system)}.",
        format_number(number, system), f"{system} numbers in figures",
        hint="You may write the number with or without commas.",
    )


def digit_value(face=False):
    number = large_number()
    exponent = random.randrange(len(str(number)))
    digit = number // 10**exponent % 10
    system = random.choice(list(PLACE_NAMES))
    kind = "face" if face else "place"
    return question(
        f"In {format_number(number, system)} ({system} system), find the {kind} value "
        f"of the digit {digit} in the {PLACE_NAMES[system][exponent].lower()} place.",
        digit if face else digit * 10**exponent, f"{kind.title()} value",
    )


def neighbour():
    number = large_number()
    successor = random.choice([True, False])
    label = "successor" if successor else "predecessor"
    return question(f"What is the {label} of {number:,}?",
                    number + (1 if successor else -1), "Successor and predecessor")


def comparison():
    left = large_number()
    right = random.choice([left, large_number(), left + random.choice([-1, 1])])
    answer = ">" if left > right else "<" if left < right else "="
    return question(f"Compare: {left:,} ___ {right:,}. Choose <, > or =.",
                    answer, "Comparison", type="mcq", options=["<", ">", "="])


def ordering():
    # Nearby numbers encourage checking beyond just the leading digits.
    base = random.randint(10_000_100, 999_999_800)
    values = [base + offset for offset in random.sample(range(100), 4)]
    descending = random.choice([True, False])
    label = "descending" if descending else "ascending"
    return question(
        f"Arrange in {label} order: " + "; ".join(f"{n:,}" for n in values),
        "; ".join(f"{n:,}" for n in sorted(values, reverse=descending)),
        "Ordering", "integer_list",
        hint="Separate numbers with semicolons (;). Commas within each number are optional.",
    )


def rounding():
    number = large_number()
    unit = 10 ** random.randint(1, 8)
    return question(f"Round {number:,} to the nearest {unit:,}.",
                    f"{round_half_up(number, unit):,}", "Rounding",
                    hint="Use the school rule: halfway values round up.")


def roman_symbol():
    symbol = random.choice(list(ROMAN_SYMBOLS))
    return question(f"What is the value of the Roman numeral symbol {symbol}?",
                    ROMAN_SYMBOLS[symbol], "Roman symbols")


def roman_rule():
    text, correct = random.choice(ROMAN_RULES)
    return question("True or False: " + text, correct, "Roman rules", type="true_false")


def roman_conversion():
    number = random.randint(1, 3999)
    if random.choice([True, False]):
        return question(f"Write {number} as a Roman numeral.", to_roman(number),
                        "Roman conversion", "roman")
    return question(f"Write the Roman numeral {to_roman(number)} as a number.",
                    number, "Roman conversion")


# Every standard worksheet includes all 15 slots. Variants within slots rotate.
WORKSHEET_GENERATORS = [
    lambda: place_chart("Indian"),
    lambda: place_chart("International"),
    lambda: names_question("Indian", True),
    lambda: names_question("Indian", False),
    lambda: names_question("International", True),
    lambda: names_question("International", False),
    lambda: digit_value(face=True),
    digit_value,
    neighbour,
    comparison,
    ordering,
    rounding,
    roman_symbol,
    roman_rule,
    roman_conversion,
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
