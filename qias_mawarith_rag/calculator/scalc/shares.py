"""
Fraction and Share utilities for inheritance calculations.
"""

from __future__ import annotations
from dataclasses import dataclass
from math import gcd
from functools import reduce
from typing import Optional


def lcm(a: int, b: int) -> int:
    """Least Common Multiple of two integers."""
    return abs(a * b) // gcd(a, b)


def lcm_multiple(*args: int) -> int:
    """LCM of multiple integers."""
    return reduce(lcm, args)


@dataclass
class Fraction:
    """
    Represents a fraction for inheritance shares.
    Automatically simplifies and provides arithmetic operations.
    """
    numerator: int
    denominator: int
    
    def __post_init__(self):
        if self.denominator == 0:
            raise ValueError("Denominator cannot be zero")
        # Simplify the fraction
        g = gcd(abs(self.numerator), abs(self.denominator))
        self.numerator //= g
        self.denominator //= g
        # Keep denominator positive
        if self.denominator < 0:
            self.numerator = -self.numerator
            self.denominator = -self.denominator
    
    @classmethod
    def zero(cls) -> Fraction:
        return cls(0, 1)
    
    @classmethod
    def one(cls) -> Fraction:
        return cls(1, 1)
    
    @classmethod
    def from_string(cls, s: str) -> Fraction:
        """Parse fraction from string like '1/2' or '2/3'."""
        if "/" in s:
            num, den = s.split("/")
            return cls(int(num), int(den))
        return cls(int(s), 1)
    
    def __add__(self, other: Fraction) -> Fraction:
        new_num = self.numerator * other.denominator + other.numerator * self.denominator
        new_den = self.denominator * other.denominator
        return Fraction(new_num, new_den)
    
    def __sub__(self, other: Fraction) -> Fraction:
        new_num = self.numerator * other.denominator - other.numerator * self.denominator
        new_den = self.denominator * other.denominator
        return Fraction(new_num, new_den)
    
    def __mul__(self, other: Fraction | int) -> Fraction:
        if isinstance(other, int):
            return Fraction(self.numerator * other, self.denominator)
        return Fraction(self.numerator * other.numerator, self.denominator * other.denominator)
    
    def __truediv__(self, other: Fraction | int) -> Fraction:
        if isinstance(other, int):
            return Fraction(self.numerator, self.denominator * other)
        return Fraction(self.numerator * other.denominator, self.denominator * other.numerator)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Fraction):
            return self.numerator == other.numerator and self.denominator == other.denominator
        return False
    
    def __lt__(self, other: Fraction) -> bool:
        return self.numerator * other.denominator < other.numerator * self.denominator
    
    def __le__(self, other: Fraction) -> bool:
        return self.numerator * other.denominator <= other.numerator * self.denominator
    
    def __gt__(self, other: Fraction) -> bool:
        return self.numerator * other.denominator > other.numerator * self.denominator
    
    def __ge__(self, other: Fraction) -> bool:
        return self.numerator * other.denominator >= other.numerator * self.denominator
    
    def __str__(self) -> str:
        if self.denominator == 1:
            return str(self.numerator)
        return f"{self.numerator}/{self.denominator}"
    
    def __repr__(self) -> str:
        return f"Fraction({self.numerator}, {self.denominator})"
    
    def to_float(self) -> float:
        return self.numerator / self.denominator
    
    def to_percentage(self) -> float:
        return round(self.to_float() * 100, 2)
    
    def is_zero(self) -> bool:
        return self.numerator == 0


@dataclass
class Share:
    """
    Represents an heir's share with both fraction and integer sihaam (shares).
    """
    fraction: Fraction
    sihaam: int  # Integer shares from base
    per_head_sihaam: int  # Shares per individual
    per_head_fraction: Optional[Fraction] = None
    percentage: float = 0.0
    
    def __post_init__(self):
        if self.per_head_fraction is None:
            self.per_head_fraction = self.fraction
        self.percentage = self.per_head_fraction.to_percentage()


# Common fractions used in Mawarith
HALF = Fraction(1, 2)          # النصف
QUARTER = Fraction(1, 4)       # الربع
EIGHTH = Fraction(1, 8)        # الثمن
TWO_THIRDS = Fraction(2, 3)    # الثلثان
THIRD = Fraction(1, 3)         # الثلث
SIXTH = Fraction(1, 6)         # السدس
ZERO = Fraction.zero()
ONE = Fraction.one()
