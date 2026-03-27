# Mawarith Calculator v2.0

**المواريث** - Islamic Inheritance Calculator

A comprehensive Python library for calculating Islamic inheritance shares according to Fiqh rules.

## Features

- **99.25% accuracy** on the Qias2026 dev dataset (5856/5900 cases)
- **Unified API** with `MiraathCase` for simple to complex calculations
- **Madhab Support** - Shafi'i, Hanafi, Maliki, Hanbali variations
- **Edge Cases** - Missing persons, pregnancy, successive deaths
- **Classical Special Cases** - العمرية، المشتركة، الأكدرية
- **Arabic & English** output support

## Installation

```bash
# The mawarith package is local to this project
# Add the project root to your path
import sys
sys.path.insert(0, '/path/to/Qias2026')
```

## Quick Start

### Simple One-Liner

```python
from mawarith import MiraathCase

# Calculate inheritance for: Husband + Mother + 2 Daughters
result = MiraathCase.quick(["زوج", "أم", ("بنت", 2)])

print(result.summary())
# Output:
# زوج (1): 1/4 = 25%
# أم (1): 1/6 = 16.67%
# بنت (2): 2/3 = 58.33%
```

### Standard Usage

```python
from mawarith import MiraathCase

case = MiraathCase(madhab="shafii")
case.add_heir("زوجة", count=2)
case.add_heir("ابن")
case.add_heir("بنت", count=3)

result = case.calculate()
print(result.summary("ar"))  # Arabic output
print(result.to_dict())      # JSON-compatible dict
```

### Madhab-Specific Calculations

```python
from mawarith import MiraathCase
from mawarith.madhab import MadhabRegistry

# Check madhab differences
shafii = MadhabRegistry("shafii")
hanafi = MadhabRegistry("hanafi")

print(f"GF blocks siblings (Shafi'i): {shafii.grandfather_blocks_siblings()}")  # False
print(f"GF blocks siblings (Hanafi): {hanafi.grandfather_blocks_siblings()}")   # True

# Calculate with specific madhab
result = MiraathCase.quick(["زوج", "أم", "أب الأب", "أخت شقيقة"], madhab="hanafi")
```

### Special Cases Detection

```python
result = MiraathCase.quick(["زوج", "أم", "أب"])
print(result.special_case)  # "العمرية" - Automatically detected!
```

## API Reference

### MiraathCase

Main class for inheritance calculations.

```python
class MiraathCase:
    def __init__(
        self,
        madhab: str = "shafii",           # School of thought
        jurisdiction: str = None,          # Country code
        apply_wasiyyah_wajibah: bool = False,
        bayt_mal_fallback: bool = True,
        include_dhul_arham: bool = False,
    )
    
    def add_heir(
        self,
        heir_type: str,       # Arabic heir name
        count: int = 1,
        name: str = None,     # For tracking in munasakhaat
        status: str = "alive",
        pregnant: bool = False,
        reserve: bool = False,
    ) -> "MiraathCase"
    
    def calculate(self) -> MiraathResult
    
    @classmethod
    def quick(cls, heirs, madhab="shafii") -> MiraathResult
```

### MiraathResult

Result of inheritance calculation.

```python
class MiraathResult:
    distribution: List[HeirShare]  # All heir shares
    base: int                      # Common denominator
    awl_applied: bool              # Deficiency scaling
    radd_applied: bool             # Excess distribution
    blocked_heirs: List[BlockedHeir]
    special_case: str              # العمرية, المشتركة, etc.
    madhab: str
    
    def summary(self, language="ar") -> str
    def to_dict(self) -> dict
    def to_table(self) -> str
```

## Supported Heirs

### Primary Heirs (أصحاب الفروض)

| Arabic | English | Fixed Share |
|--------|---------|-------------|
| زوج | Husband | 1/2 or 1/4 |
| زوجة | Wife | 1/4 or 1/8 |
| أب | Father | 1/6 + residuary |
| أم | Mother | 1/3 or 1/6 |
| بنت | Daughter | 1/2 or 2/3 |
| بنت ابن | Granddaughter | 1/2, 2/3, or 1/6 |
| أخت شقيقة | Full Sister | 1/2 or 2/3 |
| أخت لأب | Paternal Sister | 1/2, 2/3, or 1/6 |
| أخ لأم | Maternal Brother | 1/6 or 1/3 |
| أخت لأم | Maternal Sister | 1/6 or 1/3 |
| جدة | Grandmother | 1/6 |

### Residuary Heirs (العصبات)

| Arabic | English |
|--------|---------|
| ابن | Son |
| ابن ابن | Grandson |
| أخ شقيق | Full Brother |
| أخ لأب | Paternal Brother |
| ابن أخ شقيق | Full Brother's Son |
| عم شقيق | Full Paternal Uncle |
| ابن عم شقيق | Full Paternal Uncle's Son |

## Edge Cases

### Missing Person (المفقود)

```python
from mawarith.edge import calculate_with_missing

result = calculate_with_missing(heirs, "ابن", calculator_func)
# Returns two scenarios: heir alive vs dead
```

### Pregnancy (الحمل)

```python
from mawarith.edge import calculate_pregnancy_scenarios

result = calculate_pregnancy_scenarios(heirs, max_children=4, calculator_func)
# Returns all possible birth outcomes
```

### Successive Deaths (المناسخات)

```python
from mawarith.edge import calculate_munasakhaat

result = calculate_munasakhaat(
    first_decedent="أحمد",
    first_heirs=[...],
    successive_deaths=[{"heir_name": "ابن", "heirs": [...]}],
    calculator_func=calc_func,
)
```

## Madhab Differences

| Rule | Shafi'i | Hanafi | Maliki | Hanbali |
|------|---------|--------|--------|---------|
| GF with Siblings | Muqasama | Blocks | Muqasama | Muqasama |
| Mushtarakah | ✓ | ✗ | ✓ | ✗ |
| Missing Wait | 4 years | 90 years | 70 years | 4 years |

## Project Structure

```
mawarith/
├── __init__.py          # Main exports
├── case.py              # MiraathCase unified API
├── models/              # Data models
│   ├── heir.py          # Heir model
│   ├── share.py         # Share model
│   └── result.py        # MiraathResult
├── rules/               # Rule implementations
│   └── special/         # Classical special cases
│       ├── umariyyah.py
│       ├── mushtarakah.py
│       └── akdariyyah.py
├── edge/                # Edge case handlers
│   ├── missing.py       # Missing persons
│   ├── unborn.py        # Pregnancy
│   └── successive.py    # Successive deaths
├── madhab/              # School variations
│   └── registry.py      # MadhabRegistry
├── utils/               # Common utilities
└── scalc/               # Legacy calculator
```

## License

MIT License - See LICENSE file for details.

## References

- Quran: Surah An-Nisa (4:11-12, 176)
- Al-Sirajiyyah (السراجية) - Classical inheritance text
- Modern Fiqh manuals on inheritance (فقه المواريث)
