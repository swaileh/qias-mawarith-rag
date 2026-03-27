"""
Heir types and definitions for Islamic inheritance.

Production-level implementation with comprehensive heir type registry.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List, Dict
from .shares import Fraction, ZERO


class HeirCategory(Enum):
    """Categories of heirs in Islamic inheritance."""
    SPOUSE = auto()      # الزوجية
    DESCENDANT = auto()  # الفروع
    ASCENDANT = auto()   # الأصول
    SIBLING = auto()     # الإخوة
    UNCLE = auto()       # الأعمام
    COUSIN = auto()      # أبناء الأعمام


class Gender(Enum):
    MALE = "M"
    FEMALE = "F"


class InheritanceType(Enum):
    """Type of inheritance claim."""
    FARD = auto()        # فرض - Fixed share
    TASIB = auto()       # تعصيب - Residuary
    FARD_TASIB = auto()  # فرض + تعصيب
    BLOCKED = auto()     # محجوب - Blocked


class Relation(Enum):
    """Sibling/Uncle relation type."""
    FULL = "شقيق"        # Same father and mother
    PATERNAL = "لأب"     # Same father only
    MATERNAL = "لأم"     # Same mother only


@dataclass
class HeirType:
    """Definition of an heir type with its properties."""
    name_ar: str
    name_en: str
    category: HeirCategory
    gender: Gender
    level: int = 1  # Generational level (1=child, 2=grandchild, etc.)
    relation: Optional[Relation] = None
    
    # Priority for residuary inheritance (lower = higher priority)
    tasib_priority: int = 999
    
    def __hash__(self):
        return hash(self.name_ar)
    
    def __eq__(self, other):
        if isinstance(other, HeirType):
            return self.name_ar == other.name_ar
        return False


@dataclass
class Heir:
    """
    Represents an actual heir in an inheritance case.
    """
    heir_type: HeirType
    count: int = 1
    original_name: str = ""  # Preserve input name for output
    
    # Calculated values
    inheritance_type: InheritanceType = InheritanceType.FARD
    share_fraction: Fraction = field(default_factory=lambda: ZERO)
    sihaam: int = 0  # Total shares for this heir group
    per_head_sihaam: int = 0  # Shares per individual
    per_head_fraction: Fraction = field(default_factory=lambda: ZERO)
    percentage: float = 0.0
    blocked_by: Optional[str] = None
    
    @property
    def name(self) -> str:
        return self.heir_type.name_ar
    
    @property
    def is_blocked(self) -> bool:
        return self.inheritance_type == InheritanceType.BLOCKED
    
    @property
    def is_residuary(self) -> bool:
        return self.inheritance_type in (InheritanceType.TASIB, InheritanceType.FARD_TASIB)
    
    def block(self, by: str):
        """Mark this heir as blocked."""
        self.inheritance_type = InheritanceType.BLOCKED
        self.blocked_by = by
        self.share_fraction = ZERO
        self.sihaam = 0
        self.per_head_sihaam = 0
        self.per_head_fraction = ZERO
        self.percentage = 0.0

    @classmethod
    def from_list(cls, heirs_data: List[dict]) -> List[Heir]:
        """Create a list of Heir objects from input data."""
        heirs = []
        for data in heirs_data:
            name = data.get("heir")
            count = data.get("count", 1)
            heir = create_heir(name, count)
            if heir:
                heirs.append(heir)
        return heirs


# ===========================================================================
# HEIR TYPE REGISTRY
# ===========================================================================

HEIR_TYPES: Dict[str, HeirType] = {}


def register_heir(
    name_ar: str,
    name_en: str,
    category: HeirCategory,
    gender: Gender,
    level: int = 1,
    relation: Optional[Relation] = None,
    tasib_priority: int = 999,
    aliases: Optional[List[str]] = None
) -> HeirType:
    """Register an heir type with optional aliases."""
    heir_type = HeirType(
        name_ar=name_ar,
        name_en=name_en,
        category=category,
        gender=gender,
        level=level,
        relation=relation,
        tasib_priority=tasib_priority
    )
    HEIR_TYPES[name_ar] = heir_type
    if aliases:
        for alias in aliases:
            HEIR_TYPES[alias] = heir_type
    return heir_type


# ===========================================================================
# SPOUSE (الزوجية)
# ===========================================================================
register_heir("زوج", "Husband", HeirCategory.SPOUSE, Gender.MALE)
register_heir("زوجة", "Wife", HeirCategory.SPOUSE, Gender.FEMALE, aliases=["زوجـة"])


# ===========================================================================
# DESCENDANTS (الفروع) - Up to 4 levels
# ===========================================================================
# Level 1: Children
register_heir("ابن", "Son", HeirCategory.DESCENDANT, Gender.MALE, level=1, tasib_priority=1)
register_heir("بنت", "Daughter", HeirCategory.DESCENDANT, Gender.FEMALE, level=1)

# Level 2: Grandchildren
register_heir("ابن ابن", "Son's Son", HeirCategory.DESCENDANT, Gender.MALE, level=2, tasib_priority=2)
register_heir("بنت ابن", "Son's Daughter", HeirCategory.DESCENDANT, Gender.FEMALE, level=2)

# Level 3: Great-grandchildren
register_heir("ابن ابن ابن", "Son's Son's Son", HeirCategory.DESCENDANT, Gender.MALE, level=3, tasib_priority=3)
register_heir("بنت ابن ابن", "Son's Son's Daughter", HeirCategory.DESCENDANT, Gender.FEMALE, level=3)

# Level 4: Great-great-grandchildren
register_heir("ابن ابن ابن ابن", "Son's Son's Son's Son", HeirCategory.DESCENDANT, Gender.MALE, level=4, tasib_priority=4)
register_heir("بنت ابن ابن ابن", "Son's Son's Son's Daughter", HeirCategory.DESCENDANT, Gender.FEMALE, level=4)


# ===========================================================================
# ASCENDANTS (الأصول)
# ===========================================================================
# Parents
register_heir("أب", "Father", HeirCategory.ASCENDANT, Gender.MALE, level=1, tasib_priority=10)
register_heir("أم", "Mother", HeirCategory.ASCENDANT, Gender.FEMALE, level=1)

# Grandfathers (paternal only inherit)
register_heir("جد", "Grandfather", HeirCategory.ASCENDANT, Gender.MALE, level=2, tasib_priority=11, 
              aliases=["أب الأب"])
register_heir("أب أب الأب", "Great Grandfather", HeirCategory.ASCENDANT, Gender.MALE, level=3, tasib_priority=12)

# Grandmothers - Maternal line
register_heir("جدة", "Grandmother", HeirCategory.ASCENDANT, Gender.FEMALE, level=2)
register_heir("أم الأم", "Maternal Grandmother", HeirCategory.ASCENDANT, Gender.FEMALE, level=2)
register_heir("أم أم الأم", "Great Maternal Grandmother", HeirCategory.ASCENDANT, Gender.FEMALE, level=3)

# Grandmothers - Paternal line
register_heir("أم الأب", "Paternal Grandmother", HeirCategory.ASCENDANT, Gender.FEMALE, level=2)
register_heir("أم أب الأب", "Paternal Great Grandmother", HeirCategory.ASCENDANT, Gender.FEMALE, level=3)

# Grandmothers - Mixed (maternal grandmother through father)
register_heir("أم أم الأب", "Father's Maternal Grandmother", HeirCategory.ASCENDANT, Gender.FEMALE, level=3)


# ===========================================================================
# SIBLINGS (الإخوة)
# ===========================================================================
# Full siblings
register_heir("أخ شقيق", "Full Brother", HeirCategory.SIBLING, Gender.MALE, 
              relation=Relation.FULL, tasib_priority=20)
register_heir("أخت شقيقة", "Full Sister", HeirCategory.SIBLING, Gender.FEMALE, 
              relation=Relation.FULL)

# Paternal siblings
register_heir("أخ لأب", "Paternal Brother", HeirCategory.SIBLING, Gender.MALE, 
              relation=Relation.PATERNAL, tasib_priority=21)
register_heir("أخت لأب", "Paternal Sister", HeirCategory.SIBLING, Gender.FEMALE, 
              relation=Relation.PATERNAL)

# Maternal siblings
register_heir("أخ لأم", "Maternal Brother", HeirCategory.SIBLING, Gender.MALE, 
              relation=Relation.MATERNAL)
register_heir("أخت لأم", "Maternal Sister", HeirCategory.SIBLING, Gender.FEMALE, 
              relation=Relation.MATERNAL)


# ===========================================================================
# NEPHEWS (أبناء الإخوة) - Sons of brothers
# ===========================================================================
# Full brother's sons
register_heir("ابن أخ شقيق", "Full Brother's Son", HeirCategory.SIBLING, Gender.MALE, 
              level=2, relation=Relation.FULL, tasib_priority=30)
register_heir("ابن ابن أخ شقيق", "Full Brother's Son's Son", HeirCategory.SIBLING, Gender.MALE, 
              level=3, relation=Relation.FULL, tasib_priority=32)

# Paternal brother's sons
register_heir("ابن أخ لأب", "Paternal Brother's Son", HeirCategory.SIBLING, Gender.MALE, 
              level=2, relation=Relation.PATERNAL, tasib_priority=31)
register_heir("ابن ابن أخ لأب", "Paternal Brother's Son's Son", HeirCategory.SIBLING, Gender.MALE, 
              level=3, relation=Relation.PATERNAL, tasib_priority=33)


# ===========================================================================
# UNCLES (الأعمام) - Father's brothers
# ===========================================================================
# Father's full brothers
register_heir("عم شقيق", "Full Uncle", HeirCategory.UNCLE, Gender.MALE, 
              relation=Relation.FULL, tasib_priority=40)

# Father's paternal brothers
register_heir("عم لأب", "Paternal Uncle", HeirCategory.UNCLE, Gender.MALE, 
              relation=Relation.PATERNAL, tasib_priority=41)

# Grandfather's brothers
register_heir("عم الأب", "Father's Full Uncle", HeirCategory.UNCLE, Gender.MALE, 
              level=2, tasib_priority=42, aliases=["عم الأب لأب", "عم أب الأب"])


# ===========================================================================
# COUSINS (أبناء الأعمام) - Sons of uncles
# ===========================================================================
# Full uncle's sons
register_heir("ابن عم شقيق", "Full Uncle's Son", HeirCategory.COUSIN, Gender.MALE, 
              relation=Relation.FULL, tasib_priority=50)
register_heir("ابن ابن عم شقيق", "Full Uncle's Son's Son", HeirCategory.COUSIN, Gender.MALE, 
              level=2, relation=Relation.FULL, tasib_priority=52)

# Paternal uncle's sons
register_heir("ابن عم لأب", "Paternal Uncle's Son", HeirCategory.COUSIN, Gender.MALE, 
              relation=Relation.PATERNAL, tasib_priority=51)
register_heir("ابن ابن عم لأب", "Paternal Uncle's Son's Son", HeirCategory.COUSIN, Gender.MALE, 
              level=2, relation=Relation.PATERNAL, tasib_priority=53)

# Grandfather's brother's sons
register_heir("ابن عم الأب", "Father's Uncle's Son", HeirCategory.COUSIN, Gender.MALE, 
              level=2, tasib_priority=54)
register_heir("ابن ابن عم الأب", "Father's Uncle's Son's Son", HeirCategory.COUSIN, Gender.MALE, 
              level=3, tasib_priority=55)


# ===========================================================================
# LOOKUP FUNCTIONS
# ===========================================================================

def get_heir_type(name: str) -> Optional[HeirType]:
    """Get heir type by Arabic name."""
    # Direct lookup
    if name in HEIR_TYPES:
        return HEIR_TYPES[name]
    
    # Try normalized lookup (remove extra spaces, normalize characters)
    normalized = name.strip()
    
    # Handle ـ character variance
    normalized = normalized.replace("ـ", "")
    if normalized in HEIR_TYPES:
        return HEIR_TYPES[normalized]
    
    # Try without extra character
    for key in HEIR_TYPES:
        if key.replace("ـ", "") == normalized:
            return HEIR_TYPES[key]
    
    return None


def create_heir(name: str, count: int = 1) -> Optional[Heir]:
    """Create an Heir instance from name and count."""
    heir_type = get_heir_type(name)
    if heir_type:
        return Heir(heir_type=heir_type, count=count, original_name=name)
    return None


def list_all_heir_types() -> List[str]:
    """List all registered heir type names (excluding aliases)."""
    seen = set()
    result = []
    for name, heir_type in HEIR_TYPES.items():
        if heir_type.name_ar not in seen:
            result.append(heir_type.name_ar)
            seen.add(heir_type.name_ar)
    return result
