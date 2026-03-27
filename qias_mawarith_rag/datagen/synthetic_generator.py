#!/usr/bin/env python3
"""
Generate synthetic training data for QIAS 2026.

Usage (from project root):
    python -m qias_mawarith_rag.datagen.synthetic_generator [--output-dir DIR] [--count N]
"""

import argparse
from pathlib import Path

from qias_mawarith_rag.datagen.generator import FiqhDataGenerator
from qias_mawarith_rag.datagen.exporter import export_to_train_format


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Mawarith training data")
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Output directory (default: <project_root>/data/synthetic/)",
    )
    parser.add_argument("--count", type=int, default=10000, help="Total target examples (default: 10000)")
    parser.add_argument("--seed", type=int, default=2026, help="Random seed (default: 2026)")
    parser.add_argument("--unique", action="store_true", default=True, help="Deduplicate heir combinations")
    args = parser.parse_args()

    # Resolve output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(__file__).resolve().parent.parent.parent / "data" / "synthetic"

    print("=" * 60)
    print(f"GENERATING ~{args.count} SYNTHETIC TRAINING EXAMPLES")
    print(f"Output: {output_dir}")
    print("=" * 60)
    print()

    gen = FiqhDataGenerator(seed=args.seed)

    # Split into basic / advanced / edge  (50% / 35% / 15%)
    n_basic = int(args.count * 0.50)
    n_advanced = int(args.count * 0.35)
    n_edge = int(args.count * 0.15)

    print(f"Step 1/3: Generating {n_basic} basic examples...")
    basic = gen.generate_batch(n_basic, difficulty="basic", unique=args.unique)
    print()

    print(f"Step 2/3: Generating {n_advanced} advanced examples...")
    advanced = gen.generate_batch(n_advanced, difficulty="advanced", unique=args.unique)
    print()

    print(f"Step 3/3: Generating {n_edge} edge case examples...")
    edges = gen.generate_edge_cases(n_edge, unique=args.unique)
    print()

    all_examples = basic + advanced + edges
    print(f"Total examples generated: {len(all_examples)}")
    print()

    print(f"Exporting to {output_dir}/...")
    export_to_train_format(all_examples, str(output_dir))
    print()
    print("Done!")


if __name__ == "__main__":
    main()