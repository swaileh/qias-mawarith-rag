"""
Thinking Process Extractor
Analyze and evaluate the reasoning quality
"""

import re
from typing import Dict, Any, List


class ThinkingExtractor:
    """Extract and analyze thinking process quality"""
    
    def __init__(self):
        """Initialize thinking extractor"""
        # Key terms for Islamic inheritance reasoning
        self.key_terms_ar = [
            'فرض', 'عصبة', 'حجب', 'رد', 'عول', 'تصحيح',
            'سدس', 'ثلث', 'ربع', 'نصف', 'ثمن',
            'أصحاب الفروض', 'العصبات', 'ذوو الأرحام'
        ]
    
    def extract_steps(self, thinking_text: str) -> List[str]:
        """Extract reasoning steps from thinking text
        
        Args:
            thinking_text: Thinking section content
        
        Returns:
            List of reasoning steps
        """
        if not thinking_text:
            return []
        
        # Split by common delimiters
        steps = []
        
        # Try numbered steps first
        numbered_pattern = r'(?:^|\n)\s*\d+[\.:-]\s*(.+?)(?=\n\s*\d+[\.:-]|\Z)'
        matches = re.findall(numbered_pattern, thinking_text, re.MULTILINE | re.DOTALL)
        
        if matches:
            steps = [m.strip() for m in matches]
        else:
            # Try bullet points
            bullet_pattern = r'(?:^|\n)\s*[-•]\s*(.+?)(?=\n\s*[-•]|\Z)'
            matches = re.findall(bullet_pattern, thinking_text, re.MULTILINE | re.DOTALL)
            
            if matches:
                steps = [m.strip() for m in matches]
            else:
                # Split by newlines as fallback
                steps = [line.strip() for line in thinking_text.split('\n') if line.strip()]
        
        return steps
    
    def analyze_terminology(self, thinking_text: str) -> Dict[str, Any]:
        """Analyze use of Islamic law terminology
        
        Args:
            thinking_text: Thinking section content
        
        Returns:
            Dictionary with terminology analysis
        """
        # Count occurrences of key terms
        term_counts = {}
        for term in self.key_terms_ar:
            count = len(re.findall(term, thinking_text, re.IGNORECASE))
            if count > 0:
                term_counts[term] = count
        
        return {
            'terms_used': list(term_counts.keys()),
            'term_counts': term_counts,
            'total_terms': sum(term_counts.values()),
            'unique_terms': len(term_counts)
        }
    
    def assess_completeness(self, thinking_text: str, output: Dict[str, Any]) -> Dict[str, Any]:
        """Assess if thinking covers all required aspects
        
        Args:
            thinking_text: Thinking section content
            output: Structured output
        
        Returns:
            Completeness assessment
        """
        aspects_covered = {
            'heir_identification': False,
            'blocking_analysis': False,
            'share_calculation': False,
            'correction_awl_radd': False,
            'final_distribution': False
        }
        
        # Check for heir identification
        if any(term in thinking_text for term in ['ورثة', 'وريث', 'يرث']):
            aspects_covered['heir_identification'] = True
        
        # Check for blocking analysis
        if any(term in thinking_text for term in ['حجب', 'محجوب', 'ممنوع']):
            aspects_covered['blocking_analysis'] = True
        
        # Check for share calculation
        if any(term in thinking_text for term in ['نصيب', 'فرض', 'سهم', 'حساب']):
            aspects_covered['share_calculation'] = True
        
        # Check for awl/radd
        if any(term in thinking_text for term in ['عول', 'رد', 'تصحيح']):
            aspects_covered['correction_awl_radd'] = True
        
        # Check for final distribution
        if any(term in thinking_text for term in ['توزيع', 'نسبة', 'تقسيم']):
            aspects_covered['final_distribution'] = True
        
        completeness_score = sum(aspects_covered.values()) / len(aspects_covered)
        
        return {
            'aspects_covered': aspects_covered,
            'completeness_score': completeness_score,
            'total_aspects': len(aspects_covered),
            'covered_aspects': sum(aspects_covered.values())
        }
    
    def quality_score(self, thinking_text: str, output: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate overall quality score for thinking process
        
        Args:
            thinking_text: Thinking section content
            output: Optional structured output
        
        Returns:
            Quality assessment with score
        """
        if not thinking_text:
            return {
                'quality_score': 0.0,
                'length_score': 0.0,
                'terminology_score': 0.0,
                'completeness_score': 0.0
            }
        
        # Length score (longer thinking usually better, but not too long)
        ideal_length = 500  # characters
        length = len(thinking_text)
        length_score = min(1.0, length / ideal_length)
        
        # Terminology score
        term_analysis = self.analyze_terminology(thinking_text)
        terminology_score = min(1.0, term_analysis['unique_terms'] / 5)  # Expect at least 5 terms
        
        # Completeness score
        if output:
            completeness = self.assess_completeness(thinking_text, output)
            completeness_score = completeness['completeness_score']
        else:
            completeness_score = 0.5  # Default if no output provided
        
        # Weighted overall score
        quality_score = (
            0.3 * length_score +
            0.3 * terminology_score +
            0.4 * completeness_score
        )
        
        return {
            'quality_score': quality_score,
            'length_score': length_score,
            'terminology_score': terminology_score,
            'completeness_score': completeness_score,
            'thinking_length': length,
            'unique_terms_used': term_analysis['unique_terms']
        }


if __name__ == "__main__":
    # Test the extractor
    extractor = ThinkingExtractor()
    
    sample_thinking = """
1. تحديد الورثة: الأم والأب والبنت
2. الأم ترث السدس لوجود الفرع الوارث
3. البنت ترث النصف فرضاً
4. الأب يرث السدس والباقي تعصيباً
5. لا يوجد عول أو رد في هذه الحالة
6. التوزيع النهائي بعد التصحيح
"""
    
    steps = extractor.extract_steps(sample_thinking)
    print(f"Steps extracted: {len(steps)}")
    
    term_analysis = extractor.analyze_terminology(sample_thinking)
    print(f"Terms used: {term_analysis['unique_terms']}")
    
    quality = extractor.quality_score(sample_thinking)
    print(f"Quality score: {quality['quality_score']:.2f}")
