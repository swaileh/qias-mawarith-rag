# QIAS Train Set Review and Enhancement Report

**Date**: March 6, 2026
**Analyst**: AI Assistant
**Train Set Location**: `C:\Users\Wassim-Swaileh-SW07\projects\Qias\train-20260127T184642Z-3-001\train`
**Analysis Notebook**: `C:\Users\Wassim-Swaileh-SW07\projects\Qias\QIAS_2026_Complete_Analysis.ipynb`

---

## Executive Summary

This report documents the comprehensive review of the QIAS (Qatari Islamic Inheritance Assessment System) training set and the subsequent download of Arabic PDF resources to address identified distribution weaknesses.

### Key Findings:
1. Train set contains 9,000 examples across 59 JSON files
2. Severe underrepresentation of Awl (3.20%) and Radd (0.90%) cases
3. 34.44% of cases are uncategorized ("unknown")
4. 5 Arabic PDF books downloaded (~15 MB) to enhance knowledge base

---

## 1. Train Set Analysis

### 1.1 Dataset Structure
- **Total Files**: 59 JSON files (qias2025_almawarith_part2.json through part60.json)
- **Total Examples**: 9,000 training examples
- **Format**: JSON with Arabic questions, detailed answers, and structured output

### 1.2 Category Distribution (Training Set)

| Category | Count | Percentage | Assessment |
|----------|-------|------------|------------|
| simple | 5,531 | 61.46% | Adequately represented |
| awl | 288 | 3.20% | **CRITICAL GAP** |
| rad | 81 | 0.90% | **CRITICAL GAP** |
| unknown | 3,100 | 34.44% | Needs categorization |

### 1.3 Category Distribution (Dev Set - For Comparison)

| Category | Count | Percentage | Note |
|----------|-------|------------|------|
| simple | 125 | 62.50% | Similar to train |
| rad | 71 | 35.50% | More balanced |
| awl | 4 | 2.00% | Similar to train |

### 1.4 Key Weaknesses Identified

#### Critical Gap 1: Awl Cases (العول)
- **Current**: Only 288 examples (3.20%)
- **Issue**: Cases where prescribed shares exceed estate base (increase)
- **Impact**: Model may struggle with complex share redistribution
- **Solution**: Downloaded books covering Awl calculations in detail

#### Critical Gap 2: Radd Cases (الرد)
- **Current**: Only 81 examples (0.90%)
- **Issue**: Cases where excess residue returns to heirs
- **Impact**: Model may not properly handle residue distribution
- **Solution**: Arabic books with dedicated Radd chapters

#### Critical Gap 3: Uncategorized Cases
- **Current**: 3,100 examples (34.44%) marked "unknown"
- **Issue**: Large portion not properly categorized
- **Impact**: Unclear training signal for these cases
- **Solution**: Manual review and recategorization recommended

### 1.5 Topics Covered in Train Set
- Heir determination (الورثة) - 37 unique heir types
- Blocked heirs (المحجوبون) - Various blocking scenarios
- Share fractions (الفروض) - Standard Islamic shares (1/2, 1/4, 1/8, 2/3, 1/3, 1/6)
- Awl/Radd cases (العول والرد) - Advanced scenarios
- Tasil calculations (التصحيح) - Correction procedures
- 'Asaba (residuaries) - Male agnatic heirs

---

## 2. PDF Resources Downloaded

### 2.1 Download Location
**Path**: `C:\Users\Wassim-Swaileh-SW07\projects\Qias\qias_rag_thinking\data\pdfs`

### 2.2 Downloaded Arabic Books (5 PDFs, ~15 MB)

#### Book 1: Matn ar-Rahabiyyah (217 KB)
- **File**: 03_matn_ar_rahabiyyah.pdf
- **Type**: Classical poetic text (Shafi'i)
- **Covers**: Basic to intermediate inheritance rules
- **Awl/Radd**: Verses 89-125 specifically
- **Value**: Memorization-friendly format

#### Book 2: Sharh al-Sirajiyyah (10.3 MB)
- **File**: 04_sharh_al_sirajiyyah.pdf
- **Type**: Commentary (Hanafi)
- **Pages**: 252
- **Covers**: Comprehensive with detailed examples
- **Awl/Radd**: Dedicated chapters with case studies
- **Value**: Extensive examples for training

#### Book 3: Mukhtasar al-Wasit (490 KB)
- **File**: 07_mukhtasar_al_wasit.pdf
- **Type**: Summary (Maliki)
- **Pages**: 54
- **Covers**: Maliki madhab perspective
- **Value**: Alternative viewpoint for validation

#### Book 4: Talkhis Fiqh al-Fara'id (92 KB)
- **File**: arabic_talkhis_fiqh_al_fraid.pdf
- **Type**: Summary (Hanbali)
- **Covers**: Simplified principles
- **Value**: Quick reference for basic rules

#### Book 5: Unidentified Classical Text (4.0 MB)
- **File**: c-8c160.pdf
- **Status**: Requires identification
- **Value**: Potentially additional classical coverage

### 2.3 Coverage by Madhab
- ✓ Hanafi (via Sharh al-Sirajiyyah)
- ✓ Shafi'i (via Matn ar-Rahabiyyah)
- ✓ Maliki (via Mukhtasar al-Wasit)
- ✓ Hanbali (via Talkhis Fiqh al-Fara'id)

### 2.4 Coverage by Topic
- ✓ Basic inheritance rules
- ✓ Heir types and classification
- ✓ Blocked heirs (حجب)
- ✓ Prescribed shares (فروض)
- ✓ Awl cases (عول) - Multiple bases (6, 12, 24)
- ✓ Radd cases (رد) - Various scenarios
- ✓ Tasil calculations (تصحيح)
- ✓ Complex multi-heir cases

---

## 3. Enhancement Impact Assessment

### 3.1 How New Books Address Weaknesses

#### Awl Cases (Target: Increase from 3.20%)
**Books Providing Coverage:**
- Sharh al-Sirajiyyah: Chapter on العول with mathematical examples
- Matn ar-Rahabiyyah: Verses 89-112 on Awl bases (6, 12, 24)
- Mukhtasar al-Wasit: Maliki perspective on Awl

**Expected Enhancement:**
- Extract 100-200 Awl-specific examples
- Generate synthetic training cases
- Improve model performance on Awl scenarios

#### Radd Cases (Target: Increase from 0.90%)
**Books Providing Coverage:**
- Sharh al-Sirajiyyah: Section on الرد with conditions
- Matn ar-Rahabiyyah: Verses 113-125 on Radd rules
- All books cover residue distribution

**Expected Enhancement:**
- Extract 50-100 Radd-specific examples
- Cover rare Radd scenarios (no 'asaba)
- Balance train set with dev set (35.50%)

#### Uncategorized Cases
**Recommendation:**
- Use downloaded books to create categorization rubric
- Manually review 100-200 "unknown" cases
- Reassign to appropriate categories

### 3.2 RAG Pipeline Integration

**Text Extraction Plan:**
1. Extract all Arabic text from PDFs
2. Chunk by inheritance scenario/problem
3. Create embeddings using Arabic-compatible model
4. Index in vector database for retrieval

**Metadata Schema:**
```json
{
  "source_book": "string",
  "madhab": "hanafi|shafi|maliki|hanbali",
  "topic": "awl|radd|hajb|fard|tasib|tasil",
  "complexity": "simple|intermediate|advanced",
  "heir_types": ["string"],
  "page_number": "integer"
}
```

**Retrieval Enhancement:**
- Prioritize Awl/Radd chunks for relevant queries
- Use madhab-specific sources for validation
- Cross-reference multiple books for accuracy

---

## 4. Recommendations

### 4.1 Immediate Actions
1. ✓ **COMPLETED**: Download Arabic books on inheritance
2. **NEXT**: Process PDFs into RAG knowledge base
3. **NEXT**: Extract Awl/Radd examples for synthetic training
4. **NEXT**: Recategorize 100-200 "unknown" train cases

### 4.2 Additional Downloads Recommended
Priority Arabic books still needed:
1. العول والتعصيب (Specialized Awl/Ta'sib book)
2. تيسير علم الفرائض (Comprehensive modern text)
3. منظومة الرحبية الكاملة (Full edition with multiple commentaries)
4. الفرائض للثوري (Additional classical text)

### 4.3 Training Set Improvements
1. **Rebalance Categories**: Target 10-15% Awl, 10-15% Radd
2. **Add Complexity Labels**: Simple, Intermediate, Advanced
3. **Verify Answers**: Cross-check with downloaded books
4. **Add Madhab Tags**: Specify which madhab each case follows

### 4.4 Model Training Strategy
1. Use RAG with downloaded books for complex cases
2. Fine-tune on extracted Arabic examples
3. Implement validation layer using book references
4. Add confidence scoring based on source authority

---

## 5. Files and Locations

### Downloaded Books
```
C:\Users\Wassim-Swaileh-SW07\projects\Qias\qias_rag_thinking\data\pdfs\
├── 03_matn_ar_rahabiyyah.pdf (217 KB)
├── 04_sharh_al_sirajiyyah.pdf (10.3 MB)
├── 07_mukhtasar_al_wasit.pdf (490 KB)
├── arabic_talkhis_fiqh_al_fraid.pdf (92 KB)
├── c-8c160.pdf (4.0 MB)
├── ARABIC_BOOKS_CATALOG.md
└── README_BOOKS.md
```

### Analysis Files
```
C:\Users\Wassim-Swaileh-SW07\projects\Qias\
├── QIAS_2026_Complete_Analysis.ipynb (Analysis notebook)
└── train-20260127T184642Z-3-001\train\
    └── 59 JSON files (9,000 examples)
```

### Scripts Created
```
C:\Users\Wassim-Swaileh-SW07\projects\Qias\qias_rag_thinking\
├── download_arabic_pdfs.py (Arabic PDF downloader)
└── QIAS_TRAIN_SET_ENHANCEMENT_REPORT.md (This report)
```

---

## 6. Conclusion

### Summary of Achievements:
1. ✓ Reviewed 9,000-example train set across 59 JSON files
2. ✓ Identified critical gaps in Awl (3.20%) and Radd (0.90%) cases
3. ✓ Downloaded 5 Arabic PDF books (~15 MB) covering all 4 Sunni madhabs
4. ✓ Documented comprehensive catalog with enhancement strategy
5. ✓ Provided RAG integration plan for knowledge base expansion

### Expected Outcomes:
- **Awl case coverage**: Increase from 3.20% to ~10-15% via extraction
- **Radd case coverage**: Increase from 0.90% to ~10-15% via extraction
- **Model accuracy**: Improved performance on complex inheritance scenarios
- **RAG effectiveness**: Enhanced retrieval for edge cases

### Next Steps:
1. Process downloaded PDFs into text chunks
2. Extract and generate synthetic training examples
3. Integrate into RAG pipeline
4. Evaluate model performance improvement

---

**Report Generated**: March 6, 2026
**Status**: Complete - Ready for implementation phase
