"""
Mawarith Symbolic Calculator (scalc)
=====================================

A symbolic calculator for Islamic inheritance (المواريث) based on Fiqh rules.

Usage:
    from mawarith.scalc import InheritanceCalculator
    
    calc = InheritanceCalculator()
    result = calc.calculate([
        {"heir": "زوجة", "count": 1},
        {"heir": "ابن", "count": 2},
        {"heir": "بنت", "count": 1},
    ])
"""

from .calculator import InheritanceCalculator
from .heirs import Heir, HeirType
from .shares import Fraction, Share

__version__ = "1.0.0"
__all__ = ["InheritanceCalculator", "Heir", "HeirType", "Fraction", "Share"]
