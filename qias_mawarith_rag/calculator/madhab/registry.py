"""
Madhab Registry - School-specific rule variations.

The four major Sunni schools (madhabs) have differences in
certain inheritance rules. This module provides a registry
system to handle these variations.

Key Differences Between Schools:
================================

1. GRANDFATHER WITH SIBLINGS (الجد مع الإخوة):
   - Hanafi: Grandfather blocks all siblings (like father)
   - Others: Grandfather shares with siblings (muqasama/best-of-3)

2. MUSHTARAKAH (المشتركة):
   - Shafi'i/Maliki: Full siblings share in 1/3 with maternal
   - Hanafi/Hanbali: Full siblings get nothing (asabah after exhausted)

3. AKDARIYYAH (الأكدرية):
   - Hanafi: Grandfather blocks full sister
   - Others: Complex awl + muqasama solution

4. RADD (الرد):
   - Hanafi: Radd to all including spouses (some opinions)
   - Others: Radd excludes spouses

5. DHUL ARHAM (ذوو الأرحام):
   - All schools: Included if no asabah (varies in method)
   - Priority and distribution methods differ

6. UMARIYYAH (العمرية):
   - All schools: Same ruling (mother gets 1/3 of remainder)

7. WAITING PERIOD FOR MISSING (المفقود):
   - Hanafi: 90-120 years from birth
   - Maliki: 70-80 years from birth
   - Shafi'i/Hanbali: 4 years from disappearance
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class MadhabCode(Enum):
    """Supported Islamic schools of thought."""
    SHAFII = "shafii"
    HANAFI = "hanafi"
    MALIKI = "maliki"
    HANBALI = "hanbali"


@dataclass
class MadhabInfo:
    """Information about a madhab."""
    code: str
    name_ar: str
    name_en: str
    founder: str
    description: str


@dataclass
class RuleVariation:
    """A rule that varies between madhabs."""
    rule_id: str
    description_ar: str
    description_en: str
    variations: Dict[str, Any]  # madhab_code -> rule value/behavior


# Madhab information registry
MADHABS: Dict[str, MadhabInfo] = {
    "shafii": MadhabInfo(
        code="shafii",
        name_ar="الشافعي",
        name_en="Shafi'i",
        founder="الإمام محمد بن إدريس الشافعي",
        description="Founded in Egypt, emphasizes Quran, Sunnah, Ijma, and Qiyas",
    ),
    "hanafi": MadhabInfo(
        code="hanafi",
        name_ar="الحنفي",
        name_en="Hanafi",
        founder="الإمام أبو حنيفة النعمان",
        description="Largest school, emphasizes reason (ra'y) and analogy",
    ),
    "maliki": MadhabInfo(
        code="maliki",
        name_ar="المالكي",
        name_en="Maliki",
        founder="الإمام مالك بن أنس",
        description="Based in Medina, emphasizes practice of Medina people",
    ),
    "hanbali": MadhabInfo(
        code="hanbali",
        name_ar="الحنبلي",
        name_en="Hanbali",
        founder="الإمام أحمد بن حنبل",
        description="Most conservative, strictly adheres to hadith",
    ),
}


# Rule variations registry
RULE_VARIATIONS: Dict[str, RuleVariation] = {
    
    "grandfather_siblings": RuleVariation(
        rule_id="grandfather_siblings",
        description_ar="الجد مع الإخوة",
        description_en="Grandfather with siblings",
        variations={
            "shafii": "muqasama",    # Best of 3 options
            "hanafi": "blocks",      # Grandfather blocks all siblings
            "maliki": "muqasama",    # Best of 3 options
            "hanbali": "muqasama",   # Best of 3 options
        },
    ),
    
    "mushtarakah": RuleVariation(
        rule_id="mushtarakah",
        description_ar="المشتركة (الحمارية)",
        description_en="Mushtarakah case",
        variations={
            "shafii": True,   # Full siblings share with maternal
            "hanafi": False,  # Full siblings get nothing
            "maliki": True,   # Full siblings share with maternal
            "hanbali": False, # Full siblings get nothing
        },
    ),
    
    "akdariyyah_gf_blocks": RuleVariation(
        rule_id="akdariyyah_gf_blocks",
        description_ar="الأكدرية - هل يحجب الجد الأخت",
        description_en="Akdariyyah - Does grandfather block sister",
        variations={
            "shafii": False,  # No, complex solution
            "hanafi": True,   # Yes, grandfather blocks sister
            "maliki": False,  # No, complex solution
            "hanbali": False, # No (varies by scholar)
        },
    ),
    
    "radd_includes_spouse": RuleVariation(
        rule_id="radd_includes_spouse",
        description_ar="الرد على الزوجين",
        description_en="Radd includes spouses",
        variations={
            "shafii": False,  # Spouse excluded from radd
            "hanafi": False,  # Spouse excluded (majority)
            "maliki": False,  # Spouse excluded
            "hanbali": False, # Spouse excluded
        },
    ),
    
    "missing_waiting_years": RuleVariation(
        rule_id="missing_waiting_years",
        description_ar="مدة انتظار المفقود",
        description_en="Missing person waiting period (years)",
        variations={
            "shafii": 4,      # 4 years from disappearance
            "hanafi": 90,     # 90 years from birth (or 120)
            "maliki": 70,     # 70-80 years from birth
            "hanbali": 4,     # 4 years from disappearance
        },
    ),
    
    "paternal_grandmother_with_maternal": RuleVariation(
        rule_id="paternal_grandmother_with_maternal",
        description_ar="الجدة لأب مع الجدة لأم",
        description_en="Paternal grandmother with maternal grandmother",
        variations={
            "shafii": "share",    # Both share 1/6
            "hanafi": "share",    # Both share 1/6
            "maliki": "maternal_only",  # Maternal takes all 1/6
            "hanbali": "share",   # Both share 1/6
        },
    ),
}


class MadhabRegistry:
    """
    Registry for madhab-specific rule variations.
    
    Usage:
        registry = MadhabRegistry("shafii")
        if registry.get_rule("mushtarakah"):
            # Apply mushtarakah rule
    """
    
    def __init__(self, madhab: str = "shafii"):
        """
        Initialize registry with a specific madhab.
        
        Args:
            madhab: School code (shafii, hanafi, maliki, hanbali)
        """
        self.madhab = madhab.lower()
        if self.madhab not in MADHABS:
            raise ValueError(f"Unknown madhab: {madhab}. Valid: {list(MADHABS.keys())}")
    
    @property
    def info(self) -> MadhabInfo:
        """Get madhab information."""
        return MADHABS[self.madhab]
    
    def get_rule(self, rule_id: str) -> Any:
        """
        Get the value of a rule for this madhab.
        
        Args:
            rule_id: Rule identifier
        
        Returns:
            Rule value for this madhab, or None if rule not found
        """
        if rule_id not in RULE_VARIATIONS:
            return None
        
        variation = RULE_VARIATIONS[rule_id]
        return variation.variations.get(self.madhab)
    
    def grandfather_blocks_siblings(self) -> bool:
        """Check if grandfather blocks siblings in this madhab."""
        return self.get_rule("grandfather_siblings") == "blocks"
    
    def applies_mushtarakah(self) -> bool:
        """Check if mushtarakah rule applies in this madhab."""
        return bool(self.get_rule("mushtarakah"))
    
    def radd_includes_spouse(self) -> bool:
        """Check if radd includes spouse in this madhab."""
        return bool(self.get_rule("radd_includes_spouse"))
    
    def missing_waiting_years(self) -> int:
        """Get waiting period for missing person in years."""
        return self.get_rule("missing_waiting_years") or 4
    
    def describe_differences(self, other_madhab: str) -> List[str]:
        """
        List differences between this madhab and another.
        
        Args:
            other_madhab: Madhab to compare
        
        Returns:
            List of difference descriptions
        """
        other = MadhabRegistry(other_madhab)
        differences = []
        
        for rule_id, variation in RULE_VARIATIONS.items():
            my_value = self.get_rule(rule_id)
            other_value = other.get_rule(rule_id)
            
            if my_value != other_value:
                differences.append(
                    f"{variation.description_ar}: "
                    f"{self.info.name_ar}={my_value}, "
                    f"{other.info.name_ar}={other_value}"
                )
        
        return differences
    
    def to_dict(self) -> Dict[str, Any]:
        """Export madhab configuration as dictionary."""
        return {
            "madhab": self.madhab,
            "name_ar": self.info.name_ar,
            "name_en": self.info.name_en,
            "rules": {
                rule_id: self.get_rule(rule_id)
                for rule_id in RULE_VARIATIONS.keys()
            },
        }
    
    @classmethod
    def list_madhabs(cls) -> List[str]:
        """List all supported madhabs."""
        return list(MADHABS.keys())
    
    @classmethod
    def list_rules(cls) -> List[str]:
        """List all rule variations."""
        return list(RULE_VARIATIONS.keys())


def get_madhab_name(code: str, language: str = "ar") -> str:
    """Get display name for a madhab."""
    if code not in MADHABS:
        return code
    info = MADHABS[code]
    return info.name_ar if language == "ar" else info.name_en


def is_valid_madhab(code: str) -> bool:
    """Check if madhab code is valid."""
    return code.lower() in MADHABS
