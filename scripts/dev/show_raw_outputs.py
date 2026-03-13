#!/usr/bin/env python3
"""
Script to display all raw outputs from evaluation results
Add this as a new cell in your notebook after loading results
"""

import json
from pathlib import Path

# Define paths (adjust as needed)
output_base_dir = '/content/drive/MyDrive/QIAS26/qias_rag_thinking/val_results_from pdf_only'

# Find all result files
result_files = list(Path(output_base_dir).glob('*_results.json'))
print(f'Found {len(result_files)} result files:')

for result_file in result_files:
    print(f'\n{"="*60}')
    print(f'📄 Raw outputs from: {result_file.name}')
    print(f'{"="*60}')

    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)

    print(f'Total questions: {len(results)}')

    # Show raw outputs for all questions
    for i, result in enumerate(results):
        print(f"\n--- Question {result['question_id']} ---")
        print(f"Question: {result['question']}")
        print(f"Raw output ({len(result['raw_response'])} chars):")
        print(result['raw_response'])
        print("-" * 80)

        # Optional: limit output for readability
        if i >= 4:  # Show first 5 questions only
            print(f"\n... (showing first 5 questions, {len(results)-5} more available)")
            break

print(f'\n✅ Raw outputs displayed for all result files')