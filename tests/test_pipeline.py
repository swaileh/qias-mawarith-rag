"""
Test Suite for RAG Pipeline
Unit and integration tests for all components
"""

import pytest
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge.pdf_processor import PDFProcessor
from src.knowledge.vector_store import VectorStore
from src.retrieval.hybrid_retriever import HybridRetriever
from src.model.output_parser import OutputParser
from src.model.thinking_extractor import ThinkingExtractor


class TestPDFProcessor:
    """Test PDF processing"""
    
    def test_initialization(self):
        """Test PDF processor initialization"""
        processor = PDFProcessor()
        assert processor is not None
        assert processor.chunk_size > 0
    
    def test_chunking(self):
        """Test text chunking"""
        processor = PDFProcessor()
        test_text = "هذا نص تجريبي. " * 100
        metadata = {'source': 'test.pdf'}
        
        chunks = processor.chunk_text(test_text, metadata)
        
        assert len(chunks) > 0
        assert all(chunk.content for chunk in chunks)
        assert all(chunk.metadata.get('source') == 'test.pdf' for chunk in chunks)


class TestVectorStore:
    """Test vector store operations"""
    
    def test_initialization(self):
        """Test vector store initialization"""
        vs = VectorStore()
        assert vs is not None
        assert vs.embedding_model is not None
    
    def test_embedding_generation(self):
        """Test embedding generation"""
        vs = VectorStore()
        texts = ["هذا نص تجريبي", "This is a test"]
        
        embeddings = vs.embed_texts(texts)
        
        assert len(embeddings) == 2
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)


class TestOutputParser:
    """Test output parsing"""
    
    def test_thinking_extraction(self):
        """Test thinking section extraction"""
        parser = OutputParser()
        
        sample = """
<think>
هذا التفكير
</think>

<answer>
{"test": "value"}
</answer>
"""
        
        thinking, answer = parser.extract_thinking(sample)
        
        assert "هذا التفكير" in thinking
        assert "test" in answer
    
    def test_json_extraction(self):
        """Test JSON extraction"""
        parser = OutputParser()
        
        answer = '```json\n{"test": "value"}\n```'
        json_str = parser.extract_json(answer)
        
        assert json_str is not None
        assert "test" in json_str
    
    def test_complete_parsing(self):
        """Test complete parsing workflow"""
        parser = OutputParser()
        
        sample_output = """
<think>
نحدد الورثة
</think>

<answer>
```json
{
  "heirs": [{"heir": "أم", "count": 1}],
  "blocked": [],
  "shares": [{"heir": "أم", "count": 1, "fraction": "1/6"}],
  "awl_or_radd": "لا",
  "post_tasil": {
    "total_shares": 6,
    "distribution": [
      {"heir": "أم", "count": 1, "per_head_shares": "1/6", "per_head_percent": 16.67}
    ]
  }
}
```
</answer>
"""
        
        result = parser.parse(sample_output)
        
        assert result['parsing_success'] == True
        assert result['thinking'] != ""
        assert result['structured_output'] is not None


class TestThinkingExtractor:
    """Test thinking quality analysis"""
    
    def test_step_extraction(self):
        """Test reasoning step extraction"""
        extractor = ThinkingExtractor()
        
        thinking = """
1. تحديد الورثة
2. حساب الأنصبة
3. التوزيع النهائي
"""
        
        steps = extractor.extract_steps(thinking)
        
        assert len(steps) >= 3
    
    def test_terminology_analysis(self):
        """Test Islamic terminology detection"""
        extractor = ThinkingExtractor()
        
        thinking = "الأم ترث السدس فرضاً والأب يرث بالعصبة"
        
        analysis = extractor.analyze_terminology(thinking)
        
        assert analysis['total_terms'] > 0
        assert 'سدس' in analysis['terms_used'] or 'فرض' in analysis['terms_used']
    
    def test_quality_scoring(self):
        """Test quality score calculation"""
        extractor = ThinkingExtractor()
        
        thinking = """
نحدد الورثة: الأم والأب
الأم ترث السدس لوجود الفرع الوارث
الأب يرث الباقي بالعصبة
التوزيع النهائي بعد التصحيح
"""
        
        quality = extractor.quality_score(thinking)
        
        assert 'quality_score' in quality
        assert 0 <= quality['quality_score'] <= 1


class TestHybridRetriever:
    """Test hybrid retrieval"""
    
    def test_initialization(self):
        """Test retriever initialization"""
        retriever = HybridRetriever()
        assert retriever is not None
        assert retriever.top_k > 0
    
    def test_bm25_index_building(self):
        """Test BM25 index construction"""
        retriever = HybridRetriever()
        
        documents = [
            "الأم ترث السدس",
            "الأب يرث الباقي",
            "البنت ترث النصف"
        ]
        metadatas = [{'source': f'doc{i}'} for i in range(3)]
        
        retriever.build_bm25_index(documents, metadatas)
        
        assert retriever.bm25 is not None
        assert len(retriever.corpus) == 3


def run_tests():
    """Run all tests"""
    pytest.main([__file__, '-v'])


if __name__ == "__main__":
    run_tests()
