"""
Vector Store Management
Handles ChromaDB/FAISS for document embeddings and similarity search
"""

import os
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Disable HuggingFace authentication prompts to prevent KeyboardInterrupt
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "0"  # Allow online access but with better error handling


class VectorStore:
    """Manage vector database for RAG retrieval"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize vector store with configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.vs_config = self.config['vector_store']
        self.persist_dir = Path(self.vs_config['persist_directory'])
        self.collection_name = self.vs_config['collection_name']
        
        # Create persist directory if needed
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model with authentication handling
        print(f"Loading embedding model: {self.vs_config['embedding_model']}")
        try:
            self.embedding_model = SentenceTransformer(
                self.vs_config['embedding_model'],
                trust_remote_code=True,
                local_files_only=False,
                token=None  # Explicitly set token to None to avoid auth prompts
            )
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            print("Trying with local files only...")
            try:
                self.embedding_model = SentenceTransformer(
                    self.vs_config['embedding_model'],
                    trust_remote_code=True,
                    local_files_only=True  # Fallback to local files only
                )
            except Exception as e2:
                print(f"Failed to load embedding model: {e2}")
                raise RuntimeError(f"Could not load embedding model {self.vs_config['embedding_model']}. "
                                 "Please check your internet connection or try a different model.")
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": self.vs_config['distance_metric']}
        )
        
        print(f"Vector store initialized: {self.collection.count()} documents")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        embeddings = self.embedding_model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10
        )
        return embeddings.tolist()
    
    def add_documents(self, documents: List[Any]) -> None:
        """Add documents to the vector store
        
        Args:
            documents: List of Document objects from pdf_processor
        """
        if not documents:
            print("No documents to add")
            return
        
        # Extract texts and metadata
        texts = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [doc.chunk_id for doc in documents]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.embed_texts(texts)
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))
            
            self.collection.add(
                embeddings=embeddings[i:batch_end],
                documents=texts[i:batch_end],
                metadatas=metadatas[i:batch_end],
                ids=ids[i:batch_end]
            )
            
            print(f"Added batch {i//batch_size + 1}: {batch_end - i} documents")
        
        print(f"Total documents in collection: {self.collection.count()}")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents
        
        Args:
            query: Search query string
            top_k: Number of results to return
            filter_dict: Optional metadata filters
        
        Returns:
            Dictionary with documents, distances, and metadata
        """
        # Generate query embedding
        query_embedding = self.embed_texts([query])[0]
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict
        )
        
        # Format results
        formatted_results = {
            'documents': results['documents'][0] if results['documents'] else [],
            'distances': results['distances'][0] if results['distances'] else [],
            'metadatas': results['metadatas'][0] if results['metadatas'] else [],
            'ids': results['ids'][0] if results['ids'] else []
        }
        
        return formatted_results
    
    def delete_collection(self) -> None:
        """Delete the current collection"""
        self.client.delete_collection(self.collection_name)
        print(f"Deleted collection: {self.collection_name}")
    
    def reset_collection(self) -> None:
        """Reset the collection (delete and recreate)"""
        try:
            self.delete_collection()
        except Exception:
            pass
        
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": self.vs_config['distance_metric']}
        )
        print(f"Reset collection: {self.collection_name}")
    
    def get_all_documents_batched(
        self,
        batch_size: int = 500
    ) -> Dict[str, Any]:
        """Fetch all documents and metadatas in batches to avoid SQL variable limits.

        ChromaDB/SQLite fails with "too many SQL variables" when fetching
        very large collections in one call. This method paginates safely.

        Returns:
            Dict with 'documents', 'metadatas', 'ids' (flat lists)
        """
        total = self.collection.count()
        if total == 0:
            return {'documents': [], 'metadatas': [], 'ids': []}

        all_docs, all_metas, all_ids = [], [], []
        offset = 0

        while offset < total:
            batch = self.collection.get(
                limit=batch_size,
                offset=offset
            )
            docs = batch['documents'][0] if batch.get('documents') else []
            metas = batch['metadatas'][0] if batch.get('metadatas') else []
            ids_batch = batch['ids'][0] if batch.get('ids') else []

            if not docs:
                break

            # Ensure one metadata per document (ChromaDB can return fewer)
            n = len(docs)
            if not metas:
                metas = [{}] * n
            elif len(metas) < n:
                metas = list(metas) + [{}] * (n - len(metas))
            else:
                metas = metas[:n]

            all_docs.extend(docs)
            all_metas.extend(metas)
            all_ids.extend(ids_batch if ids_batch else [])
            offset += len(docs)

            if len(docs) < batch_size:
                break

        return {'documents': all_docs, 'metadatas': all_metas, 'ids': all_ids}

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        
        # Get sample to analyze metadata
        sample = self.collection.peek(limit=10)
        
        sources = set()
        if sample['metadatas']:
            for metadata in sample['metadatas']:
                if 'source' in metadata:
                    sources.add(metadata['source'])
        
        return {
            'total_documents': count,
            'collection_name': self.collection_name,
            'sample_sources': list(sources),
            'embedding_model': self.vs_config['embedding_model']
        }


if __name__ == "__main__":
    # Test the vector store
    vector_store = VectorStore()
    
    # Print stats
    stats = vector_store.get_collection_stats()
    print(f"Vector Store Stats: {stats}")
    
    # Test search
    if stats['total_documents'] > 0:
        results = vector_store.search("ما هو نصيب الأم في الميراث؟", top_k=3)
        print(f"\nTest search results: {len(results['documents'])} documents found")
