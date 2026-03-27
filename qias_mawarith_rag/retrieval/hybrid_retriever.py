"""
Hybrid Retrieval System
Combines semantic search with BM25 keyword search
"""

import yaml
import pickle
from pathlib import Path
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import numpy as np


class HybridRetriever:
    """Hybrid retrieval combining semantic and keyword search"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize hybrid retriever"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.retrieval_config = self.config['retrieval']
        self.top_k = self.retrieval_config.get('top_k', 5)
        self.semantic_weight = self.retrieval_config.get('semantic_weight', 0.7)
        self.keyword_weight = self.retrieval_config.get('keyword_weight', 0.3)
        
        # Initialize components (will be set by external code)
        self.vector_store = None
        self.bm25 = None
        self.corpus = []
        self.corpus_metadata = []
    
    def set_vector_store(self, vector_store) -> None:
        """Set the vector store for semantic search"""
        self.vector_store = vector_store
    
    def build_bm25_index(self, documents: List[str], metadatas: List[Dict]) -> None:
        """Build BM25 index for keyword search
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
        """
        # Ensure corpus and metadata stay in sync (ChromaDB can return mismatched lengths)
        n = len(documents)
        if n == 0:
            print("No documents to build BM25 index")
            return
        if not metadatas:
            metadatas = [{}] * n
        elif len(metadatas) < n:
            metadatas = list(metadatas) + [{}] * (n - len(metadatas))
        else:
            metadatas = metadatas[:n]

        tokenized_corpus = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.corpus = documents
        self.corpus_metadata = metadatas

        print(f"Built BM25 index with {len(self.corpus)} documents")

    def save_bm25_index(self, path: str) -> None:
        """Pickle the BM25 index, corpus and metadata to disk.

        Args:
            path: File path for the pickle file (e.g. './data/bm25_index.pkl')
        """
        if self.bm25 is None:
            print("BM25 index is empty — nothing to save.")
            return

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'bm25': self.bm25,
            'corpus': self.corpus,
            'corpus_metadata': self.corpus_metadata,
        }
        with open(path, 'wb') as f:
            pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"BM25 index saved to {path} ({len(self.corpus)} docs)")

    def load_bm25_index(self, path: str) -> bool:
        """Load a previously pickled BM25 index from disk.

        Args:
            path: File path to the pickle file

        Returns:
            True if loaded successfully, False if file not found
        """
        p = Path(path)
        if not p.exists():
            return False

        try:
            with open(path, 'rb') as f:
                payload = pickle.load(f)
            self.bm25 = payload['bm25']
            self.corpus = payload['corpus']
            self.corpus_metadata = payload['corpus_metadata']
            print(f"BM25 index loaded from {path} ({len(self.corpus)} docs)")
            return True
        except Exception as e:
            print(f"Failed to load BM25 index from {path}: {e}")
            return False

    def semantic_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform semantic search using vector store
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            List of results with scores
        """
        if self.vector_store is None:
            return []
        
        results = self.vector_store.search(query, top_k=top_k * 2)  # Get more for fusion
        
        # Convert distances to similarity scores (assuming cosine distance)
        formatted_results = []
        for i, doc in enumerate(results['documents']):
            # Convert distance to similarity (1 - distance for cosine)
            similarity = 1 - results['distances'][i]
            
            formatted_results.append({
                'content': doc,
                'metadata': results['metadatas'][i],
                'score': similarity,
                'source': 'semantic'
            })
        
        return formatted_results
    
    def keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform BM25 keyword search
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            List of results with scores
        """
        if self.bm25 is None or not self.corpus:
            return []
        
        # Tokenize query
        tokenized_query = query.split()
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k * 2]
        
        # Format results (bounds check in case corpus/corpus_metadata are out of sync)
        n_corpus = len(self.corpus)
        n_meta = len(self.corpus_metadata)
        formatted_results = []
        for idx in top_indices:
            if idx >= n_corpus or idx >= n_meta:
                continue
            if scores[idx] > 0:  # Only include relevant results
                formatted_results.append({
                    'content': self.corpus[idx],
                    'metadata': self.corpus_metadata[idx],
                    'score': float(scores[idx]),
                    'source': 'keyword'
                })
        return formatted_results
    
    def reciprocal_rank_fusion(
        self,
        semantic_results: List[Dict],
        keyword_results: List[Dict],
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """Combine results using Reciprocal Rank Fusion
        
        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from keyword search
            k: RRF constant (default 60)
        
        Returns:
            Fused and ranked results
        """
        # Create a mapping of document content to scores
        fused_scores = {}
        
        # Add semantic results
        for rank, result in enumerate(semantic_results):
            content = result['content']
            rrf_score = self.semantic_weight / (k + rank + 1)
            
            if content not in fused_scores:
                fused_scores[content] = {
                    'content': content,
                    'metadata': result['metadata'],
                    'score': 0,
                    'sources': []
                }
            
            fused_scores[content]['score'] += rrf_score
            fused_scores[content]['sources'].append('semantic')
        
        # Add keyword results
        for rank, result in enumerate(keyword_results):
            content = result['content']
            rrf_score = self.keyword_weight / (k + rank + 1)
            
            if content not in fused_scores:
                fused_scores[content] = {
                    'content': content,
                    'metadata': result['metadata'],
                    'score': 0,
                    'sources': []
                }
            
            fused_scores[content]['score'] += rrf_score
            fused_scores[content]['sources'].append('keyword')
        
        # Sort by fused score
        fused_results = sorted(
            fused_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return fused_results
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        use_hybrid: bool = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query
        
        Args:
            query: Search query
            top_k: Number of results (default from config)
            use_hybrid: Whether to use hybrid search (default from config)
        
        Returns:
            List of retrieved documents with scores
        """
        if top_k is None:
            top_k = self.top_k
        
        if use_hybrid is None:
            use_hybrid = self.retrieval_config.get('hybrid_search', True)
        
        if use_hybrid and self.bm25 is not None:
            # Perform both searches
            semantic_results = self.semantic_search(query, top_k)
            keyword_results = self.keyword_search(query, top_k)
            
            # Fuse results
            fused_results = self.reciprocal_rank_fusion(
                semantic_results,
                keyword_results
            )
            
            # Return top-k
            return fused_results[:top_k]
        else:
            # Semantic search only
            results = self.semantic_search(query, top_k)
            return results[:top_k]


if __name__ == "__main__":
    # Test the hybrid retriever
    retriever = HybridRetriever()
    print("Hybrid Retriever initialized successfully")
