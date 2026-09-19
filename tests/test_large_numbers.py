import random
import unittest
from collections import Counter

from answer_validation import formatted_answers_match
from curriculum.class_5 import large_numbers as ln


class LargeNumbersTests(unittest.TestCase):
    def test_names_and_grouping(self):
        cases = [
            (10_000_000, "1,00,00,000", "one crore", "ten million"),
            (100_000_000, "10,00,00,000", "ten crore", "one hundred million"),
            (123_456_789, "12,34,56,789",
             "twelve crore thirty four lakh fifty six thousand seven hundred eighty nine",
             "one hundred twenty three million four hundred fifty six thousand seven hundred eighty nine"),
            (100_000_001, "10,00,00,001", "ten crore one", "one hundred million one"),
            (90_010_010, "9,00,10,010", "nine crore ten thousand ten", "ninety million ten thousand ten"),
            (999_999_999, "99,99,99,999",
             "ninety nine crore ninety nine lakh ninety nine thousand nine hundred ninety nine",
             "nine hundred ninety nine million nine hundred ninety nine thousand nine hundred ninety nine"),
        ]
        for number, grouped, indian, international in cases:
            with self.subTest(number=number):
                self.assertEqual(ln.format_number(number, "Indian"), grouped)
                self.assertEqual(ln.format_number(number), f"{number:,}")
                self.assertEqual(ln.number_name(number, "Indian"), indian)
                self.assertEqual(ln.number_name(number, "International"), international)

    def test_rounding_boundaries_at_every_scale(self):
        for exponent in range(1, 9):
            unit = 10 ** exponent
            base = 2 * unit
            self.assertEqual(ln.round_half_up(base + unit // 2 - 1, unit), base)
            self.assertEqual(ln.round_half_up(base + unit // 2, unit), base + unit)
            self.assertEqual(ln.round_half_up(base + unit // 2 + 1, unit), base + unit)
            self.assertEqual(ln.round_half_up(base, unit), base)
        self.assertEqual(ln.round_half_up(999_999_999, 100_000_000), 1_000_000_000)

    def test_roman_conversion(self):
        examples = {1: "I", 4: "IV", 9: "IX", 40: "XL", 49: "XLIX", 90: "XC",
                    400: "CD", 900: "CM", 1994: "MCMXCIV", 3999: "MMMCMXCIX"}
        for number, numeral in examples.items():
            self.assertEqual(ln.to_roman(number), numeral)
        # Independently evaluate every numeral, and check canonical syntax.
        for number in range(1, 4000):
            numeral = ln.to_roman(number)
            self.assertRegex(numeral, r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")
            values = [ln.ROMAN_SYMBOLS[letter] for letter in numeral]
            result = sum(-value if i + 1 < len(values) and value < values[i + 1] else value
                         for i, value in enumerate(values))
            self.assertEqual(result, number)
        for number in [0, 4000, -1]:
            with self.assertRaises(ValueError):
                ln.to_roman(number)
        self.assertEqual(list(ln.ROMAN_SYMBOLS.values()), [1, 5, 10, 50, 100, 500, 1000])

    def test_answer_formats(self):
        cases = [
            ("12,34,56,789", "123456789", "integer", True),
            ("123 456 789", "123,456,789", "integer", True),
            ("123456789 kg", "123456789", "integer", False),
            ("123456788", "123456789", "integer", False),
            ("", "0", "integer", False),
            ("1.0", "1", "integer", False),
            ("One Crore and Twenty-One Lakh", "one crore twenty one lakh", "number_words", True),
            ("one million", "one crore", "number_words", False),
            ("12,000; 13,000; 14,000", "12000;13000;14000", "integer_list", True),
            ("14000;13000;12000", "12000;13000;14000", "integer_list", False),
            ("12000;13000", "12000;13000;14000", "integer_list", False),
            ("12000;;14000", "12000;13000;14000", "integer_list", False),
            (" mcmxciv ", "MCMXCIV", "roman", True),
            ("IIII", "IV", "roman", False),
        ]
        for user, expected, kind, correct in cases:
            with self.subTest(user=user, kind=kind):
                self.assertEqual(formatted_answers_match(user, expected, kind), correct)

    def test_worksheet_coverage_and_chart_values(self):
        state = random.getstate()
        self.addCleanup(random.setstate, state)
        seen_symbols = set()
        for seed in range(100):
            random.seed(seed)
            worksheet = ln.generate_balanced_worksheet()
            self.assertEqual(len(worksheet), 15)
            topics = Counter(q["topic"] for q in worksheet)
            self.assertEqual(len(topics), 15)
            for q in worksheet:
                self.assertIn(q["type"], ["mcq", "true_false", "fill"])
                if q["type"] == "fill":
                    self.assertTrue(formatted_answers_match(q["answer"], q["answer"], q["answer_format"]))
                elif q["type"] == "mcq":
                    self.assertIn(q["answer"], q["options"])
                else:
                    self.assertIn(q["answer"], ["True", "False"])
                if "chart" in q:
                    cells = [values[0] for values in q["chart"].values()]
                    self.assertEqual(cells.count("?"), 1)
                    reconstructed = "".join(q["answer"] if cell == "?" else cell for cell in cells)
                    self.assertIn(len(reconstructed), [8, 9])
                    system = q["topic"].split()[0]
                    self.assertIn(ln.format_number(int(reconstructed), system), q["question"])
                if q["topic"] == "Roman symbols":
                    seen_symbols.add(int(q["answer"]))
        self.assertEqual(seen_symbols, set(ln.ROMAN_SYMBOLS.values()))
        for size in [0, 1, 14, 16, 30]:
            self.assertEqual(len(ln.generate_balanced_worksheet(size)), size)


if __name__ == "__main__":
    unittest.main()
