"""
Validator for synthetic data.

Validates all generated examples by:
1. Parsing the question to extract heirs
2. Running the calculator
3. Comparing against expected output

Ensures 100% accuracy before training data is used.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple
import json

# Add parent to path

from qias_mawarith_rag.calculator.scalc import InheritanceCalculator
from qias_mawarith_rag.calculator.parser import MawarithParser


def validate_example(example: Dict) -> Tuple[bool, str]:
    """
    Validate a single example by parsing question and comparing to answer.
    
    This validates the full pipeline:
    1. Parse question to extract heirs
    2. Calculate using our calculator
    3. Compare against expected output
    
    Returns (is_valid, error_message)
    """
    try:
        # Method 1: Parse the question directly using the parser
        parser = MawarithParser()
        parsed = parser.parse(example)
        
        # Get heirs from parsed question
        input_heirs = [
            {"heir": h.heir_type, "count": h.count}
            for h in parsed.heirs
        ]
        
        # Also include blocked heirs in input (they were in the original question)
        for h in parsed.blocked_heirs:
            input_heirs.append({"heir": h.heir_type, "count": h.count})
        
        if not input_heirs:
            return False, "No heirs extracted from question"
        
        # Run calculator
        calc = InheritanceCalculator()
        result = calc.calculate(input_heirs)
        
        # Get expected output
        output = example.get("output", {})
        expected_shares = output.get("shares", [])
        expected_blocked = output.get("blocked", [])
        expected_awl = output.get("awl_or_radd", "لا")
        
        # Compare shares
        actual_shares = result.shares
        
        # Normalize for comparison (order-independent)
        expected_share_set = {
            (s["heir"], s.get("count", 1), s.get("fraction", "")) 
            for s in expected_shares
        }
        actual_share_set = {
            (s["heir"], s.get("count", 1), s.get("fraction", "")) 
            for s in actual_shares
        }
        
        if expected_share_set != actual_share_set:
            return False, f"Share mismatch:\n  Expected: {expected_shares}\n  Got: {actual_shares}"
        
        # Compare blocked
        actual_blocked = result.blocked
        
        expected_blocked_set = {(b["heir"], b.get("count", 1)) for b in expected_blocked}
        actual_blocked_set = {(b["heir"], b.get("count", 1)) for b in actual_blocked}
        
        if expected_blocked_set != actual_blocked_set:
            return False, f"Blocked mismatch:\n  Expected: {expected_blocked}\n  Got: {actual_blocked}"
        
        # Compare awl/radd
        actual_awl = result.awl_or_radd
        
        if expected_awl != actual_awl:
            return False, f"Awl/Radd mismatch: expected {expected_awl}, got {actual_awl}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Exception: {str(e)}"


def validate_example_output_only(example: Dict) -> Tuple[bool, str]:
    """
    Validate using only the output field (faster, doesn't parse question).
    
    Used when you want quick validation of generated data.
    """
    try:
        output = example.get("output", {})
        heirs_list = output.get("heirs", [])
        blocked_list = output.get("blocked", [])
        
        # Combine heirs and blocked for input
        all_heirs = heirs_list + blocked_list
        
        if not all_heirs:
            return False, "No heirs found"
        
        # Run calculator
        calc = InheritanceCalculator()
        result = calc.calculate(all_heirs)
        
        # Compare shares
        expected_shares = output.get("shares", [])
        actual_shares = result.shares
        
        expected_set = {(s["heir"], s.get("count", 1), s.get("fraction", "")) for s in expected_shares}
        actual_set = {(s["heir"], s.get("count", 1), s.get("fraction", "")) for s in actual_shares}
        
        if expected_set != actual_set:
            return False, "Share mismatch"
        
        # Compare blocked
        expected_blocked = output.get("blocked", [])
        actual_blocked = result.blocked
        
        expected_blocked_set = {(b["heir"], b.get("count", 1)) for b in expected_blocked}
        actual_blocked_set = {(b["heir"], b.get("count", 1)) for b in actual_blocked}
        
        if expected_blocked_set != actual_blocked_set:
            return False, "Blocked mismatch"
        
        # Compare awl/radd
        expected_awl = output.get("awl_or_radd", "لا")
        actual_awl = result.awl_or_radd
        
        if expected_awl != actual_awl:
            return False, "Awl/Radd mismatch"
        
        return True, ""
        
    except Exception as e:
        return False, f"Exception: {str(e)}"


def validate_file(filepath: str, parse_question: bool = True) -> Tuple[int, int, List[Dict]]:
    """
    Validate all examples in a JSON file.
    
    Args:
        filepath: Path to JSON file
        parse_question: If True, parse question text. If False, use output only.
    
    Returns (total, valid_count, failures)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    valid = 0
    failures = []
    
    validate_fn = validate_example if parse_question else validate_example_output_only
    
    for i, example in enumerate(data):
        is_valid, error = validate_fn(example)
        if is_valid:
            valid += 1
        else:
            failures.append({
                "index": i,
                "id": example.get("id", "unknown"),
                "question": example.get("question", "")[:100],
                "error": error,
            })
    
    return len(data), valid, failures


def validate_directory(dirpath: str, parse_question: bool = True) -> Dict[str, Any]:
    """
    Validate all JSON files in a directory.
    
    Args:
        dirpath: Directory containing JSON files
        parse_question: If True, parse question text. If False, use output only.
    
    Returns summary statistics.
    """
    dirpath = Path(dirpath)
    json_files = sorted(dirpath.glob("*.json"))
    
    total = 0
    valid = 0
    all_failures = []
    
    for filepath in json_files:
        file_total, file_valid, file_failures = validate_file(str(filepath), parse_question)
        status = "✓" if file_valid == file_total else "✗"
        print(f"{status} {filepath.name}: {file_valid}/{file_total}")
        total += file_total
        valid += file_valid
        all_failures.extend([{**f, "file": filepath.name} for f in file_failures])
    
    accuracy = (valid / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "valid": valid,
        "failures": len(all_failures),
        "accuracy": accuracy,
        "failure_details": all_failures[:20],  # First 20 failures for debugging
    }


def validate_against_train(synthetic_dir: str, train_dir: str = "train") -> Dict[str, Any]:
    """
    Validate synthetic data against original train format.
    
    Ensures synthetic data follows same structure.
    """
    
    synthetic_path = Path(synthetic_dir)
    train_path = Path(train_dir)
    
    # Check structure matches
    issues = []
    
    synth_files = list(synthetic_path.glob("*.json"))
    if not synth_files:
        issues.append("No JSON files in synthetic directory")
        return {"valid": False, "issues": issues}
    
    # Load sample from each
    with open(synth_files[0], 'r') as f:
        synth_sample = json.load(f)[0]
    
    train_files = list(train_path.glob("*.json"))
    if train_files:
        with open(train_files[0], 'r') as f:
            train_sample = json.load(f)[0]
        
        # Compare keys
        synth_keys = set(synth_sample.keys())
        train_keys = set(train_sample.keys())
        
        if synth_keys != train_keys:
            issues.append(f"Key mismatch: synth={synth_keys}, train={train_keys}")
        
        # Compare output keys
        synth_out_keys = set(synth_sample.get("output", {}).keys())
        train_out_keys = set(train_sample.get("output", {}).keys())
        
        if synth_out_keys != train_out_keys:
            issues.append(f"Output key mismatch: synth={synth_out_keys}, train={train_out_keys}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }


def main():
    """Validate synthetic data."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate synthetic inheritance data")
    parser.add_argument("path", help="Path to JSON file or directory")
    parser.add_argument("--output-only", action="store_true", 
                       help="Validate using output field only (faster)")
    parser.add_argument("--compare-train", action="store_true",
                       help="Compare format against train/ directory")
    args = parser.parse_args()
    
    path = Path(args.path)
    parse_question = not args.output_only
    
    mode = "full (parsing questions)" if parse_question else "output-only (fast)"
    print(f"Validation mode: {mode}")
    print()
    
    if path.is_file():
        total, valid, failures = validate_file(str(path), parse_question)
        print(f"\nResults: {valid}/{total} valid ({valid/total*100:.2f}%)")
        if failures:
            print("\nSample failures:")
            for f in failures[:5]:
                print(f"  #{f['index']}: {f['error']}")
    elif path.is_dir():
        result = validate_directory(str(path), parse_question)
        print()
        print("=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total examples: {result['total']}")
        print(f"Valid: {result['valid']}")
        print(f"Accuracy: {result['accuracy']:.2f}%")
        
        if result['failure_details']:
            print(f"\nSample failures ({len(result['failure_details'])} shown):")
            for f in result['failure_details'][:10]:
                print(f"  {f['file']}:{f['index']}")
                print(f"    Question: {f['question']}...")
                print(f"    Error: {f['error']}")
        
        if args.compare_train:
            print()
            print("Comparing format to train/...")
            fmt_result = validate_against_train(str(path))
            if fmt_result['valid']:
                print("✓ Format matches train/ structure")
            else:
                print("✗ Format issues:")
                for issue in fmt_result['issues']:
                    print(f"  - {issue}")


if __name__ == "__main__":
    main()
