"""
Prompt Builder for RAG
Constructs prompts with retrieved context and few-shot examples
"""

import yaml
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class PromptBuilder:
    """Build prompts for the RAG system with context and examples"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize prompt builder"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.prompt_config = self.config['prompt']
        self.system_message = self.prompt_config.get('system_message', '')
        self.max_context_length = self.prompt_config.get('max_context_length', 2048)
        self.num_few_shot = self.prompt_config.get('few_shot_examples', 3)
        
        # Load few-shot examples if available
        self.few_shot_examples = self._load_few_shot_examples()
    
    def _load_few_shot_examples(self) -> List[Dict[str, Any]]:
        """Load few-shot examples from dataset"""
        # Try to load from QIAS dataset
        dataset_path = Path(self.config['evaluation']['dataset_path'])
        examples = []
        
        try:
            # Look for example files
            for json_file in dataset_path.glob("*.json"):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Take first few examples
                    if isinstance(data, list):
                        examples.extend(data[:self.num_few_shot])
                    
                    if len(examples) >= self.num_few_shot:
                        break
        except Exception as e:
            print(f"Could not load few-shot examples: {e}")
        
        return examples[:self.num_few_shot]
    
    def format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents as context
        
        Args:
            retrieved_docs: List of retrieved documents
        
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return ""
        
        context_parts = ["# السياق المسترجع من قاعدة المعرفة:\n"]
        current_length = 0
        
        for i, doc in enumerate(retrieved_docs):
            score = doc.get('rerank_score', doc.get('score', 0.0))
            source = doc.get('metadata', {}).get('source', 'unknown')
            
            doc_text = f"\n## مرجع {i+1} (الأهمية: {score:.3f}, المصدر: {source}):\n{doc['content']}\n"
            
            if current_length + len(doc_text) > self.max_context_length:
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        return "".join(context_parts)
    
    def format_few_shot_examples(self) -> str:
        """Format few-shot examples for the prompt
        
        Returns:
            Formatted examples string
        """
        if not self.few_shot_examples:
            return ""
        
        examples_text = ["# أمثلة على الحالات المشابهة:\n"]
        
        for i, example in enumerate(self.few_shot_examples):
            question = example.get('question', '')
            answer = example.get('answer', '')
            
            # Extract just the answer part (not the thinking)
            if '<answer>' in answer:
                answer_part = answer.split('<answer>')[1].split('</answer>')[0].strip()
            else:
                answer_part = answer[:500]  # Truncate if too long
            
            examples_text.append(f"\n## مثال {i+1}:\n")
            examples_text.append(f"السؤال: {question}\n")
            examples_text.append(f"الجواب: {answer_part}\n")
        
        return "".join(examples_text)
    
    def build_structured_output_instructions(self) -> str:
        """Build instructions matching QIAS 2026 competition output format exactly"""
        instructions = """
# تعليمات إجبارية - شكل الإجابة المطلوب لمسابقة QIAS 2026:

## تنسيق الإجابة المطلوب بدقة:

ابدأ إجابتك بـ <think> واكتب تفكيرك بالعربية، ثم أغلق بـ </think>

ثم ابدأ <answer> واكتب JSON المنظم، ثم أغلق بـ </answer>

مثال على التنسيق المطلوب:
<think>
التفكير المفصل هنا بالعربية...
</think>
<answer>
```json
{
  "heirs": [{"heir": "الأم", "count": 1}],
  "blocked": [{"heir": "البنت", "count": 1}],
  "shares": [{"heir": "الأم", "count": 1, "fraction": "1/6"}],
  "tasil_stage": {"asl": 6, "distribution": [{"heir": "الأم", "count": 1, "shares": "1/6"}]},
  "awl_or_radd": "لا",
  "post_tasil": {"total_shares": 6, "distribution": [{"heir": "الأم", "count": 1, "per_head_shares": "1/6", "per_head_percent": 16.67}]}
}
```
</answer>

## مثال محدد للمسألة الحالية:
إذا كانت المسألة "مات وترك: أم و أب و بنت"، فإن الإجابة يجب أن تكون:

<answer>
```json
{
  "heirs": [
    {"heir": "الأم", "count": 1},
    {"heir": "الأب", "count": 1},
    {"heir": "البنت", "count": 1}
  ],
  "blocked": [],
  "shares": [
    {"heir": "الأم", "count": 1, "fraction": "1/6"},
    {"heir": "الأب", "count": 1, "fraction": "الباقي"},
    {"heir": "البنت", "count": 1, "fraction": "1/2"}
  ],
  "tasil_stage": {
    "asl": 6,
    "distribution": [
      {"heir": "الأم", "count": 1, "shares": "1/6"},
      {"heir": "الأب", "count": 1, "shares": "الباقي"},
      {"heir": "البنت", "count": 1, "shares": "1/2"}
    ]
  },
  "awl_or_radd": "لا",
  "post_tasil": {
    "total_shares": 6,
    "distribution": [
      {
        "heir": "الأم",
        "count": 1,
        "per_head_shares": "1/6",
        "per_head_percent": 16.67
      },
      {
        "heir": "الأب",
        "count": 1,
        "per_head_shares": "الباقي",
        "per_head_percent": 33.33
      },
      {
        "heir": "البنت",
        "count": 1,
        "per_head_shares": "1/2",
        "per_head_percent": 50.0
      }
    ]
  }
}
```
</answer>

## تنبيه هام: يجب نسخ تنسيق JSON بالضبط كما هو موضح أعلاه، وتغيير القيم فقط حسب المسألة.

## خطوات التفكير المطلوبة بالترتيب:

**الخطوة الأولى: تحديد الورثة ومن لا يرث**
حدد جميع الورثة المذكورين وصنفهم (أصحاب فروض أو عصبات أو ذوو أرحام).

**الخطوة الثانية: تحديد المحجوبين من الورثة**
اذكر من يُحجب حجب حرمان ولماذا مع ذكر القاعدة الفقهية المستقرة.

**الخطوة الثالثة: تقدير الأنصبة الشرعية لأصحاب الفروض والعصبات**
حدد الفرض المقدر لكل وارث ككسر (مثل 1/6 أو 2/3) أو أنه عصبة يأخذ الباقي.

**الخطوة الرافقة: تأصيل المسألة**
احسب أصل المسألة (asl) من مقامات الفروض.

**الخطوة الخامسة: التحقق من العول أو الرد**
هل مجموع السهام أكبر من أصل المسألة (عول) أو أقل منه (رد)؟

**الخطوة السادسة: التصحيح (إن لزم)**
إذا لم تنقسم سهام مجموعة على عدد أفرادها، صحح المسألة بضرب أصل المسألة في جزء السهم.

**الخطوة السابعة: الأنصبة النهائية**
احسب نصيب كل فرد (per_head_shares) والنسبة المئوية (per_head_percent).

بعد الانتهاء من التفكير المفصل، أغلق التفكير بـ </think> واكتب الإجابة المنظمة بـ <answer>:

## قواعد إجبارية:
١. اكتب التفكير باللغة العربية فقط
٢. استخدم المصطلحات الفقهية الدقيقة (فرض، عصبة، حجب، عول، رد، تصحيح، تأصيل)
٣. ابدأ بالضبط بـ <think> واكتب التفكير ثم </think>
٤. ثم ابدأ بالضبط بـ <answer> واكتب JSON فقط ثم </answer>
٥. في "heirs" ضع الورثة الفعليين فقط (الذين يرثون)
٦. في "blocked" ضع المحجوبين فقط (مع عددهم)
٧. في "shares" ضع الفرض ككسر بالأرقام مثل "1/6" أو "2/3"
٨. في "tasil_stage" ضع أصل المسألة (asl) ونصيب كل وارث قبل التصحيح
٩. في "per_head_shares" ضع نصيب الفرد الواحد ككسر مثل "1/6"
١٠. في "per_head_percent" ضع النسبة المئوية للفرد الواحد (مثل 16.67)
١١. تأكد أن مجموع (per_head_percent × count) لجميع الورثة يساوي 100%

التنسيق النهائي المطلوب:
<think>
[التفكير المفصل بالعربية]
</think>
<answer>
```json
[JSON المنظم كما هو موضح]
```
</answer>

ابدأ الإجابة الآن:
"""
        return instructions
    
    def build_prompt(
        self,
        question: str,
        retrieved_docs: List[Dict[str, Any]] = None,
        web_search_results: str = None,
        include_examples: bool = True
    ) -> str:
        """Build complete prompt for the model
        
        Args:
            question: User question
            retrieved_docs: Retrieved documents from RAG
            web_search_results: Optional web search results
            include_examples: Whether to include few-shot examples
        
        Returns:
            Complete prompt string
        """
        prompt_parts = []
        
        # System message
        if self.system_message:
            prompt_parts.append(self.system_message)
            prompt_parts.append("\n\n")
        
        # Few-shot examples
        if include_examples:
            examples = self.format_few_shot_examples()
            if examples:
                prompt_parts.append(examples)
                prompt_parts.append("\n\n")
        
        # Retrieved context
        if retrieved_docs:
            context = self.format_context(retrieved_docs)
            if context:
                prompt_parts.append(context)
                prompt_parts.append("\n\n")
        
        # Web search results
        if web_search_results:
            prompt_parts.append(web_search_results)
            prompt_parts.append("\n\n")
        
        # Structured output instructions
        prompt_parts.append(self.build_structured_output_instructions())
        prompt_parts.append("\n\n")
        
        # The actual question
        prompt_parts.append(f"# السؤال:\n\n{question}\n\n")
        prompt_parts.append("# الإجابة:\n")
        prompt_parts.append("ابدأ الإجابة بـ <think> واكتب التفكير المفصل، ثم <answer> واكتب JSON المنظم.\n")
        
        return "".join(prompt_parts)


if __name__ == "__main__":
    # Test the prompt builder
    builder = PromptBuilder()
    
    # Test with sample question
    question = "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟"
    prompt = builder.build_prompt(question)
    
    print("Prompt built successfully")
    print(f"Prompt length: {len(prompt)} characters")
