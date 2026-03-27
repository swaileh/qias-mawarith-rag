"""
Multi-GPU worker for parallel RAG inference.

Each worker runs in a separate process with its own GPU (CUDA_VISIBLE_DEVICES).
Writes to worker-specific file; main process merges and sorts by question_id.
"""

import os
import json
from typing import List, Dict, Any


def worker_process(
    gpu_id: int,
    items: List[Dict[str, Any]],
    output_path: str,
    config_path: str,
    is_test: bool,
) -> int:
    """Worker: load pipeline on GPU gpu_id, process items, write to JSONL.

    Must set CUDA_VISIBLE_DEVICES before any torch/transformers import.
    Writes to output_path.worker{gpu_id} for later merge.
    """
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    from qias_mawarith_rag.pipeline import RAGPipeline

    pipeline = RAGPipeline(config_path=config_path)
    worker_path = f"{output_path}.worker{gpu_id}"

    with open(worker_path, "w", encoding="utf-8") as outf:
        for item in items:
            idx = item["index"]
            question = item["question"]
            q_id = item.get("id", "")

            res = pipeline.query(question)
            res["id"] = q_id

            if is_test:
                formatted = pipeline.output_parser.format_for_evaluation(res["parsed_output"])
                entry = {"question_id": idx + 1, "id": q_id, "question": question}
                if formatted:
                    entry["answer"] = formatted["answer"]
                    entry["output"] = formatted["output"]
                else:
                    entry["answer"] = res.get("raw_output", "")
                    entry["output"] = res["parsed_output"].get("structured_output") or {}
            else:
                entry = {
                    "question_id": idx + 1,
                    "id": q_id,
                    "question": question,
                    "ground_truth": item.get("output", {}),
                    "model_prediction": res["parsed_output"].get("structured_output", {}),
                    "parsing_success": res["parsed_output"].get("parsing_success", False),
                    "validation_success": res["parsed_output"].get("validation_success", False),
                    "raw_response": res.get("raw_output", ""),
                    "thinking": res["parsed_output"].get("thinking", ""),
                }

            outf.write(json.dumps(entry, ensure_ascii=False) + "\n")
            outf.flush()

    return len(items)
