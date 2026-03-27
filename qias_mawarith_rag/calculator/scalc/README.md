# Mawarith Symbolic Calculator (scalc)

A Python symbolic calculator for Islamic Inheritance (علم المواريث / الفرائض) based on Fiqh rules.

## Features

- ✅ **Complete Heir Recognition** - 30+ heir types with Arabic names
- ✅ **Blocking Rules (الحجب)** - Full implementation of حجب حرمان and حجب نقصان
- ✅ **Share Calculation** - All Quranic shares (1/2, 1/4, 1/8, 2/3, 1/3, 1/6)
- ✅ **Tasil (تأصيل)** - Finding the base/common denominator
- ✅ **Tashih (تصحيح)** - Correction for whole number distribution
- ✅ **Awl (العول)** - Handling share deficiency
- ✅ **Radd (الرد)** - Returning excess to eligible heirs
- ✅ **Residuary Distribution (العصبات)** - With proper 2:1 male:female ratio
- ✅ **Special Cases** - العمريتان (Umariyyatan) support

## Installation

No external dependencies required. Just add to your Python path:

```python
import sys
sys.path.insert(0, '/path/to/Qias2026')

from mawarith.scalc import InheritanceCalculator
```

## Quick Start

```python
from mawarith.scalc import InheritanceCalculator

calc = InheritanceCalculator()

# Example: Deceased left wife, 1 son, and 1 daughter
result = calc.calculate([
    {"heir": "زوجة", "count": 1},
    {"heir": "ابن", "count": 1},
    {"heir": "بنت", "count": 1},
])

print(result.to_dict())
```

**Output:**
```
زوجة: 12.5%  (1/8 - wife's share with descendants)
ابن: 50.0%   (residuary, 2:1 ratio with daughter)
بنت: 25.0%   (residuary, 2:1 ratio with son)
```

## API Reference

### `InheritanceCalculator`

Main calculator class.

#### Methods

- **`calculate(heirs)`** - Calculate inheritance from a list of heir dicts
- **`calculate_from_question(question)`** - Parse Arabic natural language question

#### Input Format

```python
heirs = [
    {"heir": "heir_name_in_arabic", "count": number_of_heirs},
    ...
]
```

### `InheritanceResult`

Result dataclass with attributes:
- `heirs` - List of active heirs
- `blocked` - List of blocked heirs (محجوبون)
- `shares` - Share fractions before distribution
- `tasil_stage` - Distribution with أصل المسألة
- `awl_or_radd` - "عول", "رد", or "لا"
- `post_tasil` - Final per-head shares with percentages

## Supported Heir Types

### Descendants (الفروع)
- ابن (Son)
- بنت (Daughter)
- ابن ابن (Son's Son)
- بنت ابن (Son's Daughter)
- ابن ابن ابن (Son's Son's Son)
- بنت ابن ابن (Son's Son's Daughter)

### Ascendants (الأصول)
- أب (Father)
- أم (Mother)
- جد / أب الأب (Grandfather)
- أب أب الأب (Great Grandfather)
- جدة / أم الأم / أم الأب (Grandmothers)

### Spouses (الزوجية)
- زوج (Husband)
- زوجة (Wife)

### Siblings (الإخوة)
- أخ شقيق (Full Brother)
- أخت شقيقة (Full Sister)
- أخ لأب (Paternal Brother)
- أخت لأب (Paternal Sister)
- أخ لأم (Maternal Brother)
- أخت لأم (Maternal Sister)

### Uncles & Cousins (الأعمام وأبناؤهم)
- عم شقيق (Full Uncle)
- عم لأب (Paternal Uncle)
- ابن عم شقيق (Full Uncle's Son)
- And more...

## Example Calculations

### Example 1: العمريتان (Umariyyatan)
```python
result = calc.calculate([
    {"heir": "زوج", "count": 1},
    {"heir": "أب", "count": 1},
    {"heir": "أم", "count": 1},
])
# زوج: 50%, أب: 33.33%, أم: 16.67%
```

### Example 2: Complex Blocking
```python
result = calc.calculate([
    {"heir": "بنت", "count": 2},
    {"heir": "أخت شقيقة", "count": 1},
    {"heir": "عم شقيق", "count": 2},
    {"heir": "أخ لأم", "count": 1},
])
# Active: بنت (2), أخت شقيقة (1)
# Blocked: عم شقيق (2) - by sister as عصبة مع الغير
#          أخ لأم (1) - by descendant
```

## Running Tests

```bash
cd /path/to/Qias2026
python -m mawarith.scalc.test_calculator
```

## Architecture

```
mawarith/scalc/
├── __init__.py       # Package exports
├── shares.py         # Fraction arithmetic
├── heirs.py          # Heir types registry
├── blocking.py       # Blocking rules (الحجب)
├── rules.py          # Share calculation logic
├── calculator.py     # Main calculator
└── test_calculator.py # Test suite
```

## License

MIT License
