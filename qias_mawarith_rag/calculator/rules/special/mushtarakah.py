"""
المشتركة (Mushtarakah / Himariyyah / Yammiyyah) - The Shared Case

Also known as:
- الحمارية (Himariyyah) - "The Donkey Case" 
- اليمية (Yammiyyah)
- الحجرية (Hajariyyah)

Description:
  When husband + mother + maternal siblings + full siblings exist together,
  the full siblings share with maternal siblings in their 1/3 equally.
  
  This is against the normal rule where full siblings would be asabah
  and get nothing after fard shares exhaust the estate.

Case:
  Husband + Mother + Maternal Siblings (2+) + Full Siblings
  - Husband: 1/2
  - Mother: 1/6
  - Maternal Siblings: 1/3 (shared equally)
  - Full Siblings: Share in the 1/3 with maternal siblings
  
  Result: All siblings (maternal + full) share the 1/3 equally.

Rationale:
  Full siblings argued to Umar (رضي الله عنه): "Assume our father was a donkey,
  we still share the same mother with the maternal siblings!"
  
Note:
  This is specific to the Shafi'i and Maliki schools. Hanafi and Hanbali
  schools do not apply this rule (full siblings get nothing as asabah).
"""

from fractions import Fraction
from typing import List, Dict, Any, Tuple


def detect_mushtarakah(heirs: List[Dict[str, Any]], madhab: str = "shafii") -> bool:
    """
    Detect if this is a Mushtarakah case.
    
    Args:
        heirs: List of heir dictionaries with 'heir' and 'count' keys
        madhab: Islamic school (only applies in shafii/maliki)
    
    Returns:
        True if this is a Mushtarakah case, False otherwise
    """
    # Only applies in Shafi'i and Maliki schools
    if madhab.lower() not in ("shafii", "maliki"):
        return False
    
    # Extract heir types and counts
    heir_counts = {}
    for h in heirs:
        heir_type = h.get("heir", "")
        if not h.get("is_blocked", False):
            count = h.get("count", 1)
            heir_counts[heir_type] = heir_counts.get(heir_type, 0) + count
    
    # Requirements:
    # 1. Husband present
    has_husband = "زوج" in heir_counts
    
    # 2. Mother present
    has_mother = "أم" in heir_counts
    
    # 3. Maternal siblings (2 or more)
    maternal_count = heir_counts.get("أخ لأم", 0) + heir_counts.get("أخت لأم", 0)
    has_maternal = maternal_count >= 2
    
    # 4. Full siblings present (any number)
    full_count = heir_counts.get("أخ شقيق", 0) + heir_counts.get("أخت شقيقة", 0)
    has_full = full_count > 0
    
    # 5. No father, grandfather, or descendants (they would block)
    has_blocker = any(h in heir_counts for h in ["أب", "أب الأب", "ابن", "بنت", "ابن ابن", "بنت ابن"])
    
    return all([has_husband, has_mother, has_maternal, has_full, not has_blocker])


def calculate_mushtarakah(heirs: List[Dict[str, Any]]) -> Dict[str, Tuple[Fraction, str, int]]:
    """
    Calculate shares for a Mushtarakah case.
    
    Args:
        heirs: List of heir dictionaries
    
    Returns:
        Dictionary mapping heir type to (share, type, base) tuple
    """
    # Count all siblings
    maternal_count = 0
    full_count = 0
    
    for h in heirs:
        heir_type = h.get("heir", "")
        count = h.get("count", 1)
        if heir_type in ("أخ لأم", "أخت لأم"):
            maternal_count += count
        elif heir_type in ("أخ شقيق", "أخت شقيقة"):
            full_count += count
    
    total_siblings = maternal_count + full_count
    
    # All siblings share in 1/3 equally (males = females in this case)
    sibling_share = Fraction(1, 3) / total_siblings
    
    result = {
        "زوج": (Fraction(1, 2), "فرض", 1),
        "أم": (Fraction(1, 6), "فرض", 1),
    }
    
    # Add maternal siblings
    if maternal_count > 0:
        result["أخ لأم"] = (sibling_share * maternal_count, "ثلث مشترك", maternal_count)
    
    # Add full siblings (same share as maternal - key feature!)
    if full_count > 0:
        # For full siblings, we track full brothers and sisters separately but same share
        for h in heirs:
            heir_type = h.get("heir", "")
            count = h.get("count", 1)
            if heir_type in ("أخ شقيق", "أخت شقيقة"):
                result[heir_type] = (sibling_share * count, "ثلث مشترك", count)
    
    return result


def get_mushtarakah_base(heirs: List[Dict[str, Any]]) -> int:
    """Get the base (أصل المسألة) for a Mushtarakah case."""
    # Count total siblings
    total_siblings = 0
    for h in heirs:
        heir_type = h.get("heir", "")
        count = h.get("count", 1)
        if heir_type in ("أخ لأم", "أخت لأم", "أخ شقيق", "أخت شقيقة"):
            total_siblings += count
    
    # Base is 6, then multiply by siblings for equal division
    return 6 * total_siblings


def describe_mushtarakah(language: str = "ar") -> str:
    """Get a description of the Mushtarakah case."""
    if language == "ar":
        return "المسألة المشتركة (الحمارية): الإخوة الأشقاء يشاركون الإخوة لأم في الثلث"
    else:
        return "Mushtarakah: Full siblings share 1/3 with maternal siblings equally"
