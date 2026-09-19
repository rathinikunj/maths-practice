"""Strict unit-aware grading; no implicit conversion away from requested units."""

from decimal import Decimal
import re

UNIT_NAMES = {
    'kg': ['kg', 'kilogram', 'kilograms'],
    'g': ['g', 'gram', 'grams'],
    'l': ['l', 'litre', 'litres', 'liter', 'liters'],
    'ml': ['ml', 'millilitre', 'millilitres', 'milliliter', 'milliliters'],
    'm': ['m', 'metre', 'metres', 'meter', 'meters'],
    'cm': ['cm', 'centimetre', 'centimetres', 'centimeter', 'centimeters'],
    'km': ['km', 'kilometre', 'kilometres', 'kilometer', 'kilometers'],
    'hr': ['hr', 'hrs', 'hour', 'hours'],
    'min': ['min', 'mins', 'minute', 'minutes'],
    'day': ['day', 'days'],
    'cm2': ['cm2', 'cm²', 'cm^2', 'sq cm', 'sq. cm', 'square cm', 'square centimetre',
            'square centimetres', 'square centimeter', 'square centimeters'],
    'square': ['square', 'squares', 'square unit', 'square units'],
}
ALIASES = {alias: unit for unit, names in UNIT_NAMES.items() for alias in names}
NUMBER = r'\d+(?:,\d+)*(?:\.\d+)?'
UNIT = '|'.join(re.escape(alias) for alias in sorted(ALIASES, key=len, reverse=True))
QUANTITY = re.compile(rf'({NUMBER})\s*({UNIT})(?=\s|\d|$)', re.IGNORECASE)


def decimal(text):
    return Decimal(text.replace(',', ''))


def parse_quantities(value):
    text = ' '.join(str(value).strip().lower().split())
    pairs = []
    position = 0
    while position < len(text):
        match = QUANTITY.match(text, position)
        if match is None:
            return None
        pairs.append((decimal(match[1]), ALIASES[match[2]]))
        position = match.end()
        while position < len(text) and text[position].isspace():
            position += 1
    return pairs or None


def quantity_answers_match(user, correct, expected_unit=None):
    if user is None:
        return False
    if expected_unit is not None:
        # Bare numbers are allowed because the question supplies the target unit.
        if re.fullmatch(NUMBER, str(user).strip()):
            return decimal(str(user).strip()) == decimal(str(correct))
        pairs = parse_quantities(user)
        return pairs == [(decimal(str(correct)), expected_unit)]
    expected = parse_quantities(correct)
    return expected is not None and parse_quantities(user) == expected
