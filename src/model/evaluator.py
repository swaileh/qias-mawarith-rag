"""
QIAS 2026 Competition Evaluation Metrics
Evaluates structured Islamic inheritance reasoning outputs against ground truth.
"""

import json
from typing import Dict, Any, List, Tuple, Optional, Union
from collections import defaultdict
import math


class QIAS2026Evaluator:
    """Evaluator for QIAS 2026 Islamic inheritance reasoning competition."""

    def __init__(self):
        self.metrics = {}

    def evaluate_sample(self, prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single prediction against ground truth.

        Args:
            prediction: Model's structured output
            ground_truth: Ground truth structured output

        Returns:
            Dict with individual sample metrics
        """
        results = {
            'overall_accuracy': 0.0,
            'heirs_accuracy': 0.0,
            'blocked_accuracy': 0.0,
            'shares_accuracy': 0.0,
            'awl_radd_accuracy': 0.0,
            'tasil_stage_accuracy': 0.0,
            'post_tasil_accuracy': 0.0,
            'detailed_scores': {}
        }

        # Extract components
        pred_heirs = prediction.get('heirs', [])
        gt_heirs = ground_truth.get('heirs', [])

        pred_blocked = prediction.get('blocked', [])
        gt_blocked = ground_truth.get('blocked', [])

        pred_shares = prediction.get('shares', [])
        gt_shares = ground_truth.get('shares', [])

        pred_awl_radd = prediction.get('awl_or_radd', '')
        gt_awl_radd = ground_truth.get('awl_or_radd', '')

        pred_tasil = prediction.get('tasil_stage', {})
        gt_tasil = ground_truth.get('tasil_stage', {})

        pred_post = prediction.get('post_tasil', {})
        gt_post = ground_truth.get('post_tasil', {})

        # Evaluate each component
        results['heirs_accuracy'] = self._evaluate_heirs_list(pred_heirs, gt_heirs)
        results['blocked_accuracy'] = self._evaluate_heirs_list(pred_blocked, gt_blocked)
        results['shares_accuracy'] = self._evaluate_shares_list(pred_shares, gt_shares)
        results['awl_radd_accuracy'] = self._evaluate_awl_radd(pred_awl_radd, gt_awl_radd)
        results['tasil_stage_accuracy'] = self._evaluate_tasil_stage(pred_tasil, gt_tasil)
        results['post_tasil_accuracy'] = self._evaluate_post_tasil(pred_post, gt_post)

        # Calculate overall accuracy as weighted average
        weights = {
            'heirs_accuracy': 0.2,
            'blocked_accuracy': 0.2,
            'shares_accuracy': 0.25,
            'awl_radd_accuracy': 0.1,
            'tasil_stage_accuracy': 0.15,
            'post_tasil_accuracy': 0.1
        }

        results['overall_accuracy'] = sum(
            results[metric] * weight
            for metric, weight in weights.items()
        )

        # Add detailed component scores
        results['detailed_scores'] = {
            'heirs': self._detailed_heirs_evaluation(pred_heirs, gt_heirs),
            'blocked': self._detailed_heirs_evaluation(pred_blocked, gt_blocked),
            'shares': self._detailed_shares_evaluation(pred_shares, gt_shares),
            'awl_radd': {'predicted': pred_awl_radd, 'ground_truth': gt_awl_radd, 'correct': pred_awl_radd == gt_awl_radd},
            'tasil_stage': self._detailed_tasil_evaluation(pred_tasil, gt_tasil),
            'post_tasil': self._detailed_post_tasil_evaluation(pred_post, gt_post)
        }

        return results

    def _evaluate_heirs_list(self, pred_heirs: List[Dict], gt_heirs: List[Dict]) -> float:
        """Evaluate heirs/blocked heirs list accuracy."""
        if not gt_heirs and not pred_heirs:
            return 1.0
        if not gt_heirs or not pred_heirs:
            return 0.0

        # Convert to comparable format
        def heir_to_key(heir):
            return (heir.get('heir', '').strip(), heir.get('count', 0))

        gt_keys = set(heir_to_key(h) for h in gt_heirs)
        pred_keys = set(heir_to_key(h) for h in pred_heirs)

        if not gt_keys:
            return 1.0 if not pred_keys else 0.0

        # Calculate precision and recall
        correct = len(gt_keys & pred_keys)
        precision = correct / len(pred_keys) if pred_keys else 1.0
        recall = correct / len(gt_keys) if gt_keys else 1.0

        # F1 score
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def _evaluate_shares_list(self, pred_shares: List[Dict], gt_shares: List[Dict]) -> float:
        """Evaluate shares list accuracy."""
        if not gt_shares and not pred_shares:
            return 1.0
        if not gt_shares or not pred_shares:
            return 0.0

        # Convert to comparable format
        def share_to_key(share):
            return (share.get('heir', '').strip(), share.get('count', 0), share.get('fraction', ''))

        gt_keys = set(share_to_key(s) for s in gt_shares)
        pred_keys = set(share_to_key(s) for s in pred_shares)

        if not gt_keys:
            return 1.0 if not pred_keys else 0.0

        # Calculate precision and recall
        correct = len(gt_keys & pred_keys)
        precision = correct / len(pred_keys) if pred_keys else 1.0
        recall = correct / len(gt_keys) if gt_keys else 1.0

        # F1 score
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def _evaluate_awl_radd(self, pred: str, gt: str) -> float:
        """Evaluate awl_or_radd accuracy."""
        return 1.0 if pred.strip() == gt.strip() else 0.0

    def _evaluate_tasil_stage(self, pred_tasil: Dict, gt_tasil: Dict) -> float:
        """Evaluate tasil_stage accuracy."""
        if not gt_tasil and not pred_tasil:
            return 1.0
        if not gt_tasil or not pred_tasil:
            return 0.0

        # Check asl value
        asl_match = pred_tasil.get('asl') == gt_tasil.get('asl')

        # Check distribution
        pred_dist = pred_tasil.get('distribution', [])
        gt_dist = gt_tasil.get('distribution', [])

        dist_accuracy = self._evaluate_tasil_distribution(pred_dist, gt_dist)

        return (asl_match + dist_accuracy) / 2.0

    def _evaluate_tasil_distribution(self, pred_dist: List[Dict], gt_dist: List[Dict]) -> float:
        """Evaluate tasil distribution accuracy."""
        if not gt_dist and not pred_dist:
            return 1.0
        if not gt_dist or not pred_dist:
            return 0.0

        def dist_to_key(dist):
            return (dist.get('heir', '').strip(), dist.get('count', 0), dist.get('shares', ''))

        gt_keys = set(dist_to_key(d) for d in gt_dist)
        pred_keys = set(dist_to_key(d) for d in pred_dist)

        if not gt_keys:
            return 1.0 if not pred_keys else 0.0

        correct = len(gt_keys & pred_keys)
        precision = correct / len(pred_keys) if pred_keys else 1.0
        recall = correct / len(gt_keys) if gt_keys else 1.0

        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def _evaluate_post_tasil(self, pred_post: Dict, gt_post: Dict) -> float:
        """Evaluate post_tasil accuracy."""
        if not gt_post and not pred_post:
            return 1.0
        if not gt_post or not pred_post:
            return 0.0

        # Check total_shares
        total_match = pred_post.get('total_shares') == gt_post.get('total_shares')

        # Check distribution
        pred_dist = pred_post.get('distribution', [])
        gt_dist = gt_post.get('distribution', [])

        dist_accuracy = self._evaluate_post_distribution(pred_dist, gt_dist)

        return (total_match + dist_accuracy) / 2.0

    def _evaluate_post_distribution(self, pred_dist: List[Dict], gt_dist: List[Dict]) -> float:
        """Evaluate post_tasil distribution accuracy with percentage tolerance."""
        if not gt_dist and not pred_dist:
            return 1.0
        if not gt_dist or not pred_dist:
            return 0.0

        def dist_to_key(dist):
            return (dist.get('heir', '').strip(), dist.get('count', 0))

        # Group by heir and count
        gt_groups = defaultdict(list)
        pred_groups = defaultdict(list)

        for d in gt_dist:
            key = dist_to_key(d)
            gt_groups[key].append(d)

        for d in pred_dist:
            key = dist_to_key(d)
            pred_groups[key].append(d)

        if not gt_groups:
            return 1.0 if not pred_groups else 0.0

        correct_matches = 0
        total_gt = len(gt_groups)

        for gt_key, gt_items in gt_groups.items():
            if gt_key in pred_groups:
                pred_items = pred_groups[gt_key]
                # Check if percentages match within tolerance
                gt_pct = sum(item.get('per_head_percent', 0) * item.get('count', 1) for item in gt_items)
                pred_pct = sum(item.get('per_head_percent', 0) * item.get('count', 1) for item in pred_items)

                if abs(gt_pct - pred_pct) <= 5.0:  # 5% tolerance
                    correct_matches += 1

        return correct_matches / total_gt if total_gt > 0 else 1.0

    def _detailed_heirs_evaluation(self, pred: List[Dict], gt: List[Dict]) -> Dict[str, Any]:
        """Detailed evaluation for heirs/blocked heirs."""
        def heir_to_tuple(h):
            return (h.get('heir', '').strip(), h.get('count', 0))

        gt_set = set(heir_to_tuple(h) for h in gt)
        pred_set = set(heir_to_tuple(h) for h in pred)

        return {
            'predicted': [heir_to_tuple(h) for h in pred],
            'ground_truth': [heir_to_tuple(h) for h in gt],
            'correct': list(gt_set & pred_set),
            'false_positives': list(pred_set - gt_set),
            'false_negatives': list(gt_set - pred_set),
            'precision': len(gt_set & pred_set) / len(pred_set) if pred_set else 1.0,
            'recall': len(gt_set & pred_set) / len(gt_set) if gt_set else 1.0
        }

    def _detailed_shares_evaluation(self, pred: List[Dict], gt: List[Dict]) -> Dict[str, Any]:
        """Detailed evaluation for shares."""
        def share_to_tuple(s):
            return (s.get('heir', '').strip(), s.get('count', 0), s.get('fraction', ''))

        gt_set = set(share_to_tuple(s) for s in gt)
        pred_set = set(share_to_tuple(s) for s in pred)

        return {
            'predicted': [share_to_tuple(s) for s in pred],
            'ground_truth': [share_to_tuple(s) for s in gt],
            'correct': list(gt_set & pred_set),
            'false_positives': list(pred_set - gt_set),
            'false_negatives': list(gt_set - pred_set),
            'precision': len(gt_set & pred_set) / len(pred_set) if pred_set else 1.0,
            'recall': len(gt_set & pred_set) / len(gt_set) if gt_set else 1.0
        }

    def _detailed_tasil_evaluation(self, pred: Dict, gt: Dict) -> Dict[str, Any]:
        """Detailed evaluation for tasil_stage."""
        return {
            'predicted_asl': pred.get('asl'),
            'ground_truth_asl': gt.get('asl'),
            'asl_correct': pred.get('asl') == gt.get('asl'),
            'distribution': self._detailed_heirs_evaluation(
                pred.get('distribution', []),
                gt.get('distribution', [])
            )
        }

    def _detailed_post_tasil_evaluation(self, pred: Dict, gt: Dict) -> Dict[str, Any]:
        """Detailed evaluation for post_tasil."""
        pred_dist = pred.get('distribution', [])
        gt_dist = pred.get('distribution', [])

        # Calculate percentage differences
        def calculate_total_percentage(dist):
            return sum(
                item.get('per_head_percent', 0) * item.get('count', 1)
                for item in dist
            )

        pred_total_pct = calculate_total_percentage(pred_dist)
        gt_total_pct = calculate_total_percentage(gt_dist)

        return {
            'predicted_total_shares': pred.get('total_shares'),
            'ground_truth_total_shares': gt.get('total_shares'),
            'total_shares_correct': pred.get('total_shares') == gt.get('total_shares'),
            'predicted_total_percentage': pred_total_pct,
            'ground_truth_total_percentage': gt_total_pct,
            'percentage_difference': abs(pred_total_pct - gt_total_pct),
            'percentage_within_tolerance': abs(pred_total_pct - gt_total_pct) <= 5.0
        }

    def evaluate_dataset(self, predictions: List[Dict], ground_truths: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate entire dataset and generate comprehensive report.

        Args:
            predictions: List of model predictions
            ground_truths: List of ground truth answers

        Returns:
            Comprehensive evaluation report
        """
        if len(predictions) != len(ground_truths):
            raise ValueError("Predictions and ground truths must have same length")

        individual_results = []
        component_scores = defaultdict(list)

        for i, (pred, gt) in enumerate(zip(predictions, ground_truths)):
            # Extract structured output from prediction if it's in the full format
            if isinstance(pred, dict) and 'output' in pred:
                pred_structured = pred['output']
            else:
                pred_structured = pred

            if isinstance(gt, dict) and 'output' in gt:
                gt_structured = gt['output']
            else:
                gt_structured = gt

            result = self.evaluate_sample(pred_structured, gt_structured)
            result['sample_id'] = i + 1
            individual_results.append(result)

            # Collect component scores
            for component in ['overall_accuracy', 'heirs_accuracy', 'blocked_accuracy',
                            'shares_accuracy', 'awl_radd_accuracy', 'tasil_stage_accuracy',
                            'post_tasil_accuracy']:
                component_scores[component].append(result[component])

        # Calculate aggregate statistics
        report = {
            'dataset_size': len(predictions),
            'individual_results': individual_results,
            'aggregate_scores': {},
            'component_averages': {},
            'score_distribution': {}
        }

        # Aggregate scores
        for component, scores in component_scores.items():
            report['component_averages'][component] = {
                'mean': sum(scores) / len(scores),
                'min': min(scores),
                'max': max(scores),
                'std': math.sqrt(sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores))
            }

            # Score distribution
            bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
            distribution = [0] * (len(bins) - 1)
            for score in scores:
                for j in range(len(bins) - 1):
                    if bins[j] <= score < bins[j + 1]:
                        distribution[j] += 1
                        break
                if score == 1.0:
                    distribution[-1] += 1
            report['score_distribution'][component] = {
                'bins': [f'{bins[i]:.1f}-{bins[i+1]:.1f}' for i in range(len(bins)-1)],
                'counts': distribution
            }

        # Overall accuracy is the primary metric
        report['aggregate_scores']['overall_accuracy'] = report['component_averages']['overall_accuracy']['mean']

        # Calculate pass rates (scores >= 0.8)
        for component in component_scores.keys():
            pass_rate = sum(1 for score in component_scores[component] if score >= 0.8) / len(component_scores[component])
            report['component_averages'][component]['pass_rate_80'] = pass_rate

        return report

    def generate_report(self, evaluation_report: Dict[str, Any], output_path: str = None) -> str:
        """Generate a formatted evaluation report."""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("QIAS 2026 COMPETITION EVALUATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        report_lines.append(f"Dataset Size: {evaluation_report['dataset_size']} samples")
        report_lines.append("")

        report_lines.append("PRIMARY METRIC:")
        report_lines.append(f"Overall Accuracy: {evaluation_report['aggregate_scores']['overall_accuracy']:.3f}")
        report_lines.append("")

        report_lines.append("COMPONENT-WISE PERFORMANCE:")
        report_lines.append("-" * 50)

        components = ['overall_accuracy', 'heirs_accuracy', 'blocked_accuracy',
                     'shares_accuracy', 'awl_radd_accuracy', 'tasil_stage_accuracy',
                     'post_tasil_accuracy']

        for component in components:
            stats = evaluation_report['component_averages'][component]
            report_lines.append(f"{component.replace('_', ' ').title():<25} Mean: {stats['mean']:.3f} | Min: {stats['min']:.3f} | Max: {stats['max']:.3f} | Std: {stats['std']:.3f}")
            if 'pass_rate_80' in stats:
                report_lines.append(f"{'':<25} Pass Rate (>=80%): {stats['pass_rate_80']:.1%}")
            report_lines.append("")

        report_lines.append("SCORE DISTRIBUTIONS:")
        report_lines.append("-" * 50)

        for component in components[:3]:  # Show distributions for main components
            dist = evaluation_report['score_distribution'][component]
            report_lines.append(f"{component.replace('_', ' ').title()}:")
            for bin_range, count in zip(dist['bins'], dist['counts']):
                pct = count / evaluation_report['dataset_size'] * 100
                report_lines.append(f"  {bin_range:<8} {count:>3} samples ({pct:>5.1f}%)")
            report_lines.append("")

        report_lines.append("SAMPLE PERFORMANCE SUMMARY:")
        report_lines.append("-" * 50)

        # Show best and worst performing samples
        sorted_results = sorted(evaluation_report['individual_results'],
                              key=lambda x: x['overall_accuracy'], reverse=True)

        report_lines.append("Top 5 Best Performing Samples:")
        for i, result in enumerate(sorted_results[:5]):
            report_lines.append(f"  #{result['sample_id']:3d}: {result['overall_accuracy']:.3f}")

        report_lines.append("")
        report_lines.append("Bottom 5 Worst Performing Samples:")
        for i, result in enumerate(sorted_results[-5:]):
            report_lines.append(f"  #{result['sample_id']:3d}: {result['overall_accuracy']:.3f}")

        report_str = "\n".join(report_lines)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_str)
            print(f"Evaluation report saved to: {output_path}")

        return report_str