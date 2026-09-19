"""Class-specific chapter generators used by the practice app."""

from .class_4 import CHAPTERS as CLASS_4_CHAPTERS
from .class_5 import CHAPTERS as CLASS_5_CHAPTERS

# Insertion order determines the order shown in the class selector.
CURRICULA = {
    4: CLASS_4_CHAPTERS,
    5: CLASS_5_CHAPTERS,
}
