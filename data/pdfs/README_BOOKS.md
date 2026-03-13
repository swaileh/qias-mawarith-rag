# Arabic Islamic Inheritance Books for QIAS RAG System

## Summary

This directory contains Arabic PDF books on Islamic inheritance (Al-Mawarith/المواريث) downloaded to enhance the QIAS RAG training set knowledge base.

## Training Set Analysis

The QIAS 2026 training set contains Islamic inheritance problems with the following characteristics:

### Categories Found:
- **simple** - Standard inheritance cases
- **awl** - Cases involving 'awl (increase of shares beyond base)
- **radd** - Cases involving radd (return of excess)

### Topics Covered:
- Heir determination (الورثة)
- Blocked heirs (المحجوبون)
- Share fractions (الفروض)
- Awl/Radd cases (العول والرد)
- Tasil calculations (التصحيح)
- 'Asaba (residuaries) and inheritance by representation

### Weaknesses Identified:
Based on the analysis notebook, potential areas needing enhancement include:
- More coverage of rare/complex Awl cases
- Additional Radd scenario documentation
- Diverse calculation methods (tasil)
- Coverage of different madhab approaches
- Complex multi-heir scenarios

## Downloaded Books

### 1. 02_as_sirajiyyah_fil_mirath_english.pdf
- **Title**: As-Sirajiyyah fil Mirath (English)
- **Size**: 2.4 MB
- **Description**: Classical Hanafi text on inheritance with English translation
- **Source**: Pre-existing in collection

### 2. 03_islamic_law_of_inheritance_arifi.pdf
- **Title**: Islamic Law of Inheritance (Arifi)
- **Size**: 2.0 MB
- **Description**: Comprehensive guide on Islamic inheritance laws
- **Source**: Pre-existing in collection

### 3. 03_matn_ar_rahabiyyah.pdf
- **Title**: Matn ar-Rahabiyyah (متن الرحبية)
- **Author**: Muhammad ibn Ali ar-Rahbi (محمد بن علي الرحبي) - d. 577 AH
- **Size**: 222 KB
- **Description**: Classical Shafi'i text on inheritance in poetic form (176 verses on Bahr ar-Rajaz)
- **Covers**: Causes of inheritance, barriers to inheritance, male/female heirs, prescribed shares, residuaries
- **Source**: https://arabicpdfs.com
- **Download Date**: 2026-03-06

### 4. 04_sharh_al_sirajiyyah.pdf
- **Title**: Sharh al-Sirajiyyah (شرح السراجية)
- **Author**: As-Sayyid ash-Sharif al-Jurjani (السيد الشريف الجرجاني)
- **Size**: 10.3 MB (252 pages)
- **Description**: Comprehensive commentary on the classical Hanafi text As-Sirajiyyah
- **Source**: Archive.org
- **Download Date**: 2026-03-06

### 5. 07_mukhtasar_al_wasit.pdf
- **Title**: Mukhtasar al-Wasit fil Fara'id (مختصر الوسيط في الفرائض)
- **Author**: Ali ibn Nashib as-Sharahili (علي بن ناشب الشراحيلي)
- **Size**: 502 KB (54 pages)
- **Description**: Summary text on inheritance according to Maliki madhab
- **Source**: ArabicPDFs.com
- **Download Date**: 2026-03-06

## Additional Recommended Books (Not Yet Downloaded)

The following books were identified but not successfully downloaded:

1. **Al-Mawarith fi ash-Shari'a al-Islamiyya** (المواريث في الشريعة الإسلامية)
   - Author: Muhammad Ali as-Sabuni
   - Size: 3.9 MB, 220 pages
   - Source: alarabimag.com

2. **Talkhis Fiqh al-Fara'id** (تلخيص فقه الفرائض)
   - Author: Muhammad ibn Salih al-Uthaymeen
   - Source: Archive.org

3. **Al-Fawa'id fi Tahsil Masa'il al-Fara'id** (الفوائد في تسهيل مسائل الفرائض)
   - Author: Fayiz Ahmad al-Ghamdi
   - Size: 11.4 MB
   - Source: ebook.univeyes.com

4. **Manh al-Jalil** (منح الجليل)
   - Author: Muhammad ibn Ahmad Aleesh
   - Description: Commentary on Mukhtasar al-Allamah Khalil (Maliki fiqh)
   - Size: 370 MB
   - Source: ebook.univeyes.com

5. **Taysir al-Fara'id** (تيسير الفرائض)
   - Author: Muhammad ibn Salih al-Uthaymeen
   - Source: ebook.univeyes.com

## How to Use These Books

These books should be processed by the RAG pipeline to:
1. Extract text for the knowledge base
2. Create embeddings for semantic search
3. Enhance retrieval for complex inheritance cases
4. Provide authoritative references for the model

## Notes

- All downloaded books are in Arabic (restricted to Arabic as requested)
- Books cover multiple madhabs (Hanafi, Shafi'i, Maliki)
- Mix of classical texts (matn) and commentaries (sharh)
- Various difficulty levels suitable for different training scenarios

## Download Date
March 6, 2026
