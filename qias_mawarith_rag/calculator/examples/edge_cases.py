#!/usr/bin/env python3
"""
Example: Edge Cases - Missing, Pregnancy, Successive Deaths

This script demonstrates the edge case handlers in mawarith:
- المفقود (Missing Person)
- الحمل (Pregnancy)
- المناسخات (Successive Deaths)
"""


from mawarith.scalc import InheritanceCalculator
from mawarith.edge import (
    identify_missing_heirs,
    calculate_pregnancy_scenarios,
    calculate_munasakhaat,
)


# Calculator function wrapper
calc = InheritanceCalculator()
def calc_func(heirs):
    return calc.calculate(heirs).to_dict()


def example_missing_person():
    """Example: Missing person calculation."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: المفقود (Missing Person)")
    print("=" * 60)
    
    heirs = [
        {"heir": "زوجة", "count": 1},
        {"heir": "ابن", "count": 1, "status": "missing"},
        {"heir": "بنت", "count": 2},
    ]
    
    missing = identify_missing_heirs(heirs)
    print(f"\nIdentified Missing Heirs: {missing}")
    
    print("""
Approach:
  Two scenarios are calculated:
  1. If missing son is ALIVE - he inherits
  2. If missing son is DEAD - daughters inherit more
  
  Each heir receives the MINIMUM of the two scenarios.
  The difference is RESERVED until status is known.
""")


def example_pregnancy():
    """Example: Pregnancy calculation."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: الحمل (Pregnancy)")
    print("=" * 60)
    
    # Heirs without the unborn child
    heirs = [
        {"heir": "زوجة", "count": 1},  # This wife is pregnant
        {"heir": "ابن", "count": 1},   # Existing son
    ]
    
    result = calculate_pregnancy_scenarios(heirs, max_children=2, calculator_func=calc_func)
    
    print(f"\nNumber of scenarios calculated: {len(result.scenarios)}")
    print(f"Maximum reserve for unborn: {result.maximum_reserve}")
    print(f"Recommended reserve scenario: {result.recommended_scenario}")
    
    print("\nScenarios:")
    for scenario in result.scenarios[:3]:  # Show first 3
        print(f"  - {scenario.description}: unborn share = {scenario.unborn_share}")
    
    print("\nMinimum safe distribution for existing heirs:")
    for heir, share in result.minimum_distribution.items():
        print(f"  {heir}: {share}")


def example_successive_deaths():
    """Example: Successive deaths (munasakhaat) calculation."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: المناسخات (Successive Deaths)")
    print("=" * 60)
    
    print("""
Scenario:
  1. Ahmad dies leaving: Wife, Son (Khalid), Daughter (Sara)
  2. Before distribution, Khalid dies leaving: his Wife, his Son
  
  The son Khalid's share must be redistributed to his heirs.
""")
    
    first_heirs = [
        {"heir": "زوجة", "count": 1},  # Ahmad's wife
        {"heir": "ابن", "count": 1},    # Khalid (who dies)
        {"heir": "بنت", "count": 1},    # Sara
    ]
    
    successive = [
        {
            "heir_name": "ابن",  # Khalid
            "heirs": [
                {"heir": "زوجة", "count": 1},  # Khalid's wife
                {"heir": "ابن", "count": 1},    # Khalid's son
            ]
        }
    ]
    
    result = calculate_munasakhaat(
        first_decedent="أحمد",
        first_heirs=first_heirs,
        successive_deaths=successive,
        calculator_func=calc_func,
    )
    
    print(f"\nDeath chain length: {len(result.death_chain)}")
    print(f"Combined base: {result.combined_base}")
    
    print("\nFinal distribution of Ahmad's estate:")
    for heir, share in result.final_distribution.items():
        integer_share = int(share * result.combined_base)
        print(f"  {heir}: {share} = {integer_share}/{result.combined_base}")


def main():
    print("=" * 60)
    print("MAWARITH EDGE CASES EXAMPLES")
    print("=" * 60)
    
    example_missing_person()
    example_pregnancy()
    example_successive_deaths()
    
    print("\n" + "=" * 60)
    print("ALL EDGE CASE EXAMPLES COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
