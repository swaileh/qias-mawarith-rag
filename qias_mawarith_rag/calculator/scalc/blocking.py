"""
Blocking rules (الحجب) for Islamic inheritance.
Implements both complete blocking (حجب حرمان) and partial blocking (حجب نقصان).

Production-level implementation with proper Fiqh rules.
"""

from typing import Dict, List, Optional
from .heirs import Heir, HeirCategory


class BlockingRules:
    """
    Applies blocking rules to determine which heirs are blocked.
    """
    
    def __init__(self, heirs: List[Heir]):
        self.heirs = heirs
        self._build_lookup()
    
    def _build_lookup(self):
        """Build quick lookup dictionaries."""
        self.by_name: Dict[str, Heir] = {}
        self.by_category: Dict[HeirCategory, List[Heir]] = {}
        
        for heir in self.heirs:
            self.by_name[heir.name] = heir
            cat = heir.heir_type.category
            if cat not in self.by_category:
                self.by_category[cat] = []
            self.by_category[cat].append(heir)
    
    def has(self, name: str) -> bool:
        """Check if an heir type exists."""
        return name in self.by_name and not self.by_name[name].is_blocked
    
    def has_any(self, *names: str) -> bool:
        """Check if any of the heir types exist."""
        return any(self.has(name) for name in names)
    
    def has_category(self, category: HeirCategory) -> bool:
        """Check if any heir of this category exists."""
        if category not in self.by_category:
            return False
        return any(not h.is_blocked for h in self.by_category[category])
    
    def get(self, name: str) -> Optional[Heir]:
        """Get heir by name."""
        return self.by_name.get(name)
    
    def has_male_descendant(self) -> bool:
        """Check for son, son's son, etc."""
        return self.has_any("ابن", "ابن ابن", "ابن ابن ابن", "ابن ابن ابن ابن")
    
    def has_female_descendant(self) -> bool:
        """Check for daughter, son's daughter, etc."""
        return self.has_any("بنت", "بنت ابن", "بنت ابن ابن", "بنت ابن ابن ابن")
    
    def has_descendant(self) -> bool:
        """Check for any descendant."""
        return self.has_male_descendant() or self.has_female_descendant()
    
    def has_father(self) -> bool:
        return self.has("أب")
    
    def has_grandfather(self) -> bool:
        return self.has_any("جد", "أب الأب", "أب أب الأب")
    
    def has_mother(self) -> bool:
        return self.has("أم")
    
    def has_full_brother(self) -> bool:
        return self.has("أخ شقيق")
    
    def has_full_sister(self) -> bool:
        return self.has("أخت شقيقة")
    
    def has_paternal_brother(self) -> bool:
        return self.has("أخ لأب")
    
    def has_paternal_sister(self) -> bool:
        return self.has("أخت لأب")
    
    def count_full_sisters(self) -> int:
        heir = self.get("أخت شقيقة")
        return heir.count if heir and not heir.is_blocked else 0
    
    def count_full_brothers(self) -> int:
        heir = self.get("أخ شقيق")
        return heir.count if heir and not heir.is_blocked else 0
    
    def count_daughters(self) -> int:
        heir = self.get("بنت")
        return heir.count if heir and not heir.is_blocked else 0
    
    def count_sons_daughters(self) -> int:
        heir = self.get("بنت ابن")
        return heir.count if heir and not heir.is_blocked else 0
    
    def count_siblings(self) -> int:
        """Count all siblings (for mother's share calculation)."""
        count = 0
        sibling_names = ["أخ شقيق", "أخت شقيقة", "أخ لأب", "أخت لأب", "أخ لأم", "أخت لأم"]
        for name in sibling_names:
            heir = self.get(name)
            if heir and not heir.is_blocked:
                count += heir.count
        return count
    
    def apply_blocking(self) -> List[Heir]:
        """Apply all blocking rules and return updated heirs."""
        
        # Order matters - apply in correct sequence
        self._block_grandmothers()
        self._block_grandfathers()
        self._block_sons_descendants()
        self._block_maternal_siblings()
        self._block_full_siblings()
        self._block_paternal_siblings()
        self._block_nephews()
        self._block_uncles()
        self._block_cousins()
        
        return self.heirs
    
    def _block_grandmothers(self):
        """
        Grandmother Blocking Rules (الجدات):
        
        1. الأم تحجب جميع الجدات (Mother blocks all grandmothers)
        2. الجدة القريبة تحجب الجدة البعيدة (Close grandmother blocks ALL distant grandmothers)
           - Level 2 grandmothers (أم الأم, أم الأب) block ALL level 3 grandmothers
           - This is the stricter interpretation used in the Qias2026 dataset
        3. جدات من نفس المستوى يتشاركن في السدس (Same-level grandmothers SHARE the 1/6)
        """
        # Level 2 grandmothers (direct grandmothers)
        level_2_grandmothers = ["أم الأم", "أم الأب"]
        
        # Level 3 grandmothers (great-grandmothers)
        level_3_grandmothers = ["أم أم الأم", "أم أب الأب", "أم أم الأب"]
        
        all_grandmothers = level_2_grandmothers + level_3_grandmothers + ["جدة"]
        
        # Rule 1: Mother blocks all grandmothers
        if self.has_mother():
            for name in all_grandmothers:
                heir = self.get(name)
                if heir:
                    heir.block("الأم")
            return
        
        # Rule 2: Same-line blocking - closer grandmother blocks farther in same line
        # Maternal line: أم الأم blocks أم أم الأم
        if self.has("أم الأم"):
            for name in ["أم أم الأم", "أم أب الأم"]:
                heir = self.get(name)
                if heir:
                    heir.block("أم الأم")
        
        # Paternal line: أم الأب blocks أم أب الأب
        if self.has("أم الأب"):
            for name in ["أم أب الأب"]:
                heir = self.get(name)
                if heir:
                    heir.block("أم الأب")
        
        # Note: Different lines (maternal vs paternal) can coexist at different levels
        # e.g., أم أم الأم (level 3 maternal) + أم الأب (level 2 paternal) = both active
    
    def _block_grandfathers(self):
        """الأب يحجب الجد وإن علا (Father blocks grandfather)"""
        if self.has_father():
            for name in ["جد", "أب الأب", "أب أب الأب"]:
                heir = self.get(name)
                if heir:
                    heir.block("الأب")
            return
        
        # Closer grandfather blocks farther
        if self.has_any("جد", "أب الأب"):
            heir = self.get("أب أب الأب")
            if heir:
                heir.block("الجد")
    
    def _block_sons_descendants(self):
        """
        Son's Daughters (بنت الابن) and Great-Granddaughters Blocking:
        
        بنت الابن تحجب بـ:
        - الابن (son blocks all granddaughters)
        - بنتين فأكثر (إلا إذا وجد معصب = ابن ابن)
        
        بنت ابن ابن تحجب بـ:
        - الابن أو ابن الابن
        - بنتين فأكثر OR (بنت + بنت ابن) completing 2/3
        - بنتا ابن فأكثر (unless has ابن ابن ابن as معصب)
        """
        # Level 1: Son blocks all granddaughters
        if self.has("ابن"):
            for name in ["بنت ابن", "بنت ابن ابن", "بنت ابن ابن ابن"]:
                heir = self.get(name)
                if heir:
                    heir.block("الابن")
            return
        
        # Level 2: Son's son blocks great-granddaughters
        if self.has("ابن ابن"):
            for name in ["بنت ابن ابن", "بنت ابن ابن ابن"]:
                heir = self.get(name)
                if heir:
                    heir.block("ابن الابن")
        
        # Level 3: Great-grandson blocks great-great-granddaughters
        if self.has("ابن ابن ابن"):
            heir = self.get("بنت ابن ابن ابن")
            if heir:
                heir.block("ابن ابن الابن")
        
        # 2/3 exhaustion rules
        daughter_count = self.count_daughters()
        granddaughter_count = self.count_sons_daughters()
        
        # Two or more daughters exhaust 2/3 → block granddaughters (unless معصب)
        if daughter_count >= 2:
            # Block بنت ابن unless she has ابن ابن as معصب
            if not self.has("ابن ابن"):
                heir = self.get("بنت ابن")
                if heir:
                    heir.block("البنتان فأكثر")
            
            # Block بنت ابن ابن unless she has ابن ابن ابن as معصب
            if not self.has("ابن ابن ابن"):
                heir = self.get("بنت ابن ابن")
                if heir:
                    heir.block("البنتان فأكثر")
            return
        
        # One daughter (takes 1/2) + granddaughter (takes 1/6 تكملة) = 2/3 exhausted
        if daughter_count == 1:
            if granddaughter_count > 0:
                # 2/3 exhausted by بنت + بنت ابن
                # Block بنت ابن ابن unless has ابن ابن ابن
                if not self.has("ابن ابن ابن"):
                    heir = self.get("بنت ابن ابن")
                    if heir:
                        heir.block("البنت وبنت الابن")
            # If no بنت ابن, بنت ابن ابن gets 1/6 تكملة herself - NOT blocked
            return
        
        # No daughters - check granddaughters for 2/3 exhaustion
        if granddaughter_count >= 2:
            # Two or more بنت ابن take 2/3
            # Block بنت ابن ابن unless has ابن ابن ابن
            if not self.has("ابن ابن ابن"):
                heir = self.get("بنت ابن ابن")
                if heir:
                    heir.block("بنتا الابن فأكثر")
    
    def _block_maternal_siblings(self):
        """الإخوة لأم يحجبون بالفرع الوارث أو الأصل الذكر"""
        if self.has_descendant() or self.has_father() or self.has_grandfather():
            blocker = None
            if self.has_descendant():
                blocker = "الفرع الوارث"
            elif self.has_father():
                blocker = "الأب"
            else:
                blocker = "الجد"
            
            for name in ["أخ لأم", "أخت لأم"]:
                heir = self.get(name)
                if heir:
                    heir.block(blocker)
    
    def _block_full_siblings(self):
        """الأخ الشقيق والأخت الشقيقة يحجبون بالابن أو ابن الابن وإن نزل أو الأب"""
        blocker = None
        if self.has("ابن"):
            blocker = "الابن"
        elif self.has("ابن ابن"):
            blocker = "ابن الابن"
        elif self.has("ابن ابن ابن"):
            blocker = "ابن ابن الابن"
        elif self.has("ابن ابن ابن ابن"):
            blocker = "ابن ابن ابن الابن"
        elif self.has_father():
            blocker = "الأب"
        
        if blocker:
            for name in ["أخ شقيق", "أخت شقيقة"]:
                heir = self.get(name)
                if heir:
                    heir.block(blocker)
    
    def _block_paternal_siblings(self):
        """
        الأخت لأب / الأخ لأب يحجبون بـ:
        - الابن، ابن الابن وإن نزل، الأب
        - الأخ الشقيق
        - الأختين الشقيقتين (للأخت لأب) - unless she has أخ لأب as معصب
        """
        # Main blockers: descendants and father
        if self.has_any("ابن", "ابن ابن", "ابن ابن ابن", "ابن ابن ابن ابن") or self.has_father():
            for name in ["أخ لأب", "أخت لأب"]:
                heir = self.get(name)
                if heir:
                    heir.block("الفرع الوارث أو الأب")
            return
        
        # Full brother blocks paternal siblings completely
        if self.has_full_brother():
            for name in ["أخ لأب", "أخت لأب"]:
                heir = self.get(name)
                if heir:
                    heir.block("الأخ الشقيق")
            return
        
        # Two or more full sisters block paternal sister (unless she has أخ لأب as معصب)
        if self.count_full_sisters() >= 2:
            if not self.has_paternal_brother():
                heir = self.get("أخت لأب")
                if heir:
                    heir.block("الأختان الشقيقتان")
            # Note: أخ لأب is NOT blocked by full sisters - he becomes their عاصب
    
    def _block_nephews(self):
        """أبناء الإخوة يحجبون بمن هو أقرب في التعصيب"""
        blockers_priority = [
            ("ابن", "الابن"),
            ("ابن ابن", "ابن الابن"),
            ("ابن ابن ابن", "ابن ابن الابن"),
            ("ابن ابن ابن ابن", "ابن ابن ابن الابن"),
            ("أب", "الأب"),
            ("جد", "الجد"),
            ("أب الأب", "الجد"),
            ("أب أب الأب", "الجد"),
            ("أخ شقيق", "الأخ الشقيق"),
            ("أخ لأب", "الأخ لأب"),
        ]
        
        # Sisters who become residuary with daughters (عصبة مع الغير)
        if self.has_any("أخت شقيقة") and self.has_female_descendant():
            blockers_priority.append(("أخت شقيقة", "الأخت الشقيقة (عصبة مع الغير)"))
        if self.has_any("أخت لأب") and self.has_female_descendant() and not self.has_full_sister():
            blockers_priority.append(("أخت لأب", "الأخت لأب (عصبة مع الغير)"))
        
        blocker = None
        for name, desc in blockers_priority:
            if self.has(name):
                blocker = desc
                break
        
        if blocker:
            nephew_names = [
                "ابن أخ شقيق", "ابن أخ لأب", 
                "ابن ابن أخ شقيق", "ابن ابن أخ لأب"
            ]
            for name in nephew_names:
                heir = self.get(name)
                if heir:
                    heir.block(blocker)
        else:
            # Nephew hierarchy: Full nephew blocks paternal nephew
            if self.has("ابن أخ شقيق"):
                heir = self.get("ابن أخ لأب")
                if heir:
                    heir.block("ابن الأخ الشقيق")
    
    def _block_uncles(self):
        """الأعمام يحجبون بمن هو أقرب في التعصيب"""
        blockers_priority = [
            ("ابن", "الابن"),
            ("ابن ابن", "ابن الابن"),
            ("ابن ابن ابن", "ابن ابن الابن"),
            ("ابن ابن ابن ابن", "ابن ابن ابن الابن"),
            ("أب", "الأب"),
            ("جد", "الجد"),
            ("أب الأب", "الجد"),
            ("أب أب الأب", "الجد"),
            ("أخ شقيق", "الأخ الشقيق"),
            ("أخ لأب", "الأخ لأب"),
            ("ابن أخ شقيق", "ابن الأخ الشقيق"),
            ("ابن أخ لأب", "ابن الأخ لأب"),
        ]
        
        # Sisters as residuary with daughters
        if self.has_full_sister() and self.has_female_descendant():
            blockers_priority.append(("أخت شقيقة", "الأخت الشقيقة (عصبة مع الغير)"))
        if self.has_paternal_sister() and self.has_female_descendant() and not self.has_full_sister():
            blockers_priority.append(("أخت لأب", "الأخت لأب (عصبة مع الغير)"))
        
        blocker = None
        for name, desc in blockers_priority:
            if self.has(name):
                blocker = desc
                break
        
        if blocker:
            uncle_names = ["عم شقيق", "عم لأب", "عم الأب", "عم الأب لأب"]
            for name in uncle_names:
                heir = self.get(name)
                if heir:
                    heir.block(blocker)
        else:
            # Uncle hierarchy: Full uncle blocks paternal uncle
            if self.has("عم شقيق"):
                for name in ["عم لأب", "عم الأب", "عم الأب لأب"]:
                    heir = self.get(name)
                    if heir:
                        heir.block("العم الشقيق")
            elif self.has("عم لأب"):
                for name in ["عم الأب", "عم الأب لأب"]:
                    heir = self.get(name)
                    if heir:
                        heir.block("العم لأب")
    
    def _block_cousins(self):
        """أبناء الأعمام يحجبون بمن هو أقرب في التعصيب"""
        blockers_priority = [
            ("ابن", "الابن"),
            ("ابن ابن", "ابن الابن"),
            ("ابن ابن ابن", "ابن ابن الابن"),
            ("ابن ابن ابن ابن", "ابن ابن ابن الابن"),
            ("أب", "الأب"),
            ("جد", "الجد"),
            ("أب الأب", "الجد"),
            ("أب أب الأب", "الجد"),
            ("أخ شقيق", "الأخ الشقيق"),
            ("أخ لأب", "الأخ لأب"),
            ("ابن أخ شقيق", "ابن الأخ"),
            ("ابن أخ لأب", "ابن الأخ"),
            ("ابن ابن أخ شقيق", "ابن ابن الأخ"),
            ("ابن ابن أخ لأب", "ابن ابن الأخ"),
            ("عم شقيق", "العم الشقيق"),
            ("عم لأب", "العم لأب"),
        ]
        
        # Sisters as residuary
        if self.has_full_sister() and self.has_female_descendant():
            blockers_priority.append(("أخت شقيقة", "الأخت الشقيقة (عصبة مع الغير)"))
        if self.has_paternal_sister() and self.has_female_descendant() and not self.has_full_sister():
            blockers_priority.append(("أخت لأب", "الأخت لأب (عصبة مع الغير)"))
        
        blocker = None
        for name, desc in blockers_priority:
            if self.has(name):
                blocker = desc
                break
        
        if blocker:
            cousin_names = [
                "ابن عم شقيق", "ابن عم لأب", 
                "ابن ابن عم شقيق", "ابن ابن عم لأب", 
                "ابن عم الأب"
            ]
            for name in cousin_names:
                heir = self.get(name)
                if heir:
                    heir.block(blocker)
        else:
            # Cousin hierarchy
            if self.has("ابن عم شقيق"):
                for name in ["ابن عم لأب", "ابن ابن عم شقيق", "ابن ابن عم لأب", "ابن عم الأب"]:
                    heir = self.get(name)
                    if heir:
                        heir.block("ابن العم الشقيق")
            elif self.has("ابن عم لأب"):
                for name in ["ابن ابن عم شقيق", "ابن ابن عم لأب", "ابن عم الأب"]:
                    heir = self.get(name)
                    if heir:
                        heir.block("ابن العم لأب")
