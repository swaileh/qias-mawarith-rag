"""
Example Training Script
Demonstrates complete training workflow
"""

import json
from pathlib import Path

from qias_mawarith_rag.pipeline import RAGPipeline
from qias_mawarith_rag.training.feedback_loop import FeedbackLoop


def main():
    """Run complete training workflow"""
    
    print("="*80)
    print("QIAS RAG SYSTEM - TRAINING WORKFLOW")
    print("="*80)
    
    # Step 1: Initialize pipeline
    print("\n[1/5] Initializing RAG Pipeline...")
    pipeline = RAGPipeline()
    
    # Step 2: Build knowledge base (if PDFs available)
    print("\n[2/5] Building Knowledge Base...")
    pdf_dir = "data/pdfs"
    if Path(pdf_dir).exists():
        pipeline.build_knowledge_base(pdf_dir)
    else:
        print(f"⚠️ No PDFs found in {pdf_dir}, skipping knowledge base building")
    
    # Step 3: Load development dataset
    print("\n[3/5] Loading Development Dataset...")
    dataset_path = "../qias_shared_task_2026/data/jsonl/mawarith/qias2025_almawarith_part1.json"
    
    if not Path(dataset_path).exists():
        print(f"⚠️ Dataset not found at {dataset_path}")
        print("Please adjust the path to your QIAS dataset")
        return
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        full_dataset = json.load(f)
    
    # Use subset for training
    dev_set = full_dataset[:20]  # Adjust size as needed
    print(f"Using {len(dev_set)} cases for training")
    
    # Step 4: Run iterative improvement
    print("\n[4/5] Running Iterative Improvement...")
    feedback = FeedbackLoop()
    
    history = feedback.iterative_improvement(
        pipeline=pipeline,
        dataset=dev_set,
        max_iterations=3
    )
    
    # Step 5: Display results
    print("\n[5/5] Training Complete!")
    print("\n" + "="*80)
    print("TRAINING RESULTS")
    print("="*80)
    
    for iteration in history['iterations']:
        print(f"\nIteration {iteration['iteration']}:")
        print(f"  Success Rate: {iteration['success_rate']*100:.2f}%")
        
        error_analysis = iteration['error_analysis']
        print(f"  Parsing Failures: {error_analysis['parsing_failures']}")
        print(f"  Validation Failures: {error_analysis['validation_failures']}")
        print(f"  Low Thinking Quality: {error_analysis['low_thinking_quality']}")
    
    print(f"\n{'='*80}")
    print(f"Best Performance: {history['best_score']*100:.2f}% (Iteration {history['best_iteration']})")
    print(f"{'='*80}")
    
    # Save history
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "training_history.json", 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    print(f"\nTraining history saved to: {output_dir / 'training_history.json'}")
    
    # Next steps
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review error_analysis_iter_*.json for detailed error patterns")
    print("2. Apply suggested improvements from each iteration")
    print("3. Re-run training with updated configuration")
    print("4. Once satisfied, run full evaluation on test set")
    print("5. If >99% precision achieved, deploy to production")
    print("\nFor fine-tuning (optional):")
    print("  python -c 'from qias_mawarith_rag.training.fine_tune import FineTuner; ft=FineTuner(); ft.save_training_script()'")


if __name__ == "__main__":
    main()
