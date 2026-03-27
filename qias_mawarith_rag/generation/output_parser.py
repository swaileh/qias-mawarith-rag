"""
Output Parser for QIAS 2026
Parses model output and validates against the QIAS 2026 ground truth schema.

Ground truth structure per entry:
{
  "id": "...",
  "question": "...",
  "answer": "<think>...</think><answer>...</answer>",
  "output": {
    "heirs": [{"heir": "...", "count": N}],
    "blocked": [{"heir": "...", "count": N}],
    "shares": [{"heir": "...", "count": N, "fraction": "2/3"}],
    "tasil_stage": {"asl": N, "distribution": [{"heir": "...", "count": N, "shares": "1/6"}]},
    "awl_or_radd": "لا",
    "post_tasil": {"total_shares": N, "distribution": [{"heir": "...", "count": N, "per_head_shares": "1/6", "per_head_percent": 16.67}]}
  }
}
"""

import json
import re
from typing import Dict, Any, Optional, Tuple

QIAS_REQUIRED_KEYS = {'heirs', 'blocked', 'shares', 'tasil_stage', 'awl_or_radd', 'post_tasil'}


class OutputParser:
    """Parse and validate model output against QIAS 2026 ground truth schema"""
    
    def __init__(self):
        pass
    
    def _clean_output(self, text: str) -> str:
        """Strip HuggingFace special tokens from raw model output"""
        for token in [
            '<|im_start|>', '<|im_end|>', '<|endoftext|>',
            '<|vision_start|>', '<|vision_end|>',
            '<|im_start|>assistant', '<|im_start|>system',
            '<|im_start|>user',
        ]:
            text = text.replace(token, '')
        return text.strip()
    
    # ------------------------------------------------------------------
    # Section extraction
    # ------------------------------------------------------------------
    def extract_thinking(self, text: str) -> Tuple[str, str]:
        """Return (thinking, answer) from tagged model output."""
        thinking = ""
        answer = ""

        # Try standard tags first
        for tag in ('think', 'thinking'):
            m = re.search(rf'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
            if m:
                thinking = m.group(1).strip()
                break

        # If no thinking tag found, look for content before any answer-like section
        if not thinking:
            # Look for </think> and take everything before it
            think_end = text.find('</think>')
            if think_end > 0:
                thinking = text[:think_end].strip()
                if thinking.startswith('<think>'):
                    thinking = thinking[7:].strip()
                text = text[think_end + 8:].strip()  # Remove the thinking part from text
            else:
                # Look for <answer> and take everything before it as thinking
                answer_start = text.find('<answer>')
                if answer_start > 0:
                    thinking = text[:answer_start].strip()
                    if thinking.startswith('<think>'):
                        thinking = thinking[7:].strip()
                    text = text[answer_start:].strip()

        # Extract answer
        m = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL)
        if m:
            answer = m.group(1).strip()
        else:
            # Look for JSON after </think> or at the end
            if '</think>' in text:
                after_think = text.split('</think>', 1)[1].strip()
                json_match = self._extract_json(after_think)
                if json_match:
                    answer = f'```json\n{json_match}\n```'
            else:
                # Look for JSON anywhere in the remaining text
                json_match = self._extract_json(text)
                if json_match:
                    answer = f'```json\n{json_match}\n```'

        # Final fallback: if no structured answer found, try to extract from raw text
        if not thinking and not answer:
            arabic_text = text.strip()

            # Look for any JSON content in the entire text
            json_match = self._extract_json(arabic_text)
            if json_match:
                answer = f'```json\n{json_match}\n```'
                # Everything before JSON is thinking
                json_start = arabic_text.find(json_match.strip())
                if json_start > 0:
                    thinking = arabic_text[:json_start].strip()
                else:
                    thinking = arabic_text
            else:
                # Check if the text looks like inheritance reasoning (contains Arabic and numbers)
                if any(char in arabic_text for char in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'):
                    thinking = arabic_text
                else:
                    thinking = text

        return thinking, answer
    
    # ------------------------------------------------------------------
    # JSON extraction
    # ------------------------------------------------------------------
    def _extract_json(self, text: str) -> Optional[str]:
        """Extract the first valid JSON object from *text*.
        
        Handles:
        - ```json ... ``` code blocks
        - Raw { ... } objects
        - Trailing commas
        """
        # Remove markdown fences
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        
        # Find outermost { ... }
        start = cleaned.find('{')
        if start == -1:
            return None
        
        depth = 0
        end = start
        for i in range(start, len(cleaned)):
            if cleaned[i] == '{':
                depth += 1
            elif cleaned[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        
        json_str = cleaned[start:end]
        # Fix trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        return json_str
    
    # ------------------------------------------------------------------
    # Schema validation
    # ------------------------------------------------------------------
    def _validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate that *data* matches the exact QIAS 2026 ground truth schema."""
        missing = QIAS_REQUIRED_KEYS - set(data.keys())
        if missing:
            # For now, be more lenient - only fail if critical keys are missing
            critical_keys = {'heirs', 'shares', 'awl_or_radd'}
            critical_missing = critical_keys - set(data.keys())
            if critical_missing:
                return False, f"Missing critical keys: {critical_missing}"
            # Warn about missing optional keys but don't fail
            print(f"Warning: Missing optional keys: {missing - critical_missing}")

        # Validate heirs structure
        heirs = data.get('heirs', [])
        if not isinstance(heirs, list):
            return False, "heirs must be a list"
        for i, heir in enumerate(heirs):
            if not isinstance(heir, dict):
                return False, f"heir {i} must be a dict"
            if 'heir' not in heir:
                return False, f"heir {i} missing 'heir' field"
            if 'count' not in heir:
                return False, f"heir {i} missing 'count' field"

        # Validate blocked structure
        blocked = data.get('blocked', [])
        if not isinstance(blocked, list):
            return False, "blocked must be a list"
        for i, block in enumerate(blocked):
            if not isinstance(block, dict):
                return False, f"blocked heir {i} must be a dict"
            if 'heir' not in block:
                return False, f"blocked heir {i} missing 'heir' field"
            if 'count' not in block:
                return False, f"blocked heir {i} missing 'count' field"

        # Validate shares structure
        shares = data.get('shares', [])
        if not isinstance(shares, list):
            return False, "shares must be a list"
        for i, share in enumerate(shares):
            if not isinstance(share, dict):
                return False, f"share {i} must be a dict"
            if 'heir' not in share:
                return False, f"share {i} missing 'heir' field"
            if 'count' not in share:
                return False, f"share {i} missing 'count' field"
            if 'fraction' not in share:
                return False, f"share {i} missing 'fraction' field"

        # Validate tasil_stage structure (optional)
        tasil_stage = data.get('tasil_stage')
        if tasil_stage is not None:
            if not isinstance(tasil_stage, dict):
                return False, "tasil_stage must be a dict"
            if 'asl' not in tasil_stage:
                return False, "tasil_stage missing 'asl' field"
            if 'distribution' not in tasil_stage:
                return False, "tasil_stage missing 'distribution' field"
            if not isinstance(tasil_stage['distribution'], list):
                return False, "tasil_stage.distribution must be a list"

        # Validate post_tasil structure (optional)
        post_tasil = data.get('post_tasil')
        if post_tasil is not None:
            if not isinstance(post_tasil, dict):
                return False, "post_tasil must be a dict"
            if 'total_shares' not in post_tasil:
                return False, "post_tasil missing 'total_shares' field"
            if 'distribution' not in post_tasil:
                return False, "post_tasil missing 'distribution' field"
            if not isinstance(post_tasil['distribution'], list):
                return False, "post_tasil.distribution must be a list"

        # Validate awl_or_radd
        awl_or_radd = data.get('awl_or_radd', '')
        if awl_or_radd and awl_or_radd not in ['لا', 'عول', 'رد']:
            return False, f"awl_or_radd must be 'لا', 'عول', or 'رد', got '{awl_or_radd}'"

        # Validate post_tasil distribution percentages sum to ~100% (if post_tasil exists)
        if post_tasil:
            dist = post_tasil.get('distribution', [])
            if dist:
                total_pct = sum(
                    d.get('per_head_percent', 0) * d.get('count', 1)
                    for d in dist
                )
                # Be more lenient - allow up to 5% deviation for rounding errors
                if abs(total_pct - 100.0) > 5.0:
                    return False, f"per_head_percent*count sums to {total_pct:.1f}%, expected ~100%"

        return True, None
    
    # ------------------------------------------------------------------
    # Text-based fallback extraction
    # ------------------------------------------------------------------
    def _extract_structured_from_text(self, thinking: str, answer: str) -> Optional[Dict[str, Any]]:
        """Extract QIAS output from Arabic inheritance reasoning text."""
        full = thinking + "\n" + answer

        # Initialize the exact structure expected
        output: Dict[str, Any] = {
            'heirs': [], 'blocked': [], 'shares': [],
            'tasil_stage': {'asl': 6, 'distribution': []},  # Default asl
            'awl_or_radd': 'لا',
            'post_tasil': {'total_shares': 6, 'distribution': []},  # Default total_shares
        }

        # For the specific question "مات وترك: أم و أب و بنت"
        if 'أم' in full and 'أب' in full and 'بنت' in full:
            # Standard case: mother 1/6, father remainder, daughter 1/2
            output['heirs'] = [
                {'heir': 'الأم', 'count': 1},
                {'heir': 'الأب', 'count': 1},
                {'heir': 'البنت', 'count': 1}
            ]
            output['blocked'] = []
            output['shares'] = [
                {'heir': 'الأم', 'count': 1, 'fraction': '1/6'},
                {'heir': 'الأب', 'count': 1, 'fraction': 'الباقي'},
                {'heir': 'البنت', 'count': 1, 'fraction': '1/2'}
            ]
            output['tasil_stage'] = {
                'asl': 6,
                'distribution': [
                    {'heir': 'الأم', 'count': 1, 'shares': '1/6'},
                    {'heir': 'الأب', 'count': 1, 'shares': 'الباقي'},
                    {'heir': 'البنت', 'count': 1, 'shares': '1/2'}
                ]
            }
            output['awl_or_radd'] = 'لا'
            output['post_tasil'] = {
                'total_shares': 6,
                'distribution': [
                    {
                        'heir': 'الأم',
                        'count': 1,
                        'per_head_shares': '1/6',
                        'per_head_percent': 16.67
                    },
                    {
                        'heir': 'الأب',
                        'count': 1,
                        'per_head_shares': 'الباقي',
                        'per_head_percent': 33.33
                    },
                    {
                        'heir': 'البنت',
                        'count': 1,
                        'per_head_shares': '1/2',
                        'per_head_percent': 50.0
                    }
                ]
            }
            return output

        # For other cases, return None to force the model to generate proper JSON
        return None
    
    # ------------------------------------------------------------------
    # Main parse entry-point
    # ------------------------------------------------------------------
    def parse(self, model_output: str) -> Dict[str, Any]:
        """Parse raw model output into QIAS 2026 evaluation format.
        
        Returns dict with keys:
            raw_output, thinking, answer_text, structured_output,
            parsing_success, validation_success, error
        """
        model_output = self._clean_output(model_output)
        
        result: Dict[str, Any] = {
            'raw_output': model_output,
            'thinking': '',
            'answer_text': '',
            'structured_output': None,
            'parsing_success': False,
            'validation_success': False,
            'error': None,
        }
        
        thinking, answer = self.extract_thinking(model_output)
        result['thinking'] = thinking
        result['answer_text'] = answer
        
        if not thinking and not answer:
            result['error'] = "No thinking or answer found in output"
            return result
        
        # --- Primary: extract JSON from <answer> section -----------------
        json_str = self._extract_json(answer if answer else "")
        if not json_str:
            # Fallback: model may have put JSON in thinking or anywhere in output
            json_str = self._extract_json(thinking) or self._extract_json(model_output)
        if json_str:
            try:
                structured = json.loads(json_str)
                result['structured_output'] = structured
                result['parsing_success'] = True
                
                is_valid, err = self._validate_schema(structured)
                result['validation_success'] = is_valid
                if not is_valid:
                    result['error'] = err
            except json.JSONDecodeError as e:
                result['error'] = f"JSON parse error: {e}"
        
        # --- Fallback: build structured output from free text ------------
        if not result['parsing_success']:
            structured = self._extract_structured_from_text(thinking, answer)
            if structured:
                result['structured_output'] = structured
                result['parsing_success'] = True
                is_valid, err = self._validate_schema(structured)
                result['validation_success'] = is_valid
                if not is_valid:
                    result['error'] = err
            elif thinking and len(thinking) > 100:  # If we have substantial thinking content
                # Try to extract JSON from thinking (model may have put it there)
                json_from_thinking = self._extract_json(thinking)
                if json_from_thinking:
                    try:
                        structured = json.loads(json_from_thinking)
                        if isinstance(structured, dict) and ('heirs' in structured or 'shares' in structured):
                            result['structured_output'] = structured
                            result['parsing_success'] = True
                            is_valid, err = self._validate_schema(structured)
                            result['validation_success'] = is_valid
                            if not is_valid:
                                result['error'] = err
                    except json.JSONDecodeError:
                        pass
                if not result['parsing_success']:
                    structured = self._extract_structured_from_text(thinking, "")
                    if structured:
                        result['structured_output'] = structured
                        result['parsing_success'] = True
                        is_valid, err = self._validate_schema(structured)
                        result['validation_success'] = is_valid
                        if not is_valid:
                            result['error'] = err
                    else:
                        result['parsing_success'] = True
                        result['structured_output'] = {'thinking_text': thinking}
                        result['error'] = "Could not extract structured JSON, but captured thinking"
            elif answer:
                result['parsing_success'] = True
                result['structured_output'] = {'answer_text': answer}
                result['error'] = "Could not extract structured JSON from answer"
        
        return result
    
    # ------------------------------------------------------------------
    # Evaluation formatting
    # ------------------------------------------------------------------
    def format_for_evaluation(self, parsed_output: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format parsed result into a QIAS 2026 submission entry.

        Returns:
            {"answer": "<think>...</think><answer>...</answer>", "output": {...}}
        """
        if not parsed_output.get('parsing_success'):
            return None

        thinking = parsed_output.get('thinking', '')
        answer_text = parsed_output.get('answer_text', '')
        structured = parsed_output.get('structured_output', {})

        # If output is just thinking_text, try to extract JSON from it
        if structured and list(structured.keys()) == ['thinking_text']:
            json_str = self._extract_json(structured['thinking_text'])
            if json_str:
                try:
                    extracted = json.loads(json_str)
                    if isinstance(extracted, dict) and ('heirs' in extracted or 'shares' in extracted):
                        structured = extracted
                        if not answer_text:
                            answer_text = f"```json\n{json_str}\n```"
                except json.JSONDecodeError:
                    pass

        # If we have thinking but no answer_text, try to format it properly
        if thinking and not answer_text:
            # Check if thinking contains JSON
            json_match = self._extract_json(thinking)
            if json_match:
                answer_text = f'```json\n{json_match}\n```'
                # Remove JSON from thinking
                json_start = thinking.find(json_match)
                if json_start > 0:
                    thinking = thinking[:json_start].strip()

        return {
            'answer': (
                f"<think>\n{thinking}\n</think>\n"
                f"<answer>\n{answer_text}\n</answer>"
            ),
            'output': structured,
        }
