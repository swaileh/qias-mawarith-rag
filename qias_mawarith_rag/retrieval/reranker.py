"""
Context Reranker
Rerank retrieved documents using cross-encoder for better relevance
"""

import yaml
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
import os

# Disable HuggingFace authentication prompts
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"


class Reranker:
    """Rerank retrieved documents for improved relevance"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize reranker"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.retrieval_config = self.config['retrieval']
        self.enabled = self.retrieval_config.get('rerank', True)
        self.min_score = self.retrieval_config.get('min_relevance_score', 0.5)
        
        if self.enabled:
            model_name = self.retrieval_config.get(
                'reranker_model',
                'cross-encoder/ms-marco-MiniLM-L-6-v2'
            )
            
            print(f"Loading reranker model: {model_name}")
            try:
                self.model = CrossEncoder(
                    model_name,
                    trust_remote_code=True,
                    token=None  # Avoid authentication prompts
                )
            except Exception as e:
                print(f"Error loading reranker model: {e}")
                print("Trying with local files only...")
                try:
                    self.model = CrossEncoder(
                        model_name,
                        trust_remote_code=True,
                        local_files_only=True
                    )
                except Exception as e2:
                    print(f"Failed to load reranker model: {e2}")
                    print("Disabling reranking due to model loading failure")
                    self.enabled = False
                    self.model = None
        else:
            self.model = None
            print("Reranking disabled")
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """Rerank documents based on query relevance
        
        Args:
            query: Search query
            documents: List of retrieved documents
            top_k: Number of top results to return
        
        Returns:
            Reranked documents with updated scores
        """
        if not self.enabled or self.model is None or not documents:
            return documents
        
       # Prepare query-document pairs
        pairs = [[query, doc['content']] for doc in documents]
        
        # Get cross-encoder scores
        scores = self.model.predict(pairs)
        
        # Update documents with reranking scores
        reranked_docs = []
        for i, doc in enumerate(documents):
            doc_copy = doc.copy()
            doc_copy['rerank_score'] = float(scores[i])
            doc_copy['original_score'] = doc.get('score', 0.0)
            
            # Only include if above threshold
            if doc_copy['rerank_score'] >= self.min_score:
                reranked_docs.append(doc_copy)
        
        # Sort by rerank score
        reranked_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        # Return top-k if specified
        if top_k is not None:
            return reranked_docs[:top_k]
        
        return reranked_docs
    
    def get_diversity_rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        diversity_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Rerank with diversity consideration
        
        Args:
            query: Search query
            documents: List of retrieved documents
            diversity_weight: Weight for diversity vs relevance
        
        Returns:
            Reranked documents with diversity
        """
        # First do standard reranking
        reranked = self.rerank(query, documents)
        
        if len(reranked) <= 1:
            return reranked
        
        # Apply diversity (MMR-style selection)
        selected = [reranked[0]]  # Start with top result
        remaining = reranked[1:]
        
        while remaining and len(selected) < len(reranked):
            # Score remaining docs based on relevance and dissimilarity to selected
            best_idx = 0
            best_score = -float('inf')
            
            for i, doc in enumerate(remaining):
                relevance = doc['rerank_score']
                
                # Simple diversity: penalize if from same source
                diversity_penalty = 0
                for sel_doc in selected:
                    if doc['metadata'].get('source') == sel_doc['metadata'].get('source'):
                        diversity_penalty += 0.1
                
                # Combined score
                score = (1 - diversity_weight) * relevance - diversity_weight * diversity_penalty
                
                if score > best_score:
                    best_score = score
                    best_idx = i
            
            selected.append(remaining.pop(best_idx))
        
        return selected


if __name__ == "__main__":
    # Test the reranker
    reranker = Reranker()
    print("Reranker initialized successfully")
