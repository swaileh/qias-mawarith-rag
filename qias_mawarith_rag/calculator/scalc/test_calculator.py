#!/usr/bin/env python3
"""
Test script for the Mawarith Symbolic Calculator.
Validates the calculator against examples from the dataset.
"""

import json
from pathlib import Path

# Add parent to path for imports

from mawarith.scalc import InheritanceCalculator


def test_basic_cases():
    """Test basic inheritance cases."""
    calc = InheritanceCalculator()
    
    print("=" * 60)
    print("TEST 1: زوجة + ابن + بنت")
    print("=" * 60)
    
    result = calc.calculate([
        {"heir": "زوجة", "count": 1},
        {"heir": "ابن", "count": 1},
        {"heir": "بنت", "count": 1},
    ])
    
    print(f"Active Heirs: {result.heirs}")
    print(f"Blocked: {result.blocked}")
    print(f"Awl/Radd: {result.awl_or_radd}")
    print(f"Final Base (أصل المسألة): {result.tasil_stage['asl']}")
    print("\nDistribution:")
    for d in result.post_tasil['distribution']:
        print(f"  {d['heir']}: {d['per_head_shares']} = {d['per_head_percent']}%")
    
    print("\n" + "=" * 60)
    print("TEST 2: أب + أم + زوج (العمريتان)")
    print("=" * 60)
    
    result = calc.calculate([
        {"heir": "زوج", "count": 1},
        {"heir": "أب", "count": 1},
        {"heir": "أم", "count": 1},
    ])
    
    print(f"Active Heirs: {result.heirs}")
    print(f"Awl/Radd: {result.awl_or_radd}")
    print(f"Final Base: {result.tasil_stage['asl']}")
    print("\nDistribution:")
    for d in result.post_tasil['distribution']:
        print(f"  {d['heir']}: {d['per_head_shares']} = {d['per_head_percent']}%")
    
    print("\n" + "=" * 60)
    print("TEST 3: Complex case with blocking")
    print("=" * 60)
    
    result = calc.calculate([
        {"heir": "بنت", "count": 2},
        {"heir": "أخت شقيقة", "count": 1},
        {"heir": "عم شقيق", "count": 2},
        {"heir": "أخ لأم", "count": 1},
    ])
    
    print(f"Active Heirs: {result.heirs}")
    print(f"Blocked: {result.blocked}")
    print(f"Awl/Radd: {result.awl_or_radd}")
    print(f"Final Base: {result.tasil_stage['asl']}")
    print("\nDistribution:")
    for d in result.post_tasil['distribution']:
        print(f"  {d['heir']}: {d['per_head_shares']} = {d['per_head_percent']}%")
    
    print("\n" + "=" * 60)
    print("TEST 4: From dataset example")
    print("=" * 60)
    
    # From the dataset
    result = calc.calculate([
        {"heir": "بنت ابن", "count": 4},
        {"heir": "أخت شقيقة", "count": 2},
        {"heir": "ابن ابن عم لأب", "count": 4},
        {"heir": "أخت لأم", "count": 1},
        {"heir": "عم الأب", "count": 5},
    ])
    
    print(f"Active Heirs: {result.heirs}")
    print(f"Blocked: {result.blocked}")
    print(f"Awl/Radd: {result.awl_or_radd}")
    print(f"Final Base: {result.tasil_stage['asl']}")
    print("\nDistribution:")
    for d in result.post_tasil['distribution']:
        print(f"  {d['heir']}: {d['per_head_shares']} = {d['per_head_percent']}%")
    
    print("\n" + "=" * 60)
    print("TEST 5: Natural language parsing")
    print("=" * 60)
    
    question = "مات وترك: أربع بنات ابن و أختان شقيقتان و أربعة أبناء ابن عم لأب و أخت لأم و خمسة أعمام الأب لأب. ما هو نصيب كل وريث؟"
    result = calc.calculate_from_question(question)
    
    print(f"Question: {question[:50]}...")
    print(f"Active Heirs: {result.heirs}")
    print(f"Blocked: {result.blocked}")


def test_against_dataset():
    """Test against actual dataset examples."""
    dataset_path = Path(__file__).parent.parent.parent / "train" / "qias2025_almawarith_part2.json"
    
    if not dataset_path.exists():
        print(f"Dataset not found at: {dataset_path}")
        return
    
    print("\n" + "=" * 60)
    print("TESTING AGAINST DATASET")
    print("=" * 60)
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    calc = InheritanceCalculator()
    
    # Test first 5 examples
    correct = 0
    total = min(5, len(data))
    
    for i, example in enumerate(data[:total]):
        question = example['question']
        expected = example['output']
        
        # Parse heirs from the expected output
        heirs_input = [{"heir": h["heir"], "count": h["count"]} 
                       for h in expected.get("heirs", []) + expected.get("blocked", [])]
        
        if not heirs_input:
            continue
        
        result = calc.calculate(heirs_input)
        
        # Compare results
        expected_asl = expected.get("tasil_stage", {}).get("asl", 0)
        actual_asl = result.tasil_stage["asl"]
        
        expected_heirs = set(h["heir"] for h in expected.get("heirs", []))
        actual_heirs = set(h["heir"] for h in result.heirs)
        
        heirs_match = expected_heirs == actual_heirs
        asl_match = expected_asl == actual_asl
        
        status = "✓" if (heirs_match and asl_match) else "✗"
        if heirs_match and asl_match:
            correct += 1
        
        print(f"\n{status} Example {i+1}:")
        print(f"  Expected heirs: {expected_heirs}")
        print(f"  Actual heirs: {actual_heirs}")
        print(f"  Expected ASL: {expected_asl}, Actual: {actual_asl}")
    
    print(f"\n\nAccuracy: {correct}/{total} ({100*correct/total:.1f}%)")


if __name__ == "__main__":
    test_basic_cases()
    test_against_dataset()
