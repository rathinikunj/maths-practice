"""Existing Class 4 curriculum."""

from . import fractions_module, measurement_module, perimeter_area_module, time_module

CHAPTERS = {
    "Fractions": fractions_module.generate_balanced_worksheet,
    "Measurement": measurement_module.generate_balanced_worksheet,
    "Perimeter & Area": perimeter_area_module.generate_balanced_worksheet,
    "Time": time_module.generate_balanced_worksheet,
}
