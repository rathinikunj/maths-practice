import ast
import operator
import random
import re
import unittest
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from unittest.mock import patch
import xml.etree.ElementTree as ET

from answer_validation import formatted_answers_match, parse_integer, parse_quotient_remainder
from curriculum.class_5 import multiplication_division as chapter


def numbers(text):
    return [int(value.replace(',', '')) for value in re.findall(r'\d[\d,]*', text)]


def evaluate(expression):
    tree = ast.parse(expression.replace('×', '*').replace('÷', '/').replace('−', '-').replace(',', ''), mode='eval')
    operations = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}

    def visit(node):
        if isinstance(node, ast.Constant):
            return Fraction(node.value)
        return operations[type(node.op)](visit(node.left), visit(node.right))
    return visit(tree.body)


class MultiplicationDivisionTests(unittest.TestCase):
    def setUp(self):
        state = random.getstate()
        self.addCleanup(random.setstate, state)

    def test_generated_arithmetic_and_coverage(self):
        for seed in range(100):
            random.seed(seed)
            worksheet = chapter.generate_balanced_worksheet()
            self.assertEqual(len(worksheet), 15)
            self.assertEqual(len({q['topic'] for q in worksheet}), 15)
            for q in worksheet:
                topic, text = q['topic'], q['question']
                values = numbers(text)
                if q['type'] == 'mcq':
                    self.assertIn(q['answer'], q['options'])
                    self.assertEqual(len(q['options']), len(set(q['options'])))
                elif q['type'] == 'fill':
                    self.assertTrue(formatted_answers_match(q['answer'], q['answer'], q['answer_format']))
                else:
                    self.assertIn(q['answer'], ['True', 'False'])
                if topic in ['Multiplication tables', 'Large-number multiplication', 'Lattice multiplication',
                             'Multiplication by 10, 100 and 1000', 'Multiplication applications']:
                    self.assertEqual(parse_integer(q['answer']), values[0] * values[1])
                elif topic == 'Distributive property':
                    a, b, c = values
                    self.assertEqual(parse_integer(q['answer']), a * (b - c if '−' in text else b + c))
                elif topic == 'Estimating products':
                    a, b, repeated_a, unit, repeated_b, ten = values
                    self.assertEqual((a, b, ten), (repeated_a, repeated_b, 10))
                    def rounded(n, scale):
                        return int((Decimal(n) / scale).quantize(Decimal('1'), rounding=ROUND_HALF_UP)) * scale
                    self.assertEqual(parse_integer(q['answer']), rounded(a, unit) * rounded(b, 10))
                elif topic in ['Division by 10, 100 and 1000', 'Five-digit by two-digit division']:
                    dividend, divisor = values
                    quotient, remainder = parse_quotient_remainder(q['answer'])
                    self.assertEqual(dividend, divisor * quotient + remainder)
                    self.assertTrue(0 <= remainder < divisor)
                    self.assertTrue(10000 <= dividend <= 99999)
                elif topic == 'Division applications: unitary method':
                    units, total, target = values
                    self.assertEqual(parse_integer(q['answer']), total // units * target)
                elif topic == 'DMAS':
                    expression = text.split(': ')[1].split(' =')[0]
                    self.assertEqual(parse_integer(q['answer']), evaluate(expression))
                elif topic in ['Multiplication terms', 'Division terms']:
                    terms = (['multiplicand', 'multiplier', 'product'] if topic.startswith('Multiplication')
                             else ['dividend', 'divisor', 'quotient', 'remainder'])
                    for index, term in enumerate(terms):
                        if f'the {term}?' in text:
                            self.assertEqual(parse_integer(q['answer']), values[index])

    def test_properties_and_dmas_variants(self):
        for seed in range(20):
            random.seed(seed)
            for kind in ['identity', 'zero', 'commutative', 'associative']:
                q = chapter.multiplication_property(kind)
                if q['type'] == 'fill':
                    self.assertEqual(parse_integer(q['answer']), evaluate(q['question'].split(': ')[1].split(' =')[0]))
                else:
                    self.assertEqual(q['answer'], f'{kind.title()} property')
            for kind in ['one', 'self', 'zero_dividend', 'zero_divisor', 'identity', 'remainder']:
                q = chapter.division_property(kind)
                values = numbers(q['question'])
                if kind in ['one', 'self', 'zero_dividend']:
                    self.assertEqual(parse_integer(q['answer']), values[0] // values[1])
                elif kind == 'zero_divisor':
                    self.assertEqual(q['answer'], 'Undefined (division by zero is not allowed)')
                elif kind == 'identity':
                    d, quotient, remainder = values
                    self.assertEqual(parse_integer(q['answer']), d * quotient + remainder)
                else:
                    self.assertEqual(q['answer'], str(0 <= values[0] < values[1]))
            for kind in ['mixed', 'multiply_divide', 'subtract_add']:
                q = chapter.dmas(kind)
                self.assertEqual(parse_integer(q['answer']), evaluate(q['question'].split(': ')[1].split(' =')[0]))
            for subtract in [True, False]:
                q = chapter.distributive_property(subtract)
                a, b, c = numbers(q['question'])
                self.assertEqual(parse_integer(q['answer']), a * (b - c if subtract else b + c))

    def test_quotient_remainder_input(self):
        for user in ['1,234 R 5', '1234r5', '1234 remainder 5', '1234;5']:
            self.assertTrue(formatted_answers_match(user, '1234 R 5', 'quotient_remainder'))
        for user in ['', '1234', '1234.5', '1234 R -5', '1234 R 6', '1234 R 5 extra', '1234 R 5 R 0']:
            self.assertFalse(formatted_answers_match(user, '1234 R 5', 'quotient_remainder'))
        for dividend, divisor in [(10000, 10), (10001, 100), (99999, 99), (10000, 99), (99999, 1000)]:
            q = chapter.division_question(dividend, divisor, 'Test')
            self.assertEqual(parse_quotient_remainder(q['answer']), divmod(dividend, divisor))

    def test_lattice_cells_and_diagonal_total(self):
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        for a, b in [(1000, 10), (1234, 56), (99999, 99), (10001, 20)]:
            svg = ET.fromstring(chapter.lattice_svg(a, b))
            texts = { (int(t.attrib['x']), int(t.attrib['y'])): t.text for t in svg.findall('.//svg:text', ns)}
            self.assertEqual(len(svg.findall('.//svg:line', ns)), len(str(a)) * len(str(b)))
            total = 0
            for row, digit_b in enumerate(str(b)):
                for col, digit_a in enumerate(str(a)):
                    x, y = 40 + 56 * col, 40 + 56 * row
                    tens, ones = int(texts[x + 15, y + 23]), int(texts[x + 41, y + 48])
                    self.assertEqual(10 * tens + ones, int(digit_a) * int(digit_b))
                    exponent = len(str(a)) - col - 1 + len(str(b)) - row - 1
                    total += tens * 10 ** (exponent + 1) + ones * 10 ** exponent
            self.assertEqual(total, a * b)

    def test_estimation_halfway_and_sizes(self):
        with patch.object(chapter.random, 'randint', side_effect=[1250, 25]), \
                patch.object(chapter.random, 'choice', return_value=100):
            self.assertEqual(parse_integer(chapter.estimating_products()['answer']), 39000)
        for size in [0, 1, 14, 16, 30]:
            self.assertEqual(len(chapter.generate_balanced_worksheet(size)), size)
        for size in [-1, 1.5, '15']:
            with self.assertRaises(ValueError):
                chapter.generate_balanced_worksheet(size)


if __name__ == '__main__':
    unittest.main()
