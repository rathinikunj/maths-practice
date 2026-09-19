import random
import unittest
from fractions import Fraction

from answer_validation import formatted_answers_match
from curriculum.class_4 import fractions_module as chapter


class Class4FractionGradingTests(unittest.TestCase):
    def test_equivalent_values_and_invalid_answers(self):
        for user, expected in [('1/2', '2/4'), ('2/4', '1/2'), ('0', '0/1'),
                               ('0/7', '0'), ('2 1/3', '7/3'), (' 1 / 2 ', '2/4')]:
            self.assertTrue(formatted_answers_match(user, expected, 'fraction_value'))
        for user in ['1/0', '1//2', '1/2 extra', '', '1/3', '0 2/4']:
            self.assertFalse(formatted_answers_match(user, '1/2', 'fraction_value'))
        # Removing all spaces would confuse a mixed number with an improper fraction.
        self.assertFalse(formatted_answers_match('2 1/3', '21/3', 'fraction_value'))

    def test_conversion_forms_and_class5_strictness(self):
        self.assertTrue(formatted_answers_match('2 2/4', '2 1/2', 'fraction_mixed_value'))
        self.assertFalse(formatted_answers_match('5/2', '2 1/2', 'fraction_mixed_value'))
        self.assertTrue(formatted_answers_match('10/4', '5/2', 'fraction_improper'))
        self.assertFalse(formatted_answers_match('2 1/2', '5/2', 'fraction_improper'))
        self.assertFalse(formatted_answers_match('2/4', '1/2', 'fraction_simplified'))
        self.assertFalse(formatted_answers_match('2 2/4', '2 1/2', 'fraction_mixed'))

    def test_generated_questions_use_exact_grading(self):
        state = random.getstate()
        self.addCleanup(random.setstate, state)
        for seed in range(100):
            random.seed(seed)
            for generator in [chapter.addition_like, chapter.subtraction_like, chapter.fraction_word_problem]:
                q = generator()
                v = Fraction(q['answer'])
                equivalent = f'{v.numerator * 3}/{v.denominator * 3}'
                self.assertEqual(q['answer_format'], 'fraction_value')
                self.assertTrue(formatted_answers_match(equivalent, q['answer'], q['answer_format']))
                self.assertEqual(q['answer'], str(v))
            for generator in [chapter.mixed_to_improper, chapter.improper_to_mixed_q]:
                q = generator()
                self.assertTrue(formatted_answers_match(q['answer'], q['answer'], q['answer_format']))
