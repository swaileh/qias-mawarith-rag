"""
MiraathCase - Unified API for Islamic Inheritance Calculation.

This is the main entry point for all inheritance calculations.
Supports simple cases and all edge cases with a single, intuitive interface.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union, Tuple
from fractions import Fraction
import time

from .models import (
    Heir,
    HeirStatus,
    MiraathResult,
    HeirShare,
    BlockedHeir,
    is_valid_heir_type,
)

# Import existing calculator for backward compatibility
from .scalc import InheritanceCalculator


@dataclass
class SuccessiveDeath:
    """Represents a successive death (munasakhaat) for an heir."""
    heir_name: str
    heirs: List[Dict[str, Any]]
    before_distribution: bool = True


class MiraathCase:
    """
    Unified API for Islamic Inheritance Calculation.
    
    Handles everything from simple cases to complex edge cases
    with a single, intuitive interface.
    
    Examples:
        # Simple usage (one-liner)
        result = MiraathCase.quick(["زوج", "أم", ("بنت", 2)])
        
        # Standard usage
        case = MiraathCase()
        case.add_heir("زوجة", count=2)
        case.add_heir("ابن")
        result = case.calculate()
        
        # Advanced usage (edge cases)
        case = MiraathCase(madhab="hanafi")
        case.add_heir("أب", status="missing", reserve=True)
        case.add_heir("زوجة", pregnant=True)
        result = case.calculate()
    """
    
    def __init__(
        self,
        madhab: str = "shafii",
        jurisdiction: Optional[str] = None,
        apply_wasiyyah_wajibah: bool = False,
        bayt_mal_fallback: bool = True,
        include_dhul_arham: bool = False,
    ):
        """
        Initialize a new inheritance case.
        
        Args:
            madhab: Islamic school of thought (shafii, hanafi, maliki, hanbali)
            jurisdiction: Country code (e.g., "SA", "EG") for statutory rules
            apply_wasiyyah_wajibah: Apply obligatory bequest for grandchildren
            bayt_mal_fallback: Allow remainder to go to treasury
            include_dhul_arham: Include extended kin (dhul arham) if no asabah
        """
        self.madhab = madhab.lower()
        self.jurisdiction = jurisdiction
        self.apply_wasiyyah_wajibah = apply_wasiyyah_wajibah
        self.bayt_mal_fallback = bayt_mal_fallback
        self.include_dhul_arham = include_dhul_arham
        
        self._heirs: List[Heir] = []
        self._successive_deaths: List[SuccessiveDeath] = []
        self._warnings: List[str] = []
        
        # Madhab registry for school-specific rules
        try:
            from .madhab import MadhabRegistry
            self._madhab_registry = MadhabRegistry(self.madhab)
        except (ImportError, ValueError):
            self._madhab_registry = None
            self._warnings.append(f"Madhab '{madhab}' not fully supported")
        
        # Internal calculator (uses existing implementation)
        self._calculator = InheritanceCalculator()
    
    # ===== HEIR MANAGEMENT =====
    
    def add_heir(
        self,
        heir_type: str,
        count: int = 1,
        name: Optional[str] = None,
        status: str = "alive",
        pregnant: bool = False,
        max_children: int = 4,
        reserve: bool = False,
    ) -> "MiraathCase":
        """
        Add an heir to the case.
        
        Args:
            heir_type: Arabic heir name (e.g., "ابن", "بنت", "زوجة")
            count: Number of this heir type (default: 1)
            name: Optional name for tracking in successive deaths
            status: Heir status ("alive", "missing", "presumed_dead", "unborn")
            pregnant: Whether this is a pregnant wife
            max_children: Max children for pregnancy reserve
            reserve: Reserve share for uncertain heir
        
        Returns:
            Self for method chaining
        
        Raises:
            ValueError: If heir_type is invalid
        """
        # Validate heir type
        if not is_valid_heir_type(heir_type):
            self._warnings.append(f"Unknown heir type: {heir_type}")
        
        # Convert status string to enum
        try:
            heir_status = HeirStatus(status)
        except ValueError:
            heir_status = HeirStatus.ALIVE
            self._warnings.append(f"Unknown status '{status}', defaulting to 'alive'")
        
        # Create heir
        heir = Heir(
            heir_type=heir_type,
            count=count,
            name=name,
            status=heir_status,
            pregnant=pregnant,
            max_children=max_children,
            reserve=reserve,
        )
        
        self._heirs.append(heir)
        return self
    
    def remove_heir(self, name_or_type: str) -> "MiraathCase":
        """
        Remove an heir by name or type.
        
        Args:
            name_or_type: Heir's name or type to remove
        
        Returns:
            Self for method chaining
        """
        self._heirs = [
            h for h in self._heirs 
            if h.name != name_or_type and h.heir_type != name_or_type
        ]
        return self
    
    def clear_heirs(self) -> "MiraathCase":
        """Clear all heirs."""
        self._heirs = []
        return self
    
    @property
    def heirs(self) -> List[Heir]:
        """Get list of heirs."""
        return self._heirs.copy()
    
    # ===== EDGE CASE METHODS =====
    
    def mark_died_before_distribution(
        self,
        heir_name: str,
        heirs: List[Dict[str, Any]],
        before_distribution: bool = True,
    ) -> "MiraathCase":
        """
        Mark an heir as dying before distribution (munasakhaat).
        
        Args:
            heir_name: Name of the heir who died
            heirs: List of their heirs [{"heir": "زوجة"}, {"heir": "ابن", "count": 2}]
            before_distribution: Whether death was before distribution
        
        Returns:
            Self for method chaining
        """
        self._successive_deaths.append(SuccessiveDeath(
            heir_name=heir_name,
            heirs=heirs,
            before_distribution=before_distribution,
        ))
        return self
    
    def set_pregnancy_reserve(
        self,
        max_males: int = 2,
        max_females: int = 2,
    ) -> "MiraathCase":
        """
        Configure pregnancy reserve calculation.
        
        Args:
            max_males: Maximum number of male children to reserve for
            max_females: Maximum number of female children to reserve for
        
        Returns:
            Self for method chaining
        """
        # Update any pregnant wives with this config
        for heir in self._heirs:
            if heir.pregnant:
                heir.max_children = max_males + max_females
        return self
    
    # ===== VALIDATION =====
    
    def validate(self) -> List[str]:
        """
        Validate the case and return any errors/warnings.
        
        Returns:
            List of validation messages
        """
        messages = self._warnings.copy()
        
        # Check for basic validity
        if not self._heirs:
            messages.append("No heirs specified")
        
        # Check spouse constraints
        husbands = sum(1 for h in self._heirs if h.heir_type == "زوج")
        wives = sum(1 for h in self._heirs if h.heir_type in ("زوجة", "زوجـة"))
        
        if husbands > 1:
            messages.append("Multiple husbands not allowed")
        if husbands > 0 and wives > 0:
            messages.append("Cannot have both husband and wife")
        
        # Check for duplicate heir types (may be intentional)
        seen = {}
        for heir in self._heirs:
            if heir.heir_type in seen and heir.name is None:
                messages.append(f"Duplicate heir type: {heir.heir_type}")
            seen[heir.heir_type] = True
        
        return messages
    
    # ===== CALCULATION =====
    
    def calculate(self) -> MiraathResult:
        """
        Calculate inheritance distribution.
        
        Returns:
            MiraathResult with complete distribution information
        """
        start_time = time.time()
        
        # Convert to legacy format for existing calculator
        heirs_input = [
            {"heir": h.heir_type, "count": h.count}
            for h in self._heirs
            if h.status == HeirStatus.ALIVE
        ]
        
        # Detect special classical cases
        special_case = self._detect_special_case(heirs_input)
        
        # Use existing calculator
        legacy_result = self._calculator.calculate(heirs_input)
        
        # Convert to new result format
        result = self._convert_legacy_result(legacy_result)
        result.madhab = self.madhab
        result.special_case = special_case
        result.warnings = self._warnings.copy()
        result.calculation_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def _detect_special_case(self, heirs_input: List[Dict]) -> Optional[str]:
        """Detect if this is a classical special case."""
        try:
            from .rules import detect_umariyyah, detect_mushtarakah, detect_akdariyyah
            
            # Check Umariyyah
            umariyyah = detect_umariyyah(heirs_input)
            if umariyyah:
                return "العمرية" if umariyyah == "umariyyah_husband" else "العمرية (زوجة)"
            
            # Check Mushtarakah
            if detect_mushtarakah(heirs_input, self.madhab):
                return "المشتركة"
            
            # Check Akdariyyah
            if detect_akdariyyah(heirs_input):
                return "الأكدرية"
            
        except ImportError:
            pass  # Rules module not fully set up
        
        return None

    
    def _convert_legacy_result(self, legacy) -> MiraathResult:
        """Convert legacy calculator result to MiraathResult."""
        distribution = []
        blocked = []
        
        # Get the output dict
        output = legacy.to_dict()
        
        # Process distribution
        post_tasil = output.get("post_tasil", {})
        base = post_tasil.get("total_shares", 1)
        
        for d in post_tasil.get("distribution", []):
            heir_type = d["heir"]
            count = d["count"]
            per_head = d.get("per_head_shares", "0")
            pct = d.get("per_head_percent", 0)
            
            # Parse fraction
            try:
                if "/" in str(per_head):
                    parts = str(per_head).split("/")
                    frac = Fraction(int(parts[0]), int(parts[1]))
                else:
                    frac = Fraction(0)
            except (ValueError, TypeError, IndexError):
                frac = Fraction(0)
            
            # Calculate shares
            shares_entry = next(
                (s for s in output.get("shares", []) if s["heir"] == heir_type),
                {}
            )
            share_type = shares_entry.get("fraction", "عصبة")
            
            heir_share = HeirShare(
                heir_type=heir_type,
                count=count,
                share=frac * count,
                share_type=share_type,
                total_shares=int(base * frac * count) if frac else 0,
                per_head_shares=int(base * frac) if frac else 0,
                per_head_fraction=frac,
                percentage=pct,
            )
            distribution.append(heir_share)
        
        # Process blocked heirs
        for b in output.get("blocked", []):
            blocked.append(BlockedHeir(
                heir_type=b["heir"],
                count=b["count"],
                blocked_by=b.get("blocked_by", ""),
            ))
        
        # Check awl/radd
        awl_radd = output.get("awl_or_radd", "لا")
        awl_applied = awl_radd == "عول"
        radd_applied = awl_radd == "رد"
        
        return MiraathResult(
            distribution=distribution,
            base=base,
            total_shares=base,
            awl_applied=awl_applied,
            radd_applied=radd_applied,
            blocked_heirs=blocked,
        )
    
    # ===== QUICK METHODS =====
    
    @classmethod
    def quick(
        cls,
        heirs: List[Union[str, Tuple[str, int]]],
        madhab: str = "shafii",
    ) -> MiraathResult:
        """
        One-liner for simple cases.
        
        Args:
            heirs: List of heirs as strings or (heir_type, count) tuples
            madhab: Islamic school of thought
        
        Returns:
            MiraathResult
        
        Examples:
            result = MiraathCase.quick(["زوج", "أم", ("بنت", 2)])
        """
        case = cls(madhab=madhab)
        
        for h in heirs:
            if isinstance(h, str):
                case.add_heir(h)
            elif isinstance(h, (tuple, list)) and len(h) >= 2:
                case.add_heir(h[0], count=h[1])
            else:
                raise ValueError(f"Invalid heir specification: {h}")
        
        return case.calculate()
    
    # ===== SERIALIZATION =====
    
    def to_dict(self) -> Dict[str, Any]:
        """Export case configuration as dictionary."""
        return {
            "madhab": self.madhab,
            "jurisdiction": self.jurisdiction,
            "options": {
                "apply_wasiyyah_wajibah": self.apply_wasiyyah_wajibah,
                "bayt_mal_fallback": self.bayt_mal_fallback,
                "include_dhul_arham": self.include_dhul_arham,
            },
            "heirs": [h.to_dict() for h in self._heirs],
            "successive_deaths": [
                {"heir_name": sd.heir_name, "heirs": sd.heirs}
                for sd in self._successive_deaths
            ],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MiraathCase":
        """Create case from dictionary (JSON-compatible)."""
        options = data.get("options", {})
        
        case = cls(
            madhab=data.get("madhab", "shafii"),
            jurisdiction=data.get("jurisdiction"),
            apply_wasiyyah_wajibah=options.get("apply_wasiyyah_wajibah", False),
            bayt_mal_fallback=options.get("bayt_mal_fallback", True),
            include_dhul_arham=options.get("include_dhul_arham", False),
        )
        
        for h in data.get("heirs", []):
            case.add_heir(
                heir_type=h["heir"],
                count=h.get("count", 1),
                name=h.get("name"),
                status=h.get("status", "alive"),
            )
        
        return case
    
    def __repr__(self):
        return f"MiraathCase({len(self._heirs)} heirs, madhab={self.madhab})"
    
    def __str__(self):
        heirs_str = ", ".join(
            f"{h.heir_type}({h.count})" for h in self._heirs
        )
        return f"MiraathCase[{heirs_str}]"
