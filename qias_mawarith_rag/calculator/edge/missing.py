"""
المفقود (Mafqud) - Missing Person Handler

Handles inheritance cases where one or more heirs are missing (their
status as alive or dead is uncertain).

Islamic Fiqh Approach:
  1. Calculate TWO scenarios:
     - Scenario A: Missing person is ALIVE (they inherit)
     - Scenario B: Missing person is DEAD (their share goes to others)
  
  2. Distribution approach:
     - Give each heir the MINIMUM of what they'd get in either scenario
     - Reserve the difference until the missing person's status is known
     - After judicial waiting period, presume death and redistribute

  3. The reserved amount is held by:
     - A trustee (if appointed)
     - Bayt al-Mal (public treasury)
     - The court

Waiting Period (varies by school and jurisdiction):
  - Hanafi: 90-120 years from birth
  - Maliki: 70-80 years from birth
  - Shafi'i: 4 years from disappearance (majority opinion)
  - Hanbali: 4 years from disappearance
  - Modern statutes: Often 4 years, or 1 year for disasters
"""

from fractions import Fraction
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class MissingPersonScenario:
    """Represents a calculation scenario for missing person cases."""
    condition: str          # "المفقود حي" or "المفقود ميت"
    is_alive: bool
    distribution: Dict[str, Fraction]
    base: int
    

@dataclass
class MissingPersonResult:
    """Result of missing person calculation with scenarios."""
    scenarios: List[MissingPersonScenario]
    minimum_distribution: Dict[str, Fraction]  # Safe minimum for each heir
    reserved_amount: Fraction                   # Total reserved
    reserved_for: str                           # Name of missing person
    

def identify_missing_heirs(heirs: List[Dict[str, Any]]) -> List[str]:
    """
    Identify heirs marked as missing.
    
    Args:
        heirs: List of heir dictionaries
    
    Returns:
        List of missing heir types
    """
    missing = []
    for h in heirs:
        status = h.get("status", "alive")
        if status in ("missing", "mafqud", "مفقود"):
            missing.append(h.get("heir", ""))
    return missing


def calculate_with_missing(
    heirs: List[Dict[str, Any]],
    missing_heir: str,
    calculator_func,
) -> MissingPersonResult:
    """
    Calculate inheritance with a missing person, producing two scenarios.
    
    Args:
        heirs: List of all heirs including the missing one
        missing_heir: Type of the missing heir (e.g., "ابن")
        calculator_func: Function to calculate inheritance
    
    Returns:
        MissingPersonResult with both scenarios and minimum distribution
    """
    # Scenario A: Missing person is ALIVE
    heirs_alive = [h.copy() for h in heirs]
    for h in heirs_alive:
        if h.get("heir") == missing_heir and h.get("status") in ("missing", "mafqud", "مفقود"):
            h["status"] = "alive"
    
    result_alive = calculator_func(heirs_alive)
    dist_alive = _extract_distribution(result_alive)
    
    # Scenario B: Missing person is DEAD (excluded)
    heirs_dead = [h.copy() for h in heirs if h.get("heir") != missing_heir or 
                  h.get("status") not in ("missing", "mafqud", "مفقود")]
    
    result_dead = calculator_func(heirs_dead)
    dist_dead = _extract_distribution(result_dead)
    
    # Calculate minimum for each heir
    all_heirs = set(dist_alive.keys()) | set(dist_dead.keys())
    minimum_dist = {}
    
    for heir in all_heirs:
        if heir == missing_heir:
            continue  # Skip missing person in minimum
        share_alive = dist_alive.get(heir, Fraction(0))
        share_dead = dist_dead.get(heir, Fraction(0))
        minimum_dist[heir] = min(share_alive, share_dead)
    
    # Calculate reserved amount
    total_minimum = sum(minimum_dist.values())
    reserved = Fraction(1) - total_minimum
    
    # Create scenarios
    scenarios = [
        MissingPersonScenario(
            condition="المفقود حي",
            is_alive=True,
            distribution=dist_alive,
            base=result_alive.get("base", 1),
        ),
        MissingPersonScenario(
            condition="المفقود ميت",
            is_alive=False,
            distribution=dist_dead,
            base=result_dead.get("base", 1),
        ),
    ]
    
    return MissingPersonResult(
        scenarios=scenarios,
        minimum_distribution=minimum_dist,
        reserved_amount=reserved,
        reserved_for=missing_heir,
    )


def _extract_distribution(result) -> Dict[str, Fraction]:
    """Extract distribution dictionary from calculator result."""
    if hasattr(result, "to_dict"):
        result = result.to_dict()
    
    distribution = {}
    for d in result.get("distribution", []):
        heir = d.get("heir", "")
        # Parse fraction
        share_str = d.get("share", "0")
        try:
            if "/" in str(share_str):
                parts = str(share_str).split("/")
                share = Fraction(int(parts[0]), int(parts[1]))
            else:
                share = Fraction(0)
        except (ValueError, TypeError, IndexError):
            share = Fraction(0)
        distribution[heir] = share
    
    return distribution


def format_missing_result(result: MissingPersonResult, language: str = "ar") -> str:
    """Format missing person result for display."""
    lines = []
    
    if language == "ar":
        lines.append("=" * 50)
        lines.append(f"حالة المفقود: {result.reserved_for}")
        lines.append("=" * 50)
        
        lines.append("\nالسيناريوهات:")
        for scenario in result.scenarios:
            lines.append(f"\n  {scenario.condition}:")
            for heir, share in scenario.distribution.items():
                lines.append(f"    {heir}: {share}")
        
        lines.append("\nالتوزيع الآمن (الحد الأدنى):")
        for heir, share in result.minimum_distribution.items():
            lines.append(f"  {heir}: {share}")
        
        lines.append(f"\nالمبلغ المحجوز: {result.reserved_amount}")
        
    else:
        lines.append("=" * 50)
        lines.append(f"Missing Person: {result.reserved_for}")
        lines.append("=" * 50)
        
        lines.append("\nScenarios:")
        for scenario in result.scenarios:
            status = "Alive" if scenario.is_alive else "Dead"
            lines.append(f"\n  If {status}:")
            for heir, share in scenario.distribution.items():
                lines.append(f"    {heir}: {share}")
        
        lines.append("\nSafe Distribution (Minimum):")
        for heir, share in result.minimum_distribution.items():
            lines.append(f"  {heir}: {share}")
        
        lines.append(f"\nReserved Amount: {result.reserved_amount}")
    
    return "\n".join(lines)
