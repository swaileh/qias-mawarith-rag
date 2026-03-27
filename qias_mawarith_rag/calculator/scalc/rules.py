"""
Share calculation rules for each heir type.
Implements the Fiqh rules for determining shares (الفروض).

Production-level implementation with proper Fiqh rules.
"""

from typing import List, Optional, Tuple
from .heirs import Heir, InheritanceType
from .shares import Fraction, HALF, QUARTER, EIGHTH, TWO_THIRDS, THIRD, SIXTH, ZERO


class ShareRules:
    """
    Calculates the share for each heir based on Fiqh rules.
    
    Handles all heir types including:
    - Spouses (زوج، زوجة)
    - Parents (أب، أم)
    - Grandparents (جد، جدة)
    - Children (ابن، بنت)
    - Grandchildren (ابن ابن، بنت ابن، etc.)
    - Siblings (أخ شقيق، أخت شقيقة، etc.)
    - Extended family (uncles, cousins)
    """
    
    # Grandmother types grouped by lineage
    MATERNAL_GRANDMOTHERS = {"أم الأم", "أم أم الأم"}
    PATERNAL_GRANDMOTHERS = {"أم الأب", "أم أب الأب"}
    MIXED_GRANDMOTHERS = {"أم أم الأب"}  # Maternal grandmother of father
    ALL_GRANDMOTHERS = MATERNAL_GRANDMOTHERS | PATERNAL_GRANDMOTHERS | MIXED_GRANDMOTHERS | {"جدة"}
    
    def __init__(self, heirs: List[Heir], blocked_siblings_count: int = 0):
        self.heirs = [h for h in heirs if not h.is_blocked]
        self.blocked_siblings_count = blocked_siblings_count  # For حجب النقصان
        self._build_lookup()
    
    def _build_lookup(self):
        """Build lookup dictionaries."""
        self.by_name = {h.name: h for h in self.heirs}
    
    def has(self, name: str) -> bool:
        return name in self.by_name
    
    def get(self, name: str) -> Optional[Heir]:
        return self.by_name.get(name)
    
    def has_male_descendant(self) -> bool:
        return self.has("ابن") or self.has("ابن ابن") or self.has("ابن ابن ابن") or self.has("ابن ابن ابن ابن")
    
    def has_female_descendant(self) -> bool:
        return (self.has("بنت") or self.has("بنت ابن") or 
                self.has("بنت ابن ابن") or self.has("بنت ابن ابن ابن"))
    
    def has_grandfather(self) -> bool:
        """Check for any grandfather type."""
        return self.has("جد") or self.has("أب الأب") or self.has("أب أب الأب")
    
    def has_descendant(self) -> bool:
        return self.has_male_descendant() or self.has_female_descendant()
    
    def count_siblings(self) -> int:
        count = 0
        for name in ["أخ شقيق", "أخت شقيقة", "أخ لأب", "أخت لأب", "أخ لأم", "أخت لأم"]:
            heir = self.get(name)
            if heir:
                count += heir.count
        return count
    
    def count_daughters(self) -> int:
        heir = self.get("بنت")
        return heir.count if heir else 0
    
    def count_full_sisters(self) -> int:
        heir = self.get("أخت شقيقة")
        return heir.count if heir else 0
    
    def count_grandmothers(self) -> int:
        """Count all active grandmothers (not blocked)."""
        count = 0
        for name in self.ALL_GRANDMOTHERS:
            if self.has(name):
                count += 1
        return count
    
    def get_active_grandmothers(self) -> List[Heir]:
        """Get list of active grandmothers."""
        result = []
        for name in self.ALL_GRANDMOTHERS:
            heir = self.get(name)
            if heir:
                result.append(heir)
        return result
    
    def calculate_shares(self) -> Tuple[List[Heir], List[Heir]]:
        """
        Calculate shares for all heirs.
        Returns: (sharers, residuaries)
        """
        sharers = []
        residuaries = []
        
        # First pass: calculate individual shares
        for heir in self.heirs:
            share, inh_type = self._get_share(heir)
            heir.share_fraction = share
            heir.inheritance_type = inh_type
            
            if inh_type == InheritanceType.FARD:
                sharers.append(heir)
            elif inh_type == InheritanceType.TASIB:
                residuaries.append(heir)
            elif inh_type == InheritanceType.FARD_TASIB:
                sharers.append(heir)
                residuaries.append(heir)
        
        # Second pass: adjust grandmother shares if multiple grandmothers share
        self._adjust_grandmother_shares(sharers)
        
        return sharers, residuaries
    
    def _adjust_grandmother_shares(self, sharers: List[Heir]):
        """
        Adjust grandmother shares when multiple grandmothers exist.
        
        Fiqh Rule: Multiple grandmothers from different lines SHARE the 1/6.
        They don't each get 1/6 - they divide it among themselves.
        
        Example: أم الأم + أم الأب both exist → each gets 1/12 (half of 1/6)
        """
        grandmothers = [h for h in sharers if h.name in self.ALL_GRANDMOTHERS]
        
        if len(grandmothers) <= 1:
            return  # No adjustment needed
        
        # Calculate total grandmother count (considering heir.count for each)
        total_heads = sum(g.count for g in grandmothers)
        
        # Each grandmother group shares the 1/6
        # So each head gets 1/(6 * total_heads)
        for gm in grandmothers:
            # Total share for this grandmother group = (1/6) × (gm.count / total_heads)
            # = gm.count / (6 × total_heads)
            gm.share_fraction = Fraction(gm.count, 6 * total_heads)
    
    def _get_share(self, heir: Heir) -> Tuple[Fraction, InheritanceType]:
        """Get the share for a specific heir."""
        name = heir.name
        
        # Dispatch to specific handlers
        if name == "زوج":
            return self._husband_share()
        elif name in ("زوجة", "زوجـة"):
            return self._wife_share()
        elif name == "أب":
            return self._father_share()
        elif name == "أم":
            return self._mother_share()
        elif name in ("جد", "أب الأب", "أب أب الأب"):
            return self._grandfather_share()
        elif name in self.ALL_GRANDMOTHERS:
            return self._grandmother_share(heir)
        elif name == "بنت":
            return self._daughter_share(heir)
        elif name == "بنت ابن":
            return self._sons_daughter_share(heir)
        elif name in ("بنت ابن ابن", "بنت ابن ابن ابن"):
            return self._sons_sons_daughter_share(heir, name)
        elif name == "ابن":
            return self._son_share()
        elif name in ("ابن ابن", "ابن ابن ابن", "ابن ابن ابن ابن"):
            return self._sons_son_share()
        elif name == "أخت شقيقة":
            return self._full_sister_share(heir)
        elif name == "أخت لأب":
            return self._paternal_sister_share(heir)
        elif name in ("أخ لأم", "أخت لأم"):
            return self._maternal_sibling_share(heir)
        elif name == "أخ شقيق":
            return self._full_brother_share()
        elif name == "أخ لأب":
            return self._paternal_brother_share()
        else:
            # Default to residuary for uncles, nephews, cousins
            return (ZERO, InheritanceType.TASIB)
    
    def _husband_share(self) -> Tuple[Fraction, InheritanceType]:
        """الزوج: نصف أو ربع"""
        if self.has_descendant():
            return (QUARTER, InheritanceType.FARD)
        return (HALF, InheritanceType.FARD)
    
    def _wife_share(self) -> Tuple[Fraction, InheritanceType]:
        """الزوجة: ربع أو ثمن"""
        if self.has_descendant():
            return (EIGHTH, InheritanceType.FARD)
        return (QUARTER, InheritanceType.FARD)
    
    def _father_share(self) -> Tuple[Fraction, InheritanceType]:
        """الأب: سدس مع ابن، سدس + باقي مع بنت، باقي بدون فرع"""
        if self.has_male_descendant():
            return (SIXTH, InheritanceType.FARD)
        elif self.has_female_descendant():
            return (SIXTH, InheritanceType.FARD_TASIB)
        return (ZERO, InheritanceType.TASIB)
    
    def _mother_share(self) -> Tuple[Fraction, InheritanceType]:
        """
        الأم: سدس أو ثلث أو ثلث الباقي (العمريتان)
        
        Cases:
        1. With descendant or 2+ siblings (including blocked) → 1/6
        2. العمريتان with زوج + أب → 1/6 (1/3 of remainder)
        3. العمريتان with زوجة + أب → 1/4 (1/3 of remainder)
        4. Otherwise → 1/3
        """
        # Include blocked siblings for حجب النقصان
        total_siblings = self.count_siblings() + self.blocked_siblings_count
        if self.has_descendant() or total_siblings >= 2:
            return (SIXTH, InheritanceType.FARD)
        
        # Check for العمريتان (special cases with spouse + parents only)
        heirs_set = set(self.by_name.keys())
        
        # Case 1: زوج + أب + أم = Wife's half + mother's 1/3 of remainder = 1/6
        if heirs_set == {"زوج", "أب", "أم"}:
            return (SIXTH, InheritanceType.FARD)
        
        # Case 2: زوجة + أب + أم = Wife's 1/4 + mother's 1/3 of remainder = 1/4
        if heirs_set == {"زوجة", "أب", "أم"} or heirs_set == {"زوجـة", "أب", "أم"}:
            return (QUARTER, InheritanceType.FARD)
        
        return (THIRD, InheritanceType.FARD)
    
    def _grandfather_share(self) -> Tuple[Fraction, InheritanceType]:
        """
        الجد: مثل الأب مع بعض الاختلافات
        
        With male descendant → 1/6 (fard)
        With siblings (with or without female descendants) → Best of 3 options
        With female descendant only (no siblings) → 1/6 + residuary (fard+tasib)
        Otherwise → Pure residuary
        """
        if self.has_male_descendant():
            return (SIXTH, InheritanceType.FARD)
        
        # Check for siblings - Grandfather with siblings gets Best-of-3
        def count_heir(name):
            h = self.get(name)
            return h.count if h else 0
        
        full_siblings = count_heir("أخ شقيق") + count_heir("أخت شقيقة")
        paternal_siblings = count_heir("أخ لأب") + count_heir("أخت لأب")
        
        if full_siblings > 0 or paternal_siblings > 0:
            # Best of 3 options for Grandfather with siblings:
            # 1. السدس (1/6)
            # 2. ثلث الباقي (1/3 of remainder after other fixed shares)
            # 3. المقاسمة (sharing as if grandfather were a sibling)
            
            # Count effective sibling shares (males = 2, females = 1)
            sibling_shares = 0
            for name in ["أخ شقيق", "أخ لأب"]:
                h = self.get(name)
                if h:
                    sibling_shares += h.count * 2  # Male = 2 shares
            for name in ["أخت شقيقة", "أخت لأب"]:
                h = self.get(name)
                if h:
                    sibling_shares += h.count * 1  # Female = 1 share
            
            # Calculate fixed shares for spouse/mother (to find remainder)
            spouse_share = ZERO
            for name in ["زوج", "زوجة", "زوجـة"]:
                h = self.get(name)
                if h:
                    if name == "زوج":
                        spouse_share = HALF  # Husband without descendants
                    else:
                        spouse_share = QUARTER  # Wife without descendants
            
            mother_share = ZERO
            if self.has("أم"):
                # Mother with siblings gets 1/6, otherwise 1/3
                if full_siblings + paternal_siblings >= 2:
                    mother_share = SIXTH
                else:
                    mother_share = THIRD
            
            # Grandmother always gets 1/6 if present (and not blocked by mother)
            grandmother_share = ZERO
            if not self.has("أم"):  # Grandmother is blocked by mother
                for gm_name in ["أم الأم", "أم الأب", "أم أم الأم", "أم أم الأب", "أم أب الأب"]:
                    if self.has(gm_name):
                        grandmother_share = SIXTH
                        break  # Only 1/6 total even with multiple grandmothers
            
            # Female descendants get their Fard share
            daughter_share = ZERO
            daughter_count = count_heir("بنت")
            if daughter_count > 0:
                if daughter_count == 1:
                    daughter_share = HALF
                else:
                    daughter_share = TWO_THIRDS
            
            # Granddaughters (بنت ابن) get 1/6 completion after daughters, or their own share
            granddaughter_share = ZERO
            granddaughter_count = count_heir("بنت ابن") + count_heir("بنت ابن ابن")
            if granddaughter_count > 0:
                if daughter_count >= 2:
                    pass  # 2+ daughters = 2/3, granddaughters blocked
                elif daughter_count == 1:
                    granddaughter_share = SIXTH  # Complete the 2/3
                else:
                    if granddaughter_count == 1:
                        granddaughter_share = HALF
                    else:
                        granddaughter_share = TWO_THIRDS
            
            remainder = Fraction(1, 1) - spouse_share - mother_share - grandmother_share - daughter_share - granddaughter_share
            
            # Option 1: 1/6
            opt1 = SIXTH
            
            # Option 2: 1/3 of remainder
            opt2 = remainder * Fraction(1, 3)
            
            # Option 3: Muqasama (grandfather = 2 shares like a male sibling)
            total_shares = sibling_shares + 2  # GF = 2 shares
            opt3 = remainder * Fraction(2, total_shares)
            
            # Best option for grandfather
            best = max(opt1, opt2, opt3)
            
            # Return best share as FARD so Tashih works correctly
            return (best, InheritanceType.FARD)
        
        # No siblings - check for female descendants
        if self.has_female_descendant():
            # With female descendant only (no siblings) → 1/6 + residuary (fard+tasib)
            return (SIXTH, InheritanceType.FARD_TASIB)
        
        # No siblings, no descendants - Grandfather is pure residuary
        return (ZERO, InheritanceType.TASIB)
    
    def _grandmother_share(self, heir: Heir) -> Tuple[Fraction, InheritanceType]:
        """
        الجدة: سدس (shared if multiple)
        
        Note: Actual sharing is handled in _adjust_grandmother_shares()
        """
        return (SIXTH, InheritanceType.FARD)
    
    def _daughter_share(self, heir: Heir) -> Tuple[Fraction, InheritanceType]:
        """البنت: نصف أو ثلثان أو عصبة بالغير"""
        if self.has("ابن"):
            # With son, becomes residuary (2:1 ratio)
            return (ZERO, InheritanceType.TASIB)
        elif heir.count == 1:
            return (HALF, InheritanceType.FARD)
        else:  # 2+
            return (TWO_THIRDS, InheritanceType.FARD)
    
    def _sons_daughter_share(self, heir: Heir) -> Tuple[Fraction, InheritanceType]:
        """بنت الابن: نصف، ثلثان، سدس تكملة، أو عصبة"""
        if self.has("ابن ابن"):
            return (ZERO, InheritanceType.TASIB)
        
        daughters = self.count_daughters()
        if daughters == 0:
            if heir.count == 1:
                return (HALF, InheritanceType.FARD)
            else:
                return (TWO_THIRDS, InheritanceType.FARD)
        elif daughters == 1:
            # تكملة الثلثين
            return (SIXTH, InheritanceType.FARD)
        else:
            # Should be blocked, but handle edge case
            return (ZERO, InheritanceType.BLOCKED)
    
    def _sons_sons_daughter_share(self, heir: Heir, name: str) -> Tuple[Fraction, InheritanceType]:
        """بنت ابن الابن وما دونها: similar logic, deeper level"""
        # Check for male at same level
        male_counterpart = name.replace("بنت", "ابن")  # e.g., "ابن ابن ابن"
        if self.has(male_counterpart):
            return (ZERO, InheritanceType.TASIB)
        
        # Check higher level daughters
        daughters = self.count_daughters()
        sons_daughters = self.get("بنت ابن")
        num_sons_daughters = sons_daughters.count if sons_daughters else 0
        
        # If no higher-level females got shares, this heir gets share
        if daughters == 0 and num_sons_daughters == 0:
            if heir.count == 1:
                return (HALF, InheritanceType.FARD)
            else:
                return (TWO_THIRDS, InheritanceType.FARD)
        
        # Check if 2/3 is already exhausted
        higher_female_shares = 0
        if daughters == 1:
            higher_female_shares = 1  # 1/2 taken
        elif daughters >= 2:
            higher_female_shares = 2  # 2/3 taken
        
        if num_sons_daughters == 1 and daughters == 0:
            higher_female_shares = 1  # 1/2 taken
        elif num_sons_daughters >= 2 and daughters == 0:
            higher_female_shares = 2  # 2/3 taken
        elif num_sons_daughters > 0 and daughters == 1:
            higher_female_shares = 2  # 1/2 + 1/6 = 2/3 taken
        
        if higher_female_shares == 1:
            # تكملة الثلثين
            return (SIXTH, InheritanceType.FARD)
        elif higher_female_shares >= 2:
            # 2/3 exhausted - should be blocked
            return (ZERO, InheritanceType.BLOCKED)
        
        return (ZERO, InheritanceType.BLOCKED)
    
    def _son_share(self) -> Tuple[Fraction, InheritanceType]:
        """الابن: عصبة بالنفس"""
        return (ZERO, InheritanceType.TASIB)
    
    def _sons_son_share(self) -> Tuple[Fraction, InheritanceType]:
        """ابن الابن وما دونه: عصبة بالنفس"""
        return (ZERO, InheritanceType.TASIB)
    
    def _full_sister_share(self, heir: Heir) -> Tuple[Fraction, InheritanceType]:
        """الأخت الشقيقة"""
        # With full brother -> residuary
        if self.has("أخ شقيق"):
            return (ZERO, InheritanceType.TASIB)
        
        # With female descendant -> عصبة مع الغير
        if self.has_female_descendant():
            return (ZERO, InheritanceType.TASIB)
        
        # With grandfather (no father) -> معاقسمة مع الجد
        # BUT: If paternal siblings also exist, full sisters keep their فرض
        # Muqasama only applies when GF + same-relation siblings only
        if self.has_grandfather() and not self.has("أب"):
            # Check if paternal siblings exist - if so, full sisters get فرض
            has_paternal_siblings = self.has("أخ لأب") or self.has("أخت لأب")
            if not has_paternal_siblings:
                return (ZERO, InheritanceType.TASIB)
        
        # As sharer
        if heir.count == 1:
            return (HALF, InheritanceType.FARD)
        else:
            return (TWO_THIRDS, InheritanceType.FARD)
    
    def _paternal_sister_share(self, heir: Heir) -> Tuple[Fraction, InheritanceType]:
        """الأخت لأب"""
        # With paternal brother -> residuary
        if self.has("أخ لأب"):
            return (ZERO, InheritanceType.TASIB)
        
        # With female descendant -> عصبة مع الغير
        if self.has_female_descendant():
            return (ZERO, InheritanceType.TASIB)
        
        # With grandfather (no father) -> معاقسمة مع الجد
        if self.has_grandfather() and not self.has("أب"):
            return (ZERO, InheritanceType.TASIB)
        
        # With one full sister -> تكملة الثلثين
        full_sisters = self.count_full_sisters()
        if full_sisters == 1:
            return (SIXTH, InheritanceType.FARD)
        elif full_sisters >= 2:
            return (ZERO, InheritanceType.BLOCKED)
        
        # Alone as sharer
        if heir.count == 1:
            return (HALF, InheritanceType.FARD)
        else:
            return (TWO_THIRDS, InheritanceType.FARD)
    
    def _maternal_sibling_share(self, heir: Heir) -> Tuple[Fraction, InheritanceType]:
        """
        الإخوة لأم: one gets 1/6, two or more SHARE 1/3 equally
        
        IMPORTANT: Maternal siblings share their portion EQUALLY regardless of gender.
        When there are multiple maternal siblings (brothers and/or sisters), they
        divide 1/3 equally by head count.
        """
        # Count all maternal siblings (both types)
        total_maternal = 0
        for name in ["أخ لأم", "أخت لأم"]:
            h = self.get(name)
            if h:
                total_maternal += h.count
        
        if total_maternal == 1:
            # Single maternal sibling gets 1/6
            return (SIXTH, InheritanceType.FARD)
        else:
            # Multiple: they SHARE 1/3 total
            # This heir's share = (1/3) × (their_count / total_count)
            their_share = Fraction(1, 3) * Fraction(heir.count, total_maternal)
            return (their_share, InheritanceType.FARD)
    
    def _full_brother_share(self) -> Tuple[Fraction, InheritanceType]:
        """الأخ الشقيق: عصبة"""
        return (ZERO, InheritanceType.TASIB)
    
    def _paternal_brother_share(self) -> Tuple[Fraction, InheritanceType]:
        """الأخ لأب: عصبة"""
        return (ZERO, InheritanceType.TASIB)
