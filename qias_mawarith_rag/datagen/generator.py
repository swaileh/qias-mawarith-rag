"""
Core data generator for QIAS 2026 competition.

Generates inheritance problems with correct solutions using the Mawarith calculator.
"""

import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add parent to path

from qias_mawarith_rag.calculator.scalc import InheritanceCalculator


@dataclass
class GeneratedExample:
    """A single training example."""
    problem_text: str           # Arabic problem description
    heirs: List[Dict]           # List of heirs with counts
    blocked_heirs: List[Dict]   # Blocked heirs
    shares: List[Dict]          # Share distribution
    awl_or_radd: str           # "لا" / "عول" / "رد"
    tasil_stage: Dict          # Base calculation
    post_tasil: Dict           # Final shares
    reasoning_trace: str       # Arabic Fiqh reasoning (<think>)
    qa_nl: str                 # natural-language Q&A (السؤال / الجواب)
    difficulty: str            # "basic" or "advanced"
    

# Heir types with Arabic names and categories
HEIR_TYPES = {
    # Spouses
    "زوج": {"gender": "M", "category": "spouse", "max_count": 1},
    "زوجة": {"gender": "F", "category": "spouse", "max_count": 4},
    
    # Descendants
    "ابن": {"gender": "M", "category": "descendant", "max_count": 5},
    "بنت": {"gender": "F", "category": "descendant", "max_count": 5},
    "ابن ابن": {"gender": "M", "category": "descendant", "max_count": 4},
    "بنت ابن": {"gender": "F", "category": "descendant", "max_count": 4},
    "ابن ابن ابن": {"gender": "M", "category": "descendant", "max_count": 3},
    "بنت ابن ابن": {"gender": "F", "category": "descendant", "max_count": 3},
    
    # Ascendants
    "أب": {"gender": "M", "category": "ascendant", "max_count": 1},
    "أم": {"gender": "F", "category": "ascendant", "max_count": 1},
    "جد": {"gender": "M", "category": "ascendant", "max_count": 1},
    "أب الأب": {"gender": "M", "category": "ascendant", "max_count": 1},
    "أم الأم": {"gender": "F", "category": "ascendant", "max_count": 1},
    "أم الأب": {"gender": "F", "category": "ascendant", "max_count": 1},
    
    # Siblings
    "أخ شقيق": {"gender": "M", "category": "sibling", "max_count": 5},
    "أخت شقيقة": {"gender": "F", "category": "sibling", "max_count": 5},
    "أخ لأب": {"gender": "M", "category": "sibling", "max_count": 4},
    "أخت لأب": {"gender": "F", "category": "sibling", "max_count": 4},
    "أخ لأم": {"gender": "M", "category": "sibling", "max_count": 3},
    "أخت لأم": {"gender": "F", "category": "sibling", "max_count": 3},
    
    # Uncles/Cousins
    "عم شقيق": {"gender": "M", "category": "uncle", "max_count": 3},
    "عم لأب": {"gender": "M", "category": "uncle", "max_count": 3},
    "ابن عم شقيق": {"gender": "M", "category": "cousin", "max_count": 3},
    "ابن عم لأب": {"gender": "M", "category": "cousin", "max_count": 3},
}

# Difficulty distributions
BASIC_HEIR_TYPES = [
    "زوج", "زوجة", "ابن", "بنت", "أب", "أم", 
    "أخ شقيق", "أخت شقيقة", "جد"
]

ADVANCED_HEIR_TYPES = list(HEIR_TYPES.keys())


class FiqhDataGenerator:
    """
    Generate synthetic inheritance problems for LLM training.
    
    Usage:
        generator = FiqhDataGenerator()
        examples = generator.generate_batch(1000)
        generator.export_jsonl(examples, "training_data.jsonl")
    """
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.arabic_gen = None  # Lazy load
        self.reasoning_gen = None  # Lazy load
        self.nl_answer_gen = None  # Lazy load
        self._seen_combinations: set = set()
    
    def generate_batch(
        self, 
        count: int, 
        difficulty: str = "mixed",
        include_edge_cases: bool = True,
        unique: bool = False,
    ) -> List[GeneratedExample]:
        """Generate a batch of training examples.
        
        Args:
            count: Number of examples to generate.
            difficulty: "basic", "advanced", or "mixed".
            include_edge_cases: Reserved for future use.
            unique: When True, skip any heir combination already seen
                    across all generate_batch / generate_edge_cases calls
                    on this instance. Useful to avoid duplicate training
                    samples; disable for maximum throughput.
        """
        examples = []
        attempts = 0
        max_attempts = count * 10  # cap to avoid infinite loop when pool is exhausted

        while len(examples) < count and attempts < max_attempts:
            attempts += 1
            if attempts % 100 == 0:
                print(f"Generated {len(examples)}/{count} (attempts: {attempts})...", end="\r")

            # Determine difficulty for this example
            diff = random.choice(["basic", "advanced"]) if difficulty == "mixed" else difficulty

            # Generate random heirs
            heirs = self._generate_random_heirs(diff)

            if unique:
                key = tuple(sorted((h["heir"], h["count"]) for h in heirs))
                if key in self._seen_combinations:
                    continue
                self._seen_combinations.add(key)

            try:
                calc = InheritanceCalculator()
                result = calc.calculate(heirs)
                example = self._result_to_example(heirs, result, diff)
                examples.append(example)
            except Exception:
                continue

        if len(examples) < count:
            print(f"\nWarning: only generated {len(examples)}/{count} unique examples before exhausting attempts.")

        print(f"Generated {len(examples)} examples")
        return examples
    
    def _generate_random_heirs(self, difficulty: str) -> List[Dict]:
        """Generate a random but valid heir combination."""
        heir_pool = BASIC_HEIR_TYPES if difficulty == "basic" else ADVANCED_HEIR_TYPES
        
        # Randomly select 1-6 heir types
        num_types = random.randint(1, 6)
        selected_types = random.sample(heir_pool, min(num_types, len(heir_pool)))
        
        heirs = []
        for heir_type in selected_types:
            info = HEIR_TYPES[heir_type]
            max_count = info["max_count"]
            count = random.randint(1, max_count)
            heirs.append({"heir": heir_type, "count": count})
        
        return heirs
    
    def _result_to_example(
        self, 
        input_heirs: List[Dict], 
        result: Any,
        difficulty: str
    ) -> GeneratedExample:
        """Convert calculator result to training example."""
        from .arabic import ArabicProblemGenerator, ArabicReasoningGenerator, ArabicNLAnswerGenerator
        
        if self.arabic_gen is None:
            self.arabic_gen = ArabicProblemGenerator()
            self.reasoning_gen = ArabicReasoningGenerator()
            self.nl_answer_gen = ArabicNLAnswerGenerator()
        
        # Extract shares from result - use result.shares directly
        shares = []
        blocked = []
        
        # Get blocked heirs
        for h in result.blocked:
            heir_name = h.get("heir", "")
            count = h.get("count", 1)
            blocked.append({"heir": heir_name, "count": count})
        
        # Get shares
        for s in result.shares:
            heir_name = s.get("heir", "")
            count = s.get("count", 1)
            fraction = s.get("fraction", "0")
            shares.append({
                "heir": heir_name, 
                "count": count,
                "fraction": str(fraction)
            })
        
        # Generate Arabic problem text
        problem_text = self.arabic_gen.generate(input_heirs)
        
        # Generate reasoning trace
        reasoning = self.reasoning_gen.generate(input_heirs, shares, blocked, result)
        
        # Generate natural-language Q&A
        qa_nl = self.nl_answer_gen.generate(problem_text, shares, blocked, result)
        
        return GeneratedExample(
            problem_text=problem_text,
            heirs=[{"heir": s["heir"], "count": s["count"]} for s in shares],
            blocked_heirs=blocked,
            shares=shares,
            awl_or_radd=result.awl_or_radd,
            tasil_stage=result.tasil_stage,
            post_tasil=result.post_tasil,
            reasoning_trace=reasoning,
            qa_nl=qa_nl,
            difficulty=difficulty
        )
    
    def generate_edge_cases(self, count_per_type: int = 100, unique: bool = False) -> List[GeneratedExample]:
        """Generate examples specifically for edge cases."""
        examples = []
        
        # Awl cases (shares exceed 100%)
        awl_patterns = [
            [{"heir": "زوج", "count": 1}, {"heir": "أخت شقيقة", "count": 2}, {"heir": "أم", "count": 1}],
            [{"heir": "زوجة", "count": 1}, {"heir": "أم", "count": 1}, {"heir": "أخت شقيقة", "count": 2}, {"heir": "أخت لأم", "count": 2}],
        ]
        
        # Radd cases (shares don't reach 100%, no residuary)
        radd_patterns = [
            [{"heir": "أم", "count": 1}, {"heir": "بنت", "count": 1}],
            [{"heir": "أم", "count": 1}, {"heir": "أخت لأم", "count": 2}],
        ]
        
        # Grandfather+siblings (Muqasama)
        grandfather_patterns = [
            [{"heir": "جد", "count": 1}, {"heir": "أخ شقيق", "count": 2}],
            [{"heir": "جد", "count": 1}, {"heir": "أخت شقيقة", "count": 3}],
            [{"heir": "أب الأب", "count": 1}, {"heir": "أخ شقيق", "count": 1}, {"heir": "أخت شقيقة", "count": 2}],
        ]
        
        # Special classical cases
        special_cases = [
            # Umariyyah (العمرية)
            [{"heir": "زوج", "count": 1}, {"heir": "أم", "count": 1}, {"heir": "أب", "count": 1}],
            [{"heir": "زوجة", "count": 1}, {"heir": "أم", "count": 1}, {"heir": "أب", "count": 1}],
        ]
        
        all_patterns = awl_patterns + radd_patterns + grandfather_patterns + special_cases
        
        for pattern in all_patterns:
            if unique:
                key = tuple(sorted((h["heir"], h["count"]) for h in pattern))
                if key in self._seen_combinations:
                    continue
                self._seen_combinations.add(key)

            for _ in range(count_per_type // len(all_patterns)):
                try:
                    calc = InheritanceCalculator()
                    result = calc.calculate(pattern)
                    example = self._result_to_example(pattern, result, "advanced")
                    examples.append(example)
                except Exception:
                    continue

        return examples


def main():
    """Generate sample training data."""
    generator = FiqhDataGenerator(seed=42)
    
    # Generate mixed difficulty examples
    examples = generator.generate_batch(100, difficulty="mixed")
    
    # Add edge cases
    edge_examples = generator.generate_edge_cases(50)
    
    all_examples = examples + edge_examples
    
    print(f"\nTotal examples: {len(all_examples)}")
    print(f"Basic: {sum(1 for e in all_examples if e.difficulty == 'basic')}")
    print(f"Advanced: {sum(1 for e in all_examples if e.difficulty == 'advanced')}")
    
    # Show sample
    if all_examples:
        ex = all_examples[0]
        print("\nSample problem:")
        print(f"  Text: {ex.problem_text[:100]}...")
        print(f"  Heirs: {ex.heirs}")
        print(f"  Awl/Radd: {ex.awl_or_radd}")


if __name__ == "__main__":
    main()
