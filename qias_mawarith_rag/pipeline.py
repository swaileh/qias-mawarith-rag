"""
RAG Pipeline
Complete end-to-end RAG system for QIAS Islamic inheritance reasoning
"""

import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timezone
import json

from qias_mawarith_rag.knowledge.pdf_processor import PDFProcessor
from qias_mawarith_rag.knowledge.vector_store import VectorStore
from qias_mawarith_rag.knowledge.web_search import WebSearch
from qias_mawarith_rag.knowledge.synthetic_ingester import SyntheticIngester
from qias_mawarith_rag.retrieval.hybrid_retriever import HybridRetriever
from qias_mawarith_rag.retrieval.reranker import Reranker
from qias_mawarith_rag.retrieval.prompt_builder import PromptBuilder
from qias_mawarith_rag.generation.output_parser import OutputParser
from qias_mawarith_rag.generation.thinking_extractor import ThinkingExtractor
from qias_mawarith_rag.evaluation.relevance_evaluator import RelevanceEvaluator

# Import model client based on config
from qias_mawarith_rag.generation.qwen_hf_client import QwenHFClient
from qias_mawarith_rag.generation.qwen3_client import Qwen3Client
from qias_mawarith_rag.generation.unsloth_client import UnslothClient


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
        self.synthetic_ingester = SyntheticIngester(config_path)
        self.retriever = HybridRetriever(config_path)
        self.reranker = Reranker(config_path)
        self.prompt_builder = PromptBuilder(config_path)
        self.enable_relevance_evaluation = self.config.get("evaluation", {}).get(
            "enable_relevance_evaluation",
            True
        )
        self.relevance_evaluator = None
        if self.enable_relevance_evaluation:
            self.relevance_evaluator = RelevanceEvaluator(
                config_path,
                embedding_model=self.vector_store.embedding_model
            )

        # Choose model client based on config
        client_type = self.config['model'].get('client_type', 'ollama')
        if client_type == 'huggingface':
            print("Using HuggingFace Transformers for Qwen3.5...")
            self.qwen_client = QwenHFClient(config_path)
        elif client_type == "unsloth":
            print("Using Unsloth for model inference...")
            self.qwen_client = UnslothClient(config_path)
        else:
            print("Using Ollama for model inference...")
            self.qwen_client = Qwen3Client(config_path)
        
        self.output_parser = OutputParser()
        self.thinking_extractor = ThinkingExtractor()
        
        # Connect retriever to vector store
        self.retriever.set_vector_store(self.vector_store)

        # Paths for persistence artefacts
        data_dir = Path(self.config['vector_store']['persist_directory']).parent
        self._bm25_path     = str(data_dir / "bm25_index.pkl")
        self._manifest_path = str(data_dir / "ingestion_manifest.json")

        # Build / load BM25 index
        self._initialize_bm25()

        print("RAG Pipeline initialized successfully")
    
    # ------------------------------------------------------------------
    # Manifest helpers
    # ------------------------------------------------------------------

    def _load_manifest(self) -> Dict[str, Any]:
        """Return the ingestion manifest (empty dict if none exists)."""
        try:
            with open(self._manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_manifest(self, manifest: Dict[str, Any]) -> None:
        """Persist the ingestion manifest to disk."""
        Path(self._manifest_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self._manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # BM25 init
    # ------------------------------------------------------------------

    def _initialize_bm25(self) -> None:
        """Load BM25 from pickle if available, otherwise build from vector store."""
        # Fast path: load from cache
        if self.retriever.load_bm25_index(self._bm25_path):
            return

        # Slow path: build from vector store then cache (batched to avoid SQL limits)
        stats = self.vector_store.get_collection_stats()
        if stats['total_documents'] > 0:
            print("Building BM25 index from vector store...")
            all_results = self.vector_store.get_all_documents_batched()
            if all_results['documents']:
                self.retriever.build_bm25_index(
                    all_results['documents'],
                    all_results['metadatas']
                )
                self.retriever.save_bm25_index(self._bm25_path)
        else:
            print("No documents in vector store for BM25 index")
    
    def build_knowledge_base(
        self,
        pdf_directory: str = None,
        force_rebuild: bool = False
    ) -> None:
        """Build knowledge base from PDFs.

        Args:
            pdf_directory: Directory containing PDFs (defaults to config value)
            force_rebuild: Re-process PDFs even if already ingested
        """
        manifest = self._load_manifest()
        manifest_key = "pdf"

        if not force_rebuild and manifest_key in manifest:
            info = manifest[manifest_key]
            print(
                f"\n[SKIP] PDF KB already ingested on {info.get('ingested_at', '?')} "
                f"({info.get('document_count', '?')} chunks).\n"
                f"       Pass force_rebuild=True to re-ingest."
            )
            return

        print("\n=== Building Knowledge Base from PDFs ===")

        documents = self.pdf_processor.process_directory(pdf_directory)

        if not documents:
            print("No documents to add to knowledge base")
            return

        self.vector_store.add_documents(documents)

        # Rebuild BM25 and persist (batched fetch to avoid SQL variable limits)
        all_results = self.vector_store.get_all_documents_batched()
        if all_results['documents']:
            self.retriever.build_bm25_index(
                all_results['documents'],
                all_results['metadatas']
            )
            self.retriever.save_bm25_index(self._bm25_path)

        manifest[manifest_key] = {
            "directory":      str(pdf_directory or self.config['pdf']['source_directory']),
            "document_count": len(documents),
            "ingested_at":    datetime.now(timezone.utc).isoformat(),
        }
        self._save_manifest(manifest)

        print(f"Knowledge base built with {len(documents)} document chunks")

    def build_knowledge_base_from_synthetic(
        self,
        synthetic_directory: str,
        glob_pattern: str = "synthetic_mawarith_part*.json",
        max_files: Optional[int] = None,
        categories: Optional[List[str]] = None,
        force_rebuild: bool = False
    ) -> None:
        """Ingest synthetic Q&A data into the vector knowledge base.

        Each synthetic entry is stored as:
            "سؤال: <question>\\n\\nالتفكير التفصيلي:\\n<thinking>"

        This allows the retriever to surface similar solved cases — with full
        step-by-step reasoning — as context for new inheritance questions.

        On the first call the documents are embedded and persisted in ChromaDB
        and the BM25 index is pickled to disk.  Subsequent calls are instant
        because both artefacts are loaded from disk — unless force_rebuild=True.

        Args:
            synthetic_directory: Path to the folder containing part*.json files
            glob_pattern:        File name pattern to match (default: all parts)
            max_files:           Cap on number of files to process (None = all)
            categories:          Filter entries by category, e.g. ['simple', 'complex']
                                 None = include every category
            force_rebuild:       Re-ingest even if a previous run is recorded in
                                 the manifest (use when synthetic data changes)
        """
        manifest = self._load_manifest()
        manifest_key = "synthetic"

        # ── Skip if already ingested ──────────────────────────────────────────
        if not force_rebuild and manifest_key in manifest:
            info = manifest[manifest_key]
            print(
                f"\n[SKIP] Synthetic KB already ingested on {info.get('ingested_at', '?')} "
                f"({info.get('document_count', '?')} docs from {info.get('directory', '?')}).\n"
                f"       Pass force_rebuild=True to re-ingest."
            )
            return

        print("\n=== Ingesting Synthetic Knowledge Base ===")
        print(f"Source: {synthetic_directory}")

        # ── Clear old synthetic entries from vector store ─────────────────────
        if force_rebuild and manifest_key in manifest:
            print("Removing previous synthetic entries from vector store...")
            try:
                self.vector_store.collection.delete(
                    where={"source_type": "synthetic"}
                )
                print("  Previous synthetic entries removed.")
            except Exception as e:
                print(f"  Could not remove old entries (proceeding anyway): {e}")

        # ── Load and embed documents ──────────────────────────────────────────
        documents = self.synthetic_ingester.load_directory(
            directory=synthetic_directory,
            glob_pattern=glob_pattern,
            max_files=max_files,
            categories=categories
        )

        if not documents:
            print("No synthetic documents to add.")
            return

        self.vector_store.add_documents(documents)

        # ── Rebuild BM25 and save both artefacts (batched fetch to avoid SQL limits) ─
        all_results = self.vector_store.get_all_documents_batched()
        if all_results['documents']:
            self.retriever.build_bm25_index(
                all_results['documents'],
                all_results['metadatas']
            )
            self.retriever.save_bm25_index(self._bm25_path)

        # ── Update manifest ───────────────────────────────────────────────────
        manifest[manifest_key] = {
            "directory":      str(synthetic_directory),
            "glob_pattern":   glob_pattern,
            "max_files":      max_files,
            "categories":     categories,
            "document_count": len(documents),
            "ingested_at":    datetime.now(timezone.utc).isoformat(),
        }
        self._save_manifest(manifest)

        print(f"\nSynthetic knowledge base built: {len(documents)} entries added.")
        print(f"Manifest saved to {self._manifest_path}")

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

            # Evaluate relevance only when enabled (expensive path)
            if self.enable_relevance_evaluation and self.relevance_evaluator:
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

        # If thinking is required but missing, retry once with stricter format hint.
        # This improves compliance with QIAS "<think>...</think><answer>...</answer>" outputs.
        require_thinking = bool(self.config.get('model', {}).get('enable_thinking', False))
        retry_on_missing_thinking = bool(
            self.config.get('model', {}).get('retry_on_missing_thinking', True)
        )
        if (
            require_thinking
            and retry_on_missing_thinking
            and not parsed.get('thinking', '').strip()
        ):
            print("No <think> section detected. Retrying generation once with stricter tags...")
            retry_prompt = (
                prompt
                + "\n\n[FORMAT REQUIREMENT - STRICT]\n"
                + "يجب أن يكون الرد بالكامل داخل قسمين فقط وبالترتيب التالي:\n"
                + "<think>...خطوات التفكير التفصيلية...</think>\n"
                + "<answer>...الإجابة النهائية...</answer>\n"
                + "لا تكتب أي نص خارج هذين الوسمين.\n"
            )
            try:
                retry_output = self.qwen_client.generate(retry_prompt)
                retry_parsed = self.output_parser.parse(retry_output)
                if retry_parsed.get('thinking', '').strip():
                    print("Retry successful: thinking section captured.")
                    raw_output = retry_output
                    parsed = retry_parsed
                    result['raw_output'] = retry_output
                else:
                    print("Retry completed but thinking section is still missing.")
            except Exception as e:
                print(f"Retry generation failed: {e}")

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
        if not self.relevance_evaluator:
            return {
                "query": question,
                "num_retrieved": len(retrieved_docs),
                "error": "Relevance evaluation is disabled in configuration"
            }
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
