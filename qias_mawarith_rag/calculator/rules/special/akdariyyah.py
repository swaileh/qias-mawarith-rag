"""
الأكدرية (Akdariyyah) - The Akdar Case

Named after Akdar, the person who brought this case to Zayd ibn Thabit.

Description:
  The most complex classical case involving grandfather competing with a
  full sister in presence of spouse and mother.

Case:
  Husband + Mother + Grandfather + Full Sister
  
  Standard calculation would give:
  - Husband: 1/2 (3/6)
  - Mother: 1/3 (2/6)
  - Grandfather: 1/6 (1/6) - as fard minimum
  - Full Sister: 1/2 (3/6) - as fard
  - Total: 9/6 → Awl to 9
  
  But the Akdariyyah solution (Shafi'i/Maliki) is:
  1. Apply awl to base 9
  2. Then grandfather and sister pool their shares (1+3=4) and redistribute
     using muqasama (grandfather:2, sister:1)
  
  Final (base 27):
  - Husband: 9/27
  - Mother: 6/27
  - Grandfather: 8/27
  - Full Sister: 4/27

Note:
  Different schools have different solutions:
  - Hanafi: Grandfather blocks sister entirely
  - Hanbali: Various solutions depending on the scholar
"""

from fractions import Fraction
from typing import List, Dict, Any, Tuple


def detect_akdariyyah(heirs: List[Dict[str, Any]]) -> bool:
    """
    Detect if this is an Akdariyyah case.
    
    Args:
        heirs: List of heir dictionaries with 'heir' and 'count' keys
    
    Returns:
        True if this is an Akdariyyah case, False otherwise
    """
    # Extract heir types
    heir_types = set()
    for h in heirs:
        heir_type = h.get("heir", "")
        if not h.get("is_blocked", False):
            heir_types.add(heir_type)
    
    # Normalize grandfather names
    has_grandfather = any(gf in heir_types for gf in ["أب الأب", "جد"])
    
    # Requirements: Husband + Mother + Grandfather + Full Sister (exactly)
    has_husband = "زوج" in heir_types
    has_mother = "أم" in heir_types
    has_full_sister = "أخت شقيقة" in heir_types
    
    # Must not have father (blocks grandfather) or descendants
    has_blocker = any(h in heir_types for h in 
                      ["أب", "ابن", "بنت", "ابن ابن", "بنت ابن", "أخ شقيق"])
    
    # Check exactly these four
    if not all([has_husband, has_mother, has_grandfather, has_full_sister]):
        return False
    
    if has_blocker:
        return False
    
    # Check no other heirs (besides the four)
    base_heirs = {"زوج", "أم", "أب الأب", "جد", "أخت شقيقة"}
    other_heirs = heir_types - base_heirs
    
    return len(other_heirs) == 0


def calculate_akdariyyah(madhab: str = "shafii") -> Dict[str, Tuple[Fraction, str]]:
    """
    Calculate shares for an Akdariyyah case.
    
    Args:
        madhab: Islamic school of thought
    
    Returns:
        Dictionary mapping heir type to (share, explanation) tuple
    """
    if madhab.lower() == "hanafi":
        # Hanafi: Grandfather blocks sister
        return {
            "زوج": (Fraction(1, 2), "فرض"),
            "أم": (Fraction(1, 3), "فرض"),
            "أب الأب": (Fraction(1, 6), "عصبة"),
            "أخت شقيقة": (Fraction(0, 1), "محجوبة بالجد"),
        }
    
    else:
        # Shafi'i/Maliki: The complex Akdariyyah solution
        # Base 27 after awl and muqasama adjustment
        return {
            "زوج": (Fraction(9, 27), "فرض معول"),       # 1/2 of 6 = 3, awl to 9, × 3 = 9/27
            "أم": (Fraction(6, 27), "فرض معول"),         # 1/3 of 6 = 2, awl to 9, × 3 = 6/27
            "أب الأب": (Fraction(8, 27), "معاقسمة"),     # After pooling: 8/27 (2/3 of 4)
            "أخت شقيقة": (Fraction(4, 27), "معاقسمة"),   # After pooling: 4/27 (1/3 of 4)
        }


def get_akdariyyah_base(madhab: str = "shafii") -> int:
    """Get the base (أصل المسألة) for an Akdariyyah case."""
    if madhab.lower() == "hanafi":
        return 6
    else:
        return 27  # After awl and tashih


def describe_akdariyyah(madhab: str = "shafii", language: str = "ar") -> str:
    """Get a description of the Akdariyyah case."""
    if language == "ar":
        if madhab.lower() == "hanafi":
            return "المسألة الأكدرية (الحنفية): الجد يحجب الأخت الشقيقة"
        else:
            return "المسألة الأكدرية: زوج + أم + جد + أخت شقيقة (معاقسمة بعد العول)"
    else:
        if madhab.lower() == "hanafi":
            return "Akdariyyah (Hanafi): Grandfather blocks full sister"
        else:
            return "Akdariyyah: Husband + Mother + Grandfather + Full Sister (muqasama after awl)"


def explain_akdariyyah_calculation(language: str = "ar") -> str:
    """Provide step-by-step explanation of Akdariyyah calculation."""
    if language == "ar":
        return """
خطوات حل المسألة الأكدرية:

١. تحديد الفروض الأصلية:
   - زوج: ١/٢ = ٣/٦
   - أم: ١/٣ = ٢/٦
   - جد: ١/٦ = ١/٦
   - أخت شقيقة: ١/٢ = ٣/٦
   
٢. مجموع الفروض: ٩/٦ (أكبر من الواحد)

٣. تطبيق العول: الأصل يعول من ٦ إلى ٩

٤. بعد العول:
   - زوج: ٣/٩
   - أم: ٢/٩
   - جد + أخت: ٤/٩ (يضمان نصيبهما ويقتسمان)

٥. المعاقسمة بين الجد والأخت (٢:١):
   - جد: ٢/٣ × ٤/٩ = ٨/٢٧
   - أخت: ١/٣ × ٤/٩ = ٤/٢٧

٦. النتيجة النهائية (الأصل ٢٧):
   - زوج: ٩/٢٧
   - أم: ٦/٢٧
   - جد: ٨/٢٧
   - أخت شقيقة: ٤/٢٧
"""
    else:
        return """
Steps to solve Akdariyyah:

1. Original fard shares:
   - Husband: 1/2 = 3/6
   - Mother: 1/3 = 2/6
   - Grandfather: 1/6 = 1/6
   - Full Sister: 1/2 = 3/6
   
2. Sum of shares: 9/6 (exceeds estate)

3. Apply Awl: Base changes from 6 to 9

4. After Awl:
   - Husband: 3/9
   - Mother: 2/9
   - Grandfather + Sister: 4/9 (they pool and share)

5. Muqasama between GF and Sister (2:1 male:female):
   - Grandfather: 2/3 × 4/9 = 8/27
   - Sister: 1/3 × 4/9 = 4/27

6. Final result (base 27):
   - Husband: 9/27
   - Mother: 6/27
   - Grandfather: 8/27
   - Full Sister: 4/27
"""
