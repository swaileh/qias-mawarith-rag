# Mawarith - Islamic Inheritance Calculator Package
"""
Mawarith (المواريث) - Islamic Inheritance Calculator

A symbolic calculator for Islamic inheritance based on Fiqh rules.

Version 2.0: Unified MiraathCase API with edge case support.
"""

# NEW: Unified API (recommended)
from .case import MiraathCase

# NEW: Enhanced models
from .models import (
    Heir,
    HeirStatus,
    HeirCategory,
    Share,
    ShareType,
    ShareBasis,
    MiraathResult,
    HeirShare,
    BlockedHeir,
)

# NEW: Parser for extracting case metadata
from .parser import (
    MawarithParser,
    ParsedCase,
    ParsedHeir,
    EdgeCaseInfo,
    parse_dataset_case,
    parse_quick_input,
    detect_case_metadata,
)

# LEGACY: Backward compatibility (still works)
from .scalc import InheritanceCalculator
from .scalc import Heir as LegacyHeir
from .scalc import HeirType, Fraction
from .scalc import Share as LegacyShare

__version__ = "2.0.0"
__all__ = [
    # Unified API
    "MiraathCase",
    # Models
    "Heir",
    "HeirStatus",
    "HeirCategory",
    "Share",
    "ShareType",
    "ShareBasis",
    "MiraathResult",
    "HeirShare",
    "BlockedHeir",
    # Parser
    "MawarithParser",
    "ParsedCase",
    "ParsedHeir",
    "EdgeCaseInfo",
    "parse_dataset_case",
    "parse_quick_input",
    "detect_case_metadata",
    # Legacy
    "InheritanceCalculator",
    "HeirType",
    "Fraction",
]

