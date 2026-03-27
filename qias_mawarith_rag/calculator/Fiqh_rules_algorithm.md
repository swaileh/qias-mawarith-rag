# Islamic Inheritance (الميراث) - Fiqh Rules Algorithm

**Mawarith Calculator v2.0** | Accuracy: 99.25% (5856/5900)

## Overview

This document describes the complete algorithm for calculating Islamic inheritance shares according to the Quran, Sunnah, and scholarly consensus (إجماع).

**Implementation:** See `mawarith/scalc/` for the Python implementation.

---

## Calculation Pipeline

```
1. validate_input        →  Verify heir data integrity
2. derive_facts          →  Count heirs, identify categories
3. apply_disqualifications →  Remove murderers, non-Muslims, slaves
4. apply_hajb            →  Apply blocking rules (حجب حرمان/نقصان)
5. allocate_fard         →  Assign fixed shares (فروض)
6. apply_awl_if_needed   →  Scale down if shares exceed 1
7. allocate_asabah       →  Distribute remainder to residuaries
8. apply_radd_if_needed  →  Return excess to eligible heirs
9. finalize_tashih       →  Compute least common base
10. audit_trace          →  Record calculation steps
```

---

## 1. Heir Categories (أصناف الورثة)

### Primary Heirs (always inherit)
| Heir | Arabic | Gender | Category |
|------|--------|--------|----------|
| Husband | زوج | M | Spouse |
| Wife | زوجة | F | Spouse |
| Father | أب | M | Ascendant |
| Mother | أم | F | Ascendant |
| Son | ابن | M | Descendant |
| Daughter | بنت | F | Descendant |

### Secondary Heirs (may be blocked)
| Heir | Arabic | Blocked By |
|------|--------|------------|
| Grandfather | أب الأب | Father |
| Grandmother | أم الأم / أم الأب | Mother |
| Son's Son | ابن ابن | Son |
| Son's Daughter | بنت ابن | Son |
| Full Brother | أخ شقيق | Son, Son's Son, Father |
| Full Sister | أخت شقيقة | Son, Son's Son, Father |
| Paternal Brother | أخ لأب | + Full Brother |
| Paternal Sister | أخت لأب | + Full Brother, 2+ Full Sisters |
| Maternal Sibling | أخ لأم / أخت لأم | Descendant, Father, Grandfather |

---

## 2. Fixed Shares (الفروض المقدرة)

The Quran specifies six fixed fractions:

| Fraction | Arabic | Value |
|----------|--------|-------|
| 1/2 | النصف | 0.5 |
| 1/4 | الربع | 0.25 |
| 1/8 | الثمن | 0.125 |
| 2/3 | الثلثان | 0.667 |
| 1/3 | الثلث | 0.333 |
| 1/6 | السدس | 0.167 |

### Share Assignment Rules

#### Spouse Shares
```
IF has_descendants:
    Husband = 1/4
    Wife(s) = 1/8  (shared)
ELSE:
    Husband = 1/2
    Wife(s) = 1/4  (shared)
```

#### Mother's Share
```
IF has_descendants OR sibling_count >= 2:
    Mother = 1/6  (حجب نقصان)
ELSE IF spouse + father (الغراوين):
    Mother = 1/3 of remainder
ELSE:
    Mother = 1/3
```

#### Father's Share
```
IF has_male_descendants:
    Father = 1/6
ELSE IF has_female_descendants:
    Father = 1/6 + residuary
ELSE:
    Father = residuary (عصبة)
```

#### Daughter(s) Share
```
IF has_son:
    Daughters = residuary (2:1 with sons)
ELSE IF daughter_count == 1:
    Daughter = 1/2
ELSE:  # 2+ daughters
    Daughters = 2/3 (shared)
```

#### Son's Daughter(s) Share
```
IF has_son OR has_son's_son:
    Blocked (حجب)
ELSE IF daughter_count >= 2:
    Blocked (2/3 exhausted)
ELSE IF daughter_count == 1:
    Son's Daughters = 1/6 (تكملة الثلثين)
ELSE:
    Apply daughter rules
```

#### Full Sister(s) Share
```
IF has_full_brother:
    Residuary (عصبة بالغير, 2:1 ratio)
ELSE IF has_female_descendants:
    Residuary (عصبة مع الغير)
ELSE IF has_grandfather AND NOT has_paternal_siblings:
    Muqasama with grandfather
ELSE IF full_sister_count == 1:
    Full Sister = 1/2
ELSE:  # 2+ sisters
    Full Sisters = 2/3 (shared)
```

#### Paternal Sister(s) Share
```
IF has_full_brother OR has_paternal_brother:
    Residuary (2:1)
ELSE IF has_female_descendants:
    Residuary (عصبة مع الغير)
ELSE IF full_sister_count >= 2:
    Blocked (2/3 exhausted)
ELSE IF full_sister_count == 1:
    Paternal Sisters = 1/6 (completion)
ELSE:
    Apply full sister rules
```

#### Maternal Sibling(s) Share
```
IF has_descendants OR has_father OR has_grandfather:
    Blocked (حجب حرمان)
ELSE IF maternal_sibling_count == 1:
    Maternal Sibling = 1/6
ELSE:  # 2+
    Maternal Siblings = 1/3 (shared equally, M=F)
```

---

## 3. Grandfather with Siblings (الجد مع الإخوة)

### Best of Three Options (أحظ الثلاث)

When grandfather inherits with full/paternal siblings (no father):

```python
def grandfather_share(remainder, sibling_shares):
    # Option 1: Fixed 1/6 of estate
    opt1 = 1/6
    
    # Option 2: 1/3 of remainder after fixed shares
    opt2 = remainder * (1/3)
    
    # Option 3: Muqasama (sharing as sibling)
    # GF = 2 shares, males = 2, females = 1
    total_shares = sibling_shares + 2  # GF counts as 2
    opt3 = remainder * (2 / total_shares)
    
    return max(opt1, opt2, opt3)
```

### Special Cases
- **GF + Full Sisters + Paternal Siblings**: Full Sisters get their فرض first
- **GF + Female Descendants**: GF gets 1/6 + residuary (فرض + تعصيب)

---

## 4. Blocking Rules (الحجب)

### Complete Blocking (حجب الحرمان)

| Blocked Heir | Blocked By |
|--------------|------------|
| Grandfather | Father |
| Grandmother | Mother |
| All Grandmothers (level 3) | Any Grandmother (level 2) |
| Son's Son | Son |
| Son's Daughter | Son |
| Full Brother | Son, Son's Son, Father |
| Paternal Brother | + Full Brother |
| Paternal Sister | + 2 Full Sisters (unless has brother) |
| Maternal Siblings | Descendant, Father, Grandfather |
| Uncles | Father, Grandfather, Sons, Brothers |

### Partial Blocking (حجب النقصان)

| Affected Heir | Condition | Share Reduction |
|---------------|-----------|-----------------|
| Mother | 2+ siblings (even if blocked) | 1/3 → 1/6 |
| Husband | Has descendants | 1/2 → 1/4 |
| Wife | Has descendants | 1/4 → 1/8 |

---

## 5. Residuary Heirs (العصبات)

### Priority Order (by closeness to deceased)

```
1. عصبة بالنفس (By Self - Males)
   ابن → ابن ابن → أب → أب الأب → أخ شقيق → أخ لأب →
   ابن أخ شقيق → ابن أخ لأب → عم شقيق → عم لأب → ...

2. عصبة بالغير (With Another - Females with males)
   بنت مع ابن (2:1)
   أخت شقيقة مع أخ شقيق (2:1)
   أخت لأب مع أخ لأب (2:1)

3. عصبة مع الغير (By Another - Sisters with daughters)
   أخت شقيقة مع بنت
   أخت لأب مع بنت أو بنت ابن
```

### Distribution Formula
```python
def distribute_residuary(remainder, heirs):
    # Group by relation, then distribute 2:1 (male:female)
    total_shares = sum(h.count * (2 if h.is_male else 1) for h in heirs)
    for heir in heirs:
        weight = 2 if heir.is_male else 1
        heir.share = remainder * (heir.count * weight / total_shares)
```

---

## 6. Awl (العول) - Deficiency Adjustment

When sum of fixed shares > 1:

```python
def apply_awl(heirs, fard_sum):
    if fard_sum > 1:
        # Scale down all shares proportionally
        for heir in heirs:
            if heir.share_type == FARD:
                heir.share = heir.share / fard_sum
```

**Awl cases occur with base**: 6→7,8,9,10 | 12→13,15,17 | 24→27

---

## 7. Radd (الرد) - Excess Distribution

When sum of fixed shares < 1 and no residuary heirs:

```python
def apply_radd(heirs, fard_sum, remainder):
    # Exclude spouses from radd (Sunni view)
    eligible = [h for h in heirs if h.relation not in ['زوج', 'زوجة']]
    
    if eligible:
        # Distribute remainder proportionally
        eligible_sum = sum(h.share for h in eligible)
        for heir in eligible:
            heir.share += remainder * (heir.share / eligible_sum)
```

---

## 8. Tashih (التصحيح) - Base Calculation

Find the smallest integer base where all shares are whole numbers:

```python
def calculate_tashih(heirs):
    denominators = [h.share.denominator for h in heirs]
    base = lcm(*denominators)
    
    # Adjust for per-head distribution
    for heir in heirs:
        heir_shares = base * heir.share
        if heir_shares % heir.count != 0:
            base = lcm(base, heir.count)
    
    return base
```

---

## Special Cases (المسائل المشهورة)

### المسألة العمرية (Umariyyah)
- Heirs: Spouse + Mother + Father
- Mother gets 1/3 of **remainder** (not estate)

### المسألة الأكدرية (Akdariyyah)  
- Heirs: Husband + Mother + Grandfather + Full Sister
- Complex Awl + Muqasama interaction

### المسألة المشتركة (Mushtarakah)
- Heirs: Husband + Mother + Maternal Siblings + Full Siblings
- Full siblings share with maternal siblings in 1/3

---

## Algorithm Complexity

- **Time**: O(n²) for blocking, O(n log n) for Tashih LCM
- **Space**: O(n) for heir storage
- **Precision**: Exact rational arithmetic (no floating point)
