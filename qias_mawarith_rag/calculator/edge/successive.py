"""
المناسخات (Munasakhaat) - Successive Deaths Handler

Handles cases where an heir dies before the estate is distributed.
The deceased heir's share becomes a new estate for their own heirs.

Islamic Fiqh Approach:
  Munasakhaat (من نسخ = to copy/transfer) refers to the transfer of
  inheritance problems when an heir dies before receiving their share.

  Methods of Solution:
  1. Separate Problems Method:
     - Solve each death as a separate problem
     - Multiply bases to get combined tashih
     
  2. Combined Method (if heirs overlap):
     - Identify common heirs
     - Simplify calculations where possible

Example:
  Ahmad dies leaving: Wife, Son (Khalid), Daughter (Sara)
  Before distribution, Khalid dies leaving: Wife, Son
  
  Step 1: Calculate Ahmad's estate
    - Wife: 1/8
    - Khalid: 7/16 (residuary with Sara)
    - Sara: 7/32
    
  Step 2: Calculate Khalid's estate (his 7/16 share)
    - Khalid's Wife: 1/4 of 7/16 = 7/64
    - Khalid's Son: 3/4 of 7/16 = 21/64
    
  Final Distribution (of original estate):
    - Ahmad's Wife: 1/8 = 8/64
    - Sara: 7/32 = 14/64
    - Khalid's Wife: 7/64
    - Khalid's Son: 21/64
"""

from fractions import Fraction
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DeathEvent:
    """Represents a death in the chain."""
    decedent: str           # Name or identifier
    heirs: List[Dict]       # Their heirs
    share_of_original: Optional[Fraction] = None  # Their share of first estate
    result: Optional[Dict] = None  # Their inheritance result


@dataclass
class MunasakhResult:
    """Result of successive deaths calculation."""
    death_chain: List[DeathEvent]
    final_distribution: Dict[str, Fraction]  # Final share of original estate
    combined_base: int
    calculation_steps: List[str]


def calculate_munasakhaat(
    first_decedent: str,
    first_heirs: List[Dict[str, Any]],
    successive_deaths: List[Dict[str, Any]],
    calculator_func,
) -> MunasakhResult:
    """
    Calculate inheritance with successive deaths.
    
    Args:
        first_decedent: Name/identifier of original decedent
        first_heirs: Heirs of the first decedent
        successive_deaths: List of {heir_name, heirs} for each successive death
        calculator_func: Function to calculate inheritance
    
    Returns:
        MunasakhResult with complete chain and final distribution
    """
    steps = []
    death_chain = []
    
    # Step 1: Calculate first estate
    steps.append(f"الخطوة 1: حساب تركة {first_decedent}")
    first_result = calculator_func(first_heirs)
    first_dist = _extract_distribution(first_result)
    first_base = _get_base(first_result)
    
    steps.append(f"  أصل المسألة: {first_base}")
    for heir, share in first_dist.items():
        steps.append(f"  {heir}: {share}")
    
    death_chain.append(DeathEvent(
        decedent=first_decedent,
        heirs=first_heirs,
        share_of_original=Fraction(1),
        result=first_dist,
    ))
    
    # Track final distribution (starts with first distribution)
    final_distribution = first_dist.copy()
    combined_base = first_base
    
    # Step 2+: Process each successive death
    for i, death in enumerate(successive_deaths, 2):
        heir_name = death.get("heir_name", "")
        heir_heirs = death.get("heirs", [])
        
        steps.append(f"\nالخطوة {i}: موت {heir_name} قبل القسمة")
        
        # Find the deceased heir's share
        deceased_share = final_distribution.get(heir_name, Fraction(0))
        if deceased_share == 0:
            steps.append(f"  تحذير: {heir_name} لم يكن له نصيب")
            continue
        
        steps.append(f"  نصيب {heir_name} من التركة الأصلية: {deceased_share}")
        
        # Remove deceased from final distribution
        del final_distribution[heir_name]
        
        # Calculate the deceased heir's own inheritance
        heir_result = calculator_func(heir_heirs)
        heir_dist = _extract_distribution(heir_result)
        heir_base = _get_base(heir_result)
        
        steps.append(f"  أصل مسألة {heir_name}: {heir_base}")
        
        # Distribute the deceased's share among their heirs
        for heir, share in heir_dist.items():
            actual_share = share * deceased_share
            steps.append(f"  {heir}: {share} × {deceased_share} = {actual_share}")
            
            # Add to final distribution
            if heir in final_distribution:
                final_distribution[heir] = final_distribution[heir] + actual_share
            else:
                final_distribution[heir] = actual_share
        
        # Update combined base
        combined_base = _lcm(combined_base, heir_base)
        
        death_chain.append(DeathEvent(
            decedent=heir_name,
            heirs=heir_heirs,
            share_of_original=deceased_share,
            result=heir_dist,
        ))
    
    # Final step: Show combined result
    steps.append("\nالنتيجة النهائية:")
    steps.append(f"  الأصل المشترك: {combined_base}")
    for heir, share in final_distribution.items():
        integer_share = int(share * combined_base)
        steps.append(f"  {heir}: {share} = {integer_share}/{combined_base}")
    
    return MunasakhResult(
        death_chain=death_chain,
        final_distribution=final_distribution,
        combined_base=combined_base,
        calculation_steps=steps,
    )


def _extract_distribution(result) -> Dict[str, Fraction]:
    """Extract distribution dictionary from calculator result."""
    if hasattr(result, "to_dict"):
        result = result.to_dict()
    elif not isinstance(result, dict):
        return {}
    
    distribution = {}
    
    # Try post_tasil first
    post_tasil = result.get("post_tasil", {})
    dist_list = post_tasil.get("distribution", result.get("distribution", []))
    
    for d in dist_list:
        heir = d.get("heir", "")
        
        # Try to get fraction from various sources
        share = Fraction(0)
        
        # Try per_head_shares first
        per_head = d.get("per_head_shares", d.get("share", "0"))
        try:
            if "/" in str(per_head):
                parts = str(per_head).split("/")
                share = Fraction(int(parts[0]), int(parts[1]))
            elif isinstance(per_head, (int, float)) and per_head > 0:
                share = Fraction(per_head).limit_denominator(1000)
        except (ValueError, TypeError, IndexError):
            pass
        
        # Multiply by count
        count = d.get("count", 1)
        distribution[heir] = share * count
    
    return distribution


def _get_base(result) -> int:
    """Extract base from calculator result."""
    if hasattr(result, "to_dict"):
        result = result.to_dict()
    elif not isinstance(result, dict):
        return 1
    
    post_tasil = result.get("post_tasil", {})
    return post_tasil.get("total_shares", result.get("base", 1))


def _lcm(a: int, b: int) -> int:
    """Calculate least common multiple."""
    import math
    return abs(a * b) // math.gcd(a, b)


def format_munasakh_result(result: MunasakhResult, language: str = "ar") -> str:
    """Format munasakhaat result for display."""
    lines = []
    
    if language == "ar":
        lines.append("=" * 50)
        lines.append("المناسخات - الوفيات المتتالية")
        lines.append("=" * 50)
        
        lines.append(f"\nعدد الوفيات: {len(result.death_chain)}")
        lines.append(f"الأصل المشترك: {result.combined_base}")
        
        lines.append("\nخطوات الحساب:")
        for step in result.calculation_steps:
            lines.append(step)
        
    else:
        lines.append("=" * 50)
        lines.append("MUNASAKHAAT - SUCCESSIVE DEATHS")
        lines.append("=" * 50)
        
        lines.append(f"\nNumber of deaths: {len(result.death_chain)}")
        lines.append(f"Combined base: {result.combined_base}")
        
        lines.append("\nCalculation Steps:")
        for step in result.calculation_steps:
            lines.append(step)
    
    return "\n".join(lines)
