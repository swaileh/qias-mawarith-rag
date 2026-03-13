#!/usr/bin/env python3
"""
RAG Relevance Evaluation Script
Demonstrates how to evaluate the relevance of retrieved documents to queries
"""

import json
from pathlib import Path
from src.rag_pipeline import RAGPipeline
from src.evaluation.relevance_evaluator import print_relevance_report


def main():
    """Main evaluation function"""

    print("🔍 RAG Relevance Evaluation Demo")
    print("="*50)

    # Initialize RAG pipeline
    pipeline = RAGPipeline()

    # Example inheritance law questions
    test_questions = [
        "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟",
        "مات وترك: زوجة و أم و أب و ابن و بنت. ما هو نصيب كل وريث؟",
        "ماتت وتركت: زوج و أب وابنين. ما هو نصيب كل وريث؟"
    ]

    print(f"Evaluating {len(test_questions)} test questions...\n")

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"Question {i}: {question}")
        print('='*60)

        # Query the RAG system
        result = pipeline.query(question, top_k=3)

        # Check if retrieval was successful
        if result['error']:
            print(f"❌ Error: {result['error']}")
            continue

        retrieved_docs = result['retrieved_docs']
        relevance_eval = result['relevance_evaluation']

        # Print relevance evaluation
        if relevance_eval:
            print_relevance_report(relevance_eval)
        else:
            print("⚠️  No relevance evaluation available")

        # Show retrieved documents summary
        print("\n📄 Retrieved Documents:")
        for j, doc in enumerate(retrieved_docs[:3], 1):
            title = doc.get('title', 'No title')
            score = doc.get('score', 0.0)
            rerank_score = doc.get('rerank_score', 0.0)
            print(f"  {j}. {title[:60]}... (Score: {score:.3f}, Rerank: {rerank_score:.3f})")
        print()


def evaluate_from_json(json_file_path: str):
    """Evaluate relevance for questions from a JSON file

    Args:
        json_file_path: Path to JSON file with questions
    """

    print(f"🔍 Evaluating relevance from file: {json_file_path}")

    # Load questions from JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize RAG pipeline
    pipeline = RAGPipeline()

    # Extract questions (assuming QIAS 2026 format)
    questions = []
    if isinstance(data, list):
        # List of question objects
        questions = [item.get('question', '') for item in data if 'question' in item]
    elif isinstance(data, dict) and 'questions' in data:
        # Dict with questions key
        questions = [q.get('question', '') for q in data['questions']]

    print(f"Found {len(questions)} questions in file")

    # Evaluate first 5 questions as demo
    evaluation_results = []

    for i, question in enumerate(questions[:5]):
        print(f"\nEvaluating question {i+1}: {question[:80]}...")

        # Query and get relevance evaluation
        result = pipeline.query(question, top_k=3)

        if not result['error'] and result['relevance_evaluation']:
            eval_result = result['relevance_evaluation']
            evaluation_results.append(eval_result)

            # Print summary
            assessment = eval_result['overall_assessment']
            print(f"  Quality: {assessment['quality_level']} ({assessment['quality_score']:.3f})")

    # Calculate batch statistics
    if evaluation_results:
        avg_quality = sum(r['overall_assessment']['quality_score'] for r in evaluation_results) / len(evaluation_results)

        quality_dist = {}
        for r in evaluation_results:
            level = r['overall_assessment']['quality_level']
            quality_dist[level] = quality_dist.get(level, 0) + 1

        print("\n📊 Batch Evaluation Summary:")
        print(f"  Average Quality Score: {avg_quality:.3f}")
        print(f"  Quality Distribution: {quality_dist}")

        # Save detailed results
        output_file = Path(json_file_path).stem + "_relevance_evaluation.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'evaluation_results': evaluation_results,
                'summary': {
                    'total_questions': len(evaluation_results),
                    'avg_quality_score': avg_quality,
                    'quality_distribution': quality_dist
                }
            }, f, ensure_ascii=False, indent=2)

        print(f"\n📁 Detailed results saved to: {output_file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Evaluate from JSON file
        json_file = sys.argv[1]
        if Path(json_file).exists():
            evaluate_from_json(json_file)
        else:
            print(f"❌ File not found: {json_file}")
    else:
        # Run demo with test questions
        main()