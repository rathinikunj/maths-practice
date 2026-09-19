import random
import re
import unittest
from decimal import Decimal, ROUND_HALF_UP
from unittest.mock import patch

from answer_validation import formatted_answers_match, parse_integer
from curriculum.class_5 import addition_subtraction as chapter


def numbers(text):
    return [int(value.replace(',', '')) for value in re.findall(r'\d[\d,]*', text)]


class AdditionSubtractionTests(unittest.TestCase):
    def setUp(self):
        state = random.getstate()
        self.addCleanup(random.setstate, state)

    def test_generated_answers_and_coverage(self):
        observed_parts = set()
        for seed in range(100):
            random.seed(seed)
            questions = chapter.generate_balanced_worksheet()
            self.assertEqual(len(questions), 15)
            self.assertEqual(len({q['topic'] for q in questions}), 15)
            for q in questions:
                topic, text = q['topic'], q['question']
                values = numbers(text)
                if q['type'] == 'mcq':
                    self.assertEqual(len(q['options']), len(set(q['options'])))
                    self.assertIn(q['answer'], q['options'])
                if q['type'] == 'fill':
                    self.assertTrue(formatted_answers_match(q['answer'], q['answer'], 'integer'))
                    self.assertGreaterEqual(parse_integer(q['answer']), 0)
                if topic == 'Addition of large numbers':
                    self.assertEqual(parse_integer(q['answer']), sum(values))
                elif topic in ['Subtraction of large numbers', 'Subtraction applications']:
                    self.assertEqual(parse_integer(q['answer']), values[0] - values[1])
                elif topic == 'Addition applications':
                    expected = values[0] + values[1] - (values[2] if len(values) == 3 else 0)
                    self.assertEqual(parse_integer(q['answer']), expected)
                elif topic == 'Addition and subtraction together':
                    a, b, c = values
                    expected = a + b - c if '(' in text else a - b + c
                    self.assertEqual(parse_integer(q['answer']), expected)
                elif topic.startswith('Estimating'):
                    a, b, unit = values
                    # Decimal implements an independent half-up rounding oracle.
                    rounded = [int((Decimal(n) / unit).quantize(Decimal('1'), rounding=ROUND_HALF_UP)) * unit
                               for n in [a, b]]
                    expected = rounded[0] - rounded[1] if 'differences' in topic else sum(rounded)
                    self.assertEqual(parse_integer(q['answer']), expected)
                elif topic == 'Subtraction: associative property':
                    a, b, c, other_a, other_b, other_c = values
                    self.assertEqual((a, b, c), (other_a, other_b, other_c))
                    equality = (a - b) - c == a - (b - c)
                    self.assertEqual(q['answer'], str(not equality if '≠' in text else equality))
                elif topic.startswith('Parts of'):
                    terms = (['augend', 'addend', 'sum'] if topic.endswith('addition')
                             else ['minuend', 'subtrahend', 'difference'])
                    for index, term in enumerate(terms):
                        if f'what is the {term}?' in text:
                            observed_parts.add(term)
                            self.assertEqual(parse_integer(q['answer']), values[index])
        self.assertEqual(observed_parts, {'augend', 'addend', 'sum', 'minuend', 'subtrahend', 'difference'})

    def test_carry_borrow_and_zero(self):
        with patch.object(chapter, 'number', side_effect=[99_999_999, 1, 1]), \
                patch.object(chapter.random, 'choice', return_value=True):
            self.assertEqual(parse_integer(chapter.addition()['answer']), 100_000_000)
        for operands, expected in [([100_000_000, 99_999_999], 1), ([10_000_000, 10_000_000], 0)]:
            with patch.object(chapter, 'number', side_effect=operands):
                self.assertEqual(parse_integer(chapter.subtraction()['answer']), expected)

    def test_estimate_rounds_operands_first_and_ties_up(self):
        with patch.object(chapter, 'number', side_effect=[100_050, 100_050]), \
                patch.object(chapter.random, 'randint', return_value=2):
            self.assertEqual(parse_integer(chapter.estimation()['answer']), 200_200)
        with patch.object(chapter, 'number', side_effect=[100_149, 100_050]), \
                patch.object(chapter.random, 'randint', return_value=2):
            self.assertEqual(parse_integer(chapter.estimation(subtract=True)['answer']), 0)

    def test_mixed_operations_grouping_and_left_to_right(self):
        for grouped, expected in [(True, 110), (False, 110)]:
            with patch.object(chapter, 'number', side_effect=[100, 30]), \
                    patch.object(chapter.random, 'randint', return_value=20), \
                    patch.object(chapter.random, 'choice', return_value=grouped):
                q = chapter.mixed_operations()
                self.assertEqual(parse_integer(q['answer']), expected)
                self.assertEqual('(' in q['question'], grouped)

    def test_properties_are_mathematically_correct(self):
        for kind in ['Associative', 'Commutative', 'Identity']:
            q = chapter.addition_property(kind)
            self.assertEqual(q['answer'], f'{kind} property')
        # Exercise every static rule, including the misleading zero-on-left case.
        for index, expected in enumerate([False, True]):
            with patch.object(chapter.random, 'choice', side_effect=lambda options: options[index]):
                self.assertEqual(chapter.subtraction_commutative()['answer'], str(expected))
        for index, expected in enumerate([True, False, True, False]):
            with patch.object(chapter, 'number', return_value=10_000_000), \
                    patch.object(chapter.random, 'choice', side_effect=lambda options: options[index]):
                self.assertEqual(chapter.subtraction_zero()['answer'], str(expected))

    def test_worksheet_sizes(self):
        for size in [0, 1, 14, 16, 30]:
            self.assertEqual(len(chapter.generate_balanced_worksheet(size)), size)
        for size in [-1, 1.5, '15']:
            with self.assertRaises(ValueError):
                chapter.generate_balanced_worksheet(size)


if __name__ == '__main__':
    unittest.main()
