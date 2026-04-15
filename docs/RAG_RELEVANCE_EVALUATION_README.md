# RAG Relevance Evaluation System

This document explains how to evaluate the relevance of retrieved documents in your RAG (Retrieval-Augmented Generation) system for Islamic inheritance law questions.

## Overview

The relevance evaluation system assesses how well retrieved documents match user queries using multiple evaluation methods:

1. **Semantic Similarity**: Uses sentence embeddings to measure meaning similarity
2. **Keyword Overlap**: Analyzes shared terms between query and documents
3. **TF-IDF Similarity**: Calculates term importance overlap
4. **Retrieval Metrics**: Precision, recall, and F1-score (when ground truth available)

## How It Works

### Automatic Evaluation in RAG Pipeline

The relevance evaluator is automatically integrated into your RAG pipeline. Every query now includes a `relevance_evaluation` field in the results:

```python
from src.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()
result = pipeline.query("مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟")

# Access relevance evaluation
relevance = result['relevance_evaluation']
print(f"Quality Score: {relevance['overall_assessment']['quality_score']}")
```

### Evaluation Components

#### 1. Semantic Similarity
- Uses multilingual sentence transformers
- Measures cosine similarity between query and document embeddings
- Scale: 0.0 (no similarity) to 1.0 (perfect similarity)

#### 2. Keyword Overlap
- Extracts keywords from Arabic text
- Calculates Jaccard similarity and overlap coefficient
- Identifies common terms between query and documents

#### 3. TF-IDF Similarity
- Uses TF-IDF vectorization for term importance
- Calculates cosine similarity in TF-IDF space
- Accounts for term frequency and rarity

#### 4. Combined Scoring
- Weighted combination of all metrics
- Provides overall relevance assessment

## Usage Examples

### 1. Basic Relevance Evaluation

```python
from src.evaluation.relevance_evaluator import evaluate_retrieval_quality, print_relevance_report

# Evaluate retrieved documents for a query
evaluation = evaluate_retrieval_quality(
    query="مات وترك: زوجة و أم و ابن. ما هو نصيب كل وريث؟",
    retrieved_docs=retrieved_documents
)

# Print detailed report
print_relevance_report(evaluation)
```

### 2. Batch Evaluation

```python
from src.evaluation.relevance_evaluator import RelevanceEvaluator

evaluator = RelevanceEvaluator()

# Evaluate multiple queries
batch_results = evaluator.evaluate_batch([
    {
        'query': 'Question 1',
        'retrieved_docs': docs1
    },
    {
        'query': 'Question 2',
        'retrieved_docs': docs2
    }
])

# Summary statistics
summary = batch_results['summary_statistics']
print(f"Average semantic similarity: {summary['avg_semantic_similarity']:.3f}")
```

### 3. Evaluation with Ground Truth

```python
# When you have ground truth relevant documents
evaluation = pipeline.evaluate_retrieval_quality(
    question="مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟",
    retrieved_docs=retrieved_docs,
    ground_truth_docs=ground_truth_docs  # Known relevant documents
)

# Access retrieval metrics
metrics = evaluation['retrieval_metrics']
print(f"Precision: {metrics['precision']:.3f}")
print(f"Recall: {metrics['recall']:.3f}")
print(f"F1 Score: {metrics['f1_score']:.3f}")
```

### 4. Run Evaluation Script

```bash
# Evaluate test questions
python evaluate_relevance.py

# Evaluate questions from JSON file
python evaluate_relevance.py path/to/questions.json
```

## Quality Assessment

The system provides quality levels based on combined scores:

- **Excellent** (≥0.8): High relevance, good retrieval
- **Good** (≥0.6): Acceptable relevance
- **Fair** (≥0.4): Moderate relevance, may need improvement
- **Poor** (<0.4): Low relevance, significant issues

## Configuration

Configure evaluation settings in `config/rag_config.yaml`:

```yaml
evaluation:
  enable_relevance_evaluation: true
  min_relevance_threshold: 0.5
  evaluation_output_dir: ./evaluation_results
```

## Output Format

### Individual Query Evaluation

```json
{
  "query": "مات وترك: أم و أب و بنت...",
  "num_retrieved": 5,
  "semantic_similarity": {
    "mean": 0.723,
    "max": 0.856,
    "top_1_score": 0.856
  },
  "keyword_overlap": {
    "mean_jaccard": 0.234,
    "top_1_jaccard": 0.345
  },
  "tfidf_similarity": {
    "mean": 0.456,
    "top_1_score": 0.623
  },
  "overall_assessment": {
    "quality_score": 0.742,
    "quality_level": "good",
    "recommendations": ["Retrieval quality looks good"]
  },
  "document_scores": [...]
}
```

### Document-Level Scores

Each retrieved document gets individual scores:

```json
{
  "rank": 1,
  "doc_id": "doc_123",
  "title": "Islamic Inheritance Rules",
  "semantic_similarity": 0.856,
  "keyword_overlap": {
    "jaccard": 0.345,
    "common_terms": ["أم", "أب", "بنت", "وريث"]
  },
  "tfidf_similarity": 0.623,
  "combined_score": 0.742
}
```

## Improving Relevance

### Common Issues and Solutions

1. **Low Semantic Similarity**
   - Check embedding model quality
   - Verify document preprocessing
   - Consider domain-specific embeddings

2. **Low Keyword Overlap**
   - Improve keyword extraction
   - Enhance BM25 retrieval weights
   - Add synonym expansion

3. **Poor TF-IDF Similarity**
   - Review document tokenization
   - Adjust TF-IDF parameters
   - Consider Arabic-specific preprocessing

4. **Low Retrieval Metrics**
   - Tune hybrid search weights
   - Adjust reranking thresholds
   - Improve document indexing

### Monitoring and Iteration

Use the evaluation system to:

1. **Monitor retrieval quality** over time
2. **A/B test retrieval improvements**
3. **Identify problematic queries**
4. **Guide system optimization**

Regular evaluation helps ensure your RAG system maintains high relevance as you add more documents or modify retrieval strategies.

## API Reference

### RelevanceEvaluator Class

- `evaluate_query_relevance(query, docs, ground_truth=None)`: Evaluate single query
- `evaluate_batch(queries_and_docs, ground_truths=None)`: Evaluate multiple queries

### Convenience Functions

- `evaluate_retrieval_quality()`: Quick single-query evaluation
- `print_relevance_report()`: Formatted evaluation output

## Arabic Text Processing

The evaluator includes Arabic-specific processing:

- **Normalization**: Removes diacritics, normalizes alef/yaa variants
- **Tokenization**: Uses NLTK with Arabic support
- **Stopwords**: Arabic stopwords excluding inheritance-specific terms
- **Keyword Extraction**: Filters short words and stopwords

This ensures accurate evaluation of Arabic Islamic inheritance law content.