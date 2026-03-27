# Edge Cases in Islamic Inheritance (Mawarith) - v2.0

## Overview

This document describes the 12 classical edge cases in Islamic inheritance law and their implementation status in the Mawarith calculator.

---

## Edge Case Matrix

| # | Edge Case | Arabic | Status | Handler |
|---|-----------|--------|--------|---------|
| 1 | Successive Deaths | المناسخات | ✅ | `edge/successive.py` |
| 2 | Pregnancy/Fetus | الحمل | ✅ | `edge/unborn.py` |
| 3 | Missing Persons | المفقود | ✅ | `edge/missing.py` |
| 4 | Extended Kin | ذوي الأرحام | ⚠️ | Heirs registered, no fallback |
| 5 | Treasury Fallback | بيت المال | ❌ | Not implemented |
| 6 | Partial Blocking | حجب النقصان | ✅ | `scalc/blocking.py` |
| 7 | Classical Problems | المسائل المشهورة | ✅ | `rules/special/` |
| 8 | Grandfather+Siblings | الجد مع الإخوة | ✅ | `scalc/distribution.py` |
| 9 | Obligatory Bequest | الوصية الواجبة | ❌ | Not implemented |
| 10 | Multiple Spouses | تعدد الزوجات | ✅ | Sharing implemented |
| 11 | Lineage Nuances | أنواع الإخوة | ✅ | Full/paternal/maternal |
| 12 | Base Arithmetic | التأصيل والتصحيح | ✅ | LCM, Awl, Radd |

---

## Implemented Edge Cases

### 1. Successive Deaths (المناسخات)

**Handler:** `mawarith/edge/successive.py`

When an heir dies before estate distribution, their share is recalculated through their own heirs.

```python
from mawarith.edge import calculate_munasakhaat

result = calculate_munasakhaat(
    first_decedent_heirs=[...],
    second_decedent_heirs=[...],
    second_decedent_share=1/4
)
```

---

### 2. Pregnancy (الحمل)

**Handler:** `mawarith/edge/unborn.py`

Reserves the maximum potential share for an unborn heir (up to 4 children).

```python
from mawarith.edge import calculate_pregnancy_scenarios

scenarios = calculate_pregnancy_scenarios(
    known_heirs=[{"heir": "زوجة", "count": 1}],
    unborn_relationship="ابن"  # Expected relation to deceased
)
```

---

### 3. Missing Persons (المفقود)

**Handler:** `mawarith/edge/missing.py`

Calculates two scenarios (alive vs. deceased) and distributes the safer share.

```python
from mawarith.edge import identify_missing_heirs

result = identify_missing_heirs(
    heirs=[...],
    missing_heir_type="ابن"
)
```

---

### 4. Classical Problems (المسائل المشهورة)

**Handlers:** `mawarith/rules/special/`

#### 4.1 Umariyyatayn (العمرية)
- **Condition:** Husband/Wife + Mother + Father only
- **Rule:** Mother gets 1/3 of remainder, not 1/3 of estate
- **Handler:** `rules/special/umariyyah.py`

#### 4.2 Mushtarakah (المشتركة)
- **Condition:** Husband + Mother + 2+ Maternal siblings + Full siblings
- **Rule:** Full siblings share with maternal siblings (Shafi'i/Maliki only)
- **Handler:** `rules/special/mushtarakah.py`

#### 4.3 Akdariyyah (الأكدرية)
- **Condition:** Husband + Mother + Grandfather + Full Sister
- **Rule:** Complex Awl and Muqasama
- **Handler:** `rules/special/akdariyyah.py`

---

### 5. Grandfather with Siblings (الجد مع الإخوة)

**Handler:** `mawarith/scalc/distribution.py`

Implements the "Best of 3" or "Best of 2" optimization:

**With female descendants:**
- 1/6 of estate
- 1/3 of remainder
- Muqasama (sharing as brother)

**Without female descendants:**
- 1/3 of estate
- Muqasama

---

## Not Yet Implemented

### Treasury Fallback (بيت المال)
When no heirs exist, estate goes to Islamic treasury.

### Obligatory Bequest (الوصية الواجبة)
Orphaned grandchildren receive their parent's share (some jurisdictions).

### Extended Kin Priority (ذوي الأرحام)
Full fallback logic for distant relatives when no standard heirs exist.

---

## Madhab Variations

Different schools have different rules for edge cases:

| Edge Case | Hanafi | Maliki | Shafi'i | Hanbali |
|-----------|--------|--------|---------|---------|
| GF blocks siblings | ✅ | ❌ | ❌ | ❌ |
| Mushtarakah applies | ❌ | ✅ | ✅ | ❌ |
| Missing wait (years) | 90 | 70 | 4 | 4 |

See `mawarith/madhab/registry.py` for full madhab configuration.