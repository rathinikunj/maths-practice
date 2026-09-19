"""Exact grading for fraction values and explicitly requested answer forms."""

from fractions import Fraction
from math import gcd
import re


def parse_fraction(text):
    text = str(text).strip()
    if re.fullmatch(r'[0-9]+', text):
        return Fraction(int(text)), 'whole', True
    match = re.fullmatch(r'(?:(\d+)\s+)?(\d+)\s*/\s*(\d+)', text)
    if not match:
        return None
    whole, numerator, denominator = match.groups()
    n, d = int(numerator), int(denominator)
    if d == 0:
        return None
    if whole is not None:
        w = int(whole)
        if w < 1 or not 0 < n < d:
            return None
        return Fraction(w) + Fraction(n, d), 'mixed', gcd(n, d) == 1
    return Fraction(n, d), 'improper' if n >= d else 'proper', gcd(n, d) == 1 and d != 1


def fraction_answers_match(user, correct, answer_format):
    if answer_format == 'fraction_list':
        user_parts = [parse_fraction(part) for part in str(user).split(';')]
        correct_parts = [parse_fraction(part) for part in str(correct).split(';')]
        return (all(user_parts) and all(correct_parts)
                and [p[0] for p in user_parts] == [p[0] for p in correct_parts])
    parsed, expected = parse_fraction(user), parse_fraction(correct)
    if parsed is None or expected is None or parsed[0] != expected[0]:
        return False
    _, kind, reduced = parsed
    if answer_format == 'fraction_value':
        return True
    if answer_format == 'fraction_simplified':
        return reduced
    if answer_format == 'fraction_improper':
        return kind == 'improper'
    if answer_format == 'fraction_mixed':
        return kind == 'mixed' and reduced
    if answer_format == 'fraction_mixed_value':
        return kind == 'mixed'
    raise ValueError(f'Unknown fraction format: {answer_format}')
