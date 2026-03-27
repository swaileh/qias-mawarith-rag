"""
العمرية (Umariyyatayn / Gharrawayn) - The Two Omar Cases

Named after Umar ibn al-Khattab (رضي الله عنه) who adjudicated these cases.

Description:
  When only spouse + mother + father remain, the mother gets 1/3 of the
  REMAINDER (after spouse's share), not 1/3 of the whole estate.

Cases:
  1. Husband + Mother + Father (العمرية الأولى)
     - Husband: 1/2, Mother: 1/3 of remainder = 1/6, Father: remainder = 2/6
     
  2. Wife + Mother + Father (العمرية الثانية)  
     - Wife: 1/4, Mother: 1/3 of remainder = 1/4, Father: remainder = 2/4

Rationale:
  Without this rule, mother would get 1/3 and father (as asabah) gets less
  than mother, which contradicts the principle that males inherit double females.
"""

from fractions import Fraction
from typing import List, Dict, Any, Optional, Tuple


def detect_umariyyah(heirs: List[Dict[str, Any]]) -> Optional[str]:
    """
    Detect if this is an Umariyyah case.
    
    Args:
        heirs: List of heir dictionaries with 'heir' and 'count' keys
    
    Returns:
        "umariyyah_husband" or "umariyyah_wife" if detected, None otherwise
    """
    # Extract heir types (handle blocked heirs)
    active_heirs = set()
    for h in heirs:
        heir_type = h.get("heir", "")
        if not h.get("is_blocked", False):
            active_heirs.add(heir_type)
    
    # Check for exactly: spouse + mother + father
    has_husband = "زوج" in active_heirs
    has_wife = "زوجة" in active_heirs or "زوجـة" in active_heirs
    has_mother = "أم" in active_heirs
    has_father = "أب" in active_heirs
    
    # Must have exactly these three, no more
    required_count = sum([has_husband or has_wife, has_mother, has_father])
    
    if required_count != 3:
        return None
    
    # Check no other heirs exist (except blocked ones)
    other_heirs = active_heirs - {"زوج", "زوجة", "زوجـة", "أم", "أب"}
    if other_heirs:
        return None
    
    if has_husband:
        return "umariyyah_husband"
    elif has_wife:
        return "umariyyah_wife"
    
    return None


def calculate_umariyyah(case_type: str) -> Dict[str, Tuple[Fraction, str]]:
    """
    Calculate shares for an Umariyyah case.
    
    Args:
        case_type: "umariyyah_husband" or "umariyyah_wife"
    
    Returns:
        Dictionary mapping heir type to (share, basis) tuple
    """
    if case_type == "umariyyah_husband":
        # Husband: 1/2, Mother: 1/6, Father: 2/6 (remainder)
        # Base: 6
        return {
            "زوج": (Fraction(1, 2), "فرض"),
            "أم": (Fraction(1, 6), "ثلث الباقي"),  # 1/3 of 1/2 remainder
            "أب": (Fraction(1, 3), "عصبة"),        # 2/6 = 1/3
        }
    
    elif case_type == "umariyyah_wife":
        # Wife: 1/4, Mother: 1/4, Father: 2/4 (remainder)
        # Base: 4
        return {
            "زوجة": (Fraction(1, 4), "فرض"),
            "أم": (Fraction(1, 4), "ثلث الباقي"),  # 1/3 of 3/4 remainder = 1/4
            "أب": (Fraction(1, 2), "عصبة"),        # 2/4 = 1/2
        }
    
    return {}


def get_umariyyah_base(case_type: str) -> int:
    """Get the base (أصل المسألة) for an Umariyyah case."""
    if case_type == "umariyyah_husband":
        return 6
    elif case_type == "umariyyah_wife":
        return 4
    return 1


def describe_umariyyah(case_type: str, language: str = "ar") -> str:
    """Get a description of the Umariyyah case."""
    if language == "ar":
        if case_type == "umariyyah_husband":
            return "المسألة العمرية الأولى: زوج + أم + أب"
        elif case_type == "umariyyah_wife":
            return "المسألة العمرية الثانية: زوجة + أم + أب"
    else:
        if case_type == "umariyyah_husband":
            return "First Umariyyah: Husband + Mother + Father"
        elif case_type == "umariyyah_wife":
            return "Second Umariyyah: Wife + Mother + Father"
    return ""
