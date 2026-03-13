"""
QIAS RAG Training Script for Google Colab
Implements the complete training workflow from TRAINING_GUIDE.md

Steps:
1. Build knowledge base from PDFs
2. Run initial evaluation
3. Analyze errors with feedback loop
4. Apply improvements
5. Run iterative improvement loop
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# ============================================================================
# STEP 0: Setup and Imports
# ============================================================================

def setup_environment():
    """Setup the environment for training"""
    print("="*80)
    print("QIAS RAG TRAINING - Following TRAINING_GUIDE.md")
    print("="*80)
    print()
    
    # Check if running in Colab
    try:
        from google.colab import drive
        IN_COLAB = True
        print("✓ Running in Google Colab")
    except ImportError:
        IN_COLAB = False
        print("✓ Running in local environment")
    
    return IN_COLAB

def install_dependencies():
    """Install required packages"""
    print("\n--- Installing Dependencies ---")
    
    packages = [
        "chromadb>=0.5.0",
        "sentence-transformers>=3.0.0",
        "PyMuPDF>=1.25.0",
        "pdfplumber>=0.11.0",
        "arabic-reshaper>=3.0.0",
        "python-bidi>=0.6.0",
        "rank-bm25>=0.2.0",
        "transformers>=4.40.0",
        "pydantic>=2.0.0",
        "PyYAML>=6.0.0",
        "bitsandbytes>=0.45.0",
        "accelerate>=1.0.0"
    ]
    
    for package in packages:
        print(f"  Installing {package}...")
        os.system(f"pip install -q {package}")
    
    print("✓ Dependencies installed")

# ============================================================================
# STEP 1: Build Knowledge Base
# ============================================================================

def step1_build_knowledge_base(pipeline, pdf_directory: str) -> Dict[str, Any]:
    """
    Step 1: Build knowledge base from PDFs
    
    From TRAINING_GUIDE.md:
    - Process PDFs in the data directory
    - Create vector embeddings
    - Build BM25 index for hybrid search
    """
    print("\n" + "="*80)
    print("STEP 1: Building Knowledge Base")
    print("="*80)
    
    # Check for PDFs
    pdf_path = Path(pdf_directory)
    if not pdf_path.exists():
        print(f"✗ PDF directory not found: {pdf_directory}")
        return {'status': 'failed', 'error': 'PDF directory not found'}
    
    pdf_files = list(pdf_path.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"  • {pdf.name} ({size_mb:.2f} MB)")
    
    if not pdf_files:
        print("✗ No PDF files found!")
        return {'status': 'failed', 'error': 'No PDF files found'}
    
    # Build knowledge base
    print("\nProcessing PDFs and building knowledge base...")
    try:
        pipeline.build_knowledge_base(str(pdf_directory))
        
        # Get stats
        stats = pipeline.vector_store.get_collection_stats()
        print("\n✓ Knowledge base built successfully!")
        print(f"\nKnowledge Base Statistics:")
        print(f"  Total documents: {stats.get('total_documents', 0)}")
        print(f"  Sample sources: {stats.get('sample_sources', [])}")
        
        return {
            'status': 'success',
            'num_pdfs': len(pdf_files),
            'stats': stats
        }
    except Exception as e:
        print(f"✗ Error building knowledge base: {e}")
        return {'status': 'failed', 'error': str(e)}

# ============================================================================
# STEP 2: Run Initial Evaluation
# ============================================================================

def step2_initial_evaluation(pipeline, dataset: List[Dict], 
                             num_samples: int = 10) -> Dict[str, Any]:
    """
    Step 2: Run initial evaluation on dev set
    
    From TRAINING_GUIDE.md:
    - Load dev dataset
    - Run batch query
    - Calculate baseline metrics
    """
    print("\n" + "="*80)
    print("STEP 2: Running Initial Evaluation (Baseline)")
    print("="*80)
    
    # Use subset for faster evaluation
    eval_subset = dataset[:num_samples]
    print(f"Evaluating on {len(eval_subset)} questions...")
    
    try:
        # Run batch query
        results = pipeline.batch_query(eval_subset, save_results=True)
        
        # Calculate metrics
        successful = sum(
            1 for r in results 
            if r['parsed_output'].get('validation_success')
        )
        parsing_successful = sum(
            1 for r in results 
            if r['parsed_output'].get('parsing_success')
        )
        
        # Calculate thinking quality
        thinking_scores = [
            r.get('thinking_quality', {}).get('quality_score', 0)
            for r in results if r.get('thinking_quality')
        ]
        avg_thinking = sum(thinking_scores) / len(thinking_scores) if thinking_scores else 0
        
        success_rate = successful / len(results)
        parsing_rate = parsing_successful / len(results)
        
        print("\n" + "-"*80)
        print("BASELINE RESULTS:")
        print("-"*80)
        print(f"  Total questions: {len(results)}")
        print(f"  Parsing success: {parsing_successful}/{len(results)} ({parsing_rate*100:.1f}%)")
        print(f"  Validation success: {successful}/{len(results)} ({success_rate*100:.1f}%)")
        print(f"  Avg thinking quality: {avg_thinking:.2f}/1.0")
        print("-"*80)
        
        return {
            'status': 'success',
            'results': results,
            'metrics': {
                'total': len(results),
                'parsing_success': parsing_successful,
                'validation_success': successful,
                'success_rate': success_rate,
                'avg_thinking_quality': avg_thinking
            }
        }
    except Exception as e:
        print(f"✗ Error during evaluation: {e}")
        return {'status': 'failed', 'error': str(e)}

# ============================================================================
# STEP 3: Analyze Errors with Feedback Loop
# ============================================================================

def step3_error_analysis(feedback_loop, results: List[Dict], 
                         references: List[Dict]) -> Dict[str, Any]:
    """
    Step 3: Analyze errors using feedback loop
    
    From TRAINING_GUIDE.md:
    - Analyze errors in predictions
    - Get improvement suggestions
    - Save error report
    """
    print("\n" + "="*80)
    print("STEP 3: Error Analysis with Feedback Loop")
    print("="*80)
    
    try:
        # Analyze errors
        print("\nAnalyzing errors...")
        error_analysis = feedback_loop.analyze_errors(results, references)
        
        print("\n" + "-"*80)
        print("ERROR ANALYSIS RESULTS:")
        print("-"*80)
        print(f"  Total cases analyzed: {error_analysis['total_cases']}")
        print(f"  Parsing failures: {error_analysis['parsing_failures']}")
        print(f"  Validation failures: {error_analysis['validation_failures']}")
        print(f"  Low thinking quality: {error_analysis['low_thinking_quality']}")
        print(f"  Incorrect heirs: {len(error_analysis['incorrect_heirs'])}")
        print(f"  Retrieval issues: {len(error_analysis['retrieval_issues'])}")
        
        print("\n  Top Error Categories:")
        for category, count in error_analysis['error_categories'].most_common(5):
            print(f"    • {category}: {count} cases")
        print("-"*80)
        
        # Get improvement suggestions
        print("\nGenerating improvement suggestions...")
        suggestions = feedback_loop.suggest_improvements(error_analysis)
        
        print("\n" + "-"*80)
        print("IMPROVEMENT SUGGESTIONS:")
        print("-"*80)
        for suggestion in suggestions:
            print(f"  {suggestion}")
        print("-"*80)
        
        # Save error report
        feedback_loop.save_error_report(error_analysis, "error_analysis_baseline.json")
        
        return {
            'status': 'success',
            'error_analysis': error_analysis,
            'suggestions': suggestions
        }
    except Exception as e:
        print(f"✗ Error during analysis: {e}")
        return {'status': 'failed', 'error': str(e)}

# ============================================================================
# STEP 4: Apply Improvements (Manual/Automated)
# ============================================================================

def step4_apply_improvements(pipeline, config_path: str, 
                             error_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 4: Apply improvements based on error analysis
    
    From TRAINING_GUIDE.md:
    - If retrieval is poor: adjust retrieval parameters
    - If prompts need improvement: refine prompt_builder.py
    - If thinking quality is low: adjust temperature, add examples
    """
    print("\n" + "="*80)
    print("STEP 4: Applying Improvements")
    print("="*80)
    
    improvements = []
    
    # Check for retrieval issues
    retrieval_issues = error_analysis.get('retrieval_issues', [])
    if retrieval_issues:
        print(f"\n⚠ Found {len(retrieval_issues)} cases with poor retrieval")
        print("  → Suggested improvements:")
        print("    - Increase top_k from 5 to 10")
        print("    - Adjust semantic_weight in config")
        print("    - Add more PDFs to knowledge base")
        improvements.append('retrieval_params')
    
    # Check for parsing failures
    parsing_failures = error_analysis.get('parsing_failures', 0)
    if parsing_failures > 0:
        print(f"\n⚠ Found {parsing_failures} parsing failures")
        print("  → Suggested improvements:")
        print("    - Add more few-shot examples in prompt_builder.py")
        print("    - Improve structured output instructions")
        improvements.append('prompt_examples')
    
    # Check for low thinking quality
    low_quality = error_analysis.get('low_thinking_quality', 0)
    if low_quality > 0:
        print(f"\n⚠ Found {low_quality} cases with low thinking quality")
        print("  → Suggested improvements:")
        print("    - Increase temperature slightly (0.0 → 0.1)")
        print("    - Add more detailed reasoning examples")
        improvements.append('thinking_quality')
    
    # Check for incorrect heirs
    incorrect_heirs = error_analysis.get('incorrect_heirs', [])
    if incorrect_heirs:
        print(f"\n⚠ Found {len(incorrect_heirs)} cases with incorrect heir identification")
        print("  → Suggested improvements:")
        print("    - Add more PDF content on heir identification rules")
        print("    - Improve retrieval for blocking (حجب) cases")
        improvements.append('heir_knowledge')
    
    if not improvements:
        print("\n✓ No major issues detected. System performing well!")
    
    print("\n" + "-"*80)
    print("Improvements to apply:", improvements)
    print("-"*80)
    
    return {
        'status': 'success',
        'improvements': improvements
    }

# ============================================================================
# STEP 5: Run Iterative Improvement Loop
# ============================================================================

def step5_iterative_improvement(feedback_loop, pipeline, dataset: List[Dict],
                                max_iterations: int = 3) -> Dict[str, Any]:
    """
    Step 5: Run iterative improvement loop
    
    From TRAINING_GUIDE.md:
    - Run automatic iterative improvement
    - Track best score across iterations
    - Save error reports for each iteration
    """
    print("\n" + "="*80)
    print(f"STEP 5: Iterative Improvement Loop ({max_iterations} iterations)")
    print("="*80)
    
    try:
        # Run iterative improvement
        history = feedback_loop.iterative_improvement(
            pipeline=pipeline,
            dataset=dataset[:20],  # Use subset for speed
            max_iterations=max_iterations
        )
        
        # Display results
        print("\n" + "="*80)
        print("ITERATIVE IMPROVEMENT COMPLETE")
        print("="*80)
        print(f"\nBest Score: {history['best_score']*100:.2f}%")
        print(f"Best Iteration: {history['best_iteration']}")
        
        print("\nIteration Summary:")
        for iter_data in history['iterations']:
            print(f"  Iteration {iter_data['iteration']}: "
                  f"{iter_data['success_rate']*100:.2f}% success rate")
        
        print("="*80)
        
        return {
            'status': 'success',
            'history': history,
            'best_score': history['best_score'],
            'best_iteration': history['best_iteration']
        }
    except Exception as e:
        print(f"✗ Error during iterative improvement: {e}")
        return {'status': 'failed', 'error': str(e)}

# ============================================================================
# STEP 6: Final Evaluation
# ============================================================================

def step6_final_evaluation(pipeline, dataset: List[Dict], 
                          baseline_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 6: Final evaluation on test set
    """
    print("\n" + "="*80)
    print("STEP 6: Final Evaluation on Test Set")
    print("="*80)
    
    # Use different subset for final test
    test_subset = dataset[30:40]  # Questions 30-40
    
    print(f"\nEvaluating on {len(test_subset)} test questions...")
    
    try:
        results = pipeline.batch_query(test_subset, save_results=True)
        
        # Calculate metrics
        successful = sum(
            1 for r in results 
            if r['parsed_output'].get('validation_success')
        )
        success_rate = successful / len(results)
        
        thinking_scores = [
            r.get('thinking_quality', {}).get('quality_score', 0)
            for r in results if r.get('thinking_quality')
        ]
        avg_thinking = sum(thinking_scores) / len(thinking_scores) if thinking_scores else 0
        
        baseline_rate = baseline_metrics.get('success_rate', 0)
        improvement = success_rate - baseline_rate
        
        print("\n" + "-"*80)
        print("FINAL TEST RESULTS:")
        print("-"*80)
        print(f"  Success Rate: {success_rate*100:.2f}%")
        print(f"  Baseline Rate: {baseline_rate*100:.2f}%")
        print(f"  Improvement: {improvement*100:+.2f}%")
        print(f"  Avg Thinking Quality: {avg_thinking:.2f}/1.0")
        print("-"*80)
        
        # Achievement check
        if success_rate >= 0.99:
            print("\n🎉 TARGET ACHIEVED: >99% SUCCESS RATE!")
        elif success_rate >= 0.95:
            print("\n⭐ Great progress! Close to target (>95%)")
        else:
            print("\n📋 Continue iterating to improve results")
        
        return {
            'status': 'success',
            'success_rate': success_rate,
            'improvement': improvement,
            'avg_thinking_quality': avg_thinking
        }
    except Exception as e:
        print(f"✗ Error during final evaluation: {e}")
        return {'status': 'failed', 'error': str(e)}

# ============================================================================
# Main Training Function
# ============================================================================

def run_training_workflow(config_path: str = "config/rag_config.yaml",
                          pdf_directory: str = "data/pdfs",
                          dataset_path: str = None,
                          max_iterations: int = 3):
    """
    Run the complete training workflow as described in TRAINING_GUIDE.md
    """
    
    # Setup
    IN_COLAB = setup_environment()
    
    # Install dependencies if in Colab
    if IN_COLAB:
        install_dependencies()
    
    # Mount drive if in Colab
    if IN_COLAB:
        from google.colab import drive
        drive.mount('/content/drive')
        # Adjust paths for Colab
        pdf_directory = '/content/drive/MyDrive/QIAS_RAG/data/pdfs'
        config_path = '/content/qias_rag_thinking/config/rag_config.yaml'
    
    # Add paths
    if IN_COLAB:
        sys.path.insert(0, '/content/qias_rag_thinking')
        sys.path.insert(0, '/content/qias_shared_task_2026')
    else:
        # Local paths
        sys.path.insert(0, os.getcwd())
    
    # Imports
    print("\n--- Importing RAG Components ---")
    from src.rag_pipeline import RAGPipeline
    from src.training.feedback_loop import FeedbackLoop
    print("✓ Imports successful")
    
    # Initialize pipeline
    print("\n--- Initializing RAG Pipeline ---")
    pipeline = RAGPipeline(config_path=config_path)
    
    # Initialize feedback loop
    feedback_loop = FeedbackLoop(config_path=config_path)
    
    # =========================================================================
    # STEP 1: Build Knowledge Base
    # =========================================================================
    kb_result = step1_build_knowledge_base(pipeline, pdf_directory)
    if kb_result['status'] != 'success':
        print("\n✗ Knowledge base building failed. Exiting.")
        return
    
    # =========================================================================
    # Load Dataset
    # =========================================================================
    print("\n--- Loading Dataset ---")
    
    # Try to load QIAS dataset
    if dataset_path and Path(dataset_path).exists():
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        print(f"✓ Loaded {len(dataset)} questions from {dataset_path}")
    else:
        # Create synthetic dataset for testing
        print("⚠ Dataset not found. Creating synthetic test cases...")
        dataset = [
            {
                'id': f'q_{i}',
                'question': f'مات وترك: أم وأب وبنت. ما هو نصيب كل وريث؟ (Case {i})',
                'output': {'heirs': [{'heir': 'أم', 'share': '1/6'}, {'heir': 'أب', 'share': '1/6 + الباقي'}, {'heir': 'بنت', 'share': '1/2'}]}
            }
            for i in range(50)
        ]
        print(f"✓ Created {len(dataset)} synthetic test cases")
    
    # =========================================================================
    # STEP 2: Initial Evaluation (Baseline)
    # =========================================================================
    baseline_result = step2_initial_evaluation(pipeline, dataset, num_samples=10)
    if baseline_result['status'] != 'success':
        print("\n✗ Initial evaluation failed.")
        return
    
    # =========================================================================
    # STEP 3: Error Analysis
    # =========================================================================
    analysis_result = step3_error_analysis(
        feedback_loop,
        baseline_result['results'],
        dataset[:10]
    )
    if analysis_result['status'] != 'success':
        print("\n✗ Error analysis failed.")
        return
    
    # =========================================================================
    # STEP 4: Apply Improvements
    # =========================================================================
    improvements_result = step4_apply_improvements(
        pipeline,
        config_path,
        analysis_result['error_analysis']
    )
    
    # =========================================================================
    # STEP 5: Iterative Improvement
    # =========================================================================
    iteration_result = step5_iterative_improvement(
        feedback_loop,
        pipeline,
        dataset,
        max_iterations=max_iterations
    )
    if iteration_result['status'] != 'success':
        print("\n✗ Iterative improvement failed.")
        return
    
    # =========================================================================
    # STEP 6: Final Evaluation
    # =========================================================================
    final_result = step6_final_evaluation(
        pipeline,
        dataset,
        baseline_result['metrics']
    )
    
    # =========================================================================
    # Summary Report
    # =========================================================================
    print("\n" + "="*80)
    print("TRAINING WORKFLOW COMPLETE - SUMMARY REPORT")
    print("="*80)
    print(f"\n📊 Baseline Performance:")
    print(f"   Success Rate: {baseline_result['metrics']['success_rate']*100:.2f}%")
    print(f"   Avg Thinking Quality: {baseline_result['metrics']['avg_thinking_quality']:.2f}")
    
    print(f"\n📈 Training Progress:")
    print(f"   Best Iteration: {iteration_result['best_iteration']}")
    print(f"   Best Score: {iteration_result['best_score']*100:.2f}%")
    
    print(f"\n🎯 Final Test Results:")
    if final_result['status'] == 'success':
        print(f"   Success Rate: {final_result['success_rate']*100:.2f}%")
        print(f"   Improvement: {final_result['improvement']*100:+.2f}%")
        print(f"   Avg Thinking Quality: {final_result['avg_thinking_quality']:.2f}")
    
    print(f"\n📋 Files Generated:")
    print(f"   - error_analysis_baseline.json")
    print(f"   - error_analysis_iter_1.json")
    print(f"   - error_analysis_iter_2.json")
    print(f"   - error_analysis_iter_3.json")
    print(f"   - rag_predictions.json")
    
    print("\n" + "="*80)
    print("Next Steps:")
    print("  1. Review error analysis files in results/ directory")
    print("  2. Apply manual improvements based on suggestions")
    print("  3. Re-run training if needed")
    print("  4. Once >99% achieved, proceed to full evaluation")
    print("="*80)
    
    return {
        'baseline': baseline_result,
        'analysis': analysis_result,
        'improvements': improvements_result,
        'iterations': iteration_result,
        'final': final_result
    }

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run the training workflow
    results = run_training_workflow(
        config_path="config/rag_config.yaml",
        pdf_directory="data/pdfs",
        dataset_path=None,  # Will use synthetic data if not found
        max_iterations=3
    )
