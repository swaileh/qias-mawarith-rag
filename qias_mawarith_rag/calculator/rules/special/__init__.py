"""
Special classical cases in Islamic inheritance.

These are well-known historical cases that require special handling
because they don't follow the standard calculation rules.
"""

from .umariyyah import detect_umariyyah, calculate_umariyyah
from .mushtarakah import detect_mushtarakah, calculate_mushtarakah
from .akdariyyah import detect_akdariyyah, calculate_akdariyyah

__all__ = [
    # العمرية - Umariyyatayn
    "detect_umariyyah",
    "calculate_umariyyah",
    # المشتركة - Mushtarakah
    "detect_mushtarakah",
    "calculate_mushtarakah",
    # الأكدرية - Akdariyyah
    "detect_akdariyyah",
    "calculate_akdariyyah",
]
