"""
Shared data models for the unified calculator API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Any, Dict, List, Optional

from .scalc.heirs import HeirCategory as LegacyHeirCategory
from .scalc.heirs import get_heir_type, list_all_heir_types


class HeirStatus(str, Enum):
    """Lifecycle status of an heir."""

    ALIVE = "alive"
    MISSING = "missing"
    PRESUMED_DEAD = "presumed_dead"
    UNBORN = "unborn"
    BLOCKED = "blocked"


# Re-export the legacy heir category enum to keep one source of truth.
HeirCategory = LegacyHeirCategory


class ShareType(str, Enum):
    """High-level share type for API metadata."""

    FIXED = "fixed"
    RESIDUARY = "residuary"
    MIXED = "mixed"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class ShareBasis(str, Enum):
    """Reference basis for a share assignment."""

    QURAN = "quran"
    SUNNAH = "sunnah"
    IJMA = "ijma"
    QIYAS = "qiyas"
    DERIVED = "derived"


@dataclass
class Share:
    """Normalized share representation."""

    fraction: Fraction = Fraction(0, 1)
    percentage: float = 0.0
    share_type: ShareType = ShareType.UNKNOWN
    basis: ShareBasis = ShareBasis.DERIVED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fraction": str(self.fraction),
            "percentage": self.percentage,
            "share_type": self.share_type.value,
            "basis": self.basis.value,
        }


@dataclass
class Heir:
    """Unified heir input record for MiraathCase."""

    heir_type: str
    count: int = 1
    name: Optional[str] = None
    status: HeirStatus = HeirStatus.ALIVE
    pregnant: bool = False
    max_children: int = 4
    reserve: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "heir": self.heir_type,
            "count": self.count,
            "name": self.name,
            "status": self.status.value,
            "pregnant": self.pregnant,
            "max_children": self.max_children,
            "reserve": self.reserve,
        }


@dataclass
class HeirShare:
    """Computed distribution entry for one heir group."""

    heir_type: str
    count: int = 1
    share: Fraction = Fraction(0, 1)
    share_type: str = ""
    total_shares: int = 0
    per_head_shares: int = 0
    per_head_fraction: Fraction = Fraction(0, 1)
    percentage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "heir_type": self.heir_type,
            "count": self.count,
            "share": str(self.share),
            "share_type": self.share_type,
            "total_shares": self.total_shares,
            "per_head_shares": self.per_head_shares,
            "per_head_fraction": str(self.per_head_fraction),
            "percentage": self.percentage,
        }


@dataclass
class BlockedHeir:
    """Represents an heir blocked from inheritance."""

    heir_type: str
    count: int = 1
    blocked_by: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "heir_type": self.heir_type,
            "count": self.count,
            "blocked_by": self.blocked_by,
        }


@dataclass
class MiraathResult:
    """Unified calculator output."""

    distribution: List[HeirShare] = field(default_factory=list)
    base: int = 1
    total_shares: int = 1
    awl_applied: bool = False
    radd_applied: bool = False
    blocked_heirs: List[BlockedHeir] = field(default_factory=list)
    special_case: Optional[str] = None
    madhab: str = "shafii"
    warnings: List[str] = field(default_factory=list)
    calculation_time_ms: float = 0.0

    def summary(self, language: str = "ar") -> str:
        if language == "en":
            return (
                f"Base={self.base}, heirs={len(self.distribution)}, "
                f"blocked={len(self.blocked_heirs)}, awl={self.awl_applied}, radd={self.radd_applied}"
            )
        return (
            f"أصل المسألة: {self.base} | عدد الورثة: {len(self.distribution)} | "
            f"المحجوبون: {len(self.blocked_heirs)}"
        )

    def to_table(self) -> str:
        rows = ["heir_type | count | per_head_fraction | percentage"]
        for item in self.distribution:
            rows.append(
                f"{item.heir_type} | {item.count} | {item.per_head_fraction} | {item.percentage:.2f}"
            )
        return "\n".join(rows)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distribution": [item.to_dict() for item in self.distribution],
            "base": self.base,
            "total_shares": self.total_shares,
            "awl_applied": self.awl_applied,
            "radd_applied": self.radd_applied,
            "blocked_heirs": [item.to_dict() for item in self.blocked_heirs],
            "special_case": self.special_case,
            "madhab": self.madhab,
            "warnings": list(self.warnings),
            "calculation_time_ms": self.calculation_time_ms,
        }


def is_valid_heir_type(heir_type: str) -> bool:
    """Validate heir names against the registered legacy heir registry."""
    if not heir_type:
        return False
    return get_heir_type(heir_type) is not None or heir_type in set(list_all_heir_types())

