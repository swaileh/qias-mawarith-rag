"""
Inheritance Distribution Engine.
Handles distribution of fixed shares and residuary logic, including complex Grandfather cases.

Production-level implementation with proper Fiqh rules.
"""
from typing import List
from math import gcd
from .heirs import Heir, HeirCategory, Gender
from .shares import Fraction


def lcm(a: int, b: int) -> int:
    """Least Common Multiple of two integers."""
    return abs(a * b) // gcd(a, b)


class DistributionEngine:
    """Handles distribution of shares to heirs."""
    
    def distribute_fixed_shares(self, heirs: List[Heir], base: int):
        """
        Step 5: Distribute shares based on the base.
        
        Calculates sihaam (integer shares) for each heir based on their fraction.
        """
        for heir in heirs:
            if not heir.is_blocked:
                if heir.share_fraction.numerator > 0:
                    # Calculate: (numerator * base) / denominator
                    heir.sihaam = (heir.share_fraction.numerator * base) // heir.share_fraction.denominator
                else:
                    heir.sihaam = 0

    def distribute_remainder(self, all_heirs: List[Heir], residuaries: List[Heir], 
                             remainder: int, base: int) -> int:
        """
        Distribute remainder to residuary heirs (العصبات).
        
        IMPORTANT: This function distributes the GROUP total, NOT per-head shares.
        Per-head integer correction is handled by Tashih.
        
        Returns multiplier applied to base (1 if no multiplication needed for distribution).
        """
        if not residuaries or remainder <= 0:
            return 1
        
        # Filter active residuaries (those who should take remainder)
        # IMPORTANT RULES:
        # 1. Father (أب): ALWAYS takes remainder - never skipped
        # 2. Grandfather (جد/أب الأب): Skips remainder ONLY when siblings are present
        #    (siblings take it via muqasama - but this is handled elsewhere)
        
        # Check if there are siblings who might take remainder instead of grandfather
        has_siblings = any(h.heir_type.category == HeirCategory.SIBLING and not h.is_blocked 
                          for h in residuaries)
        
        active_residuaries = []
        for h in residuaries:
            if h.is_blocked:
                continue
            
            # For FARD_TASIB heirs who already got their share:
            # - Father (أب): Always include - he takes remainder
            # - Grandfather (جد/أب الأب/أب أب الأب): Skip if siblings present
            if h.inheritance_type.name == 'FARD_TASIB' and h.sihaam > 0:
                if h.name == "أب":
                    # Father always takes remainder
                    pass  # Include
                elif h.name in ("جد", "أب الأب", "أب أب الأب") and has_siblings:
                    # Grandfather skips if siblings will take remainder
                    continue
                # Otherwise include
            
            active_residuaries.append(h)
        
        if not active_residuaries:
            return 1
        
        # Sort by priority
        active_residuaries.sort(key=lambda h: h.heir_type.tasib_priority)
        
        # Group residuaries by category
        descendants = [h for h in active_residuaries if h.heir_type.category == HeirCategory.DESCENDANT]
        siblings = [h for h in active_residuaries if h.heir_type.category == HeirCategory.SIBLING]
        grandfathers = [h for h in active_residuaries if h.name in ("جد", "أب الأب", "أب أب الأب")]
        others = [h for h in active_residuaries 
                  if h.heir_type.category not in (HeirCategory.DESCENDANT, HeirCategory.SIBLING) 
                  and h.name not in ("جد", "أب الأب", "أب أب الأب")]
        
        # Determine top residuary group based on priority
        top_residuaries = []
        
        if descendants:
            top_residuaries = descendants
        elif grandfathers and siblings:
            # Special Grandfather + Siblings Case (المقاسمة)
            # This only applies when grandfather doesn't already have a fixed share
            return self._solve_grandfather_case(all_heirs, grandfathers, siblings, remainder, base)
        elif siblings:
            # Find highest priority sibling group by RELATION
            # Important: Sisters of same relation inherit WITH brothers as عصبة بالغير
            # We group by RELATION (full/paternal/maternal), not by tasib_priority
            siblings.sort(key=lambda h: h.heir_type.tasib_priority)
            highest_priority = siblings[0].heir_type.tasib_priority
            relation = siblings[0].heir_type.relation
            
            # Include ALL siblings of same relation (brothers AND sisters)
            # This implements عصبة بالغير - sisters become residuary with brothers
            top_residuaries = [h for h in siblings 
                               if h.heir_type.relation == relation]
        elif grandfathers:
            top_residuaries = grandfathers
        elif others:
            # Take highest priority uncle/cousin
            first_priority = others[0].heir_type.tasib_priority
            top_residuaries = [h for h in others if h.heir_type.tasib_priority == first_priority]
        
        if not top_residuaries:
            return 1
                
        # Simple weighted distribution (2:1 male:female)
        # No base multiplication here - Tashih will handle per-head correction
        return self._distribute_weighted_simple(top_residuaries, remainder, all_heirs, base)

    def _distribute_weighted_simple(self, recipients: List[Heir], remainder: int, 
                                     all_heirs: List[Heir], base: int) -> int:
        """
        Distribute remainder to recipients.
        
        Logic:
        - If all recipients are same gender: divide by total HEAD count
        - If mixed genders: use 2:1 male:female WEIGHT ratio × count
        
        IMPORTANT: Per-head integer division is Tashih's job, not ours.
        We only multiply if the group distribution requires it.
        """
        if not recipients:
            return 1
        
        # Check if mixed genders
        genders = set(h.heir_type.gender for h in recipients)
        is_mixed = len(genders) > 1
        
        if is_mixed:
            # Mixed genders: each group's weight = count × gender_weight
            # Son weight = count × 2, Daughter weight = count × 1
            total_weight = sum(
                h.count * (2 if h.heir_type.gender == Gender.MALE else 1) 
                for h in recipients
            )
        else:
            # Same gender: distribute equally by head count (group total)
            total_weight = sum(h.count for h in recipients)
        
        if total_weight == 0:
            return 1
        
        multiplier = 1
        
        # Check if we need to multiply to make remainder divisible
        if remainder % total_weight != 0:
            g = gcd(remainder, total_weight)
            needed_factor = total_weight // g
            multiplier = needed_factor
            
            # Apply multiplier to ALL existing shares
            for h in all_heirs:
                if not h.is_blocked:
                    h.sihaam *= multiplier
            remainder *= multiplier
        
        # Now distribute
        unit = remainder // total_weight
        
        if is_mixed:
            # Mixed: each heir GROUP gets unit × (count × gender_weight)
            for h in recipients:
                gender_weight = 2 if h.heir_type.gender == Gender.MALE else 1
                h.sihaam += unit * h.count * gender_weight
        else:
            # Same gender: each heir group gets unit × count
            for h in recipients:
                h.sihaam += unit * h.count
        
        return multiplier

    def _solve_grandfather_case(self, all_heirs: List[Heir], grandfathers: List[Heir], 
                                 siblings: List[Heir], remainder: int, base: int) -> int:
        """
        Solve Grandfather + Siblings case using Best of 3/2 optimization.
        
        With female descendants: Best of (1/6 estate, 1/3 remainder, muqasama)
        Without female descendants: Best of (1/3 estate, muqasama)
        """
        # Check for female descendants
        has_female_desc = any(h for h in all_heirs if not h.is_blocked and 
                              h.name in ("بنت", "بنت ابن", "بنت ابن ابن", "بنت ابن ابن ابن"))
        
        grandfather = grandfathers[0]  # Assume one grandfather
        
        # Calculate options using Fraction for precision
        f_base = Fraction(base, 1)
        f_remainder = Fraction(remainder, 1)
        
        # Calculate muqasama share
        gf_weight = 2
        sib_weight = sum(2 if s.heir_type.gender == Gender.MALE else 1 for s in siblings)
        total_weight = gf_weight + sib_weight
        
        muqasama_share = f_remainder * Fraction(gf_weight, total_weight) if total_weight > 0 else Fraction(0, 1)
        
        if has_female_desc:
            # Best of 3: (1/6 estate, 1/3 remainder, muqasama)
            opt_sixth = f_base * Fraction(1, 6)
            opt_third_rem = f_remainder * Fraction(1, 3)
            
            options = [
                ('sixth', opt_sixth),
                ('third_remainder', opt_third_rem),
                ('muqasama', muqasama_share)
            ]
            
            best_choice, best_share = max(options, key=lambda x: x[1])
        else:
            # Best of 2: (1/3 estate, muqasama)
            opt_third = f_base * Fraction(1, 3)
            
            options = [
                ('third_estate', opt_third),
                ('muqasama', muqasama_share)
            ]
            
            best_choice, best_share = max(options, key=lambda x: x[1])
        
        # Apply choice
        if best_choice == 'muqasama':
            return self._distribute_weighted_simple(grandfathers + siblings, remainder, all_heirs, base)
        
        # For fixed share options, we need proper multiplier
        multiplier = 1
        
        if best_choice == 'sixth':
            # GF gets 1/6 of base
            if base % 6 != 0:
                m = 6 // gcd(base, 6)
                multiplier = m
                for h in all_heirs:
                    if not h.is_blocked:
                        h.sihaam *= multiplier
                base *= multiplier
                remainder *= multiplier
            
            gf_share = base // 6
            grandfather.sihaam += gf_share
            rem_for_siblings = remainder - gf_share
            
        elif best_choice == 'third_remainder':
            # GF gets 1/3 of remainder
            if remainder % 3 != 0:
                m = 3 // gcd(remainder, 3)
                multiplier = m
                for h in all_heirs:
                    if not h.is_blocked:
                        h.sihaam *= multiplier
                base *= multiplier
                remainder *= multiplier
            
            gf_share = remainder // 3
            grandfather.sihaam += gf_share
            rem_for_siblings = remainder - gf_share
            
        elif best_choice == 'third_estate':
            # GF gets 1/3 of base
            if base % 3 != 0:
                m = 3 // gcd(base, 3)
                multiplier = m
                for h in all_heirs:
                    if not h.is_blocked:
                        h.sihaam *= multiplier
                base *= multiplier
                remainder *= multiplier
            
            gf_share = base // 3
            grandfather.sihaam += gf_share
            rem_for_siblings = remainder - gf_share
        
        # Distribute remaining to siblings
        if siblings and rem_for_siblings > 0:
            sub_m = self._distribute_weighted_simple(siblings, rem_for_siblings, all_heirs, base)
            multiplier *= sub_m
        
        return multiplier
