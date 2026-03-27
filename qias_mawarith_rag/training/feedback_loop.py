"""
RAG Feedback Loop
Analyze errors and iteratively improve the RAG system
"""

import yaml
import json
from typing import Dict, Any, List
from pathlib import Path
from collections import Counter


class FeedbackLoop:
    """Analyze RAG performance and provide improvement suggestions"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize feedback loop"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.training_config = self.config.get('training', {})
        self.output_dir = Path(self.config['evaluation']['output_directory'])
    
    def analyze_errors(
        self,
        results: List[Dict[str, Any]],
        references: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze error patterns in RAG results
        
        Args:
            results: List of RAG results
            references: List of reference answers
        
        Returns:
            Error analysis dictionary
        """
        error_analysis = {
            'total_cases': len(results),
            'parsing_failures': 0,
            'validation_failures': 0,
            'low_thinking_quality': 0,
            'incorrect_heirs': [],
            'incorrect_shares': [],
            'retrieval_issues': [],
            'error_categories': Counter()
        }
        
        # Build reference lookup
        ref_lookup = {r['id']: r for r in references}
        
        for result in results:
            result_id = result.get('id')
            parsed = result.get('parsed_output', {})
            
            # Check parsing/validation
            if not parsed.get('parsing_success'):
                error_analysis['parsing_failures'] += 1
                error_analysis['error_categories']['parsing_error'] += 1
                continue
            
            if not parsed.get('validation_success'):
                error_analysis['validation_failures'] += 1
                error_analysis['error_categories']['validation_error'] += 1
                continue
            
            # Check thinking quality
            thinking_quality = result.get('thinking_quality', {})
            if thinking_quality.get('quality_score', 0) < 0.5:
                error_analysis['low_thinking_quality'] += 1
                error_analysis['error_categories']['poor_reasoning'] += 1
            
            # Compare with reference
            if result_id in ref_lookup:
                ref = ref_lookup[result_id]
                ref_output = ref.get('output', {})
                pred_output = parsed.get('structured_output', {})
                
                # Check heirs
                ref_heirs = {h['heir'] for h in ref_output.get('heirs', [])}
                pred_heirs = {h['heir'] for h in pred_output.get('heirs', [])}
                
                if ref_heirs != pred_heirs:
                    error_analysis['incorrect_heirs'].append({
                        'id': result_id,
                        'expected': list(ref_heirs),
                        'predicted': list(pred_heirs),
                        'missing': list(ref_heirs - pred_heirs),
                        'extra': list(pred_heirs - ref_heirs)
                    })
                    error_analysis['error_categories']['heir_identification'] += 1
                
                # Check if retrieval was poor
                retrieved_docs = result.get('retrieved_docs', [])
                if len(retrieved_docs) < 3:
                    error_analysis['retrieval_issues'].append({
                        'id': result_id,
                        'retrieved_count': len(retrieved_docs)
                    })
                    error_analysis['error_categories']['poor_retrieval'] += 1
        
        return error_analysis
    
    def suggest_improvements(self, error_analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on error analysis
        
        Args:
            error_analysis: Error analysis from analyze_errors
        
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Parsing failures
        if error_analysis['parsing_failures'] > 0:
            rate = error_analysis['parsing_failures'] / error_analysis['total_cases']
            suggestions.append(
                f"🔴 {error_analysis['parsing_failures']} parsing failures ({rate*100:.1f}%)\n"
                "   → Improve structured output instructions in prompt\n"
                "   → Add more few-shot examples with correct JSON format"
            )
        
        # Validation failures
        if error_analysis['validation_failures'] > 0:
            rate = error_analysis['validation_failures'] / error_analysis['total_cases']
            suggestions.append(
                f"🔴 {error_analysis['validation_failures']} validation failures ({rate*100:.1f}%)\n"
                "   → Check JSON schema compatibility\n"
                "   → Improve output parser error correction"
            )
        
        # Low thinking quality
        if error_analysis['low_thinking_quality'] > 0:
            rate = error_analysis['low_thinking_quality'] / error_analysis['total_cases']
            suggestions.append(
                f"⚠️ {error_analysis['low_thinking_quality']} cases with low thinking quality ({rate*100:.1f}%)\n"
                "   → Add more detailed reasoning examples\n"
                "   → Emphasize Islamic law terminology in prompt"
            )
        
        # Incorrect heirs
        if error_analysis['incorrect_heirs']:
            suggestions.append(
                f"⚠️ {len(error_analysis['incorrect_heirs'])} cases with incorrect heir identification\n"
                "   → Add more PDF content on heir identification rules\n"
                "   → Improve retrieval for blocking (حجب) cases"
            )
        
        # Retrieval issues
        if error_analysis['retrieval_issues']:
            suggestions.append(
                f"⚠️ {len(error_analysis['retrieval_issues'])} cases with poor retrieval\n"
                "   → Add more comprehensive PDF sources\n"
                "   → Adjust retrieval top-k or reranking threshold"
            )
        
        # Top error categories
        suggestions.append("\n📊 Top Error Categories:")
        for category, count in error_analysis['error_categories'].most_common(5):
            suggestions.append(f"   • {category}: {count} cases")
        
        return suggestions
    
    def save_error_report(
        self,
        error_analysis: Dict[str, Any],
        filename: str = "error_analysis.json"
    ) -> None:
        """Save error analysis to file
        
        Args:
            error_analysis: Error analysis dictionary
            filename: Output filename
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(error_analysis, f, ensure_ascii=False, indent=2)
        
        print(f"Error analysis saved to {output_path}")
    
    def iterative_improvement(
        self,
        pipeline,
        dataset: List[Dict[str, Any]],
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """Run iterative improvement loop
        
        Args:
            pipeline: RAGPipeline instance
            dataset: Test dataset
            max_iterations: Maximum improvement iterations
        
        Returns:
            Improvement history
        """
        history = {
            'iterations': [],
            'best_score': 0,
            'best_iteration': 0
        }
        
        references = dataset
        
        for iteration in range(max_iterations):
            print(f"\n{'='*80}")
            print(f"ITERATION {iteration + 1}/{max_iterations}")
            print(f"{'='*80}")
            
            # Run evaluation
            results = pipeline.batch_query(dataset, save_results=False)
            
            # Analyze errors
            error_analysis = self.analyze_errors(results, references)
            
            # Calculate success rate
            success_rate = (
                error_analysis['total_cases'] -
                error_analysis['parsing_failures'] -
                error_analysis['validation_failures']
            ) / error_analysis['total_cases']
            
            print(f"\nSuccess Rate: {success_rate*100:.2f}%")
            
            # Get suggestions
            suggestions = self.suggest_improvements(error_analysis)
            print("\nImprovement Suggestions:")
            for suggestion in suggestions:
                print(suggestion)
            
            # Save iteration results
            history['iterations'].append({
                'iteration': iteration + 1,
                'success_rate': success_rate,
                'error_analysis': error_analysis,
                'suggestions': suggestions
            })
            
            # Track best
            if success_rate > history['best_score']:
                history['best_score'] = success_rate
                history['best_iteration'] = iteration + 1
            
            # Save error report
            self.save_error_report(
                error_analysis,
                f"error_analysis_iter_{iteration + 1}.json"
            )
        
        return history


if __name__ == "__main__":
    # Test feedback loop
    feedback = FeedbackLoop()
    print("Feedback Loop initialized")
