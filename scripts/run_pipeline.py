#!/usr/bin/env python3
"""
QIAS 2026 RAG Pipeline - Full Test Script

  1. Build knowledge base (synthetic + optional PDF)
  2. Single question test with detailed output
  3. Batch evaluation on DEV (id, question, output) → predict + evaluate
  4. Batch inference on TEST (id, question only) → predict for submission
  5. QIAS 2026 competition evaluation report (dev only)

Data:
  - Dev:  /mnt/salah/qias/data/dev/qias2025_almawarith_part*.json
  - Test: /mnt/salah/qias/data/test/qias2025_almawarith_test_id_question.json

Usage:
  python test.py                    # All: KB + single + dev batch + eval
  python test.py --single           # Single question only
  python test.py --batch            # Dev: predict + evaluate
  python test.py --test             # Test: predict only (submission format)
  python test.py --eval             # Competition eval (requires prior --batch)
  python test.py --kb-only          # Build KB only
  python test.py --batch --num-gpus 2   # Use 2 GPUs for faster inference
  python test.py --test --num-gpus 2 --start 200   # Resume from question 201 (0-based index 200)
"""

import argparse
import json
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "rag_config.yaml"
SYNTHETIC_DIR = PROJECT_ROOT / "data" / "synthetic"
# Dev: has id, question, answer, output (ground truth) → for evaluation
DEV_DATA_DIR = PROJECT_ROOT / "data" / "dev"
# Test: has id, question only → for inference/submission (no ground truth)
TEST_DATA_DIR = PROJECT_ROOT / "data" / "test"
OUTPUT_DIR = PROJECT_ROOT / "results"
PDF_DIR = PROJECT_ROOT / "data" / "pdfs"

TEST_QUESTION = "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟"


def run_single_question(pipeline):
    """Step 6: Test single question with detailed output (like notebook)."""
    print("\n" + "=" * 80)
    print("SINGLE QUESTION TEST")
    print("=" * 80)
    print(f"Question: {TEST_QUESTION}")
    print(f"Model: {pipeline.qwen_client.model_name}\n")

    result = pipeline.query(TEST_QUESTION, top_k=5)
    raw = result.get("raw_output", "")
    parsed = result["parsed_output"]

    # Thinking
    print("=" * 80)
    print("THINKING:")
    print("=" * 80)
    thinking = parsed.get("thinking", "")
    if thinking:
        print(thinking[:2000] + ("..." if len(thinking) > 2000 else ""))
    else:
        print("No thinking captured")
        print(f"\nRaw (first 500 chars):\n{raw[:500]}")

    # Structured output
    print("\n" + "=" * 80)
    print("PREDICTION OUTPUT:")
    print("=" * 80)
    structured = parsed.get("structured_output")
    if structured and isinstance(structured, dict) and "heirs" in structured:
        print(json.dumps(structured, ensure_ascii=False, indent=2))
        required = {"heirs", "blocked", "shares", "tasil_stage", "awl_or_radd", "post_tasil"}
        present = required & set(structured.keys())
        print(f"\nSchema: {len(present)}/{len(required)} keys")
        if required - present:
            print(f"Missing: {required - present}")
    else:
        print("Could not extract structured output")
        if parsed.get("answer_text"):
            print(f"\nAnswer text:\n{parsed['answer_text'][:500]}")

    # Metrics
    print("\n" + "=" * 80)
    print("METRICS:")
    print("=" * 80)
    print(f"Parsing:    {parsed.get('parsing_success', False)}")
    print(f"Validation: {parsed.get('validation_success', False)}")
    print(f"Response:   {len(raw)} chars")
    if parsed.get("error"):
        print(f"Error:      {parsed['error']}")

    return result


def _run_batch_single_gpu(pipeline, dataset, output_path, is_dev=True, start_index=0):
    """Single-GPU loop for batch evaluation."""
    # When resuming (start_index > 0), load existing and merge at end
    existing = []
    op = Path(output_path)
    if start_index > 0 and op.exists():
        with open(op, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    existing.append(json.loads(line))

    new_rows = []
    for i, q_data in enumerate(dataset):
        q_id = start_index + i + 1
        print(f"[{q_id}/{start_index + len(dataset)}] {q_data.get('question', '')[:60]}...")
        res = pipeline.query(q_data.get("question", ""))
        res["id"] = q_data.get("id", f"q_{i}")

        if is_dev:
            output_item = {
                "question_id": q_id,
                "id": q_data.get("id", ""),
                "question": q_data.get("question", ""),
                "ground_truth": q_data.get("output", {}),
                "model_prediction": res["parsed_output"].get("structured_output", {}),
                "parsing_success": res["parsed_output"].get("parsing_success", False),
                "validation_success": res["parsed_output"].get("validation_success", False),
                "raw_response": res.get("raw_output", ""),
                "thinking": res["parsed_output"].get("thinking", ""),
            }
        else:
            formatted = pipeline.output_parser.format_for_evaluation(res["parsed_output"])
            output_item = {"question_id": q_id, "id": q_data.get("id", ""), "question": q_data.get("question", "")}
            if formatted:
                output_item["answer"] = formatted["answer"]
                output_item["output"] = formatted["output"]
            else:
                output_item["answer"] = res.get("raw_output", "")
                output_item["output"] = res["parsed_output"].get("structured_output") or {}

        new_rows.append(output_item)

    if start_index == 0:
        with open(output_path, "w", encoding="utf-8") as outf:
            for r in new_rows:
                outf.write(json.dumps(r, ensure_ascii=False) + "\n")
    elif new_rows:
        # Merge with existing when resuming
        new_ids = {r["question_id"] for r in new_rows}
        merged = [r for r in existing if r["question_id"] not in new_ids] + new_rows
        merged.sort(key=lambda r: r["question_id"])
        with open(output_path, "w", encoding="utf-8") as outf:
            for r in merged:
                outf.write(json.dumps(r, ensure_ascii=False) + "\n")


def _run_batch_multi_gpu(dataset, output_path, config_path, num_gpus, is_test=False, start_index=0):
    """Multi-GPU: spawn workers, merge results."""
    import multiprocessing
    from multiprocessing import Process
    from qias_mawarith_rag.workers import worker_process

    try:
        multiprocessing.set_start_method("spawn", force=True)
    except RuntimeError:
        pass

    # Round-robin split (index = start_index + i for correct question_id)
    chunks = [[] for _ in range(num_gpus)]
    for i, q_data in enumerate(dataset):
        gpu_id = i % num_gpus
        chunks[gpu_id].append({
            "index": start_index + i,
            "id": q_data.get("id", ""),
            "question": q_data.get("question", ""),
            "output": q_data.get("output", {}),
        })

    procs = []
    for gpu_id in range(num_gpus):
        if not chunks[gpu_id]:
            continue
        p = Process(
            target=worker_process,
            args=(gpu_id, chunks[gpu_id], str(output_path), str(config_path), is_test),
        )
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

    # Merge worker files and sort by question_id
    new_rows = []
    for gpu_id in range(num_gpus):
        wp = Path(f"{output_path}.worker{gpu_id}")
        if wp.exists():
            with open(wp, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        new_rows.append(json.loads(line))
            wp.unlink()

    # Merge with existing file if --start was used (do not overwrite prior results)
    all_rows = new_rows
    if start_index > 0:
        op = Path(output_path)
        if op.exists():
            existing = []
            with open(op, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        existing.append(json.loads(line))
            new_ids = {r["question_id"] for r in new_rows}
            merged = [r for r in existing if r["question_id"] not in new_ids] + new_rows
            all_rows = sorted(merged, key=lambda r: r["question_id"])

    with open(output_path, "w", encoding="utf-8") as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return all_rows


def run_batch_evaluation(pipeline, dev_dir, output_dir, batch_size=10, max_files=None, num_gpus=1, start_index=0):
    """Step 7–8: Batch evaluation on dev dataset with intermediate saves."""
    print("\n" + "=" * 80)
    print("BATCH EVALUATION ON DEV DATASET")
    print("=" * 80)

    output_dir.mkdir(parents=True, exist_ok=True)
    dev_files = sorted(Path(dev_dir).glob("*.json"))

    if not dev_files:
        print(f"❌ No JSON files in {dev_dir}")
        return

    if max_files:
        dev_files = dev_files[:max_files]

    print(f"Found {len(dev_files)} dev files | GPUs: {num_gpus}")
    for f in dev_files:
        print(f"  - {f.name}")

    for dev_file in dev_files:
        print(f"\n{'=' * 80}")
        print(f"Processing: {dev_file.name}")
        print("=" * 80)

        try:
            with open(dev_file, "r", encoding="utf-8") as f:
                dataset = json.load(f)

            dataset_slice = dataset[start_index:]
            print(f"Loaded {len(dataset)} questions" + (f" | Starting from index {start_index} ({len(dataset_slice)} to process)" if start_index > 0 else ""))
            output_path = output_dir / (dev_file.stem + "_results.jsonl")

            if start_index > 0:
                print("Resume mode: will merge with existing results\n")

            if num_gpus <= 1:
                print("Saving to JSONL after each question (tail -f to monitor)\n")
                _run_batch_single_gpu(pipeline, dataset_slice, output_path, is_dev=True, start_index=start_index)
            else:
                print(f"Using {num_gpus} GPUs in parallel\n")
                _run_batch_multi_gpu(dataset_slice, output_path, CONFIG_PATH, num_gpus, is_test=False, start_index=start_index)

            output_data = []
            with open(output_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        output_data.append(json.loads(line))

            n = len(output_data)
            parse_ok = sum(1 for r in output_data if r["parsing_success"])
            valid_ok = sum(1 for r in output_data if r["validation_success"])
            print(f"\n🎉 Completed {dev_file.name}")
            print(f"   Total: {n} | Parsing: {parse_ok}/{n} ({100 * parse_ok / n:.1f}%) | Validation: {valid_ok}/{n} ({100 * valid_ok / n:.1f}%)")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 80}")
    print("BATCH EVALUATION COMPLETE")
    print("=" * 80)
    print(f"Results in: {output_dir}")


def run_test_inference(pipeline, test_file, output_dir, batch_size=10, num_gpus=1, start_index=0):
    """Run inference on TEST data (id + question only) and save predictions for submission."""
    print("\n" + "=" * 80)
    print("TEST INFERENCE (submission format)")
    print("=" * 80)

    test_path = Path(test_file)
    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(test_path, "r", encoding="utf-8") as f:
        dataset_full = json.load(f)

    dataset = dataset_full[start_index:]
    print(f"Loaded {len(dataset_full)} questions from {test_path.name}" + (f" | Starting from index {start_index} ({len(dataset)} to process)" if start_index > 0 else ""))
    out_path = output_dir / (test_path.stem + "_predictions.jsonl")

    if start_index > 0:
        print("Resume mode: will merge with existing results (existing file preserved)\n")

    if num_gpus <= 1:
        print("Saving to JSONL after each question (tail -f to monitor)\n")
        _run_batch_single_gpu(pipeline, dataset, out_path, is_dev=False, start_index=start_index)
    else:
        print(f"Using {num_gpus} GPUs in parallel\n")
        _run_batch_multi_gpu(dataset, out_path, CONFIG_PATH, num_gpus, is_test=True, start_index=start_index)

    output_data = []
    with open(out_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                output_data.append(json.loads(line))
    has_output = sum(1 for r in output_data if r.get("output"))
    print(f"\n✅ Saved {len(output_data)} predictions to {out_path}")
    print(f"   With structured output: {has_output}/{len(dataset)}")


def run_competition_eval(output_dir):
    """Step 9: QIAS 2026 competition evaluation report."""
    print("\n" + "=" * 80)
    print("QIAS 2026 COMPETITION EVALUATION")
    print("=" * 80)

    from qias_mawarith_rag.generation.evaluator import QIAS2026Evaluator

    evaluator = QIAS2026Evaluator()
    result_files = list(Path(output_dir).glob("*_results.jsonl")) or list(Path(output_dir).glob("*_results.json"))

    if not result_files:
        print(f"❌ No *_results.jsonl or *_results.json in {output_dir}")
        print("   Run batch evaluation first.")
        return

    def load_results(path):
        if path.suffix == ".jsonl":
            data = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            return data
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"Found {len(result_files)} result files:")
    for f in result_files:
        print(f"  📄 {f.name}")

    all_predictions = []
    all_ground_truths = []
    all_individual_results = []

    for result_file in result_files:
        print(f"\n📊 Processing {result_file.name}...")

        results = load_results(result_file)

        predictions = [r["model_prediction"] for r in results]
        ground_truths = [r["ground_truth"] for r in results]

        all_predictions.extend(predictions)
        all_ground_truths.extend(ground_truths)

        eval_report = evaluator.evaluate_dataset(predictions, ground_truths)

        # Add competition scores to each result
        for i, result in enumerate(results):
            scores = eval_report["individual_results"][i]
            result.update(
                competition_overall_accuracy=scores["overall_accuracy"],
                competition_heirs_accuracy=scores["heirs_accuracy"],
                competition_blocked_accuracy=scores["blocked_accuracy"],
                competition_shares_accuracy=scores["shares_accuracy"],
                competition_awl_radd_accuracy=scores["awl_radd_accuracy"],
                competition_tasil_stage_accuracy=scores["tasil_stage_accuracy"],
                competition_post_tasil_accuracy=scores["post_tasil_accuracy"],
                competition_detailed_scores=scores["detailed_scores"],
            )

        with open(result_file, "w", encoding="utf-8") as f:
            if result_file.suffix == ".jsonl":
                for r in results:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            else:
                json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"   Overall Accuracy: {eval_report['aggregate_scores']['overall_accuracy']:.3f}")
        print(f"   Dataset Size: {eval_report['dataset_size']}")

        all_individual_results.extend(eval_report["individual_results"])

    # Overall report (evaluate combined dataset to get full report structure)
    if all_predictions and all_ground_truths:
        print("\n🏆 Generating Overall QIAS 2026 Competition Report...")
        overall_report = evaluator.evaluate_dataset(all_predictions, all_ground_truths)
        report_path = output_dir / "qias2026_competition_report.txt"
        report = evaluator.generate_report(overall_report, output_path=str(report_path))
        print(report)
        print(f"\n✅ Report saved to {report_path}")


def main():
    parser = argparse.ArgumentParser(description="QIAS 2026 RAG Pipeline Test")
    parser.add_argument("--single", action="store_true", help="Run single question test")
    parser.add_argument("--batch", action="store_true", help="Dev: predict + evaluate (has ground truth)")
    parser.add_argument("--test", action="store_true", help="Test: predict only for submission (id+question)")
    parser.add_argument("--eval", action="store_true", help="Run competition evaluation (needs batch results)")
    parser.add_argument("--kb-only", action="store_true", help="Build KB only, no queries")
    parser.add_argument("--force-rebuild", action="store_true", help="Force rebuild synthetic KB")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for dev evaluation")
    parser.add_argument("--max-files", type=int, default=None, help="Max dev files to process (default: all)")
    parser.add_argument("--dev-dir", type=str, default=None, help="Dev data directory")
    parser.add_argument("--test-file", type=str, default=None, help="Test JSON file (id+question)")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for results")
    parser.add_argument("--num-gpus", type=int, default=1, help="Number of GPUs for parallel inference (default: 1)")
    parser.add_argument("--start", type=int, default=0, help="Start from question index (0-based). E.g. --start 200 skips first 200, processes from 201st. Merges with existing output file if present.")
    args = parser.parse_args()

    # If no mode specified, run all (single + dev batch + eval)
    run_all = not (args.single or args.batch or args.test or args.eval or args.kb_only)
    if run_all:
        args.single = True
        args.batch = True
        args.eval = True

    dev_dir = Path(args.dev_dir) if args.dev_dir else DEV_DATA_DIR
    test_file = Path(args.test_file) if args.test_file else (TEST_DATA_DIR / "qias2025_almawarith_test_id_question.json")
    output_dir = Path(args.output_dir) if args.output_dir else OUTPUT_DIR

    # ── Step 1–4: Load pipeline ───────────────────────────────────────────────
    print("Loading RAG Pipeline...")
    from qias_mawarith_rag.pipeline import RAGPipeline

    pipeline = RAGPipeline(config_path=str(CONFIG_PATH))

    # ── Step 5: Build knowledge base ─────────────────────────────────────────
    if run_all or args.kb_only or args.single or args.batch or args.test:
        print("\n=== Building Knowledge Base ===")

        # Synthetic (from qa_nl)
        if SYNTHETIC_DIR.exists():
            pipeline.build_knowledge_base_from_synthetic(
                synthetic_directory=str(SYNTHETIC_DIR),
                force_rebuild=args.force_rebuild,
            )
        else:
            print(f"Synthetic dir not found: {SYNTHETIC_DIR}")

        # Optional: PDF
        if PDF_DIR.exists() and list(PDF_DIR.glob("*.pdf")):
            pipeline.build_knowledge_base(pdf_directory=str(PDF_DIR), force_rebuild=False)
        else:
            print(f"No PDFs in {PDF_DIR} (skipping)")

        if args.kb_only:
            print("KB-only mode: stopping after knowledge base build.")
            return

    # ── Step 6: Single question ───────────────────────────────────────────────
    if args.single:
        run_single_question(pipeline)

    # ── Step 7–8: Batch evaluation on DEV ────────────────────────────────────
    if args.batch:
        if not dev_dir.exists():
            print(f"❌ Dev dir not found: {dev_dir}")
        else:
            run_batch_evaluation(
                pipeline,
                dev_dir=dev_dir,
                output_dir=output_dir,
                batch_size=args.batch_size,
                max_files=args.max_files,
                num_gpus=args.num_gpus,
                start_index=args.start,
            )

    # ── Test inference (submission) ──────────────────────────────────────────
    if args.test:
        run_test_inference(
            pipeline,
            test_file=test_file,
            output_dir=output_dir,
            batch_size=args.batch_size,
            num_gpus=args.num_gpus,
            start_index=args.start,
        )

    # ── Step 9: Competition evaluation ───────────────────────────────────────
    if args.eval:
        run_competition_eval(output_dir)

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
