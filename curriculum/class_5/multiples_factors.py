"""Factors and positive multiples of positive whole numbers."""

import random
from math import gcd, isqrt

from .large_numbers import question

CHAPTER_NAME = "Multiples and Factors"
DIVISIBILITY_RULES = {
    2: "The last digit is even.",
    3: "The sum of the digits is divisible by 3.",
    4: "The number formed by the last two digits is divisible by 4.",
    5: "The last digit is 0 or 5.",
    6: "The number is divisible by both 2 and 3.",
    7: "Double the last digit and subtract it from the remaining number; repeat if needed. The result must be divisible by 7 (zero counts).",
    8: "The number formed by the last three digits is divisible by 8.",
    9: "The sum of the digits is divisible by 9.",
    10: "The last digit is 0.",
    11: "The difference between alternate digit sums is divisible by 11 (zero counts).",
}


def factors(number):
    result = set()
    for divisor in range(1, isqrt(number) + 1):
        if number % divisor == 0:
            result.update([divisor, number // divisor])
    return sorted(result)


def prime_factors(number):
    result = []
    divisor = 2
    while divisor * divisor <= number:
        while number % divisor == 0:
            result.append(divisor)
            number //= divisor
        divisor += 1
    if number > 1:
        result.append(number)
    return result


def is_prime(number):
    return number >= 2 and all(number % d for d in range(2, isqrt(number) + 1))


def true_false(text, answer, topic, **extra):
    return question("True or False: " + text, answer, topic, type="true_false", **extra)


def factor_properties():
    text, answer = random.choice([
        ("1 is the smallest positive factor of every positive whole number.", True),
        ("Every positive whole number other than 1 has at least two positive factors.", True),
        ("A factor divides a number exactly, leaving no remainder.", True),
        ("A positive factor can be greater than the number it divides.", False),
        ("A positive whole number is its own greatest factor.", True),
        ("1 has two different positive factors.", False),
    ])
    return true_false(text, answer, "Properties of factors")


def rainbow_svg(number):
    values = factors(number)
    positions = {value: 25 + i * 34 for i, value in enumerate(values)}
    width = len(values) * 34 + 20
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="180" '
             f'viewBox="0 0 {width} 180" role="img" aria-label="Factor rainbow for {number}">',
             f'<rect width="{width}" height="180" fill="white"/>']
    for index, a in enumerate(values):
        b = number // a
        if a > b:
            break
        x, end = positions[a], positions[b]
        # A square's repeated factor is represented by a loop, not a duplicate.
        if a == b:
            path = f'M {x - 7} 142 Q {x} 104 {x + 7} 142'
        else:
            path = f'M {x} 142 Q {(x + end) / 2} {15 + index * 15} {end} 142'
        parts.append(f'<path d="{path}" fill="none" stroke="#2563eb" stroke-width="2"/>')
    for value, x in positions.items():
        parts.append(f'<text x="{x}" y="163" text-anchor="middle" font-family="sans-serif" '
                     f'font-size="14" fill="#172554">{value}</text>')
    parts.append('</svg>')
    return ''.join(parts)


def rainbow_factors():
    number = random.choice([12, 18, 24, 30, 36, 42, 48, 60, 64, 72, 81, 100])
    # Practice the method without displaying the complete answer in advance.
    return question(f"Use factor pairs (the rainbow method) to list ALL positive factors of {number}.",
                    "; ".join(map(str, factors(number))), "Rainbow factors", "factor_set",
                    hint="Start with 1 and the number. Try divisors in order and pair each with its quotient. "
                         "Stop when the pairs meet. List each factor once, separated by commas or semicolons.",
                    solution_diagram=rainbow_svg(number))


def multiple_properties():
    text, answer = random.choice([
        ("Every positive whole number is a multiple of itself and of 1.", True),
        ("A positive whole number has only finitely many positive multiples.", False),
        ("Every positive multiple of a positive whole number is at least that number.", True),
        ("The smallest positive multiple of a positive whole number is the number itself.", True),
        ("The smallest positive multiple of 8 is 0.", False),
    ])
    return true_false(text, answer, "Properties of multiples")


def multiples():
    number, position = random.randint(2, 25), random.randint(2, 12)
    return question(f"What is positive multiple number {position} of {number}? "
                    f"Count {number} as multiple number 1.", number * position, "Multiples")


def divisibility(divisor=None):
    divisor = divisor or random.choice(list(DIVISIBILITY_RULES))
    number = divisor * random.randint(100, 9999)
    if random.choice([True, False]):
        number += random.randint(1, divisor - 1)
    return true_false(f"{number:,} is divisible by {divisor}.", number % divisor == 0,
                      "Divisibility tests", hint=DIVISIBILITY_RULES[divisor])


def prime_composite():
    number = random.choice([1, 2, random.randint(3, 100)])
    answer = "Prime" if is_prime(number) else "Neither prime nor composite" if number == 1 else "Composite"
    return question(f"Classify {number}.", answer, "Prime and composite numbers", type="mcq",
                    options=["Prime", "Composite", "Neither prime nor composite"])


def twin_primes():
    a = random.choice([3, 5, 7, 11, 17, 23, 29, 41, 59, 71])
    b = a + random.choice([2, 4])
    return true_false(f"{a} and {b} are twin primes.", is_prime(a) and is_prime(b) and b - a == 2,
                      "Twin primes", hint="Both numbers must be prime and differ by exactly 2.")


def coprimes():
    a, b = random.sample(range(2, 51), 2)
    return true_false(f"{a} and {b} are co-prime.", gcd(a, b) == 1, "Co-prime numbers",
                      hint="Co-prime numbers have only 1 as a common positive factor. They need not be prime.")


def factor_tree_svg(number):
    # Show the first split; learners finish factoring both branches themselves.
    left = next(d for d in range(2, isqrt(number) + 1) if number % d == 0)
    right = number // left
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="160" '
            f'role="img" aria-label="Factor tree starting with {number}">'
            '<rect width="300" height="160" fill="white"/>'
            '<path d="M150 45 L75 95 M150 45 L225 95" stroke="#2563eb" fill="none"/>'
            '<g fill="#172554" text-anchor="middle" font-family="sans-serif" font-size="20">'
            f'<text x="150" y="35">{number}</text><text x="75" y="120">{left}</text>'
            f'<text x="225" y="120">{right}</text></g></svg>')


def factorisation(tree=True):
    number = random.choice([24, 36, 48, 60, 72, 84, 90, 100, 120, 144, 180, 210])
    method = "factor tree" if tree else "division method"
    extra = {"diagram": factor_tree_svg(number)} if tree else {
        "chart": {"Prime divisor": ["?"], "Number to divide": [number], "Quotient": ["?"]}}
    return question(f"Find the prime factorisation of {number} using the {method}.",
                    " × ".join(map(str, prime_factors(number))),
                    "Factor tree" if tree else "Prime factorisation by division", "prime_product",
                    hint="Keep splitting into factors" + ("" if tree else " by dividing by primes") +
                         ". Stop when all factors are prime. Enter repeated prime factors, e.g. 2 × 2 × 3 (no powers).",
                    **extra)


def common_division_rows(a, b, hcf):
    rows = []
    while True:
        prime = next((p for p in range(2, max(a, b) + 1) if is_prime(p) and
                      ((a % p == 0 and b % p == 0) if hcf else (a % p == 0 or b % p == 0))), None)
        if prime is None:
            break
        rows.append((prime, a, b))
        a = a // prime if a % prime == 0 else a
        b = b // prime if b % prime == 0 else b
    rows.append(("—", a, b))
    return {"Divisor": [r[0] for r in rows], "First number": [r[1] for r in rows],
            "Second number": [r[2] for r in rows]}


def common_division(hcf=True):
    a, b = random.randint(2, 100), random.randint(2, 100)
    label = "HCF" if hcf else "LCM"
    answer = gcd(a, b) if hcf else a * b // gcd(a, b)
    return question(f"Find the {label} of {a} and {b} using common division.", answer,
                    f"{label} by common division",
                    hint=("Divide both numbers by common prime factors until none remain. Multiply the common divisors; "
                          "if there are none, the HCF is 1." if hcf else
                          "Divide by a prime that divides at least one number; carry unchanged numbers down. "
                          "Continue until both are 1, then multiply the prime divisors."),
                    solution_chart=common_division_rows(a, b, hcf))


def hcf_lcm_relationship():
    a, b = random.randint(2, 60), random.randint(2, 60)
    hcf = gcd(a, b)
    return question(f"Two positive whole numbers are {a} and {b}. Their HCF is {hcf}. Find their LCM.",
                    a * b // hcf, "HCF and LCM relationship",
                    hint="For two positive whole numbers: HCF × LCM = first number × second number.")


WORKSHEET_GENERATORS = [factor_properties, rainbow_factors, multiple_properties, multiples,
                        divisibility, divisibility, divisibility, prime_composite, twin_primes,
                        coprimes, factorisation, lambda: factorisation(False),
                        common_division, lambda: common_division(False), hcf_lcm_relationship]


def generate_balanced_worksheet(total_questions=15):
    if not isinstance(total_questions, int) or total_questions < 0:
        raise ValueError("total_questions must be a nonnegative integer")
    questions = []
    while len(questions) < total_questions:
        generators = list(WORKSHEET_GENERATORS)
        random.shuffle(generators)
        divisors = random.sample(list(DIVISIBILITY_RULES), 3)
        for generator in generators[:total_questions - len(questions)]:
            item = divisibility(divisors.pop()) if generator is divisibility else generator()
            item["worksheet_type"] = item["topic"]
            questions.append(item)
    random.shuffle(questions)
    return questions
