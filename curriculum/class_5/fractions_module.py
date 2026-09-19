"""Class 5 Fractions: exact arithmetic, visual models and explicit answer forms."""

import random
from fractions import Fraction
from math import gcd, lcm

from .large_numbers import question

CHAPTER_NAME = "Fractions"
ANSWER_HINT = "Give a simplest fraction or simplified mixed number; use a whole number for a whole-number result. Example: 7/3 or 2 1/3."


def value():
    return Fraction(random.randint(1, 15), random.randint(2, 12))


def fraction_question(text, answer, topic, **extra):
    return question(text, str(answer), topic, 'fraction_simplified', hint=ANSWER_HINT, **extra)


def mixed_text(value):
    whole, remainder = divmod(value.numerator, value.denominator)
    return f'{whole} {remainder}/{value.denominator}' if remainder else str(whole)


def number_line_svg(numerator, denominator, wholes):
    end = denominator * wholes
    width, left, span = 560, 30, 500
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="140" '
             f'role="img" aria-label="Number line from zero to {wholes}, each whole divided into {denominator} equal parts">',
             '<rect width="560" height="140" fill="white"/>',
             '<line x1="30" y1="65" x2="530" y2="65" stroke="#334155"/>']
    for index in range(end + 1):
        x = left + span * index / end
        parts.append(f'<line x1="{x}" y1="57" x2="{x}" y2="73" stroke="#334155"/>')
        if index % denominator == 0:
            parts.append(f'<text x="{x}" y="98" text-anchor="middle" fill="#172554">{index // denominator}</text>')
    x = left + span * numerator / end
    parts.extend([f'<circle cx="{x}" cy="65" r="5" fill="#2563eb"/>',
                  f'<text x="{x}" y="42" text-anchor="middle" fill="#172554">A</text>', '</svg>'])
    return ''.join(parts)


def number_line():
    d = random.randint(2, 8)
    wholes = random.choice([1, 2, 3])
    n = random.randint(1 if wholes == 1 else d + 1, d * wholes - 1)
    return question(f'The number line runs from 0 to {wholes}. Each whole has {d} equal parts. '
                    'What number does point A represent?', str(Fraction(n, d)), 'Fractions on a number line',
                    'fraction_value', diagram=number_line_svg(n, d, wholes),
                    hint='Enter a fraction or mixed number, for example 3/4 or 1 1/4.')


def types(kind=None):
    kind = kind or random.choice(['like', 'unit', 'proper', 'mixed'])
    d = random.randint(3, 12)
    if kind == 'like':
        other = random.choice([d, d + 1])
        return question(f'Are 2/{d} and 1/{other} like or unlike fractions?',
                        'Like' if d == other else 'Unlike', 'Types of fractions', type='mcq',
                        options=['Like', 'Unlike'])
    if kind == 'unit':
        return question(f'Which is a unit fraction (numerator 1)?', f'1/{d}', 'Types of fractions',
                        type='mcq', options=[f'1/{d}', f'2/{d}', f'{d + 1}/{d}', f'2 1/{d}'])
    if kind == 'mixed':
        return question(f'What type of number is 2 1/{d}?', 'Mixed fraction', 'Types of fractions',
                        type='mcq', options=['Unit fraction', 'Proper fraction', 'Improper fraction', 'Mixed fraction'])
    n = random.randint(2, 2 * d)
    return question(f'Is {n}/{d} proper (numerator smaller) or improper (numerator at least the denominator)?',
                    'Proper' if n < d else 'Improper', 'Types of fractions', type='mcq', options=['Proper', 'Improper'])


def conversion(to_mixed=False):
    d = random.randint(2, 12)
    v = Fraction(random.randint(1, 5)) + Fraction(random.randint(1, d - 1), d)
    if to_mixed:
        return question(f'Convert {v} to a mixed number with its fractional part in simplest form.',
                        mixed_text(v), 'Improper to mixed', 'fraction_mixed', hint='Write it as whole numerator/denominator, e.g. 2 1/3.')
    return question(f'Convert {mixed_text(v)} to an improper fraction.', str(v), 'Mixed to improper',
                    'fraction_improper', hint='Write numerator/denominator, not a mixed number.')


def simplifying():
    v = value()
    multiplier = random.randint(2, 6)
    n, d = v.numerator * multiplier, v.denominator * multiplier
    use_hcf = random.choice([True, False])
    if use_hcf:
        hint = 'Find the HCF of the numerator and denominator, then divide both by it.'
        rows = [(f'Divide both by HCF {gcd(n, d)}', str(v))]
    else:
        hint = 'Repeatedly divide the numerator and denominator by a common factor until they have only 1 in common.'
        rows = []
        a, b = n, d
        while gcd(a, b) > 1:
            factor = next(k for k in range(2, gcd(a, b) + 1) if a % k == b % k == 0)
            a, b = a // factor, b // factor
            rows.append((f'Divide both by {factor}', f'{a}/{b}'))
    return question(f'Reduce {n}/{d} to simplest form.', str(v), 'Simplifying fractions', 'fraction_simplified',
                    hint=hint + ' Use a whole number if the result is whole.',
                    solution_chart={'Step': [r[0] for r in rows], 'Fraction': [r[1] for r in rows]})


def equivalence():
    n, d, multiplier = random.randint(1, 9), random.randint(2, 12), random.randint(2, 5)
    other_n = n * multiplier + random.choice([0, 1])
    other_d = d * multiplier
    method = random.choice(['cross multiplication', 'reducing both fractions'])
    return question(f'True or False: {n}/{d} and {other_n}/{other_d} are equivalent. Check by {method}.',
                    str(Fraction(n, d) == Fraction(other_n, other_d)), 'Equivalent fractions', type='true_false')


def comparison(kind=None):
    kind = kind or random.choice(['same numerator', 'same denominator', 'LCM', 'cross multiplication'])
    n, d = random.randint(1, 9), random.randint(2, 12)
    other_n, other_d = random.randint(1, 9), random.randint(2, 12)
    if kind == 'same numerator':
        other_n = n
    elif kind == 'same denominator':
        other_d = d
    else:
        other_d = d + random.randint(1, 5)
    a, b = Fraction(n, d), Fraction(other_n, other_d)
    hint = {'same numerator': 'For the same positive numerator, a larger denominator means a smaller fraction.',
            'same denominator': 'Compare the numerators.',
            'LCM': 'Use the LCM of the denominators to convert to like fractions.',
            'cross multiplication': 'Compare numerator × opposite denominator on each side.'}[kind]
    return question(f'Compare {n}/{d} ___ {other_n}/{other_d}.', '<' if a < b else '>' if a > b else '=',
                    'Comparing fractions', type='mcq', options=['<', '>', '='], hint=hint)


def ordering():
    values = set()
    while len(values) < 4:
        values.add(value())
    values = list(values)
    random.shuffle(values)
    descending = random.choice([True, False])
    return question('Arrange in ' + ('descending' if descending else 'ascending') + ' order: ' +
                    '; '.join(map(str, values)), '; '.join(map(str, sorted(values, reverse=descending))),
                    'Ordering fractions', 'fraction_list', hint='Separate answers with semicolons, e.g. 1/4; 1/2; 3/4.')


def add_subtract(subtract=False):
    d = random.randint(2, 12)
    other_d = random.choice([d, d + random.randint(1, 6)])
    n, other_n = random.randint(1, 15), random.randint(1, 15)
    a, b = Fraction(n, d), Fraction(other_n, other_d)
    if subtract and a < b:
        n, d, other_n, other_d, a, b = other_n, other_d, n, d, b, a
    denominator = lcm(d, other_d)
    first, second = n * (denominator // d), other_n * (denominator // other_d)
    symbol = '−' if subtract else '+'
    return fraction_question(f'{n}/{d} {symbol} {other_n}/{other_d} = ?', a - b if subtract else a + b,
                             'Subtracting fractions' if subtract else 'Adding fractions',
                             solution_chart={'Step': ['Convert to like fractions', 'Combine numerators, keep denominator'],
                                             'Calculation': [f'{first}/{denominator} {symbol} {second}/{denominator}',
                                                             f'{first - second if subtract else first + second}/{denominator}']})


def multiplication():
    a, b = value(), value()
    return fraction_question(f'Multiply {a} × {b}. Simplify before multiplying where possible.', a * b,
                             'Multiplying fractions')


def multiplication_properties():
    statement, correct = random.choice([
        ('Multiplying a fraction by 1 leaves it unchanged.', True),
        ('Multiplying a fraction by 0 gives 0.', True),
        ('Changing the order of two fractions changes their product.', False),
        ('Regrouping three factors leaves their product unchanged.', True),
        ('Multiplication distributes over addition and subtraction of fractions.', True),
    ])
    return question('True or False: ' + statement, str(correct), 'Multiplication properties', type='true_false')


def reciprocal():
    a = random.choice([Fraction(0), Fraction(1), Fraction(random.randint(2, 9)), value()])
    if a == 0:
        return question('What is the reciprocal of 0?', 'It has no reciprocal', 'Reciprocals', type='mcq',
                        options=['0', '1', 'It has no reciprocal'])
    return fraction_question(f'Find the reciprocal of {a}.', 1 / a, 'Reciprocals')


def division():
    a, b = random.choice([Fraction(random.randint(1, 9)), value()]), value()
    return fraction_question(f'Divide {a} ÷ {b}. Multiply by the reciprocal of the divisor.', a / b,
                             'Dividing fractions')


def division_properties(kind=None):
    a = value()
    kind = kind or random.choice(['zero dividend', 'self', 'zero divisor', 'one dividend', 'one divisor'])
    if kind == 'zero divisor':
        return question(f'What is {a} ÷ 0?', 'Undefined', 'Division properties', type='mcq',
                        options=['0', str(a), 'Undefined'])
    expression, result = {'zero dividend': (f'0 ÷ {a}', Fraction(0)), 'self': (f'{a} ÷ {a}', Fraction(1)),
                          'one dividend': (f'1 ÷ {a}', 1 / a), 'one divisor': (f'{a} ÷ 1', a)}[kind]
    return fraction_question(f'{expression} = ?', result, 'Division properties')


WORKSHEET_GENERATORS = [number_line, types, conversion, lambda: conversion(True), simplifying, equivalence,
                        comparison, ordering, add_subtract, lambda: add_subtract(True), multiplication,
                        multiplication_properties, reciprocal, division, division_properties]


def generate_balanced_worksheet(total_questions=15):
    if not isinstance(total_questions, int) or total_questions < 0:
        raise ValueError('total_questions must be a nonnegative integer')
    questions = []
    while len(questions) < total_questions:
        generators = list(WORKSHEET_GENERATORS)
        random.shuffle(generators)
        for generator in generators[:total_questions - len(questions)]:
            item = generator()
            item['worksheet_type'] = item['topic']
            questions.append(item)
    random.shuffle(questions)
    return questions
