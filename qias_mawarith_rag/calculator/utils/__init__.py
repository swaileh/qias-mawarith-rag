"""
Utilities package - Common helpers for mawarith.
"""

from fractions import Fraction
from typing import List, Tuple
import math


def lcm(a: int, b: int) -> int:
    """Calculate least common multiple of two integers."""
    return abs(a * b) // math.gcd(a, b)


def lcm_list(numbers: List[int]) -> int:
    """Calculate least common multiple of a list of integers."""
    result = 1
    for n in numbers:
        if n != 0:
            result = lcm(result, n)
    return result


def simplify_fraction(num: int, den: int) -> Tuple[int, int]:
    """Simplify a fraction to lowest terms."""
    if den == 0:
        raise ValueError("Denominator cannot be zero")
    g = math.gcd(num, den)
    return num // g, den // g


def fraction_to_arabic(frac: Fraction) -> str:
    """Convert fraction to Arabic name."""
    mapping = {
        Fraction(1, 2): "النصف",
        Fraction(1, 4): "الربع",
        Fraction(1, 8): "الثمن",
        Fraction(2, 3): "الثلثان",
        Fraction(1, 3): "الثلث",
        Fraction(1, 6): "السدس",
    }
    return mapping.get(frac, str(frac))


def calculate_base(fractions: List[Fraction]) -> int:
    """Calculate common base (أصل المسألة) for a list of fractions."""
    denominators = [f.denominator for f in fractions if f > 0]
    if not denominators:
        return 1
    return lcm_list(denominators)


def is_awl_case(fard_sum: Fraction) -> bool:
    """Check if this is an Awl case (shares exceed estate)."""
    return fard_sum > Fraction(1, 1)


def is_radd_case(fard_sum: Fraction, has_asabah: bool) -> bool:
    """Check if this is a Radd case (excess remains, no asabah)."""
    return fard_sum < Fraction(1, 1) and not has_asabah


__all__ = [
    "lcm",
    "lcm_list",
    "simplify_fraction",
    "fraction_to_arabic",
    "calculate_base",
    "is_awl_case",
    "is_radd_case",
]
