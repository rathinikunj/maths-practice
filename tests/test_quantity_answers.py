import unittest
from unittest.mock import patch

from quantity_answers import quantity_answers_match
from answer_validation import formatted_answers_match
from curriculum.class_4 import measurement_module as measurement, perimeter_area_module as geometry, time_module as time


class QuantityAnswerTests(unittest.TestCase):
    def test_clock_answers_do_not_use_quantity_substring_matching(self):
        self.assertTrue(formatted_answers_match('3:00PM', '03:00 PM', 'clock_12'))
        self.assertTrue(formatted_answers_match('3:00', '03:00', 'clock_24'))
        for answer in ['4:00 PM', '3:00 PM junk', '3:00 AM', '13:00 PM']:
            self.assertFalse(formatted_answers_match(answer, '03:00 PM', 'clock_12'))

    def test_requested_unit_and_aliases(self):
        for user in ['1000', '1000.0', '1,000 m', '1000m', '1000 metres', '1000 METERS']:
            self.assertTrue(quantity_answers_match(user, '1000', 'm'), user)
        for user in ['1000 kg', '1000 cm', '1 km', '1000 bananas', '1000 m extra', 'wrong 1000 m', '1000 m 0 cm', '', '1000 m²']:
            self.assertFalse(quantity_answers_match(user, '1000', 'm'), user)
        for user, unit in [('2 litres', 'l'), ('2 L', 'l'), ('2 milliliters', 'ml'), ('2 hours', 'hr'), ('2 mins', 'min'), ('2 days', 'day')]:
            self.assertTrue(quantity_answers_match(user, '2', unit))

    def test_area_and_counts(self):
        for user in ['16', '16 cm²', '16 cm2', '16 cm^2', '16 square centimetres', '16 sq. cm']:
            self.assertTrue(quantity_answers_match(user, '16', 'cm2'), user)
        for user in ['16 cm', '16 m2', '16 squares']:
            self.assertFalse(quantity_answers_match(user, '16', 'cm2'))
        self.assertTrue(quantity_answers_match('16 squares', '16', 'square'))
        self.assertFalse(quantity_answers_match('16 cm²', '16', 'square'))

    def test_compound_quantities_consume_entire_input(self):
        for user in ['4 hours 20 minutes', '4hr20min', '4 HR 20 MIN']:
            self.assertTrue(quantity_answers_match(user, '4 hr 20 min'), user)
        for user in ['4 hr 20 min garbage', 'garbage 4 hr 20 min', '4 kg 20 g', '4 hr 20 min 7', '4 hr 20 min 0 day', '4:20']:
            self.assertFalse(quantity_answers_match(user, '4 hr 20 min'), user)
        self.assertTrue(quantity_answers_match('2 kilograms 0 grams', '2 kg 0 g'))
        self.assertTrue(quantity_answers_match('2 meters 30 centimeters', '2 m 30 cm'))

    def test_generators_declare_target_units(self):
        for branch in [True, False]:
            with patch.object(measurement.random, 'choice', return_value=branch):
                self.assertEqual(measurement.convert_length()['expected_unit'], 'm' if branch else 'cm')
                self.assertEqual(measurement.convert_mass()['expected_unit'], 'g' if branch else 'kg')
                self.assertEqual(measurement.convert_capacity()['expected_unit'], 'ml' if branch else 'l')
        for generator, unit in [(measurement.estimate_rounding, 'g'), (geometry.square_area, 'cm2'),
                                (geometry.rectangle_area, 'cm2'), (geometry.square_perimeter, 'cm'),
                                (geometry.rectangle_perimeter, 'cm'), (geometry.irregular_perimeter, 'cm'),
                                (geometry.tiling_area, 'square'), (geometry.shaded_area, 'square'),
                                (time.convert_hours_to_minutes, 'min'), (time.convert_days_to_hours, 'hr'),
                                (time.duration_in_days, 'day')]:
            q = generator()
            self.assertEqual(q['expected_unit'], unit)
            self.assertTrue(quantity_answers_match(q['answer'], q['answer'], unit))
        for generator in [measurement.add_length, measurement.subtract_mass, time.add_time]:
            q = generator()
            self.assertEqual(q['answer_format'], 'quantity')
            self.assertTrue(quantity_answers_match(q['answer'], q['answer']))
