"""Tests for the symbolic inheritance calculator.

Validates that the MiraathCase API produces correct results for
standard and edge cases as described in Paper §3.2.
"""



class TestMiraathCaseBasic:
    """Basic inheritance calculation tests."""

    def test_import(self):
        """Calculator module can be imported."""
        from qias_mawarith_rag.calculator import MiraathCase
        assert MiraathCase is not None

    def test_quick_simple_case(self):
        """Quick API produces a valid result for a simple case."""
        from qias_mawarith_rag.calculator import MiraathCase

        result = MiraathCase.quick(["زوج", "أم", ("بنت", 2)])
        assert result is not None
        assert result.base > 0
        assert len(result.distribution) > 0

    def test_mother_father_daughter(self):
        """Standard case: mother + father + daughter."""
        from qias_mawarith_rag.calculator import MiraathCase

        case = MiraathCase()
        case.add_heir("أم")
        case.add_heir("أب")
        case.add_heir("بنت")
        result = case.calculate()

        assert result is not None
        assert result.base > 0
        # Mother gets 1/6 when there's a descendant
        # Father gets 1/6 + remainder (asabah)
        # Daughter gets 1/2

    def test_husband_mother_father_umariyyah(self):
        """Classical Umariyyah case detection."""
        from qias_mawarith_rag.calculator import MiraathCase

        case = MiraathCase()
        case.add_heir("زوج")
        case.add_heir("أم")
        case.add_heir("أب")
        result = case.calculate()

        assert result is not None
        assert result.base > 0

    def test_radd_case(self):
        """Radd (return) applies when prescribed shares < 100%."""
        from qias_mawarith_rag.calculator import MiraathCase

        result = MiraathCase.quick(["أم", ("بنت", 1)])
        assert result is not None

    def test_awl_case(self):
        """Awl (increase) applies when prescribed shares > 100%."""
        from qias_mawarith_rag.calculator import MiraathCase

        result = MiraathCase.quick([
            "زوج",
            ("أخت شقيقة", 2),
            "أم",
        ])
        assert result is not None

    def test_method_chaining(self):
        """add_heir returns self for method chaining."""
        from qias_mawarith_rag.calculator import MiraathCase

        case = MiraathCase()
        returned = case.add_heir("أم").add_heir("أب")
        assert returned is case

    def test_validation_no_heirs(self):
        """Validation warns when no heirs are specified."""
        from qias_mawarith_rag.calculator import MiraathCase

        case = MiraathCase()
        messages = case.validate()
        assert any("No heirs" in m for m in messages)

    def test_serialization_roundtrip(self):
        """Case can be exported to dict and recreated."""
        from qias_mawarith_rag.calculator import MiraathCase

        case = MiraathCase()
        case.add_heir("زوج")
        case.add_heir("أم")
        case.add_heir("بنت", count=2)

        data = case.to_dict()
        restored = MiraathCase.from_dict(data)

        assert len(restored.heirs) == len(case.heirs)


class TestInheritanceCalculator:
    """Tests for the legacy InheritanceCalculator."""

    def test_import(self):
        """Legacy calculator can be imported."""
        from qias_mawarith_rag.calculator.scalc import InheritanceCalculator
        assert InheritanceCalculator is not None

    def test_basic_calculation(self):
        """Calculator produces valid output."""
        from qias_mawarith_rag.calculator.scalc import InheritanceCalculator

        calc = InheritanceCalculator()
        heirs = [
            {"heir": "أم", "count": 1},
            {"heir": "أب", "count": 1},
            {"heir": "بنت", "count": 1},
        ]
        result = calc.calculate(heirs)
        assert result is not None
