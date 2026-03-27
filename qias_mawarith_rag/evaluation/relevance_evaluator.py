"""
RAG Relevance Evaluator
Comprehensive evaluation of retrieved document relevance to queries
"""

import yaml
import numpy as np
from typing import Dict, Any, List, Optional
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Try to ensure NLTK data exists (fails silently if SSL/cert issues prevent download)
def _ensure_nltk_data():
    for resource in ['punkt_tab', 'punkt', 'stopwords']:
        try:
            if resource == 'punkt_tab':
                nltk.data.find('tokenizers/punkt_tab')
            elif resource == 'punkt':
                nltk.data.find('tokenizers/punkt')
            else:
                nltk.data.find('corpora/stopwords')
        except LookupError:
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                pass  # SSL or network issues - will use fallback tokenization

_ensure_nltk_data()


class RelevanceEvaluator:
    """Comprehensive relevance evaluation for RAG systems"""

    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize relevance evaluator"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Initialize semantic similarity model
        embedding_model = self.config.get('vector_store', {}).get(
            'embedding_model',
            'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
        )

        print(f"Loading embedding model for relevance evaluation: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)

        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=self._get_arabic_stopwords(),
            ngram_range=(1, 2)
        )

        # Arabic stopwords
        self.arabic_stopwords = self._get_arabic_stopwords()

        print("Relevance evaluator initialized")

    def _get_arabic_stopwords(self) -> List[str]:
        """Get Arabic stopwords (empty list if NLTK data unavailable)"""
        try:
            arabic_stops = stopwords.words('arabic')
        except (LookupError, OSError, Exception):
            arabic_stops = []

        # Exclude Islamic inheritance terms from stopword filtering
        inheritance_terms = [
            'أب', 'أم', 'ابن', 'بنت', 'أخ', 'أخت', 'زوج', 'زوجة',
            'جد', 'جدة', 'عم', 'عمه', 'خال', 'خاله', 'وريث', 'ورثة',
            'ميراث', 'تركة', 'نصيب', 'سهم', 'فرض', 'كتابة'
        ]

        return [word for word in arabic_stops if word not in inheritance_terms]

    def evaluate_query_relevance(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        ground_truth_docs: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Comprehensive relevance evaluation for a single query

        Args:
            query: The search query
            retrieved_docs: Documents retrieved by RAG system
            ground_truth_docs: Ground truth relevant documents (if available)

        Returns:
            Dictionary with various relevance metrics
        """

        evaluation = {
            'query': query,
            'num_retrieved': len(retrieved_docs),
            'semantic_similarity': {},
            'keyword_overlap': {},
            'tfidf_similarity': {},
            'retrieval_metrics': {},
            'document_scores': []
        }

        if not retrieved_docs:
            return evaluation

        # Evaluate each retrieved document
        doc_scores = []
        for i, doc in enumerate(retrieved_docs):
            doc_eval = self._evaluate_single_document(query, doc, i)
            doc_scores.append(doc_eval)

        evaluation['document_scores'] = doc_scores

        # Aggregate semantic similarity metrics
        if doc_scores:
            semantic_scores = [d['semantic_similarity'] for d in doc_scores]
            evaluation['semantic_similarity'] = {
                'mean': np.mean(semantic_scores),
                'max': np.max(semantic_scores),
                'min': np.min(semantic_scores),
                'std': np.std(semantic_scores),
                'top_1_score': semantic_scores[0] if semantic_scores else 0,
                'top_3_mean': np.mean(semantic_scores[:3]) if len(semantic_scores) >= 3 else np.mean(semantic_scores)
            }

            # Keyword overlap metrics
            keyword_scores = [d['keyword_overlap']['jaccard'] for d in doc_scores]
            evaluation['keyword_overlap'] = {
                'mean_jaccard': np.mean(keyword_scores),
                'max_jaccard': np.max(keyword_scores),
                'top_1_jaccard': keyword_scores[0] if keyword_scores else 0
            }

            # TF-IDF similarity metrics
            tfidf_scores = [d['tfidf_similarity'] for d in doc_scores]
            evaluation['tfidf_similarity'] = {
                'mean': np.mean(tfidf_scores),
                'max': np.max(tfidf_scores),
                'top_1_score': tfidf_scores[0] if tfidf_scores else 0
            }

        # Calculate retrieval metrics if ground truth is available
        if ground_truth_docs:
            evaluation['retrieval_metrics'] = self._calculate_retrieval_metrics(
                retrieved_docs, ground_truth_docs
            )

        # Overall relevance assessment
        evaluation['overall_assessment'] = self._assess_overall_relevance(evaluation)

        return evaluation

    def _evaluate_single_document(
        self,
        query: str,
        document: Dict[str, Any],
        rank: int
    ) -> Dict[str, Any]:
        """Evaluate relevance of a single document to the query"""

        doc_content = document.get('content', '')
        doc_title = document.get('title', '')

        evaluation = {
            'rank': rank + 1,
            'doc_id': document.get('id', f'doc_{rank}'),
            'title': doc_title,
            'content_preview': doc_content[:200] + '...' if len(doc_content) > 200 else doc_content,
            'semantic_similarity': 0.0,
            'keyword_overlap': {},
            'tfidf_similarity': 0.0,
            'retrieval_score': document.get('score', 0.0),
            'rerank_score': document.get('rerank_score', 0.0)
        }

        # Semantic similarity using embeddings
        evaluation['semantic_similarity'] = self._calculate_semantic_similarity(query, doc_content)

        # Keyword overlap analysis
        evaluation['keyword_overlap'] = self._calculate_keyword_overlap(query, doc_content)

        # TF-IDF similarity
        evaluation['tfidf_similarity'] = self._calculate_tfidf_similarity(query, doc_content)

        # Combined relevance score
        evaluation['combined_score'] = self._calculate_combined_score(evaluation)

        return evaluation

    def _calculate_semantic_similarity(self, query: str, document: str) -> float:
        """Calculate semantic similarity using sentence embeddings"""
        try:
            query_embedding = self.embedding_model.encode([query])[0]
            doc_embedding = self.embedding_model.encode([document])[0]
            similarity = cosine_similarity([query_embedding], [doc_embedding])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return 0.0

    def _calculate_keyword_overlap(self, query: str, document: str) -> Dict[str, Any]:
        """Calculate keyword overlap between query and document"""

        # Extract keywords from query and document
        query_keywords = self._extract_keywords(query)
        doc_keywords = self._extract_keywords(document)

        # Calculate overlap metrics
        query_set = set(query_keywords)
        doc_set = set(doc_keywords)

        intersection = query_set.intersection(doc_set)
        union = query_set.union(doc_set)

        jaccard = len(intersection) / len(union) if union else 0.0
        overlap_coefficient = len(intersection) / len(query_set) if query_set else 0.0

        # Term frequency overlap
        query_counter = Counter(query_keywords)
        doc_counter = Counter(doc_keywords)

        common_terms = set(query_counter.keys()).intersection(set(doc_counter.keys()))
        tf_overlap = sum(min(query_counter[term], doc_counter[term]) for term in common_terms)

        return {
            'jaccard': jaccard,
            'overlap_coefficient': overlap_coefficient,
            'tf_overlap': tf_overlap,
            'common_terms': list(common_terms),
            'query_terms': list(query_set),
            'doc_terms': list(doc_set)
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from Arabic text"""
        text = self._normalize_arabic(text)

        # Tokenize (fallback when NLTK punkt is unavailable due to SSL/download issues)
        try:
            tokens = word_tokenize(text)
        except (LookupError, Exception):
            # Fallback: regex for Arabic + alphanumeric tokens
            tokens = re.findall(r'[\u0600-\u06FF]+|[a-zA-Z0-9]+', text)

        keywords = [
            token for token in tokens
            if len(token) > 1 and token not in self.arabic_stopwords
        ]
        return keywords

    def _normalize_arabic(self, text: str) -> str:
        """Basic Arabic text normalization"""
        # Remove diacritics (harakat)
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)

        # Normalize alef variants
        text = re.sub(r'[أإآ]', 'ا', text)

        # Normalize yaa variants
        text = re.sub(r'[يى]', 'ي', text)

        return text

    def _calculate_tfidf_similarity(self, query: str, document: str) -> float:
        """Calculate TF-IDF cosine similarity"""
        try:
            # Combine query and document for vectorization
            texts = [query, document]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"Error calculating TF-IDF similarity: {e}")
            return 0.0

    def _calculate_combined_score(self, doc_evaluation: Dict[str, Any]) -> float:
        """Calculate combined relevance score"""
        weights = {
            'semantic': 0.5,
            'keyword_jaccard': 0.3,
            'tfidf': 0.2
        }

        combined = (
            weights['semantic'] * doc_evaluation['semantic_similarity'] +
            weights['keyword_jaccard'] * doc_evaluation['keyword_overlap']['jaccard'] +
            weights['tfidf'] * doc_evaluation['tfidf_similarity']
        )

        return combined

    def _calculate_retrieval_metrics(
        self,
        retrieved_docs: List[Dict[str, Any]],
        ground_truth_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate precision, recall, and other retrieval metrics"""

        retrieved_ids = set(doc.get('id', doc.get('title', str(i)))
                          for i, doc in enumerate(retrieved_docs))
        ground_truth_ids = set(doc.get('id', doc.get('title', str(i)))
                              for i, doc in enumerate(ground_truth_docs))

        # Calculate metrics
        true_positives = len(retrieved_ids.intersection(ground_truth_ids))
        false_positives = len(retrieved_ids - ground_truth_ids)
        false_negatives = len(ground_truth_ids - retrieved_ids)

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'total_retrieved': len(retrieved_ids),
            'total_relevant': len(ground_truth_ids)
        }

    def _assess_overall_relevance(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Provide overall assessment of retrieval quality"""

        assessment = {
            'quality_score': 0.0,
            'quality_level': 'poor',
            'recommendations': []
        }

        # Calculate overall quality score
        semantic_score = evaluation['semantic_similarity'].get('top_1_score', 0)
        keyword_score = evaluation['keyword_overlap'].get('top_1_jaccard', 0)
        tfidf_score = evaluation['tfidf_similarity'].get('top_1_score', 0)

        # Weighted quality score
        quality_score = (
            0.4 * semantic_score +
            0.3 * keyword_score +
            0.3 * tfidf_score
        )

        assessment['quality_score'] = quality_score

        # Determine quality level
        if quality_score >= 0.8:
            assessment['quality_level'] = 'excellent'
        elif quality_score >= 0.6:
            assessment['quality_level'] = 'good'
        elif quality_score >= 0.4:
            assessment['quality_level'] = 'fair'
        else:
            assessment['quality_level'] = 'poor'

        # Generate recommendations
        if semantic_score < 0.5:
            assessment['recommendations'].append("Consider improving semantic search - retrieved documents may not be semantically relevant")

        if keyword_score < 0.2:
            assessment['recommendations'].append("Low keyword overlap - consider enhancing keyword-based retrieval")

        if tfidf_score < 0.3:
            assessment['recommendations'].append("TF-IDF similarity is low - documents may lack relevant terms")

        if not assessment['recommendations']:
            assessment['recommendations'].append("Retrieval quality looks good - continue monitoring")

        return assessment

    def evaluate_batch(
        self,
        queries_and_docs: List[Dict[str, Any]],
        ground_truths: Optional[List[List[Dict[str, Any]]]] = None
    ) -> Dict[str, Any]:
        """Evaluate relevance for a batch of queries

        Args:
            queries_and_docs: List of dicts with 'query' and 'retrieved_docs' keys
            ground_truths: Optional list of ground truth documents for each query

        Returns:
            Batch evaluation results
        """

        batch_results = []
        summary_stats = {
            'total_queries': len(queries_and_docs),
            'avg_semantic_similarity': [],
            'avg_keyword_overlap': [],
            'avg_tfidf_similarity': [],
            'quality_distribution': {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        }

        for i, query_data in enumerate(queries_and_docs):
            query = query_data['query']
            retrieved_docs = query_data['retrieved_docs']
            ground_truth = ground_truths[i] if ground_truths and i < len(ground_truths) else None

            result = self.evaluate_query_relevance(query, retrieved_docs, ground_truth)
            batch_results.append(result)

            # Update summary stats
            semantic_score = result['semantic_similarity'].get('top_1_score', 0)
            keyword_score = result['keyword_overlap'].get('top_1_jaccard', 0)
            tfidf_score = result['tfidf_similarity'].get('top_1_score', 0)

            if semantic_score > 0:
                summary_stats['avg_semantic_similarity'].append(semantic_score)
            if keyword_score > 0:
                summary_stats['avg_keyword_overlap'].append(keyword_score)
            if tfidf_score > 0:
                summary_stats['avg_tfidf_similarity'].append(tfidf_score)

            quality_level = result['overall_assessment']['quality_level']
            summary_stats['quality_distribution'][quality_level] += 1

        # Calculate averages
        summary_stats['avg_semantic_similarity'] = np.mean(summary_stats['avg_semantic_similarity']) if summary_stats['avg_semantic_similarity'] else 0.0
        summary_stats['avg_keyword_overlap'] = np.mean(summary_stats['avg_keyword_overlap']) if summary_stats['avg_keyword_overlap'] else 0.0
        summary_stats['avg_tfidf_similarity'] = np.mean(summary_stats['avg_tfidf_similarity']) if summary_stats['avg_tfidf_similarity'] else 0.0

        return {
            'individual_results': batch_results,
            'summary_statistics': summary_stats
        }


# Convenience functions for quick evaluation
def evaluate_retrieval_quality(
    query: str,
    retrieved_docs: List[Dict[str, Any]],
    ground_truth_docs: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Quick function to evaluate retrieval quality"""
    evaluator = RelevanceEvaluator()
    return evaluator.evaluate_query_relevance(query, retrieved_docs, ground_truth_docs)


def print_relevance_report(evaluation_result: Dict[str, Any]) -> None:
    """Print a formatted relevance evaluation report"""
    print("\n" + "="*80)
    print("RAG RETRIEVAL RELEVANCE EVALUATION REPORT")
    print("="*80)

    print(f"\nQuery: {evaluation_result['query'][:100]}...")
    print(f"Number of retrieved documents: {evaluation_result['num_retrieved']}")

    # Overall assessment
    assessment = evaluation_result['overall_assessment']
    print(f"\nOverall Quality: {assessment['quality_level'].upper()} (Score: {assessment['quality_score']:.3f})")

    print("\nRecommendations:")
    for rec in assessment['recommendations']:
        print(f"  • {rec}")

    # Detailed metrics
    semantic = evaluation_result['semantic_similarity']
    if semantic:
        print("\nSemantic Similarity:")
        print(f"  Mean: {semantic['mean']:.4f}")
        print(f"  Max:  {semantic['max']:.4f}")
        print(f"  Top-1 Score: {semantic['top_1_score']:.4f}")

    keyword = evaluation_result['keyword_overlap']
    if keyword:
        print("\nKeyword Overlap:")
        print(f"  Mean Jaccard: {keyword['mean_jaccard']:.4f}")
        print(f"  Max Jaccard:  {keyword['max_jaccard']:.4f}")

    tfidf = evaluation_result['tfidf_similarity']
    if tfidf:
        print("\nTF-IDF Similarity:")
        print(f"  Mean: {tfidf['mean']:.4f}")
        print(f"  Top-1 Score: {tfidf['top_1_score']:.4f}")

    # Retrieval metrics
    retrieval = evaluation_result['retrieval_metrics']
    if retrieval:
        print("\nRetrieval Metrics:")
        print(f"  Precision: {retrieval['precision']:.4f}")
        print(f"  Recall:    {retrieval['recall']:.4f}")
        print(f"  F1 Score:  {retrieval['f1_score']:.4f}")
        print(f"  True Positives: {retrieval['true_positives']}")
        print(f"  False Positives: {retrieval['false_positives']}")
        print(f"  False Negatives: {retrieval['false_negatives']}")

    # Top document details
    if evaluation_result['document_scores']:
        print("\nTop Retrieved Document:")
        top_doc = evaluation_result['document_scores'][0]
        print(f"  Title: {top_doc['title']}")
        print(f"  Semantic Similarity: {top_doc['semantic_similarity']:.4f}")
        print(f"  TF-IDF Similarity:   {top_doc['tfidf_similarity']:.4f}")
        print(f"  Retrieval Score:     {top_doc['retrieval_score']:.4f}")
        print(f"  Combined Score: {top_doc['combined_score']:.4f}")

    print("\n" + "="*80)