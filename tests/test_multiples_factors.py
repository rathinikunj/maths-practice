import random
import re
import unittest
from math import gcd, prod

from answer_validation import formatted_answers_match
from curriculum.class_5 import multiples_factors as chapter


class MultiplesFactorsTests(unittest.TestCase):
    def setUp(self):
        state = random.getstate()
        self.addCleanup(random.setstate, state)

    def test_factors_and_primes(self):
        for n in range(1, 301):
            expected = [d for d in range(1, n + 1) if n % d == 0]
            self.assertEqual(chapter.factors(n), expected)
            self.assertEqual(chapter.is_prime(n), len(expected) == 2)
            primes = chapter.prime_factors(n)
            self.assertEqual(prod(primes), n)
            self.assertTrue(all(chapter.is_prime(p) for p in primes))
        self.assertEqual(chapter.factors(1), [1])
        self.assertEqual(chapter.factors(36), [1, 2, 3, 4, 6, 9, 12, 18, 36])

    def test_divisibility_all_rules(self):
        self.assertEqual(set(chapter.DIVISIBILITY_RULES), set(range(2, 12)))
        for divisor in range(2, 12):
            seen = set()
            for _ in range(100):
                q = chapter.divisibility(divisor)
                n = int(re.search(r'([\d,]+) is divisible', q['question'])[1].replace(',', ''))
                self.assertEqual(q['answer'], str(n % divisor == 0))
                seen.add(q['answer'])
            self.assertEqual(seen, {'True', 'False'})

    def test_common_division_steps_and_identity(self):
        for a, b in [(12, 18), (8, 9), (36, 36), (2, 100), (64, 96), (7, 11)]:
            for hcf in [True, False]:
                chart = chapter.common_division_rows(a, b, hcf)
                divisors = chart['Divisor'][:-1]
                self.assertEqual(prod(divisors), gcd(a, b) if hcf else a * b // gcd(a, b))
                for i, p in enumerate(divisors):
                    left, right = chart['First number'][i], chart['Second number'][i]
                    self.assertTrue(chapter.is_prime(p))
                    self.assertTrue((left % p == 0 and right % p == 0) if hcf else (left % p == 0 or right % p == 0))
                    self.assertEqual(chart['First number'][i + 1], left // p if left % p == 0 else left)
                    self.assertEqual(chart['Second number'][i + 1], right // p if right % p == 0 else right)
                if not hcf:
                    self.assertEqual((chart['First number'][-1], chart['Second number'][-1]), (1, 1))

    def test_answer_formats(self):
        for answer in ['1, 2, 3, 6', '6;3;2;1', '1 2 3 6']:
            self.assertTrue(formatted_answers_match(answer, '1; 2; 3; 6', 'factor_set'))
        for answer in ['1;2;3', '1;2;3;6;6', '1;2;3;6;12', '', '1,,2,3,6']:
            self.assertFalse(formatted_answers_match(answer, '1;2;3;6', 'factor_set'))
        for answer in ['2 × 2 × 3', '3*2*2', '2x3x2']:
            self.assertTrue(formatted_answers_match(answer, '2 × 2 × 3', 'prime_product'))
        for answer in ['12', '4 × 3', '2 × 3', '1 × 2 × 2 × 3', '', '2**2*3']:
            self.assertFalse(formatted_answers_match(answer, '2 × 2 × 3', 'prime_product'))

    def test_balanced_worksheets(self):
        seen_divisors = set()
        for seed in range(100):
            random.seed(seed)
            questions = chapter.generate_balanced_worksheet()
            self.assertEqual(len(questions), 15)
            self.assertEqual(len({q['topic'] for q in questions}), 13)
            divisibility = [q for q in questions if q['topic'] == 'Divisibility tests']
            divisors = {int(re.search(r'divisible by (\d+)', q['question'])[1]) for q in divisibility}
            self.assertEqual(len(divisors), 3)
            seen_divisors.update(divisors)
            for q in questions:
                if q['type'] == 'fill':
                    self.assertTrue(formatted_answers_match(q['answer'], q['answer'], q['answer_format']))
                if q['topic'] == 'HCF and LCM relationship':
                    a, b, h = map(int, re.findall(r'\d+', q['question']))
                    self.assertEqual(h * int(q['answer']), a * b)
        self.assertEqual(seen_divisors, set(range(2, 12)))
        for size in [0, 1, 14, 16, 30]:
            self.assertEqual(len(chapter.generate_balanced_worksheet(size)), size)
