#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
# run_dev.sh — End-to-end dev evaluation for QIAS Mawarith RAG
#
# Orchestrates all prerequisites then runs the pipeline on data/dev/:
#   1. Generate synthetic training data  (if data/synthetic/ is empty)
#   2. Download Arabic PDF books          (if data/pdfs/*.pdf missing)
#   3. Run the RAG pipeline on data/dev/ with evaluation
#
# Usage:
#   bash scripts/run_dev.sh                  # Full run
#   bash scripts/run_dev.sh --skip-datagen   # Skip synthetic generation
#   bash scripts/run_dev.sh --force-datagen  # Regenerate even if exists
#   bash scripts/run_dev.sh --eval-only      # Only run competition eval
# ──────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Resolve project root ─────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$PROJECT_ROOT"

# ── Config ────────────────────────────────────────────────────────
SYNTHETIC_DIR="$PROJECT_ROOT/data/synthetic"
PDF_DIR="$PROJECT_ROOT/data/pdfs"
DEV_DIR="$PROJECT_ROOT/data/dev"
RESULTS_DIR="$PROJECT_ROOT/results"
SYNTHETIC_COUNT=100000
SYNTHETIC_SEED=2026

# ── Parse arguments ───────────────────────────────────────────────
SKIP_DATAGEN=false
FORCE_DATAGEN=false
EVAL_ONLY=false

for arg in "$@"; do
    case $arg in
        --skip-datagen)   SKIP_DATAGEN=true ;;
        --force-datagen)  FORCE_DATAGEN=true ;;
        --eval-only)      EVAL_ONLY=true ;;
        *)                echo "Unknown arg: $arg"; exit 1 ;;
    esac
done

echo "═══════════════════════════════════════════════════════════════"
echo " QIAS Mawarith RAG — Dev Evaluation Pipeline"
echo "═══════════════════════════════════════════════════════════════"
echo " Project root : $PROJECT_ROOT"
echo " Synthetic dir: $SYNTHETIC_DIR"
echo " PDF dir      : $PDF_DIR"
echo " Dev dir      : $DEV_DIR"
echo " Results dir  : $RESULTS_DIR"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ══════════════════════════════════════════════════════════════════
# Step 1: Generate synthetic training data
# ══════════════════════════════════════════════════════════════════
if [ "$EVAL_ONLY" = false ]; then

    SYNTH_FILE_COUNT=0
    if [ -d "$SYNTHETIC_DIR" ]; then
        SYNTH_FILE_COUNT=$(find "$SYNTHETIC_DIR" -name "*.json" 2>/dev/null | wc -l)
    fi

    if [ "$SKIP_DATAGEN" = true ]; then
        echo "⏭  Skipping synthetic data generation (--skip-datagen)"
        echo "   Existing files: $SYNTH_FILE_COUNT"
        echo ""
    elif [ "$SYNTH_FILE_COUNT" -gt 0 ] && [ "$FORCE_DATAGEN" = false ]; then
        echo "✅ Synthetic data already exists: $SYNTH_FILE_COUNT files in $SYNTHETIC_DIR"
        echo "   Pass --force-datagen to regenerate."
        echo ""
    else
        if [ "$FORCE_DATAGEN" = true ] && [ -d "$SYNTHETIC_DIR" ]; then
            echo "🗑  Removing old synthetic data..."
            rm -rf "$SYNTHETIC_DIR"
        fi

        echo "🔧 Step 1/3: Generating ~${SYNTHETIC_COUNT} synthetic training examples..."
        echo "   Seed: $SYNTHETIC_SEED | Output: $SYNTHETIC_DIR"
        echo ""

        python -m qias_mawarith_rag.datagen.synthetic_generator \
            --count "$SYNTHETIC_COUNT" \
            --seed "$SYNTHETIC_SEED" \
            --output-dir "$SYNTHETIC_DIR"

        SYNTH_FILE_COUNT=$(find "$SYNTHETIC_DIR" -name "*.json" | wc -l)
        echo ""
        echo "✅ Synthetic data generated: $SYNTH_FILE_COUNT files"
        echo ""
    fi

    # ══════════════════════════════════════════════════════════════
    # Step 2: Download Arabic PDF books
    # ══════════════════════════════════════════════════════════════
    PDF_COUNT=0
    if [ -d "$PDF_DIR" ]; then
        PDF_COUNT=$(find "$PDF_DIR" -name "*.pdf" 2>/dev/null | wc -l)
    fi

    if [ "$PDF_COUNT" -gt 0 ]; then
        echo "✅ Arabic PDFs already present: $PDF_COUNT files in $PDF_DIR"
        echo ""
    else
        echo "📥 Step 2/3: Downloading Arabic PDF books..."
        echo ""

        # Try both download scripts (English references + Arabic books)
        python scripts/download_pdfs.py || echo "   ⚠  Some English PDF downloads failed (non-critical)"
        echo ""
        python scripts/download_arabic_pdfs.py || echo "   ⚠  Some Arabic PDF downloads failed (non-critical)"
        echo ""

        PDF_COUNT=$(find "$PDF_DIR" -name "*.pdf" 2>/dev/null | wc -l)
        if [ "$PDF_COUNT" -gt 0 ]; then
            echo "✅ Downloaded $PDF_COUNT PDF files"
        else
            echo "⚠  No PDFs downloaded (Archive.org may be unreachable)."
            echo "   The pipeline will use synthetic data only as the knowledge base."
        fi
        echo ""
    fi

    # ══════════════════════════════════════════════════════════════
    # Step 3: Run pipeline on dev split
    # ══════════════════════════════════════════════════════════════
    if [ ! -d "$DEV_DIR" ] || [ -z "$(ls "$DEV_DIR"/*.json 2>/dev/null)" ]; then
        echo "❌ No dev data found in $DEV_DIR"
        exit 1
    fi

    DEV_COUNT=$(python -c "
import json, glob
total = 0
for f in glob.glob('$DEV_DIR/*.json'):
    with open(f) as fh:
        total += len(json.load(fh))
print(total)
")

    echo "🚀 Step 3/3: Running RAG pipeline on dev split ($DEV_COUNT questions)..."
    echo "   Dev dir  : $DEV_DIR"
    echo "   Output   : $RESULTS_DIR"
    echo ""

    python scripts/run_pipeline.py \
        --batch \
        --dev-dir "$DEV_DIR" \
        --output-dir "$RESULTS_DIR"
fi

# ══════════════════════════════════════════════════════════════════
# Step 4: Competition evaluation (MIR-E)
# ══════════════════════════════════════════════════════════════════
if [ -d "$RESULTS_DIR" ] && [ -n "$(ls "$RESULTS_DIR"/*_results.jsonl 2>/dev/null)" ]; then
    echo ""
    echo "📊 Running QIAS 2026 competition evaluation (MIR-E)..."
    echo ""
    python scripts/run_pipeline.py \
        --eval \
        --output-dir "$RESULTS_DIR"
else
    echo ""
    echo "⚠  No result files found in $RESULTS_DIR — skipping evaluation."
    echo "   Run without --eval-only first to generate results."
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo " ✅ Done."
echo "═══════════════════════════════════════════════════════════════"
