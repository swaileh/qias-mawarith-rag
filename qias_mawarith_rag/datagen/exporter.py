"""
Export utilities for training data.

Exports generated examples to various formats for LLM fine-tuning.
"""

import json
from pathlib import Path
from typing import List, Any


def export_to_jsonl(examples: List[Any], output_path: str) -> None:
    """
    Export examples to JSONL format for fine-tuning.
    
    Each line is a JSON object with:
    - input: Arabic problem text
    - output: JSON with heirs, shares, reasoning
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for ex in examples:
            record = {
                "input": ex.problem_text,
                "think": ex.reasoning_trace,
                "qa_nl": ex.qa_nl,
                "answer": {
                    "heirs": ex.heirs,
                    "blocked": ex.blocked_heirs,
                    "shares": ex.shares,
                    "awl_or_radd": ex.awl_or_radd,
                    "tasil_stage": ex.tasil_stage,
                    "post_tasil": ex.post_tasil,
                },
                "difficulty": ex.difficulty,
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"Exported {len(examples)} examples to {output_path}")


def export_to_hf_format(examples: List[Any], output_dir: str) -> None:
    """
    Export to Hugging Face datasets format.
    
    Creates train.jsonl and metadata.json.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export data
    export_to_jsonl(examples, output_dir / "train.jsonl")
    
    # Create metadata
    metadata = {
        "name": "qias2026-synthetic",
        "description": "Synthetic training data for Islamic inheritance reasoning",
        "total_examples": len(examples),
        "difficulty_distribution": {
            "basic": sum(1 for e in examples if e.difficulty == "basic"),
            "advanced": sum(1 for e in examples if e.difficulty == "advanced"),
        },
        "features": {
            "input": {"type": "string", "description": "Arabic problem text"},
            "think": {"type": "string", "description": "Step-by-step reasoning"},
            "qa_nl": {"type": "string", "description": "Natural-language Q&A (السؤال / الجواب)"},
            "answer": {"type": "object", "description": "Structured answer JSON"},
            "difficulty": {"type": "string", "description": "basic or advanced"},
        }
    }
    
    with open(output_dir / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"Exported HuggingFace dataset to {output_dir}")


def export_to_chat_format(examples: List[Any], output_path: str) -> None:
    """
    Export to chat/instruction format for fine-tuning.
    
    Format:
    {"messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]}
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    system_prompt = """أنت خبير في علم المواريث الإسلامي (الفرائض).
مهمتك: حل مسائل الميراث خطوة بخطوة.

عند استلام مسألة ميراث:
1. حدد الورثة الموجودين
2. طبق قواعد الحجب
3. حدد فرض كل وارث
4. احسب أصل المسألة
5. طبق العول أو الرد إن لزم
6. أعطِ الإجابة النهائية بصيغة JSON"""

    with open(output_path, 'w', encoding='utf-8') as f:
        for ex in examples:
            answer_json = json.dumps({
                "heirs": ex.heirs,
                "blocked": ex.blocked_heirs,
                "shares": ex.shares,
                "awl_or_radd": ex.awl_or_radd,
            }, ensure_ascii=False, indent=2)
            
            assistant_response = f"""<think>
{ex.reasoning_trace}
</think>

<answer>
{answer_json}
</answer>"""
            
            record = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": ex.problem_text},
                    {"role": "assistant", "content": assistant_response}
                ]
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"Exported {len(examples)} chat examples to {output_path}")


def export_to_train_format(examples: List[Any], output_dir: str, examples_per_file: int = 100) -> None:
    """
    Export to the same format as ./train dataset.
    
    Creates multiple JSON files with 100 examples each, matching
    the qias2025_almawarith_part*.json structure.
    
    Format:
    {
        "id": "...",
        "question": "...",
        "answer": "<think>...</think>\n\n<answer>...</answer>",
        "category": "simple" | "complex",
        "output": { heirs, blocked, shares, tasil_stage, awl_or_radd, post_tasil }
    }
    """
    import uuid
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Split into chunks
    chunks = [examples[i:i + examples_per_file] for i in range(0, len(examples), examples_per_file)]
    
    total_exported = 0
    for chunk_idx, chunk in enumerate(chunks, 1):
        records = []
        for ex in chunk:
            # Build answer with <think> and <answer> tags
            answer_json = json.dumps({
                "heirs": ex.heirs,
                "blocked": ex.blocked_heirs,
                "shares": ex.shares,
                "awl_or_radd": ex.awl_or_radd,
            }, ensure_ascii=False, indent=2)
            
            answer = f"<think>\n{ex.reasoning_trace}\n</think>\n\n<answer>\n{answer_json}\n</answer>"
            
            # Build output structure
            output = {
                "heirs": ex.heirs,
                "blocked": ex.blocked_heirs,
                "shares": ex.shares,
                "tasil_stage": ex.tasil_stage,
                "awl_or_radd": ex.awl_or_radd,
                "post_tasil": ex.post_tasil,
            }
            
            record = {
                "id": uuid.uuid4().hex[:8],
                "question": ex.problem_text,
                "answer": answer,
                "qa_nl": ex.qa_nl,
                "category": "simple" if ex.difficulty == "basic" else "complex",
                "output": output,
            }
            records.append(record)
        
        # Write file
        filename = f"synthetic_mawarith_part{chunk_idx:02d}.json"
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        total_exported += len(records)
    
    print(f"Exported {total_exported} examples to {len(chunks)} files in {output_dir}")
