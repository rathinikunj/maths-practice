import unittest
from decimal import Decimal, ROUND_HALF_UP
from unittest.mock import patch

from curriculum.class_4.measurement_module import estimate_rounding
from quantity_answers import quantity_answers_match


class Class4RoundingTests(unittest.TestCase):
    def test_entire_generator_range_uses_school_rounding(self):
        for value in range(100, 1000):
            with self.subTest(value=value), patch(
                'curriculum.class_4.measurement_module.random.randint', return_value=value
            ):
                q = estimate_rounding()
                expected = int(Decimal(value).quantize(Decimal('1E2'), rounding=ROUND_HALF_UP))
                self.assertEqual(q['answer'], str(expected))
                self.assertEqual(q['expected_unit'], 'g')

    def test_halfway_answer_is_graded_correctly(self):
        with patch('curriculum.class_4.measurement_module.random.randint', return_value=250):
            q = estimate_rounding()
        for answer in ['300', '300 grams']:
            self.assertTrue(quantity_answers_match(answer, q['answer'], q['expected_unit']))
        self.assertFalse(quantity_answers_match('200 g', q['answer'], q['expected_unit']))
