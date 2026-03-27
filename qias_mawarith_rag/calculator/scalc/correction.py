"""
Inheritance Correction Engine.
Handles Tasil (finding base), Awl/Radd detection, and Tashih (integer correction).

Production-level implementation with proper Fiqh rules.
"""
from typing import List, Tuple
from math import gcd
from functools import reduce
from .heirs import Heir, InheritanceType, HeirCategory
from .shares import Fraction, lcm


class CorrectionEngine:
    """Handles mathematical corrections for inheritance problems."""
    
    def find_base(self, sharers: List[Heir]) -> int:
        """
        Step 4: Tasil (التأصيل) - Find the base of the problem.
        LCM of all denominators of fixed shares.
        """
        if not sharers:
            return 1
            
        denominators = [h.share_fraction.denominator for h in sharers if h.share_fraction.numerator > 0]
        if not denominators:
            return 1
            
        return reduce(lcm, denominators)
    
    def check_awl_radd(self, heirs: List[Heir], base: int, residuaries: List[Heir]) -> Tuple[str, int]:
        """
        Step 6: Check for Awl (العول) or Radd (الرد).
        
        Awl: Fixed shares exceed base → proportionally reduce all shares
        Radd: Fixed shares less than base AND no residuaries → redistribute excess
        
        Returns: (status, new_base)
        """
        # Calculate total fixed shares (FARD and FARD_TASIB count for fixed portion)
        total_fixed = sum(h.sihaam for h in heirs 
                         if h.inheritance_type in (InheritanceType.FARD, InheritanceType.FARD_TASIB))
        
        # Count pure residuaries (those who only take remainder, not FARD_TASIB)
        pure_residuaries = [h for h in residuaries 
                           if h.inheritance_type == InheritanceType.TASIB]
        
        # Total shares currently assigned (including residuaries)
        total_assigned = sum(h.sihaam for h in heirs if not h.is_blocked)
        
        if total_assigned > base:
            # Awl: Shares exceed base → base increases to total shares
            return ("عول", total_assigned)
            
        elif total_assigned < base:
            # Check if there are pure residuaries who would take the remainder
            if not pure_residuaries:
                # No pure residuaries → Radd applies
                return ("رد", base)
                
        return ("لا", base)
    
    def calculate_tashih(self, heirs: List[Heir], base: int) -> int:
        """
        Step 7: Tashih (التصحيح) - Correct the base to ensure integer shares per head.
        
        Only multiplies when NECESSARY - avoids over-correction.
        
        Returns the final corrected base.
        """
        multiplier = 1
        
        # Check each group of heirs with multiple heads
        for h in heirs:
            if h.count > 1 and h.sihaam > 0:
                # Check if shares can be evenly divided among heads
                if h.sihaam % h.count != 0:
                    # Find the minimal multiplier needed
                    # We need: (sihaam * m) % count == 0
                    # Which means: m = count / gcd(sihaam, count)
                    g = gcd(h.sihaam, h.count)
                    needed_factor = h.count // g
                    
                    # Update global multiplier (LCM of all needed factors)
                    multiplier = lcm(multiplier, needed_factor)
        
        return base * multiplier

    def apply_tashih_to_heirs(self, heirs: List[Heir], old_base: int, new_base: int):
        """Update heir shares based on the new Tashih base."""
        if new_base == old_base:
            return
            
        multiplier = new_base // old_base
        for h in heirs:
            if not h.is_blocked:
                h.sihaam *= multiplier
    
    def apply_radd(self, heirs: List[Heir], base: int) -> int:
        """
        Apply Radd (الرد) - Return excess to eligible sharers.
        
        Fiqh Rules:
        1. Spouses (زوج/زوجة) are EXCLUDED from Radd
        2. Remaining estate is distributed proportionally to other sharers
        3. Base effectively reduces to the sum of shares (or adjusts for spouse)
        
        Returns: The new base after Radd
        """
        # Identify eligible heirs (FARD sharers excluding spouses)
        radd_heirs = [h for h in heirs 
                      if h.inheritance_type == InheritanceType.FARD 
                      and h.heir_type.category != HeirCategory.SPOUSE
                      and not h.is_blocked]
        
        # Identify spouse
        spouses = [h for h in heirs 
                   if h.heir_type.category == HeirCategory.SPOUSE 
                   and not h.is_blocked]
        
        if not radd_heirs:
            # No eligible heirs for Radd - should not happen normally
            return base
        
        # Calculate current shares
        spouse_sihaam = sum(s.sihaam for s in spouses)
        radd_sihaam = sum(h.sihaam for h in radd_heirs)
        total_current = spouse_sihaam + radd_sihaam
        
        if total_current >= base:
            # No excess to redistribute
            return base
        
        remainder = base - total_current
        
        if not spouses:
            # Case 1: No spouse - simple Radd
            # Redistribute remainder proportionally to all Radd heirs
            # New base = sum of all Radd heir shares (base shrinks)
            self._distribute_radd_proportionally(radd_heirs, remainder, radd_sihaam)
            return sum(h.sihaam for h in heirs if not h.is_blocked)
        else:
            # Case 2: Spouse exists - complex Radd
            # Spouse keeps their share, remainder goes to others proportionally
            # But the base needs adjustment
            return self._apply_radd_with_spouse(heirs, spouses, radd_heirs, base, remainder)
    
    def _distribute_radd_proportionally(self, heirs: List[Heir], remainder: int, total_shares: int):
        """
        Distribute remainder proportionally to heirs based on their current shares.
        Uses fraction arithmetic for precision.
        """
        if total_shares == 0:
            return
        
        # First pass: calculate exact proportional additions
        additions = []
        for h in heirs:
            # Each heir gets: remainder × (their_shares / total_shares)
            proportion = Fraction(h.sihaam, total_shares)
            addition = proportion * Fraction(remainder, 1)
            additions.append((h, addition))
        
        # Find LCM of all denominators to ensure integer arithmetic
        denoms = [a[1].denominator for a in additions]
        common_denom = reduce(lcm, denoms) if denoms else 1
        
        # If we need to scale up to get integers, do so
        if common_denom > 1:
            # Scale all existing shares and additions
            for h in heirs:
                h.sihaam *= common_denom
            remainder *= common_denom
            total_shares *= common_denom
        
        # Now add the proportional amounts (should be integers now)
        for h, addition in additions:
            add_amount = (addition.numerator * common_denom) // addition.denominator
            h.sihaam += add_amount
    
    def _apply_radd_with_spouse(self, all_heirs: List[Heir], spouses: List[Heir], 
                                 radd_heirs: List[Heir], base: int, remainder: int) -> int:
        """
        Apply Radd when spouse exists.
        
        CORRECT FIQH RULE:
        1. Spouse keeps their ORIGINAL FRACTION of the FINAL estate
           - If spouse has 1/8, they get 1/8 of final shares
        2. Radd heirs divide the remaining portion (7/8 if spouse=1/8)
           in proportion to their original share fractions
        
        Example: Wife 1/8, GM 1/6, Daughter 2/3
        - Wife keeps 1/8 of final = 5/40
        - GM and Daughter share 7/8 in ratio 1:4 (1/6 : 2/3)
        - GM gets 7/40, Daughter gets 28/40
        
        Returns: New base after Radd
        """
        # Calculate spouse fraction (fraction of total estate)
        spouse_fraction = sum((s.share_fraction for s in spouses), Fraction(0, 1))
        
        # Calculate radd heir fractions
        radd_fractions = [(h, h.share_fraction) for h in radd_heirs]
        radd_total_fraction = sum((f for _, f in radd_fractions), Fraction(0, 1))
        
        if radd_total_fraction == Fraction(0,1):
            return sum(h.sihaam for h in all_heirs if not h.is_blocked)
        
        # The non-spouse portion of the estate
        non_spouse_fraction = Fraction(1, 1) - spouse_fraction
        
        # Calculate each heir's final fraction of the estate
        final_fractions = {}
        
        # Spouse keeps their original fraction
        for s in spouses:
            final_fractions[s.name] = s.share_fraction
        
        # Radd heirs divide the non-spouse portion proportionally
        for h, orig_frac in radd_fractions:
            # This heir's proportion of the radd pool
            proportion = orig_frac / radd_total_fraction
            # Their final fraction of the estate
            final_fractions[h.name] = non_spouse_fraction * proportion
        
        # Find LCM of all denominators for integer base
        all_denoms = [f.denominator for f in final_fractions.values()]
        new_base = reduce(lcm, all_denoms) if all_denoms else base
        
        # Assign sihaam based on new base
        for h in all_heirs:
            if h.is_blocked:
                continue
            if h.name in final_fractions:
                frac = final_fractions[h.name]
                h.sihaam = (frac.numerator * new_base) // frac.denominator
        
        return sum(h.sihaam for h in all_heirs if not h.is_blocked)


def calculate_proper_base_for_radd(spouse_fraction: Fraction, 
                                    radd_fractions: List[Fraction]) -> int:
    """
    Calculate the proper base for a Radd case with spouse.
    
    The approach:
    1. Spouse gets their fraction of the FULL estate
    2. Radd heirs divide (1 - spouse_fraction) in proportion to their original shares
    
    Returns: The optimal base for integer arithmetic
    """
    if not radd_fractions:
        return spouse_fraction.denominator
    
    # Sum of Radd heir fractions
    radd_sum = reduce(lambda a, b: a + b, radd_fractions)
    
    # All denominators involved
    all_denoms = [spouse_fraction.denominator, radd_sum.denominator]
    all_denoms.extend(f.denominator for f in radd_fractions)
    
    return reduce(lcm, all_denoms)
