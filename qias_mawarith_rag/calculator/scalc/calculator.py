"""
Main Inheritance Calculator.
Combines all components to solve Mawarith problems.

Production-level implementation with proper Fiqh rules.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from math import gcd

from .heirs import Heir
from .blocking import BlockingRules
from .rules import ShareRules
from .correction import CorrectionEngine
from .distribution import DistributionEngine


def simplify_fraction(num: int, denom: int) -> Tuple[int, int]:
    """Simplify a fraction to lowest terms."""
    if num == 0:
        return (0, 1)
    g = gcd(num, denom)
    return (num // g, denom // g)


@dataclass
class CalculationResult:
    """Complete result of an inheritance calculation."""
    heirs: List[Dict[str, Any]]
    blocked: List[Dict[str, Any]]
    shares: List[Dict[str, Any]]
    tasil_stage: Dict[str, Any]
    awl_or_radd: str
    awl_stage: Optional[Dict[str, Any]]
    post_tasil: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "heirs": self.heirs,
            "blocked": self.blocked,
            "shares": self.shares,
            "tasil_stage": self.tasil_stage,
            "awl_or_radd": self.awl_or_radd,
            "post_tasil": self.post_tasil,
        }
        if self.awl_stage:
            result["awl_stage"] = self.awl_stage
        return result


class InheritanceCalculator:
    """
    Calculator for Islamic inheritance shares (Mawarith).
    Orchestrates the calculation process using specialized engines.
    
    Implements full Fiqh rules for:
    - Fixed shares (الفروض)
    - Blocking (الحجب)
    - Residuary inheritance (التعصيب)
    - Awl (العول) - when shares exceed 100%
    - Radd (الرد) - when shares < 100% with no residuary
    - Tashih (التصحيح) - integer correction
    """
    
    def __init__(self):
        self.correction_engine = CorrectionEngine()
        self.distribution_engine = DistributionEngine()
        
    def calculate(self, input_heirs: List[Dict[str, Any]], 
                  blocked_siblings_count: int = 0) -> CalculationResult:
        """
        Calculate inheritance shares for the given heirs.
        
        Full Fiqh-compliant process:
        1. Parse and deduplicate input
        2. Apply blocking rules (الحجب)
        3. Determine fixed shares (الفروض)
        4. Calculate base (التأصيل)
        5. Distribute fixed shares
        6. Distribute remainder to residuaries (التعصيب)
        7. Check for Awl/Radd
        8. Apply Radd if needed
        9. Final Tashih correction
        
        Args:
            input_heirs: List of heir dicts with 'heir' and 'count' keys
            blocked_siblings_count: Count of blocked siblings for حجب النقصان
                                   (reduces Mother from 1/3 to 1/6 when >= 2)
        """
        # 1. Parse Heirs (with deduplication)
        heirs = self._parse_and_deduplicate(input_heirs)
        
        # 2. Apply Blocking Rules (الحجب)
        blocking_rules = BlockingRules(heirs)
        blocking_rules.apply_blocking()
        active_heirs = [h for h in heirs if not h.is_blocked]
        blocked_heirs = [h for h in heirs if h.is_blocked]
        
        # 3. Determine Fixed Shares (with blocked siblings context for حجب النقصان)
        share_rules = ShareRules(active_heirs, blocked_siblings_count=blocked_siblings_count)
        sharers, residuaries = share_rules.calculate_shares()

        # 4. Find Base (التأصيل) - LCM of denominators
        base = self.correction_engine.find_base(sharers)

        # 5. Distribute Fixed Shares
        self.distribution_engine.distribute_fixed_shares(sharers, base)
        
        # Calculate initial totals
        total_fixed = sum(h.sihaam for h in sharers)
        remainder = base - total_fixed
        
        # 6. Distribute Remainder to Residuaries (التعصيب)
        multiplier = self.distribution_engine.distribute_remainder(
            active_heirs, residuaries, remainder, base
        )
        
        if multiplier > 1:
            base *= multiplier
        
        # Recalculate totals after distribution
        total_shares = sum(h.sihaam for h in active_heirs)
        
        # 7. Check for Awl or Radd
        awl_or_radd, awl_stage = self._check_and_apply_awl_radd(
            active_heirs, sharers, residuaries, base, total_shares
        )
        
        if awl_or_radd == "عول":
            base = total_shares  # In Awl, base increases to total
        elif awl_or_radd == "رد":
            base = self.correction_engine.apply_radd(active_heirs, base)
        
        # Recalculate after Awl/Radd
        total_shares = sum(h.sihaam for h in active_heirs)
        
        # 8. Simplify base and shares (reduce to lowest common terms)
        total_shares = self._simplify_shares(active_heirs)
        
        # 9. Tashih (التصحيح) - Correct for integer shares per head
        final_base = self.correction_engine.calculate_tashih(active_heirs, total_shares)
        if final_base != total_shares:
            self.correction_engine.apply_tashih_to_heirs(active_heirs, total_shares, final_base)
        
        # 9. Format and return result
        return self._format_result(
            all_heirs=heirs,
            active_heirs=active_heirs,
            blocked_heirs=blocked_heirs,
            total_shares=final_base,
            awl_or_radd=awl_or_radd,
            awl_stage=awl_stage
        )
    
    def _parse_and_deduplicate(self, input_heirs: List[Dict[str, Any]]) -> List[Heir]:
        """
        Parse input and merge duplicate heir types.
        Some datasets have duplicate entries for the same heir type.
        """
        # Group by heir name and sum counts
        merged: Dict[str, int] = {}
        for h in input_heirs:
            name = h.get("heir", "")
            count = h.get("count", 1)
            if name in merged:
                merged[name] += count
            else:
                merged[name] = count
        
        # Convert to Heir objects
        deduplicated = [{"heir": name, "count": count} for name, count in merged.items()]
        return Heir.from_list(deduplicated)
    
    def _simplify_shares(self, heirs: List[Heir]) -> int:
        """
        Simplify shares to lowest common terms.
        
        Divides all shares by their GCD to get the smallest integer representation.
        Returns the new total (simplified base).
        """
        from functools import reduce
        
        shares = [h.sihaam for h in heirs if h.sihaam > 0]
        if not shares:
            return 0
        
        # Find GCD of all shares
        common_divisor = reduce(gcd, shares)
        
        if common_divisor > 1:
            for h in heirs:
                h.sihaam //= common_divisor
        
        return sum(h.sihaam for h in heirs)
    
    def _check_and_apply_awl_radd(self, active_heirs: List[Heir], 
                                   sharers: List[Heir],
                                   residuaries: List[Heir],
                                   base: int, 
                                   total_shares: int) -> Tuple[str, Optional[Dict]]:
        """
        Check and determine Awl/Radd status.
        
        Returns: (status, awl_stage_data)
        """
        awl_stage = None
        
        # Pure residuaries (not FARD_TASIB who already got shares)
        pure_residuaries = [h for h in residuaries if h.sihaam > 0 and 
                          h.inheritance_type.name == 'TASIB']
        
        if total_shares > base:
            # Awl: Shares exceed base
            # All shares are reduced proportionally (base increases to total)
            awl_stage = {
                "asl_after_awl": total_shares,
                "distribution": self._format_distribution_simple(active_heirs, total_shares)
            }
            return ("عول", awl_stage)
        
        elif total_shares < base:
            # Check if there are pure residuaries who took remainder
            if not pure_residuaries:
                # No residuaries took anything → Radd
                return ("رد", None)
        
        return ("لا", None)

    def _format_result(self, all_heirs: List[Heir],
                       active_heirs: List[Heir], 
                       blocked_heirs: List[Heir], 
                       total_shares: int, 
                       awl_or_radd: str,
                       awl_stage: Optional[Dict]) -> CalculationResult:
        """Format the calculation result matching dataset format."""
        
        # Heirs list (active only)
        heirs_list = [{"heir": h.original_name, "count": h.count} for h in active_heirs]
        
        # Blocked list
        blocked_list = [{"heir": h.original_name, "count": h.count} for h in blocked_heirs]
        
        # Shares list (with fraction shares)
        shares_list = self._format_shares(active_heirs)
        
        # Tasil stage
        tasil_stage = {
            "asl": total_shares,
            "distribution": self._format_distribution_for_tasil(active_heirs, total_shares)
        }
        
        # Post-tasil (final distribution)
        post_tasil = {
            "total_shares": total_shares,
            "distribution": self._format_distribution_final(active_heirs, total_shares)
        }
        
        return CalculationResult(
            heirs=heirs_list,
            blocked=blocked_list,
            shares=shares_list,
            tasil_stage=tasil_stage,
            awl_or_radd=awl_or_radd,
            awl_stage=awl_stage,
            post_tasil=post_tasil
        )
    
    def _format_shares(self, heirs: List[Heir]) -> List[Dict]:
        """Format shares in Fiqh terminology."""
        result = []
        for h in heirs:
            share_str = self._get_share_description(h)
            result.append({
                "heir": h.original_name,
                "count": h.count,
                "fraction": share_str
            })
        return result
    
    def _get_share_description(self, heir: Heir) -> str:
        """Get Fiqh share description for an heir."""
        if heir.share_fraction.is_zero():
            return "باقى التركة"  # Residuary
        
        # Return simplified fraction
        num, denom = simplify_fraction(
            heir.share_fraction.numerator, 
            heir.share_fraction.denominator
        )
        
        # Special cases
        if num == 1 and denom == 2:
            return "1/2"
        elif num == 1 and denom == 4:
            return "1/4"
        elif num == 1 and denom == 8:
            return "1/8"
        elif num == 2 and denom == 3:
            return "2/3"
        elif num == 1 and denom == 3:
            return "1/3"
        elif num == 1 and denom == 6:
            return "1/6"
        else:
            return f"{num}/{denom}"
    
    def _format_distribution_simple(self, heirs: List[Heir], base: int) -> List[Dict]:
        """Simple distribution format."""
        result = []
        for h in heirs:
            per_head = h.sihaam // h.count if h.count > 0 else h.sihaam
            num, denom = simplify_fraction(per_head, base)
            result.append({
                "heir": h.original_name,
                "count": h.count,
                "per_head_shares": f"{num}/{denom}" if denom != 1 else str(num)
            })
        return result
    
    def _format_distribution_for_tasil(self, heirs: List[Heir], base: int) -> List[Dict]:
        """Format distribution for tasil stage."""
        result = []
        for h in heirs:
            num, denom = simplify_fraction(h.sihaam, base)
            result.append({
                "heir": h.original_name,
                "count": h.count,
                "shares": f"{num}/{denom}" if denom != 1 else str(num)
            })
        return result
    
    def _format_distribution_final(self, heirs: List[Heir], base: int) -> List[Dict]:
        """Format final distribution with per-head shares and percentages."""
        result = []
        for h in heirs:
            # Per-head shares
            per_head = h.sihaam // h.count if h.count > 0 else h.sihaam
            num, denom = simplify_fraction(per_head, base)
            per_head_str = f"{num}/{denom}" if denom != 1 else str(num)
            
            # Per-head percentage
            per_head_pct = (per_head / base * 100) if base > 0 else 0
            
            result.append({
                "heir": h.original_name,
                "count": h.count,
                "per_head_shares": per_head_str,
                "per_head_percent": round(per_head_pct, 2)
            })
        return result
    
    def calculate_from_question(self, question: str) -> CalculationResult:
        """
        Parse a natural language question and calculate inheritance.
        
        Example: "مات وترك: ابن وبنتين وزوجة"
        """
        heirs = self._parse_question(question)
        return self.calculate(heirs)
    
    def _parse_question(self, question: str) -> List[Dict[str, Any]]:
        """
        Parse Arabic natural language question to extract heirs.
        
        Handles formats like:
        - "مات وترك: ابن وبنتين وزوجة"
        - "توفي عن: ثلاثة أبناء وأربع بنات"
        """
        from .heirs import HEIR_TYPES
        
        # Number words mapping
        numbers = {
            "اثنان": 2, "اثنين": 2, "اثنتان": 2, "اثنتين": 2,
            "ثلاث": 3, "ثلاثة": 3,
            "أربع": 4, "أربعة": 4,
            "خمس": 5, "خمسة": 5,
            "ست": 6, "ستة": 6,
            "سبع": 7, "سبعة": 7,
            "ثمان": 8, "ثمانية": 8,
            "تسع": 9, "تسعة": 9,
            "عشر": 10, "عشرة": 10,
        }
        
        heirs = []
        
        # Split by connectors
        parts = question.replace("مات وترك:", "").replace("توفي عن:", "")
        parts = parts.replace("ما هو نصيب كل وريث؟", "")
        parts = parts.replace(" و ", "|").replace("،", "|")
        
        for part in parts.split("|"):
            part = part.strip()
            if not part:
                continue
            
            # Try to extract count and heir type
            count = 1
            heir_name = part
            
            # Check for number prefix
            words = part.split()
            if len(words) >= 2:
                first_word = words[0]
                if first_word in numbers:
                    count = numbers[first_word]
                    heir_name = " ".join(words[1:])
                elif first_word.isdigit():
                    count = int(first_word)
                    heir_name = " ".join(words[1:])
            
            # Handle dual forms (بنتان -> بنت with count 2)
            if heir_name.endswith("ان") or heir_name.endswith("ين"):
                count = 2 if count == 1 else count
                heir_name = heir_name[:-2] + "ة" if heir_name.endswith("تان") else heir_name[:-2]
            
            # Check if this is a valid heir
            heir_name_clean = heir_name.strip()
            if heir_name_clean and heir_name_clean in HEIR_TYPES:
                heirs.append({"heir": heir_name_clean, "count": count})
        
        return heirs
