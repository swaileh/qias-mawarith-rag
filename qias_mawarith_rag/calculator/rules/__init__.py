"""
Rules package - Fard, Asabah, Hajb rules.

Includes special classical cases:
- العمرية (Umariyyatayn)
- المشتركة (Mushtarakah)
- الأكدرية (Akdariyyah)
"""

from .special import (
    detect_umariyyah,
    calculate_umariyyah,
    detect_mushtarakah,
    calculate_mushtarakah,
    detect_akdariyyah,
    calculate_akdariyyah,
)

__all__ = [
    "detect_umariyyah",
    "calculate_umariyyah",
    "detect_mushtarakah",
    "calculate_mushtarakah",
    "detect_akdariyyah",
    "calculate_akdariyyah",
]

