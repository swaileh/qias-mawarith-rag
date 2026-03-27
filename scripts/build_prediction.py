#!/usr/bin/env python3
"""
Build prediction.json for QIAS challenge submission from batch results.

Reads *_results.jsonl from results directory, extracts model predictions,
and outputs a valid prediction.json with structure: [{id, question, output}, ...]

Usage:
  python build_prediction.py
  python build_prediction.py --results-dir ./results --output /mnt/salah/qias/prediction.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


# Minimal valid output when model_prediction is invalid or missing
EMPTY_OUTPUT = {
    "heirs": [],
    "blocked": [],
    "shares": [],
    "awl_or_radd": "لا",
    "post_tasil": {"total_shares": 0, "distribution": []},
}


def sanitize_output(pred: Any) -> Dict[str, Any]:
    """Ensure output conforms to QIAS schema. Remove invalid keys, fix types."""
    if not pred or not isinstance(pred, dict):
        return EMPTY_OUTPUT.copy()

    # Reject thinking_text-only output
    if set(pred.keys()) == {"thinking_text"}:
        return EMPTY_OUTPUT.copy()

    # Build sanitized output with required keys
    out: Dict[str, Any] = {
        "heirs": _sanitize_list(pred.get("heirs"), ["heir", "count"]),
        "blocked": _sanitize_list(pred.get("blocked"), ["heir", "count"]),
        "shares": _sanitize_shares(pred.get("shares")),
        "awl_or_radd": _sanitize_awl_radd(pred.get("awl_or_radd")),
        "post_tasil": _sanitize_post_tasil(pred.get("post_tasil")),
    }

    # Optional: include tasil_stage if valid
    tasil = pred.get("tasil_stage")
    if tasil and isinstance(tasil, dict) and "asl" in tasil and "distribution" in tasil:
        out["tasil_stage"] = {
            "asl": int(tasil["asl"]) if isinstance(tasil.get("asl"), (int, float)) else tasil["asl"],
            "distribution": _sanitize_tasil_dist(tasil.get("distribution", [])),
        }

    return out


def _sanitize_list(items: Any, required_keys: List[str]) -> List[Dict[str, Any]]:
    """Sanitize heirs/blocked list."""
    if not isinstance(items, list):
        return []
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if not all(k in item for k in required_keys):
            continue
        clean = {k: item[k] for k in required_keys}
        if "count" in clean and not isinstance(clean["count"], int):
            try:
                clean["count"] = int(clean["count"])
            except (ValueError, TypeError):
                continue
        result.append(clean)
    return result


def _sanitize_shares(items: Any) -> List[Dict[str, Any]]:
    """Sanitize shares list (heir, count, fraction)."""
    if not isinstance(items, list):
        return []
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if "heir" not in item or "count" not in item or "fraction" not in item:
            continue
        clean = {
            "heir": str(item["heir"]),
            "count": int(item["count"]) if isinstance(item.get("count"), (int, float)) else item["count"],
            "fraction": str(item["fraction"]),
        }
        result.append(clean)
    return result


def _sanitize_awl_radd(val: Any) -> str:
    """Ensure awl_or_radd is valid."""
    if val in ("لا", "عول", "رد"):
        return val
    return "لا"


def _sanitize_post_tasil(pt: Any) -> Dict[str, Any]:
    """Sanitize post_tasil structure."""
    if not pt or not isinstance(pt, dict):
        return {"total_shares": 0, "distribution": []}

    dist = pt.get("distribution", [])
    if not isinstance(dist, list):
        dist = []

    clean_dist = []
    for d in dist:
        if not isinstance(d, dict) or "heir" not in d or "count" not in d:
            continue
        entry = {
            "heir": str(d["heir"]),
            "count": int(d["count"]) if isinstance(d.get("count"), (int, float)) else d["count"],
            "per_head_shares": str(d.get("per_head_shares", "0")),
            "per_head_percent": float(d.get("per_head_percent", 0)) if isinstance(d.get("per_head_percent"), (int, float)) else 0,
        }
        clean_dist.append(entry)

    total = pt.get("total_shares", 0)
    if not isinstance(total, (int, float)):
        try:
            total = int(total)
        except (ValueError, TypeError):
            total = 0

    return {"total_shares": int(total), "distribution": clean_dist}


def _sanitize_tasil_dist(dist: Any) -> List[Dict[str, Any]]:
    """Sanitize tasil_stage distribution."""
    if not isinstance(dist, list):
        return []
    result = []
    for d in dist:
        if not isinstance(d, dict) or "heir" not in d or "count" not in d:
            continue
        result.append({
            "heir": str(d["heir"]),
            "count": int(d["count"]) if isinstance(d.get("count"), (int, float)) else d["count"],
            "shares": str(d.get("shares", "0")),
        })
    return result


def load_results(results_dir: Path) -> List[Dict[str, Any]]:
    """Load and merge all *_results.jsonl files, sorted by question_id."""
    all_rows = []
    for p in sorted(results_dir.glob("*_results.jsonl")):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    all_rows.append(row)
                except json.JSONDecodeError as e:
                    print(f"Warning: Skip invalid JSON in {p}: {e}", file=sys.stderr)

    all_rows.sort(key=lambda r: r.get("question_id", 0))
    return all_rows


def build_predictions(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert result rows to submission format."""
    predictions = []
    for row in rows:
        pred = {
            "id": row.get("id", ""),
            "question": row.get("question", ""),
            "output": sanitize_output(row.get("model_prediction")),
        }
        predictions.append(pred)
    return predictions


def main():
    parser = argparse.ArgumentParser(description="Build prediction.json from RAG batch results")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path(__file__).parent / "results",
        help="Directory containing *_results.jsonl files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/mnt/salah/qias/prediction.json"),
        help="Output prediction.json path",
    )
    args = parser.parse_args()

    if not args.results_dir.exists():
        print(f"Error: Results directory not found: {args.results_dir}", file=sys.stderr)
        sys.exit(1)

    rows = load_results(args.results_dir)
    if not rows:
        print(f"Error: No results found in {args.results_dir}", file=sys.stderr)
        sys.exit(1)

    predictions = build_predictions(rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)

    # Validate output is loadable
    with open(args.output, "r", encoding="utf-8") as f:
        json.load(f)

    print(f"Wrote {len(predictions)} predictions to {args.output}")


if __name__ == "__main__":
    main()
