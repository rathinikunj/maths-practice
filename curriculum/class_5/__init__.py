"""Class 5 chapters based on the supplied curriculum."""

from . import addition_subtraction, large_numbers, multiplication_division, multiples_factors
from . import fractions_module

CHAPTERS = {
    "Large Numbers": large_numbers.generate_balanced_worksheet,
    addition_subtraction.CHAPTER_NAME: addition_subtraction.generate_balanced_worksheet,
    multiplication_division.CHAPTER_NAME: multiplication_division.generate_balanced_worksheet,
    multiples_factors.CHAPTER_NAME: multiples_factors.generate_balanced_worksheet,
    fractions_module.CHAPTER_NAME: fractions_module.generate_balanced_worksheet,
}
