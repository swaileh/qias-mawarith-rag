"""
Edge cases package - Handlers for special inheritance scenarios.

Supported edge cases:
- missing (مفقود) - Missing persons
- unborn (حمل) - Pregnancy/fetus
- successive (مناسخات) - Successive deaths
- extended_kin (ذوي الأرحام) - Extended kin
- treasury (بيت المال) - Treasury fallback
- wasiyyah (وصية واجبة) - Obligatory bequest
"""

from .missing import (
    identify_missing_heirs,
    calculate_with_missing,
    MissingPersonResult,
    MissingPersonScenario,
    format_missing_result,
)

from .unborn import (
    calculate_pregnancy_scenarios,
    PregnancyResult,
    PregnancyScenario,
    format_pregnancy_result,
)

from .successive import (
    calculate_munasakhaat,
    MunasakhResult,
    DeathEvent,
    format_munasakh_result,
)

__all__ = [
    # Missing person
    "identify_missing_heirs",
    "calculate_with_missing",
    "MissingPersonResult",
    "MissingPersonScenario",
    "format_missing_result",
    # Pregnancy
    "calculate_pregnancy_scenarios",
    "PregnancyResult",
    "PregnancyScenario",
    "format_pregnancy_result",
    # Successive deaths
    "calculate_munasakhaat",
    "MunasakhResult",
    "DeathEvent",
    "format_munasakh_result",
]

