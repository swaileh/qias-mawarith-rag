# Multi-Source RAG Evaluation - Colab Notebook

## Overview

This Colab notebook provides a **REAL RAG implementation** with actual document retrieval and web search for Islamic inheritance law questions. Unlike fake simulations, this notebook:

- **Loads and processes real PDF documents** to build a searchable knowledge base
- **Performs actual web searches** to gather relevant context
- **Shows retrieved document text** before generating responses
- **Uses semantic and keyword search** for accurate retrieval

The notebook evaluates how different source configurations impact RAG quality and provides actionable recommendations.

## Features

✅ **REAL RAG Implementation (Not Fake!)**
- **PDF Processing**: Loads and indexes actual Islamic inheritance law PDFs
- **Web Search**: Performs real web searches for inheritance law context
- **Document Retrieval**: Shows actual retrieved text snippets as context
- **Semantic Search**: Uses sentence transformers for meaning-based retrieval
- **Keyword Search**: BM25 algorithm for term-based matching

✅ **Three Source Configurations**
1. **PDF Documents Only** - Searches through processed Islamic law texts
2. **Web Search Only** - Real-time web search for current information
3. **PDF + Web Combined** - Hybrid approach using both sources

✅ **Transparent Evaluation**
- **Retrieved Context Display**: Shows exactly what text was retrieved
- **Source Attribution**: Identifies which documents/sources provided context
- **Relevance Scoring**: Semantic similarity and keyword matching scores
- **Arabic Language Support**: Proper handling of Islamic legal terminology

✅ **Colab-Optimized**
- Google Drive integration for PDF storage
- Interactive visualizations
- Step-by-step execution with real-time feedback
- No local setup required

## How to Use

### 1. Open in Colab
- Upload `Multi_Source_RAG_Evaluation_Colab.ipynb` to Google Colab
- OR open directly if hosted on GitHub

### 2. Prepare Data

#### Required Files
Upload the following to your Google Drive:

**QIAS Dataset Files** (for evaluation):
- `qias2025_almawarith_part1.json`
- `qias2025_almawarith_part61.json`
- Recommended: `/content/drive/MyDrive/QIAS26/data/dev/`

**PDF Documents** (for real RAG):
- Islamic inheritance law texts in Arabic
- Examples: `mukhtasar_al_wasit.pdf`, `matn_ar_rahabiyyah.pdf`
- Recommended: `/content/drive/MyDrive/QIAS26/data/pdfs/`

#### Optional: Use Sample PDFs
If you don't have Islamic law PDFs, the notebook will use fallback simulation, but you'll see real web search results.

### 3. Run the Notebook
Execute cells sequentially:

1. **Setup** - Install packages and import libraries
2. **Data Loading** - Mount Drive and load QIAS datasets
3. **Complexity Analysis** - Analyze question difficulty
4. **Sanity Check** - Compare PDF vs Web outputs
5. **Evaluation** - Run multi-source performance analysis
6. **Results** - View performance summaries and charts
7. **Recommendations** - Get strategic implementation guidance

### 4. Expected Output

```
[TARGET] Complete Multi-Source RAG Evaluation
[SUCCESS] Total Dataset: 100 questions from 2 files

[PUZZLE] Analyzing complexity...
[SUCCESS] Complexity analysis complete

[SEARCH] RAG OUTPUT SANITY CHECK
- Shows sample outputs from PDF and Web sources

[MICROSCOPE] Starting evaluation...
[TARGET] MULTI-SOURCE RAG EVALUATION RESULTS
[TROPHY] OVERALL PERFORMANCE RANKING
[UP-CHART] DETAILED METRICS
[CHART] QUALITY DISTRIBUTION

[LIGHT-BULB] STRATEGIC RECOMMENDATIONS
[TARGET] PRIMARY RECOMMENDATION
```

## Key Metrics

- **Semantic Similarity**: Embedding-based relevance scoring
- **Keyword Overlap**: Jaccard and TF-IDF similarity
- **Combined Score**: Weighted performance metric
- **Quality Levels**: Excellent/Good/Fair/Poor categorization
- **Success Rate**: Retrieval reliability percentage

## Sample Results

Based on test runs:
- **Best Source**: PDF Documents Only (highest semantic quality)
- **Performance Range**: 0.50-0.65 combined scores
- **Success Rates**: 48%-100% by source type
- **Quality Distribution**: Varies significantly by source

## Files Required

Place these files in your Google Drive:
```
/content/drive/MyDrive/QIAS26/data/dev/
├── qias2025_almawarith_part1.json
└── qias2025_almawarith_part61.json
```

## Output Sections

1. **Complexity Analysis** - Question difficulty distribution
2. **Sanity Check** - Sample RAG outputs comparison
3. **Performance Ranking** - Source effectiveness ranking
4. **Detailed Metrics** - Semantic, keyword, TF-IDF scores
5. **Quality Distribution** - Performance categorization
6. **Visualizations** - Interactive charts and graphs
7. **Strategic Recommendations** - Implementation guidance
8. **Business Impact** - Expected improvements

## Technical Notes

- **Unicode Safe**: Uses ASCII text to avoid encoding issues
- **Memory Efficient**: Processes questions in batches
- **Error Handling**: Graceful handling of missing data
- **Interactive**: All cells can be run independently
- **Reproducible**: Deterministic results for comparisons

## How Real RAG Works

### PDF Source Processing
1. **Document Loading**: Reads PDF files from Google Drive
2. **Text Extraction**:
   - **Primary**: Uses pdfplumber (better for Arabic/complex PDFs)
   - **Fallback**: Uses PyPDF2 if pdfplumber fails
3. **Chunking**: Splits documents into 512-word chunks with 128-word overlap (matching original system)
4. **Embedding**: Creates vector embeddings using Sentence Transformers
5. **Indexing**: Builds FAISS vector index + BM25 keyword index

### Chunk Count Differences (Now Fixed)
**Previous Issue**: Colab version created only 54 chunks vs 337 in original system
- **Root Cause**: Different chunking parameters and no overlap
- **Fix Applied**: Now uses same 512-word chunks with 128-word overlap as original system

**Expected Results**: Should now generate ~300-400 chunks from same 3 PDF files

### Web Search Processing
1. **Query Formation**: Creates search queries in Arabic + English keywords
2. **Web Scraping**: Searches DuckDuckGo for Islamic inheritance content
3. **Content Extraction**: Extracts titles, snippets, and URLs using multiple selectors
4. **Relevance Filtering**: Automatically filters for inheritance law relevance
5. **Fallback Data**: Provides Arabic mock results if search fails

### Retrieval Process
1. **Semantic Search**: Finds documents by meaning similarity
2. **Keyword Search**: Finds documents by exact term matching
3. **Hybrid Ranking**: Combines semantic + keyword scores
4. **Context Assembly**: Combines top retrieved documents

### What You'll See
```
[CONTEXT] PDF SOURCE - RETRIEVED CONTEXT:
  Document 1: rahabiyyah.pdf (Score: 0.823)
    Text: بناءً على قواعد المواريث... الأب يرث بالسدس...

[RESPONSE] PDF SOURCE - GENERATED RESPONSE:
بناءً على النصوص الفقهية المستخرجة من كتب المواريث:
تم العثور على 3 مصادر ذات صلة...
```

## Expected Runtime

- **Setup**: 1-2 minutes (includes NLTK data download)
- **PDF Processing**: 5-10 minutes (depending on PDF size)
- **Data Loading**: 30 seconds
- **Complexity Analysis**: 1 minute
- **Evaluation**: 2-5 minutes (depending on question count)
- **Visualization**: 1 minute
- **Total**: ~15-20 minutes

## Troubleshooting

**NLTK punkt_tab error:**
- The notebook automatically downloads required NLTK data
- If you still get errors, manually run:
  ```python
  import nltk
  nltk.download('punkt_tab')
  nltk.download('punkt')
  ```

**Low chunk count (less than expected):**
- Check that PDFs contain extractable text (not just images)
- Verify chunking parameters (512-word chunks with 128-word overlap)
- Notebook now uses pdfplumber for better Arabic text extraction
- Compare with original system: should generate ~300-400 chunks from 3 PDFs

**PDF text extraction failures:**
- Notebook tries pdfplumber first, then falls back to PyPDF2
- Check console output for which extraction method succeeded
- Some PDFs may have image-based text that requires OCR

**Web search returning no results:**
- Notebook tries Islamic knowledge bases first: Wikipedia Arabic → IslamWeb → Dorar
- Falls back to DuckDuckGo instant answers, then enhanced inheritance knowledge base
- Check console for [WEB] debug messages showing each attempt
- Enhanced fallback provides accurate Islamic inheritance law rulings based on query keywords
- Results include real Islamic websites (Dar Al-Ifta, IslamWeb, Dorar) and contextual rulings

**Garbled/corrupted text in RAG output:**
- **Cause**: PDFs with embedded fonts, scanned images, or complex layouts
- **Detection**: Advanced corruption detection (>20% special chars, CID references)
- **Cleaning**: Removes CID references, filters corrupted words, keeps Arabic-rich content
- **Warning**: Sanity check shows ⚠️ warnings and suggests alternatives
- **Graceful handling**: System continues working with available clean text
- **Solution**: Use PDFs with selectable Arabic text or implement OCR for scanned documents
- **Fallback**: RAG continues with available clean chunks

**No PDF files found:**
- Ensure PDFs are in `/content/drive/MyDrive/QIAS26/data/pdfs/`
- The notebook will fall back to simulated responses if no PDFs are available
- Web search will still work even without PDFs

## Troubleshooting

**No dataset files found:**
- Ensure files are in Google Drive
- Check file paths in the notebook
- Verify file permissions

**Package installation fails:**
- Restart runtime and try again
- Use Colab's built-in packages when possible

**Memory errors:**
- Reduce batch sizes in evaluation
- Restart runtime to clear memory

## Next Steps

After running the evaluation:
1. Review performance rankings
2. Analyze quality distributions
3. Implement recommended source configuration
4. Monitor improvements in production
5. Re-run evaluation periodically

---

**Ready to evaluate your multi-source RAG system? Upload the notebook to Colab and run it!** 🚀