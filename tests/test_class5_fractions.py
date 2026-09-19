import random
import re
import unittest
from fractions import Fraction
from unittest.mock import patch
import xml.etree.ElementTree as ET

from answer_validation import formatted_answers_match
from fraction_answers import parse_fraction
from curriculum.class_5 import fractions_module as chapter


class Class5FractionsTests(unittest.TestCase):
    def setUp(self):
        state = random.getstate()
        self.addCleanup(random.setstate, state)

    def test_forms_and_equivalence(self):
        cases = [
            ('2/4', '1/2', 'fraction_value', True),
            ('2/4', '1/2', 'fraction_simplified', False),
            ('7 / 3', '2 1/3', 'fraction_simplified', True),
            ('2 1/3', '7/3', 'fraction_simplified', True),
            ('2 2/6', '7/3', 'fraction_simplified', False),
            ('7/3', '2 1/3', 'fraction_mixed', False),
            ('2 1/3', '7/3', 'fraction_mixed', True),
            ('14/6', '7/3', 'fraction_improper', True),
            ('2 1/3', '7/3', 'fraction_improper', False),
            ('0', '0', 'fraction_simplified', True),
            ('0/7', '0', 'fraction_simplified', False),
            ('2/1', '2', 'fraction_simplified', False),
            ('1/0', '1', 'fraction_value', False),
            ('2 4/3', '10/3', 'fraction_value', False),
            ('0.5', '1/2', 'fraction_value', False),
            ('1/2 extra', '1/2', 'fraction_value', False),
            ('', '1/2', 'fraction_value', False),
            ('2/8; 2/4; 3/4', '1/4;1/2;3/4', 'fraction_list', True),
            ('3/4;1/2;1/4', '1/4;1/2;3/4', 'fraction_list', False),
            ('1/4;;3/4', '1/4;1/2;3/4', 'fraction_list', False),
        ]
        for user, correct, kind, expected in cases:
            with self.subTest(user=user, kind=kind):
                self.assertEqual(formatted_answers_match(user, correct, kind), expected)

    def test_generated_answers_and_coverage(self):
        for seed in range(100):
            random.seed(seed)
            questions = chapter.generate_balanced_worksheet()
            self.assertEqual(len(questions), 15)
            self.assertEqual(len({q['topic'] for q in questions}), 15)
            for q in questions:
                text, topic = q['question'], q['topic']
                if q['type'] == 'fill':
                    self.assertTrue(formatted_answers_match(q['answer'], q['answer'], q['answer_format']), q)
                elif q['type'] == 'mcq':
                    self.assertIn(q['answer'], q['options'])
                if topic in ['Adding fractions', 'Subtracting fractions']:
                    a, b = map(Fraction, re.findall(r'\d+/\d+', text))
                    self.assertEqual(parse_fraction(q['answer'])[0], a + b if topic.startswith('Adding') else a - b)
                elif topic in ['Multiplying fractions', 'Dividing fractions']:
                    expression = text.split('. ')[0].replace('Multiply ', '').replace('Divide ', '').rstrip('.')
                    a, b = map(Fraction, re.split(r' [×÷] ', expression))
                    self.assertEqual(parse_fraction(q['answer'])[0], a * b if '×' in expression else a / b)
                elif topic == 'Simplifying fractions':
                    self.assertEqual(parse_fraction(q['answer'])[0], Fraction(re.search(r'\d+/\d+', text)[0]))
                elif topic == 'Equivalent fractions':
                    a, b = map(Fraction, re.findall(r'\d+/\d+', text))
                    self.assertEqual(q['answer'], str(a == b))
                elif topic == 'Comparing fractions':
                    a, b = map(Fraction, re.findall(r'\d+/\d+', text))
                    self.assertEqual(q['answer'], '<' if a < b else '>' if a > b else '=')
                elif topic == 'Ordering fractions':
                    values = [Fraction(v) for v in text.split(': ')[1].split('; ')]
                    answer = [Fraction(v) for v in q['answer'].split('; ')]
                    self.assertEqual(answer, sorted(values, reverse='descending' in text))

    def test_number_line_coordinates(self):
        ns = {'s': 'http://www.w3.org/2000/svg'}
        for n, d, wholes in [(1, 2, 1), (7, 4, 2), (17, 6, 3)]:
            root = ET.fromstring(chapter.number_line_svg(n, d, wholes))
            circle = root.find('s:circle', ns)
            self.assertAlmostEqual(float(circle.attrib['cx']), 30 + 500 * n / (d * wholes))
            self.assertEqual(len(root.findall('s:line', ns)), d * wholes + 2)

    def test_zero_one_reciprocals_and_division(self):
        for a in [Fraction(0), Fraction(1), Fraction(2), Fraction(2, 3), Fraction(3, 2)]:
            with patch.object(chapter.random, 'choice', return_value=a):
                q = chapter.reciprocal()
            if a == 0:
                self.assertEqual(q['answer'], 'It has no reciprocal')
            else:
                self.assertEqual(parse_fraction(q['answer'])[0] * a, 1)
        for kind, expected in [('zero dividend', 0), ('self', 1), ('one dividend', Fraction(3, 2)),
                               ('one divisor', Fraction(2, 3)), ('zero divisor', None)]:
            with patch.object(chapter, 'value', return_value=Fraction(2, 3)):
                q = chapter.division_properties(kind)
            if expected is None:
                self.assertEqual(q['answer'], 'Undefined')
            else:
                self.assertEqual(parse_fraction(q['answer'])[0], expected)
        for size in [0, 1, 16, 30]:
            self.assertEqual(len(chapter.generate_balanced_worksheet(size)), size)
