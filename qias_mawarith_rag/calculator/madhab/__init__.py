"""
Madhab package - School-specific rule variations.

Supported madhabs:
- shafii (default) - الشافعي
- hanafi - الحنفي
- maliki - المالكي
- hanbali - الحنبلي
"""

from .registry import (
    MadhabCode,
    MadhabInfo,
    MadhabRegistry,
    RuleVariation,
    MADHABS,
    RULE_VARIATIONS,
    get_madhab_name,
    is_valid_madhab,
)

DEFAULT_MADHAB = "shafii"

__all__ = [
    "MadhabCode",
    "MadhabInfo",
    "MadhabRegistry",
    "RuleVariation",
    "MADHABS",
    "RULE_VARIATIONS",
    "DEFAULT_MADHAB",
    "get_madhab_name",
    "is_valid_madhab",
]

