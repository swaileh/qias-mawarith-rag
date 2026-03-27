"""
Synthetic Data Ingester
Loads synthetic Islamic inheritance Q&A data into the vector store.

Each JSON entry has:
  - id, question, answer, qa_nl (natural-language Q&A), category, output

The document stored in the vector store is built from qa_nl when present:
  "السؤال:\n{question}\n\nالجواب:\n{answer details}"

This allows the retriever to surface similar solved cases (with full reasoning)
as context for new questions.
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from qias_mawarith_rag.knowledge.pdf_processor import Document


class SyntheticIngester:
    """Ingest synthetic inheritance Q&A data into the RAG knowledge base"""

    def __init__(self, config_path: str = "config/rag_config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.vs_config = self.config['vector_store']
        self.chunk_size = self.vs_config.get('chunk_size', 512)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_thinking(self, answer: str) -> str:
        """Pull the content between <think>...</think> tags."""
        m = re.search(r'<think>(.*?)</think>', answer, re.DOTALL)
        if m:
            return m.group(1).strip()
        # Fallback: everything before <answer>
        if '<answer>' in answer:
            return answer.split('<answer>')[0].replace('<think>', '').strip()
        return ""

    def _build_document_content(self, question: str, thinking: str) -> str:
        """Combine question + thinking into a single retrievable document."""
        parts = [f"سؤال: {question.strip()}"]
        if thinking:
            parts.append(f"\nالتفكير التفصيلي:\n{thinking}")
        return "\n".join(parts)

    def _entry_to_document(
        self,
        entry: Dict[str, Any],
        source_file: str
    ) -> Optional[Document]:
        """Convert a single JSON entry to a Document object.

        Prefers qa_nl (natural-language Q&A) when present; falls back to
        question + thinking from answer field.
        """
        entry_id = entry.get('id', 'unknown')
        category = entry.get('category', 'unknown')
        question = entry.get('question', '').strip()

        # Primary: use qa_nl (السؤال:\n...\n\nالجواب:\n...)
        qa_nl = entry.get('qa_nl', '').strip()
        if qa_nl:
            content = qa_nl
        else:
            # Fallback: question + thinking from answer
            if not question:
                return None
            thinking = self._extract_thinking(entry.get('answer', ''))
            content = self._build_document_content(question, thinking)

        if not content:
            return None

        # Truncate if excessively long
        if len(content) > self.chunk_size * 3:
            content = content[:self.chunk_size * 3]

        metadata = {
            'source': os.path.basename(source_file),
            'source_type': 'synthetic',
            'entry_id': entry_id,
            'category': category,
            'question': (question or qa_nl[:200])[:200],
        }

        chunk_id = f"synthetic_{entry_id}"
        return Document(content=content, metadata=metadata, chunk_id=chunk_id)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_file(self, json_path: str) -> List[Document]:
        """Load all entries from a single synthetic JSON file.

        Args:
            json_path: Path to a synthetic_mawarith_partXX.json file

        Returns:
            List of Document objects
        """
        documents = []
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                print(f"  Unexpected format in {json_path}, skipping")
                return []

            for entry in data:
                doc = self._entry_to_document(entry, json_path)
                if doc:
                    documents.append(doc)

        except Exception as e:
            print(f"  Error reading {json_path}: {e}")

        return documents

    def load_directory(
        self,
        directory: str,
        glob_pattern: str = "synthetic_mawarith_part*.json",
        max_files: Optional[int] = None,
        categories: Optional[List[str]] = None
    ) -> List[Document]:
        """Load synthetic data from all matching files in a directory.

        Args:
            directory:     Path to the synthetic data directory
            glob_pattern:  Pattern to match JSON files (default: all part files)
            max_files:     Limit number of files to process (None = all)
            categories:    Filter by category ('simple', 'medium', 'complex', ...)
                           None = include all categories

        Returns:
            List of all Document objects
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Synthetic data directory not found: {directory}")

        json_files = sorted(dir_path.glob(glob_pattern))

        if max_files is not None:
            json_files = json_files[:max_files]

        print(f"Found {len(json_files)} synthetic data file(s) in {directory}")

        all_documents: List[Document] = []

        for i, json_file in enumerate(json_files, 1):
            docs = self.load_file(str(json_file))

            # Filter by category if requested
            if categories:
                docs = [
                    d for d in docs
                    if d.metadata.get('category') in categories
                ]

            all_documents.extend(docs)
            if i % 50 == 0 or i == len(json_files):
                print(f"  Loaded {i}/{len(json_files)} files → {len(all_documents)} documents so far")

        print(f"Total synthetic documents loaded: {len(all_documents)}")
        return all_documents
