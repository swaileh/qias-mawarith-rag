"""Tests for the output parser and validation logic.

Validates the multi-stage extraction and schema validation
described in Paper §3.3.3.
"""



class TestOutputParser:
    """Tests for OutputParser extraction and validation."""

    def test_import(self):
        """OutputParser can be imported from new location."""
        from qias_mawarith_rag.generation.output_parser import OutputParser
        assert OutputParser is not None

    def test_extract_think_answer_tags(self):
        """Extracts content from <think> and <answer> tags."""
        from qias_mawarith_rag.generation.output_parser import OutputParser

        parser = OutputParser()

        raw = '''<think>
هذه مسألة ميراث بسيطة
الأم ترث السدس
</think>
<answer>
{"heirs": [{"heir": "أم", "count": 1}], "blocked": [], "shares": [{"heir": "أم", "count": 1, "fraction": "1/6"}], "awl_or_radd": "لا", "tasil_stage": {"asl": 6, "distribution": [{"heir": "أم", "count": 1, "shares": "1"}]}, "post_tasil": {"total_shares": 6, "distribution": [{"heir": "أم", "count": 1, "per_head_shares": "1/6", "per_head_percent": 16.67}]}}
</answer>'''

        result = parser.parse(raw)
        assert result["parsing_success"] is True
        assert "thinking" in result
        assert result["thinking"] != ""

    def test_extract_json_from_raw(self):
        """Extracts JSON when tags are missing but JSON is present."""
        from qias_mawarith_rag.generation.output_parser import OutputParser

        parser = OutputParser()

        raw = '''Some text before
{"heirs": [{"heir": "ابن", "count": 1}], "blocked": [], "shares": [{"heir": "ابن", "count": 1, "fraction": "عصبة"}], "awl_or_radd": "لا", "post_tasil": {"total_shares": 1, "distribution": []}}
Some text after'''

        result = parser.parse(raw)
        structured = result.get("structured_output")
        assert structured is not None
        assert "heirs" in structured

    def test_empty_input(self):
        """Handles empty input gracefully."""
        from qias_mawarith_rag.generation.output_parser import OutputParser

        parser = OutputParser()
        result = parser.parse("")
        assert result["parsing_success"] is False

    def test_invalid_json(self):
        """Handles malformed JSON gracefully."""
        from qias_mawarith_rag.generation.output_parser import OutputParser

        parser = OutputParser()
        result = parser.parse("<answer>not valid json{{{</answer>")
        # Should not crash
        assert isinstance(result, dict)


class TestThinkingExtractor:
    """Tests for thinking quality assessment."""

    def test_import(self):
        """ThinkingExtractor can be imported."""
        from qias_mawarith_rag.generation.thinking_extractor import ThinkingExtractor
        assert ThinkingExtractor is not None

    def test_quality_score_nonempty(self):
        """Quality score is > 0 for substantive thinking text."""
        from qias_mawarith_rag.generation.thinking_extractor import ThinkingExtractor

        extractor = ThinkingExtractor()
        thinking = """
        1. تحديد الورثة: الأم والأب والبنت
        2. الأم ترث السدس لوجود الفرع الوارث
        3. البنت ترث النصف فرضاً
        4. الأب يرث السدس والباقي تعصيباً
        5. التوزيع النهائي
        """
        score = extractor.quality_score(thinking)
        assert score["quality_score"] > 0

    def test_quality_score_empty(self):
        """Quality score is 0 for empty input."""
        from qias_mawarith_rag.generation.thinking_extractor import ThinkingExtractor

        extractor = ThinkingExtractor()
        score = extractor.quality_score("")
        assert score["quality_score"] == 0.0
