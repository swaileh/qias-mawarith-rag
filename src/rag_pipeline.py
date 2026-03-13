"""
RAG Pipeline
Complete end-to-end RAG system for QIAS Islamic inheritance reasoning
"""

import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

from src.knowledge.pdf_processor import PDFProcessor
from src.knowledge.vector_store import VectorStore
from src.knowledge.web_search import WebSearch
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.reranker import Reranker
from src.retrieval.prompt_builder import PromptBuilder
from src.model.output_parser import OutputParser
from src.model.thinking_extractor import ThinkingExtractor
from src.evaluation.relevance_evaluator import RelevanceEvaluator

# Import model client based on config
from src.model.qwen_hf_client import QwenHFClient
from src.model.qwen3_client import Qwen3Client


class RAGPipeline:
    """Complete RAG pipeline for QIAS 2026 task"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize RAG pipeline with all components"""
        print("Initializing RAG Pipeline...")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.pdf_processor = PDFProcessor(config_path)
        self.vector_store = VectorStore(config_path)
        self.web_search = WebSearch(config_path)
        self.retriever = HybridRetriever(config_path)
        self.reranker = Reranker(config_path)
        self.prompt_builder = PromptBuilder(config_path)
        self.relevance_evaluator = RelevanceEvaluator(config_path)

        # Choose model client based on config
        client_type = self.config['model'].get('client_type', 'ollama')
        if client_type == 'huggingface':
            print("Using HuggingFace Transformers for Qwen3.5...")
            self.qwen_client = QwenHFClient(config_path)
        else:
            print("Using Ollama for model inference...")
            self.qwen_client = Qwen3Client(config_path)
        
        self.output_parser = OutputParser()
        self.thinking_extractor = ThinkingExtractor()
        
        # Connect retriever to vector store
        self.retriever.set_vector_store(self.vector_store)
        
        # Build BM25 index if documents exist
        self._initialize_bm25()
        
        print("RAG Pipeline initialized successfully")
    
    def _initialize_bm25(self) -> None:
        """Initialize BM25 index from vector store"""
        stats = self.vector_store.get_collection_stats()
        
        if stats['total_documents'] > 0:
            print("Building BM25 index from vector store...")
            
            # Get all documents from vector store
            sample_size = min(1000, stats['total_documents'])
            results = self.vector_store.collection.get(limit=sample_size)
            
            if results['documents']:
                self.retriever.build_bm25_index(
                    results['documents'],
                    results['metadatas']
                )
        else:
            print("No documents in vector store for BM25 index")
    
    def build_knowledge_base(self, pdf_directory: str = None) -> None:
        """Build knowledge base from PDFs
        
        Args:
            pdf_directory: Directory containing PDFs
        """
        print("\n=== Building Knowledge Base ===")
        
        # Process PDFs
        documents = self.pdf_processor.process_directory(pdf_directory)
        
        if not documents:
            print("No documents to add to knowledge base")
            return
        
        # Add to vector store
        self.vector_store.add_documents(documents)
        
        # Rebuild BM25 index
        self._initialize_bm25()
        
        print(f"Knowledge base built with {len(documents)} document chunks")
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        use_web_search: bool = False
    ) -> Dict[str, Any]:
        """Process a single question through RAG pipeline
        
        Args:
            question: Question in Arabic
            top_k: Number of documents to retrieve
            use_web_search: Whether to use web search
        
        Returns:
            Complete result dictionary
        """
        print(f"\n=== Processing Question ===\n{question[:100]}...")
        
        result = {
            'question': question,
            'retrieved_docs': [],
            'web_results': None,
            'prompt': '',
            'raw_output': '',
            'parsed_output': {},
            'thinking_quality': {},
            'relevance_evaluation': {},
            'error': None
        }
        
        # Retrieve relevant documents
        print("Retrieving documents...")
        retrieved_docs = self.retriever.retrieve(question, top_k=top_k)
        
        # Rerank documents
        if retrieved_docs:
            print("Reranking documents...")
            retrieved_docs = self.reranker.rerank(question, retrieved_docs, top_k=top_k)
            result['retrieved_docs'] = retrieved_docs

            # Evaluate relevance of retrieved documents
            print("Evaluating retrieval relevance...")
            relevance_eval = self.relevance_evaluator.evaluate_query_relevance(
                question, retrieved_docs
            )
            result['relevance_evaluation'] = relevance_eval
        
        # Optional web search
        web_search_formatted = None
        if use_web_search and self.web_search.enabled:
            print("Searching web...")
            web_results = self.web_search.search(question)
            if web_results:
                web_search_formatted = self.web_search.format_for_rag(web_results)
                result['web_results'] = web_results
        
        # Build prompt
        print("Building prompt...")
        prompt = self.prompt_builder.build_prompt(
            question,
            retrieved_docs=retrieved_docs,
            web_search_results=web_search_formatted
        )
        result['prompt'] = prompt
        
        # Generate response
        print("Generating response with Qwen3...")
        try:
            raw_output = self.qwen_client.generate(prompt)
            result['raw_output'] = raw_output
        except Exception as e:
            result['error'] = f"Generation error: {e}"
            return result
        
        # Parse output
        print("Parsing output...")
        parsed = self.output_parser.parse(raw_output)
        result['parsed_output'] = parsed
        
        # Analyze thinking quality
        if parsed['thinking']:
            quality = self.thinking_extractor.quality_score(
                parsed['thinking'],
                parsed.get('structured_output')
            )
            result['thinking_quality'] = quality
        
        print(f"✓ Parsing success: {parsed['parsing_success']}")
        print(f"✓ Validation success: {parsed['validation_success']}")

        return result

    def evaluate_retrieval_quality(
        self,
        question: str,
        retrieved_docs: List[Dict[str, Any]],
        ground_truth_docs: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Evaluate the relevance quality of retrieved documents

        Args:
            question: The query question
            retrieved_docs: Documents retrieved by the system
            ground_truth_docs: Optional ground truth relevant documents

        Returns:
            Comprehensive relevance evaluation
        """
        return self.relevance_evaluator.evaluate_query_relevance(
            question, retrieved_docs, ground_truth_docs
        )

    def batch_query(
        self,
        questions: List[Dict[str, Any]],
        save_results: bool = True
    ) -> List[Dict[str, Any]]:
        """Process multiple questions and save in QIAS 2026 submission format.
        
        Each saved prediction matches the ground truth entry structure:
        {"id": "...", "question": "...", "answer": "<think>...</think><answer>...</answer>", "output": {...}}
        
        Args:
            questions: List of question dicts with 'id' and 'question'
            save_results: Whether to save results to disk
        
        Returns:
            List of results
        """
        print(f"\n=== Processing {len(questions)} Questions ===")
        
        results = []
        
        for i, q_data in enumerate(questions):
            print(f"\n[{i+1}/{len(questions)}]")
            
            question_id = q_data.get('id', f'q_{i}')
            question_text = q_data.get('question', '')
            
            result = self.query(question_text)
            result['id'] = question_id
            
            # Always try to format, even if validation failed
            formatted = self.output_parser.format_for_evaluation(
                result['parsed_output']
            )
            result['formatted_output'] = formatted
            
            results.append(result)
        
        if save_results:
            output_dir = Path(self.config['evaluation']['output_directory'])
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "rag_predictions.json"
            
            # Build QIAS 2026 submission format:
            # {"id", "question", "answer", "output"}
            predictions = []
            for r in results:
                entry = {
                    'id': r['id'],
                    'question': r['question'],
                }
                if r.get('formatted_output'):
                    entry['answer'] = r['formatted_output']['answer']
                    entry['output'] = r['formatted_output']['output']
                else:
                    entry['answer'] = r.get('raw_output', '')
                    entry['output'] = {}
                predictions.append(entry)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(predictions, f, ensure_ascii=False, indent=2)
            
            print(f"\nSaved {len(predictions)} predictions to {output_file}")
        
        return results


if __name__ == "__main__":
    # Test the pipeline
    pipeline = RAGPipeline()
    
    # Test with sample question
    test_question = "مات وترك: أم و أب و بنت. ما هو نصيب كل وريث؟"
    
    result = pipeline.query(test_question)
    
    if result['parsed_output'].get('validation_success'):
        print("\n✓ Pipeline test successful!")
    else:
        print(f"\n✗ Pipeline test failed: {result.get('error')}")
