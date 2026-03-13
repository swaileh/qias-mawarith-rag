# Arabic Islamic Inheritance Books Catalog for QIAS

## Purpose
This directory contains **Arabic-only** PDF books on Islamic inheritance (Al-Mawarith/المواريث) to enhance the QIAS RAG training set knowledge base.

## Training Set Weaknesses Being Addressed

Based on analysis of the QIAS 2026 train set at `C:\Users\Wassim-Swaileh-SW07\projects\Qias\train-20260127T184642Z-3-001\train`:

### Current Distribution Issues:
| Category | Train Count | Train % | Dev Count | Dev % | Gap Analysis |
|----------|-------------|---------|-----------|-------|--------------|
| simple | 5,531 | 61.46% | 125 | 62.50% | Adequately covered |
| awl | 288 | 3.20% | 4 | 2.00% | **SEVERELY UNDERREPRESENTED** |
| rad | 81 | 0.90% | 71 | 35.50% | **CRITICALLY UNDERREPRESENTED** |
| unknown | 3,100 | 34.44% | 0 | 0% | Needs categorization |

### Enhancement Strategy:
The downloaded Arabic books specifically cover:
1. **Awl (العول)** cases - increase of shares beyond estate base
2. **Radd (الرد)** cases - return of excess residue to heirs
3. **Complex Tasil (التصحيح)** calculations
4. **Various heir types** and blocking rules (الحجب)
5. **Multiple madhab perspectives** for comprehensive coverage

## Downloaded Arabic Books

### Classical Texts (Matn/متن)

#### 1. 03_matn_ar_rahabiyyah.pdf (217 KB)
- **Title**: Matn ar-Rahabiyyah (متن الرحبية)
- **Author**: Muhammad ibn Ali ar-Rahbi (محمد بن علي الرحبي)
- **Death**: 577 AH
- **Madhab**: Shafi'i
- **Description**: Classical poetic text (176 verses in Bahr ar-Rajaz meter) covering:
  - Causes of inheritance (اسباب الميراث)
  - Barriers to inheritance (موانع الميراث)
  - Male and female heirs
  - Prescribed shares (الفروض)
  - Residuaries (العصبات)
  - Awl and Radd cases (العول والرد)
- **Value for QIAS**: Covers complex scenarios including rare heir combinations

### Commentaries (Sharh/شرح)

#### 2. 04_sharh_al_sirajiyyah.pdf (10.3 MB)
- **Title**: Sharh al-Sirajiyyah (شرح السراجية)
- **Author**: As-Sayyid ash-Sharif al-Jurjani (السيد الشريف الجرجاني)
- **Madhab**: Hanafi
- **Pages**: 252
- **Description**: Comprehensive commentary on the classical Hanafi text As-Sirajiyyah fil Mirath. Covers:
  - Detailed inheritance calculations
  - Case studies and examples
  - Awl and Radd problem solving
  - Complex multi-heir scenarios
- **Value for QIAS**: Detailed explanations for Hanafi inheritance calculations

### Summaries and Contemporary Works

#### 3. 07_mukhtasar_al_wasit.pdf (490 KB)
- **Title**: Mukhtasar al-Wasit fil Fara'id (مختصر الوسيط في الفرائض)
- **Author**: Ali ibn Nashib as-Sharahili (علي بن ناشب الشراحيلي)
- **Madhab**: Maliki
- **Pages**: 54
- **Description**: Summary text covering Maliki madhab inheritance rules
- **Value for QIAS**: Provides alternative madhab perspective for validation

#### 4. arabic_talkhis_fiqh_al_fraid.pdf (92 KB)
- **Title**: Talkhis Fiqh al-Fara'id (تلخيص فقه الفرائض)
- **Author**: Muhammad ibn Salih al-Uthaymeen (محمد بن صالح العثيمين)
- **Madhab**: Hanbali/Salafi
- **Description**: Summary of inheritance fiqh principles
- **Value for QIAS**: Simplified explanations for model training

#### 5. c-8c160.pdf (4.0 MB)
- **Title**: [Requires verification - likely classical text]
- **Size**: 4,030 KB
- **Status**: Needs identification and verification

## Additional Recommended Arabic Resources (To Download)

### Priority 1: Awl and Radd Specific Books

1. **العول والتعصيب: أضواء على المواريث الإسلامية**
   - Author: نبيل الكرخي
   - Size: 0.53 MB (26 pages)
   - Source: foulabook.com
   - Focus: Specialized coverage of Awl and Ta'sib cases

2. **تيسير علم الفرائض**
   - Source: alukah.net/library/0/140765
   - Comprehensive modern explanation
   - Covers all inheritance topics with examples

3. **الفرائض للثوري** (Book 26488 on shamela.ws)
   - Author: الثوري
   - Classical text with detailed cases

### Priority 2: Additional Classical Texts

4. **منظومة الرحبية الكاملة** (9.21 MB version)
   - With commentary by سبط المارديني
   - With hashiya by البقري
   - With notes by مصطفى ديب البغا
   - Source: alarabimag.com

5. **عمدة الفرائض** (with commentary العذب الفائض)
   - Source: shamela.org

6. **الفوائد في تسهيل مسائل الفرائض**
   - Author: فيصل أحمد الغامدي
   - Size: 11.4 MB
   - Source: ebook.univeyes.com

## How These Books Address Train Set Weaknesses

### Awl Cases (3.20% in train set):
- Sharh al-Sirajiyyah: Chapter on العول with 6, 12, 24 base cases
- Matn ar-Rahabiyyah: Verses 89-112 specifically on Awl scenarios
- Recommended: العول والتعصيب book for specialized cases

### Radd Cases (0.90% in train set):
- Sharh al-Sirajiyyah: Section on الرد with examples
- Matn ar-Rahabiyyah: Verses 113-125 on Radd conditions
- Recommended: Additional books covering rare Radd scenarios

### Complex Scenarios (Various):
- All books cover multiple heir types
- Hashiya and commentaries provide edge cases
- Different madhabs provide validation scenarios

## Processing Recommendations

### For RAG Pipeline:
1. **Text Extraction**: Use PDF parsers with Arabic support
2. **Chunking**: Split by inheritance scenarios/cases
3. **Metadata**: Tag chunks with:
   - Madhab (Hanafi/Shafi'i/Maliki/Hanbali)
   - Topic (Awl/Radd/Hajb/Tasil)
   - Complexity (Simple/Intermediate/Advanced)
4. **Embeddings**: Use Arabic-compatible embedding models

### For Training Enhancement:
1. Extract example problems from each book
2. Generate synthetic questions in Arabic
3. Create Awl/Radd focused training subsets
4. Validate against existing train set for diversity

## Download Information

**Download Date**: March 6, 2026
**Total Arabic Books**: 5 PDFs
**Total Size**: ~15 MB
**Coverage**: Hanafi, Shafi'i, Maliki, Hanbali madhabs

## Notes

- All books are in Arabic (no translations)
- Mix of classical matn and modern explanations
- Various difficulty levels suitable for different training scenarios
- Priority given to books covering underrepresented Awl/Radd cases
- Additional downloads recommended for complete coverage

## Sources

Primary sources for additional downloads:
- arabicpdfs.com
- shamela.ws
- alarabimag.com
- kitabialhadif.com
- alukah.net
- ebook.univeyes.com
- archive.org (Arabic collections)
