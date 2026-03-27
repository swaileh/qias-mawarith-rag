"""
Test Suite for RAG Pipeline Components

Tests that can run without GPU dependencies (torch, sentence-transformers).
Heavy modules are mocked to prevent import failures in CPU-only environments.
"""

import pytest
from unittest.mock import MagicMock, patch

from qias_mawarith_rag.generation.output_parser import OutputParser
from qias_mawarith_rag.generation.thinking_extractor import ThinkingExtractor


class TestOutputParserIntegration:
    """Integration tests for output parsing workflow."""

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
        json_str = parser._extract_json(answer)

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

        assert result['parsing_success']
        assert result['thinking'] != ""
        assert result['structured_output'] is not None


class TestThinkingExtractorIntegration:
    """Integration tests for thinking quality analysis."""

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


class TestPipelineConfig:
    """Test pipeline configuration loading."""

    def test_config_file_exists(self, config_path):
        """Config file should exist at expected location"""
        from pathlib import Path
        assert Path(config_path).exists()

    def test_config_has_required_sections(self, config):
        """Config should have all required top-level sections"""
        required = {'model', 'retrieval', 'vector_store', 'pdf', 'evaluation'}
        assert required.issubset(set(config.keys()))

    def test_model_config(self, config):
        """Model config should have required fields"""
        model = config['model']
        assert 'hf_model_name' in model
        assert 'client_type' in model

    def test_retrieval_weights_sum(self, config):
        """Retrieval weights should be valid"""
        retrieval = config['retrieval']
        total = retrieval['semantic_weight'] + retrieval['keyword_weight']
        assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, expected 1.0"


def run_tests():
    """Run all tests"""
    pytest.main([__file__, '-v'])


if __name__ == "__main__":
    run_tests()
