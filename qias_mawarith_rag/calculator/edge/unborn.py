"""
الحمل (Haml) - Pregnancy/Unborn Heir Handler

Handles inheritance cases where the decedent's wife is pregnant.
The unborn child has inheritance rights if born alive.

Islamic Fiqh Approach:
  1. The fetus is entitled to inherit if born alive
  2. Sex and number of children are unknown at time of calculation
  3. Multiple scenarios must be calculated to reserve maximum impact
  
Reserve Calculation:
  Calculate shares assuming the WORST case for other heirs:
  - Assume maximum number of children (typically 4)
  - Assume the sex that most reduces others' shares
  - Reserve that amount until birth

Possible Scenarios:
  1. No live birth (miscarriage/stillborn) - fetus gets nothing
  2. One male child
  3. One female child
  4. Two male children
  5. Two female children
  6. One male + one female
  7. Multiple births (up to 4)

The reserve is the maximum possible share for the unborn heir(s).
"""

from fractions import Fraction
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class PregnancyScenario:
    """Represents a calculation scenario for pregnancy cases."""
    description: str          # e.g., "ولد ذكر واحد"
    children: List[Dict]      # e.g., [{"heir": "ابن", "count": 1}]
    distribution: Dict[str, Fraction]
    base: int
    unborn_share: Fraction    # Total share for unborn


@dataclass
class PregnancyResult:
    """Result of pregnancy calculation with all scenarios."""
    scenarios: List[PregnancyScenario]
    minimum_distribution: Dict[str, Fraction]  # Safe minimum for each heir
    maximum_reserve: Fraction                   # Max possible for unborn
    recommended_scenario: str                   # Which scenario to reserve for


def calculate_pregnancy_scenarios(
    heirs: List[Dict[str, Any]],
    max_children: int,
    calculator_func,
) -> PregnancyResult:
    """
    Calculate all pregnancy scenarios and determine safe distribution.
    
    Args:
        heirs: List of heirs (excluding the unborn)
        max_children: Maximum number of children to consider (default 4)
        calculator_func: Function to calculate inheritance
    
    Returns:
        PregnancyResult with all scenarios and minimum distribution
    """
    scenarios = []
    
    # Scenario 0: No live birth
    result_none = calculator_func(heirs)
    dist_none = _extract_distribution(result_none)
    scenarios.append(PregnancyScenario(
        description="لا ولادة حية",
        children=[],
        distribution=dist_none,
        base=result_none.get("base", 1) if hasattr(result_none, "get") else 1,
        unborn_share=Fraction(0),
    ))
    
    # Generate child combinations
    child_combinations = _generate_combinations(max_children)
    
    for combo in child_combinations:
        desc = _describe_combination(combo)
        
        # Add unborn children to heirs
        test_heirs = heirs.copy()
        for child_type, count in combo.items():
            if count > 0:
                test_heirs.append({"heir": child_type, "count": count})
        
        result = calculator_func(test_heirs)
        dist = _extract_distribution(result)
        
        # Calculate unborn share
        unborn_share = Fraction(0)
        for child_type in ("ابن", "بنت"):
            if child_type in dist:
                unborn_share += dist[child_type]
        
        scenarios.append(PregnancyScenario(
            description=desc,
            children=[{"heir": k, "count": v} for k, v in combo.items() if v > 0],
            distribution=dist,
            base=result.get("base", 1) if hasattr(result, "get") else 1,
            unborn_share=unborn_share,
        ))
    
    # Find minimum for each existing heir
    existing_heirs = set()
    for h in heirs:
        existing_heirs.add(h.get("heir", ""))
    
    minimum_dist = {}
    for heir in existing_heirs:
        min_share = Fraction(1)  # Start with maximum
        for scenario in scenarios:
            share = scenario.distribution.get(heir, Fraction(0))
            min_share = min(min_share, share)
        minimum_dist[heir] = min_share
    
    # Find maximum reserve (worst case for existing heirs)
    max_reserve = Fraction(0)
    recommended = "لا ولادة حية"
    for scenario in scenarios:
        if scenario.unborn_share > max_reserve:
            max_reserve = scenario.unborn_share
            recommended = scenario.description
    
    return PregnancyResult(
        scenarios=scenarios,
        minimum_distribution=minimum_dist,
        maximum_reserve=max_reserve,
        recommended_scenario=recommended,
    )


def _generate_combinations(max_children: int) -> List[Dict[str, int]]:
    """Generate all possible child combinations up to max."""
    combinations = []
    
    for total in range(1, max_children + 1):
        for males in range(0, total + 1):
            females = total - males
            combo = {}
            if males > 0:
                combo["ابن"] = males
            if females > 0:
                combo["بنت"] = females
            if combo:
                combinations.append(combo)
    
    return combinations


def _describe_combination(combo: Dict[str, int]) -> str:
    """Create Arabic description of child combination."""
    parts = []
    
    males = combo.get("ابن", 0)
    females = combo.get("بنت", 0)
    
    if males == 1:
        parts.append("ولد ذكر واحد")
    elif males == 2:
        parts.append("ولدان ذكران")
    elif males > 2:
        parts.append(f"{males} أولاد ذكور")
    
    if females == 1:
        parts.append("بنت واحدة")
    elif females == 2:
        parts.append("بنتان")
    elif females > 2:
        parts.append(f"{females} بنات")
    
    return " و ".join(parts) if parts else "لا أولاد"


def _extract_distribution(result) -> Dict[str, Fraction]:
    """Extract distribution dictionary from calculator result."""
    if hasattr(result, "to_dict"):
        result = result.to_dict()
    elif not isinstance(result, dict):
        return {}
    
    distribution = {}
    for d in result.get("distribution", []):
        heir = d.get("heir", "")
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


def format_pregnancy_result(result: PregnancyResult, language: str = "ar") -> str:
    """Format pregnancy result for display."""
    lines = []
    
    if language == "ar":
        lines.append("=" * 50)
        lines.append("حالة الحمل")
        lines.append("=" * 50)
        
        lines.append(f"\nعدد السيناريوهات: {len(result.scenarios)}")
        lines.append(f"أقصى احتياطي: {result.maximum_reserve}")
        lines.append(f"السيناريو الموصى به للاحتياطي: {result.recommended_scenario}")
        
        lines.append("\nالتوزيع الآمن (الحد الأدنى للورثة الحاليين):")
        for heir, share in result.minimum_distribution.items():
            lines.append(f"  {heir}: {share}")
        
    else:
        lines.append("=" * 50)
        lines.append("PREGNANCY CASE")
        lines.append("=" * 50)
        
        lines.append(f"\nNumber of scenarios: {len(result.scenarios)}")
        lines.append(f"Maximum reserve: {result.maximum_reserve}")
        lines.append(f"Recommended reserve scenario: {result.recommended_scenario}")
        
        lines.append("\nSafe Distribution (Minimum for existing heirs):")
        for heir, share in result.minimum_distribution.items():
            lines.append(f"  {heir}: {share}")
    
    return "\n".join(lines)
