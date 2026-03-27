"""
Mawarith Input Parser

Extracts and normalizes inheritance case data from various input formats:
- Dataset JSON format (current training data)
- Full schema format (mawarith4.md 2026 schema)
- Quick input format (list of heirs)

Extracts:
- Heirs with status (alive, missing, unborn)
- Edge case indicators
- Madhab/jurisdiction hints
- Decedent information
- Estate deductions
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class HeirStatus(Enum):
    """Status of an heir."""
    ALIVE = "alive"
    MISSING = "missing"       # مفقود
    DECEASED = "deceased"     # Died before distribution
    UNBORN = "unborn"         # حمل
    BLOCKED = "blocked"       # محجوب


@dataclass
class ParsedHeir:
    """Parsed heir information."""
    heir_type: str           # Arabic name (e.g., "ابن")
    count: int = 1
    status: HeirStatus = HeirStatus.ALIVE
    name: Optional[str] = None
    notes: Optional[str] = None
    

@dataclass
class EdgeCaseInfo:
    """Detected edge case information."""
    case_type: str           # e.g., "مفقود", "حمل", "مناسخات"
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedCase:
    """Fully parsed inheritance case."""
    # Core data
    heirs: List[ParsedHeir]
    blocked_heirs: List[ParsedHeir]
    
    # Metadata
    case_id: Optional[str] = None
    category: Optional[str] = None
    
    # Edge cases
    edge_cases: List[EdgeCaseInfo] = field(default_factory=list)
    
    # Madhab & Jurisdiction
    madhab: str = "shafii"
    jurisdiction: Optional[str] = None
    
    # Estate info
    estate_value: Optional[float] = None
    currency: str = "SAR"
    funeral_expenses: float = 0.0
    debts: float = 0.0
    wasiyyah: float = 0.0
    
    # Special cases detected
    special_case: Optional[str] = None  # العمرية، المشتركة، الأكدرية
    
    # Raw data
    raw_question: Optional[str] = None
    raw_answer: Optional[str] = None
    

class MawarithParser:
    """
    Parser for Mawarith inheritance cases.
    
    Handles multiple input formats and extracts:
    - Heirs with status
    - Edge case indicators
    - Madhab/jurisdiction hints
    """
    
    # Madhab detection patterns
    MADHAB_PATTERNS = {
        "hanafi": [r"الحنفي", r"أبو حنيفة", r"hanafi"],
        "maliki": [r"المالكي", r"مالك", r"maliki"],
        "shafii": [r"الشافعي", r"shafii"],
        "hanbali": [r"الحنبلي", r"أحمد بن حنبل", r"hanbali"],
    }
    
    # Edge case detection patterns
    EDGE_CASE_PATTERNS = {
        "mafqud": [r"مفقود", r"missing", r"غائب"],
        "haml": [r"حمل", r"pregnancy", r"حامل", r"جنين"],
        "munasakhaat": [r"مناسخ", r"successive", r"مات قبل", r"توفي بعد"],
        "wasiyyah_wajibah": [r"وصية واجبة", r"obligatory bequest"],
        "dhul_arham": [r"ذوي الأرحام", r"extended kin"],
    }
    
    # Special classical case patterns
    SPECIAL_CASE_PATTERNS = {
        "umariyyah": [r"العمرية", r"عمرية"],
        "mushtarakah": [r"المشتركة", r"الحمارية", r"مشتركة"],
        "akdariyyah": [r"الأكدرية", r"أكدرية"],
    }
    
    # Jurisdiction patterns (country codes)
    JURISDICTION_PATTERNS = {
        "SA": [r"السعودية", r"حسب القانون السعودي"],
        "EG": [r"مصر", r"القانون المصري"],
        "AE": [r"الإمارات", r"القانون الإماراتي"],
        "JO": [r"الأردن", r"القانون الأردني"],
        "DZ": [r"الجزائر", r"القانون الجزائري"],
        "MA": [r"المغرب", r"القانون المغربي"],
    }
    
    def __init__(self, default_madhab: str = "shafii"):
        self.default_madhab = default_madhab
    
    def parse(self, data: Dict[str, Any]) -> ParsedCase:
        """
        Parse a case from various formats.
        
        Args:
            data: Input data (dataset format, schema format, or dict)
        
        Returns:
            ParsedCase with all extracted information
        """
        # Detect format and delegate
        if "output" in data:
            return self._parse_dataset_format(data)
        elif "case" in data and "meta" in data:
            return self._parse_schema_format(data)
        elif "heirs" in data:
            return self._parse_simple_format(data)
        else:
            raise ValueError("Unknown input format")
    
    def _parse_dataset_format(self, data: Dict) -> ParsedCase:
        """Parse current training dataset format."""
        output = data.get("output", {})
        question = data.get("question", "")
        answer = data.get("answer", "")
        
        # Parse heirs
        heirs = []
        for h in output.get("heirs", []):
            heir = ParsedHeir(
                heir_type=h.get("heir", ""),
                count=h.get("count", 1),
                status=HeirStatus.ALIVE,
            )
            heirs.append(heir)
        
        # Parse blocked heirs
        blocked_heirs = []
        for h in output.get("blocked", []):
            heir = ParsedHeir(
                heir_type=h.get("heir", ""),
                count=h.get("count", 1),
                status=HeirStatus.BLOCKED,
            )
            blocked_heirs.append(heir)
        
        # Detect madhab from question/answer
        madhab = self._detect_madhab(question + " " + answer)
        
        # Detect jurisdiction
        jurisdiction = self._detect_jurisdiction(question + " " + answer)
        
        # Detect edge cases
        edge_cases = self._detect_edge_cases(question + " " + answer)
        
        # Detect special cases
        special_case = self._detect_special_case(question + " " + answer)
        
        return ParsedCase(
            heirs=heirs,
            blocked_heirs=blocked_heirs,
            case_id=data.get("id"),
            category=data.get("category"),
            edge_cases=edge_cases,
            madhab=madhab,
            jurisdiction=jurisdiction,
            special_case=special_case,
            raw_question=question,
            raw_answer=answer,
        )
    
    def _parse_schema_format(self, data: Dict) -> ParsedCase:
        """Parse full 2026 schema format."""
        meta = data.get("meta", {})
        case_data = data.get("case", {})
        
        # Extract madhab from meta
        calc_method = meta.get("calculationMethod", {})
        madhab = calc_method.get("madhhab", self.default_madhab)
        
        # Extract estate info
        estate = case_data.get("estate", {})
        deductions = estate.get("deductions", {})
        
        # Parse heirs
        heirs = []
        for h in case_data.get("heirs", []):
            status = HeirStatus.ALIVE
            if not h.get("alive", True):
                status = HeirStatus.DECEASED
            if not h.get("eligibility", {}).get("isEligible", True):
                status = HeirStatus.BLOCKED
            
            # Check for special attributes
            attrs = h.get("attributes", {})
            if attrs.get("missing"):
                status = HeirStatus.MISSING
            if attrs.get("unborn"):
                status = HeirStatus.UNBORN
            
            heir = ParsedHeir(
                heir_type=h.get("relation", ""),
                count=h.get("count", 1),
                status=status,
                name=h.get("name"),
            )
            heirs.append(heir)
        
        # Separate blocked heirs
        blocked_heirs = [h for h in heirs if h.status == HeirStatus.BLOCKED]
        active_heirs = [h for h in heirs if h.status != HeirStatus.BLOCKED]
        
        return ParsedCase(
            heirs=active_heirs,
            blocked_heirs=blocked_heirs,
            madhab=madhab,
            estate_value=estate.get("gross"),
            currency=estate.get("currency", "SAR"),
            funeral_expenses=deductions.get("funeralExpenses", 0),
            debts=deductions.get("debts", 0),
            wasiyyah=deductions.get("wasiyyah", {}).get("amount", 0),
        )
    
    def _parse_simple_format(self, data: Dict) -> ParsedCase:
        """Parse simple format with just heirs list."""
        heirs = []
        for h in data.get("heirs", []):
            if isinstance(h, str):
                heirs.append(ParsedHeir(heir_type=h))
            elif isinstance(h, dict):
                heirs.append(ParsedHeir(
                    heir_type=h.get("heir", h.get("type", "")),
                    count=h.get("count", 1),
                    status=HeirStatus(h.get("status", "alive")),
                ))
            elif isinstance(h, tuple) and len(h) == 2:
                heirs.append(ParsedHeir(heir_type=h[0], count=h[1]))
        
        return ParsedCase(
            heirs=heirs,
            blocked_heirs=[],
            madhab=data.get("madhab", self.default_madhab),
            jurisdiction=data.get("jurisdiction"),
        )
    
    def _detect_madhab(self, text: str) -> str:
        """Detect madhab from text content."""
        text_lower = text.lower()
        for madhab, patterns in self.MADHAB_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return madhab
        return self.default_madhab
    
    def _detect_jurisdiction(self, text: str) -> Optional[str]:
        """Detect jurisdiction from text content."""
        for code, patterns in self.JURISDICTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return code
        return None
    
    def _detect_edge_cases(self, text: str) -> List[EdgeCaseInfo]:
        """Detect edge cases from text content."""
        edge_cases = []
        for case_type, patterns in self.EDGE_CASE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    edge_cases.append(EdgeCaseInfo(case_type=case_type))
                    break
        return edge_cases
    
    def _detect_special_case(self, text: str) -> Optional[str]:
        """Detect special classical case from text."""
        for case_name, patterns in self.SPECIAL_CASE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return case_name
        return None
    
    def to_miraath_case_args(self, parsed: ParsedCase) -> Dict[str, Any]:
        """
        Convert ParsedCase to MiraathCase initialization arguments.
        
        Returns:
            Dict ready to be passed to MiraathCase() or MiraathCase.from_dict()
        """
        heirs = []
        for h in parsed.heirs:
            heir_dict = {
                "heir_type": h.heir_type,
                "count": h.count,
            }
            if h.status != HeirStatus.ALIVE:
                heir_dict["status"] = h.status.value
            if h.name:
                heir_dict["name"] = h.name
            heirs.append(heir_dict)
        
        return {
            "madhab": parsed.madhab,
            "jurisdiction": parsed.jurisdiction,
            "heirs": heirs,
            "edge_cases": [{"type": e.case_type, **e.details} for e in parsed.edge_cases],
        }


def parse_quick_input(heirs_input: List) -> List[Dict[str, Any]]:
    """
    Parse quick input format to standard format.
    
    Supports:
    - "زوج" -> {"heir": "زوج", "count": 1}
    - ("بنت", 2) -> {"heir": "بنت", "count": 2}
    - {"heir": "ابن", "count": 1, "status": "missing"}
    
    Args:
        heirs_input: List of heirs in various formats
    
    Returns:
        Normalized list of heir dictionaries
    """
    normalized = []
    for h in heirs_input:
        if isinstance(h, str):
            normalized.append({"heir": h, "count": 1})
        elif isinstance(h, tuple) and len(h) == 2:
            normalized.append({"heir": h[0], "count": h[1]})
        elif isinstance(h, dict):
            normalized.append({
                "heir": h.get("heir", h.get("type", "")),
                "count": h.get("count", 1),
                "status": h.get("status", "alive"),
            })
    return normalized


def detect_case_metadata(text: str) -> Dict[str, Any]:
    """
    Extract metadata hints from Arabic text (question/answer).
    
    Returns dict with:
    - madhab: detected school (or None)
    - jurisdiction: detected country code (or None)
    - edge_cases: list of detected edge case types
    - special_case: detected classical special case
    """
    parser = MawarithParser()
    return {
        "madhab": parser._detect_madhab(text),
        "jurisdiction": parser._detect_jurisdiction(text),
        "edge_cases": [e.case_type for e in parser._detect_edge_cases(text)],
        "special_case": parser._detect_special_case(text),
    }


# For backward compatibility with evaluate.py
def parse_dataset_case(example: Dict) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Parse a dataset case for the evaluator.
    
    Returns:
        (heirs_input, metadata)
    """
    parser = MawarithParser()
    parsed = parser.parse(example)
    
    heirs_input = [
        {"heir": h.heir_type, "count": h.count}
        for h in parsed.heirs
    ]
    
    metadata = {
        "madhab": parsed.madhab,
        "jurisdiction": parsed.jurisdiction,
        "edge_cases": [e.case_type for e in parsed.edge_cases],
        "special_case": parsed.special_case,
        "blocked_count": sum(h.count for h in parsed.blocked_heirs),
    }
    
    return heirs_input, metadata
