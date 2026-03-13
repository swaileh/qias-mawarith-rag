"""
MIR-E Evaluation Wrapper
Integration with QIAS evaluation framework
"""

import yaml
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

# Add parent directory to path to import from qias_shared_task_2026
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "qias_shared_task_2026"))


class MIREvaluator:
    """Wrapper for MIR-E evaluation"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize evaluator"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.eval_config = self.config['evaluation']
        self.dataset_path = Path(self.eval_config['dataset_path'])
        self.output_dir = Path(self.eval_config['output_directory'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_reference_dataset(self, filename: str = None) -> List[Dict[str, Any]]:
        """Load reference dataset
        
        Args:
            filename: Optional specific file to load
        
        Returns:
            List of reference cases
        """
        references = []
        
        if filename:
            file_path = self.dataset_path / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    references.extend(data)
                else:
                    references.append(data)
        else:
            # Load all JSON files in dataset directory
            for json_file in self.dataset_path.glob("*.json"):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        references.extend(data)
                    else:
                        references.append(data)
        
        return references
    
    def save_predictions(self, predictions: List[Dict[str, Any]], filename: str) -> Path:
        """Save predictions to file
        
        Args:
            predictions: List of prediction dictionaries
            filename: Output filename
        
        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(predictions, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(predictions)} predictions to {output_path}")
        
        return output_path
    
    def evaluate_predictions(
        self,
        predictions_file: str,
        reference_file: str = None
    ) -> Dict[str, Any]:
        """Evaluate predictions using MIR-E framework
        
        Args:
            predictions_file: Path to predictions JSON
            reference_file: Optional reference file (auto-detect if None)
        
        Returns:
            Evaluation results
        """
        try:
            # Import evaluation module from qias_shared_task_2026
            from src.mawarith_benchmark.evaluation import evaluate_predictions
        except ImportError:
            print("Error: Cannot import evaluation module from qias_shared_task_2026")
            print("Make sure qias_shared_task_2026 is in the parent directory")
            return {}
        
        # Load predictions
        with open(predictions_file, 'r', encoding='utf-8') as f:
            predictions = json.load(f)
        
        # Load reference
        if reference_file:
            with open(reference_file, 'r', encoding='utf-8') as f:
                references = json.load(f)
        else:
            references = self.load_reference_dataset()
        
        # Run evaluation
        results = evaluate_predictions(predictions, references)
        
        return results
    
    def generate_report(
        self,
        results: Dict[str, Any],
        output_filename: str = "evaluation_report.txt"
    ) -> None:
        """Generate evaluation report
        
        Args:
            results: Evaluation results
            output_filename: Output file name
        """
        report_path = self.output_dir / output_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# QIAS RAG System Evaluation Report\n\n")
            
            # Overall scores
            f.write("## Overall Scores\n")
            f.write(f"MIR-E Score: {results.get('average_mir_e', 0):.4f}\n")
            f.write(f"Total Cases: {results.get('total_cases', 0)}\n\n")
            
            # Subscores
            f.write("## Subscores\n")
            subscores = results.get('subscores', {})
            for key, value in subscores.items():
                f.write(f"{key}: {value:.4f}\n")
            
            f.write("\n")
            
            # Per-case results summary
            if 'per_case' in results:
                f.write(f"## Per-Case Results ({len(results['per_case'])} cases)\n")
                
                # Count by score range
                score_ranges = {'0.9-1.0': 0, '0.8-0.9': 0, '0.7-0.8': 0, '<0.7': 0}
                
                for case in results['per_case']:
                    score = case.get('mir_e', 0)
                    if score >= 0.9:
                        score_ranges['0.9-1.0'] += 1
                    elif score >= 0.8:
                        score_ranges['0.8-0.9'] += 1
                    elif score >= 0.7:
                        score_ranges['0.7-0.8'] += 1
                    else:
                        score_ranges['<0.7'] += 1
                
                for range_name, count in score_ranges.items():
                    percentage = (count / len(results['per_case'])) * 100
                    f.write(f"{range_name}: {count} cases ({percentage:.1f}%)\n")
        
        print(f"Report saved to {report_path}")
    
    def compare_with_baseline(
        self,
        rag_results_file: str,
        baseline_results_file: str
    ) -> Dict[str, Any]:
        """Compare RAG results with baseline
        
        Args:
            rag_results_file: RAG predictions file
            baseline_results_file: Baseline predictions file
        
        Returns:
            Comparison results
        """
        # Load both result files
        with open(rag_results_file, 'r', encoding='utf-8') as f:
            rag_results = json.load(f)
        
        with open(baseline_results_file, 'r', encoding='utf-8') as f:
            baseline_results = json.load(f)
        
        # Calculate improvement
        comparison = {
            'rag_score': rag_results.get('average_mir_e', 0),
            'baseline_score': baseline_results.get('average_mir_e', 0),
            'improvement': 0,
            'improvement_pct': 0
        }
        
        if comparison['baseline_score'] > 0:
            comparison['improvement'] = comparison['rag_score'] - comparison['baseline_score']
            comparison['improvement_pct'] = (comparison['improvement'] / comparison['baseline_score']) * 100
        
        return comparison


if __name__ == "__main__":
    # Test the evaluator
    evaluator = MIREvaluator()
    
    # Load reference dataset
    references = evaluator.load_reference_dataset()
    print(f"Loaded {len(references)} reference cases")
