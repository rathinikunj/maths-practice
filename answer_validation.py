"""Explicit answer formats for chapters needing more than text equality."""

import re
from datetime import datetime
from fraction_answers import fraction_answers_match
from quantity_answers import quantity_answers_match


def parse_integer(value):
    # Only digits and grouping separators: units and other text are not accepted.
    text = re.sub(r"[\s,]", "", str(value))
    return int(text) if re.fullmatch(r"[0-9]+", text) else None


def normalize_number_words(value):
    words = re.sub(r"[-,]", " ", str(value).lower()).split()
    aliases = {"crores": "crore", "lakhs": "lakh", "millions": "million"}
    return [aliases.get(word, word) for word in words if word != "and"]


def parse_quotient_remainder(value):
    parts = re.split(r"\s*(?:remainder|r|;)\s*", str(value).strip(), flags=re.IGNORECASE)
    if len(parts) != 2:
        return None
    values = tuple(parse_integer(part) for part in parts)
    return values if None not in values else None


def formatted_answers_match(user_answer, correct_answer, answer_format):
    if user_answer is None:
        return False
    if answer_format in ("clock_12", "clock_24"):
        pattern = r"\d{1,2}:\d{2}\s*(?:AM|PM)" if answer_format == "clock_12" else r"\d{1,2}:\d{2}"
        def parse_clock(value):
            text = str(value).strip().upper()
            if not re.fullmatch(pattern, text):
                return None
            text = re.sub(r"\s*(AM|PM)$", r" \1", text)
            try:
                return datetime.strptime(text, "%I:%M %p" if answer_format == "clock_12" else "%H:%M")
            except ValueError:
                return None
        user = parse_clock(user_answer)
        return user is not None and user == parse_clock(correct_answer)
    if answer_format == "quantity":
        return quantity_answers_match(user_answer, correct_answer)
    if answer_format.startswith("fraction_"):
        return fraction_answers_match(user_answer, correct_answer, answer_format)
    if answer_format in ("factor_set", "prime_product"):
        pattern = r"\s*[,;]\s*|\s+" if answer_format == "factor_set" else r"\s*[×xX*]\s*"
        def parse_terms(value):
            parts = re.split(pattern, str(value).strip())
            if not parts or any(not re.fullmatch(r"[0-9]+", part) for part in parts):
                return None
            terms = [int(part) for part in parts]
            if answer_format == "factor_set" and len(terms) != len(set(terms)):
                return None
            return sorted(terms)
        user = parse_terms(user_answer)
        return user is not None and user == parse_terms(correct_answer)
    if answer_format == "quotient_remainder":
        user = parse_quotient_remainder(user_answer)
        return user is not None and user == parse_quotient_remainder(correct_answer)
    if answer_format == "integer":
        user = parse_integer(user_answer)
        return user is not None and user == parse_integer(correct_answer)
    if answer_format == "integer_list":
        user = [parse_integer(part) for part in str(user_answer).split(";")]
        correct = [parse_integer(part) for part in str(correct_answer).split(";")]
        return None not in user and user == correct
    if answer_format == "number_words":
        return normalize_number_words(user_answer) == normalize_number_words(correct_answer)
    if answer_format == "roman":
        return str(user_answer).strip().upper() == str(correct_answer).strip().upper()
    raise ValueError(f"Unknown answer format: {answer_format}")
