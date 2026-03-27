"""
Fine-tuning Script for Qwen3 Model (Optional)
LoRA fine-tuning on QIAS dataset for improved performance
"""

import yaml
import json
from typing import List, Dict, Any
from pathlib import Path


class FineTuner:
    """Fine-tune Qwen3 model using LoRA/QLoRA"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize fine-tuner"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        print("⚠️ Fine-tuning requires additional setup:")
        print("   1. Install Unsloth: pip install unsloth")
        print("   2. Have QIAS training data ready")
        print("   3. GPU with sufficient memory (A100 recommended)")
    
    def prepare_training_data(
        self,
        dataset: List[Dict[str, Any]],
        output_file: str = "training_data.jsonl"
    ) -> None:
        """Convert QIAS dataset to fine-tuning format
        
        Args:
            dataset: QIAS dataset
            output_file: Output file for training data
        """
        training_data = []
        
        for item in dataset:
            question = item.get('question', '')
            answer = item.get('answer', '')
            
            # Format for instruction tuning
            training_example = {
                "instruction": question,
                "input": "",  # Can add retrieved context here
                "output": answer
            }
            
            training_data.append(training_example)
        
        # Save to JSONL
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in training_data:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"Prepared {len(training_data)} training examples")
        print(f"Saved to: {output_path}")
    
    def create_training_script(self) -> str:
        """Generate training script template
        
        Returns:
            Training script as string
        """
        script = """
# Fine-tuning Script for Qwen3 with Unsloth
# This is a template - adjust parameters as needed

from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

# Load model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen2.5-7B-Instruct",  # Start with 7B
    max_seq_length=8192,
    dtype=None,  # Auto-detect
    load_in_4bit=True,  # Use QLoRA
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    use_gradient_checkpointing=True
)

# Load training data
dataset = load_dataset("json", data_files="training_data.jsonl")

# Format prompts
def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs = examples["input"]
    outputs = examples["output"]
    
    texts = []
    for instruction, input_text, output in zip(instructions, inputs, outputs):
        text = f"### Instruction:\\n{instruction}\\n\\n"
        if input_text:
            text += f"### Input:\\n{input_text}\\n\\n"
        text += f"### Response:\\n{output}"
        texts.append(text)
    
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)

# Training arguments
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    dataset_text_field="text",
    max_seq_length=8192,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=100,  # Adjust based on dataset size
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=10,
        output_dir="outputs",
        save_steps=50,
    ),
)

# Train
trainer.train()

# Save model
model.save_pretrained("qwen3_qias_lora")
tokenizer.save_pretrained("qwen3_qias_lora")

print("✓ Fine-tuning complete!")
"""
        return script
    
    def save_training_script(self, filename: str = "train_qwen3.py") -> None:
        """Save training script to file
        
        Args:
            filename: Output filename
        """
        script = self.create_training_script()
        
        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"Training script saved to: {output_path}")
        print("\nTo fine-tune:")
        print("  1. Install Unsloth: pip install unsloth")
        print("  2. Prepare data: python -c 'from qias_mawarith_rag.training.fine_tune import FineTuner; ft=FineTuner(); ft.prepare_training_data(dataset)'")
        print(f"  3. Run training: python {filename}")


if __name__ == "__main__":
    # Example usage
    tuner = FineTuner()
    
    # Generate training script
    tuner.save_training_script("train_qwen3.py")
    
    print("\n✓ Fine-tuning setup complete")
    print("\nNote: Fine-tuning is optional. The RAG system works well without it.")
    print("Only fine-tune if you need better performance on specific cases.")
