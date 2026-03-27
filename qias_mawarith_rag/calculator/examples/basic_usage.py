#!/usr/bin/env python3
"""
Example: Basic Usage of MiraathCase

This script demonstrates the basic usage of the MiraathCase unified API
for calculating Islamic inheritance shares.
"""


from mawarith import MiraathCase


def main():
    print("=" * 60)
    print("MAWARITH CALCULATOR v2.0 - BASIC EXAMPLES")
    print("=" * 60)
    
    # Example 1: Quick one-liner
    print("\n" + "=" * 50)
    print("Example 1: Quick Method (One-liner)")
    print("=" * 50)
    print("\nHeirs: Husband + Mother + 2 Daughters")
    
    result = MiraathCase.quick(["زوج", "أم", ("بنت", 2)])
    print(result.summary("ar"))
    
    # Example 2: Chained method calls
    print("\n" + "=" * 50)
    print("Example 2: Chained Method Calls")
    print("=" * 50)
    print("\nHeirs: 2 Wives + Son + 3 Daughters")
    
    case = MiraathCase()
    case.add_heir("زوجة", count=2)
    case.add_heir("ابن")
    case.add_heir("بنت", count=3)
    result = case.calculate()
    print(result.summary("en"))
    
    # Example 3: Special case detection
    print("\n" + "=" * 50)
    print("Example 3: Special Case Detection (العمرية)")
    print("=" * 50)
    print("\nHeirs: Husband + Mother + Father")
    
    result = MiraathCase.quick(["زوج", "أم", "أب"])
    print(f"Special Case Detected: {result.special_case}")
    print(result.summary("ar"))
    
    # Example 4: Awl case (shares exceed estate)
    print("\n" + "=" * 50)
    print("Example 4: Awl Case (عول)")
    print("=" * 50)
    print("\nHeirs: Husband + Mother + 2 Full Sisters")
    
    result = MiraathCase.quick(["زوج", "أم", ("أخت شقيقة", 2)])
    print(f"Awl Applied: {result.awl_applied}")
    print(result.summary("ar"))
    
    # Example 5: JSON output
    print("\n" + "=" * 50)
    print("Example 5: JSON Output")
    print("=" * 50)
    
    result = MiraathCase.quick(["زوجة", "ابن"])
    output = result.to_dict()
    print(f"Base: {output['base']}")
    print(f"Distribution: {len(output['distribution'])} heirs")
    print(f"Madhab: {output['madhab']}")
    
    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
