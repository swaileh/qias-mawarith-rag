#!/usr/bin/env python3
"""
Solution for handling corrupted PDF text extraction
"""

def is_text_corrupted(text):
    """Check if extracted text is corrupted"""
    if not text or len(text.strip()) < 10:
        return True

    # Count corrupted indicators
    cid_count = text.count('(cid:')
    total_chars = len(text)

    # If more than 5% of text is CID references, consider it corrupted
    if cid_count > 0 and (cid_count * 20) > total_chars:
        return True

    # Check for excessive special characters
    special_chars = 0
    for c in text:
        if not ('\u0600' <= c <= '\u06FF' or  # Arabic range
               '\u0020' <= c <= '\u007E' or  # Basic ASCII
               c in '\u2000-\u206F'):        # General punctuation
            special_chars += 1

    if special_chars > len(text) * 0.2:  # More than 20% special chars
        return True

    return False

def clean_extracted_text(text):
    """Clean extracted text by removing corruption indicators"""
    if not text:
        return ""

    import re
    # Remove CID references
    text = re.sub(r'\(cid:\d+\)', '', text)

    # Remove other common PDF artifacts
    text = re.sub(r'\(obj\)', '', text)
    text = re.sub(r'\(endobj\)', '', text)
    text = re.sub(r'\[.*?\]', '', text)

    # Keep only Arabic characters, basic ASCII, and common punctuation
    cleaned = []
    for char in text:
        # Keep Arabic characters and basic ASCII
        if ('\u0600' <= char <= '\u06FF' or  # Arabic
            '\u0020' <= char <= '\u007E'):  # Basic ASCII
            cleaned.append(char)

    return ''.join(cleaned).strip()

# Test the solution
print("SOLUTION: Handling Corrupted PDF Text Extraction")
print("=" * 60)

# The corrupted text you showed
corrupted_text = "م%`(cid:31)أ Kﺙ3ﺙ K-(cid:9)((cid:14)(cid:6) ــ ج Ž(cid:17);(cid:6)%(cid:24) K-(cid:9)((cid:6)%(cid:24) ص%ﺥ اHهو ل%(cid:30)(cid:6)ا ](cid:3)(cid:30)ﺝ Hﺥأ 7F;(cid:12) د(cid:8)(cid:17)&ا '(cid:12) نأ ـ١"

print("1. DETECTING CORRUPTED TEXT:")
print(f"   - Contains {corrupted_text.count('(cid:')} CID references")
print(f"   - Total length: {len(corrupted_text)} characters")
print(f"   - Is corrupted: {is_text_corrupted(corrupted_text)}")
print()

print("2. CLEANING THE TEXT:")
cleaned = clean_extracted_text(corrupted_text)
print(f"   - Original: {len(corrupted_text)} characters")
print(f"   - Cleaned: {len(cleaned)} characters")
print(f"   - Still corrupted: {is_text_corrupted(cleaned)}")
print()

print("3. WHAT HAPPENS IN THE NOTEBOOK:")
print("   - PDF extraction detects corrupted text")
print("   - Text gets cleaned automatically")
print("   - Corrupted chunks get warning flags")
print("   - Sanity check shows warnings for corrupted content")
print("   - RAG continues with available clean chunks")
print()

print("4. EXPECTED SANITY CHECK OUTPUT:")
print("   [CONTEXT] PDF SOURCE - RETRIEVED CONTEXT:")
print("     Document 1: filename.pdf (Score: 0.850)")
print("     ⚠️  Text appears corrupted (CID references detected)")
print("     Clean preview: [readable Arabic text if any]...")
print()

print("5. RECOMMENDATIONS:")
print("   - Use PDFs with selectable text (not scanned images)")
print("   - pdfplumber works better than PyPDF2 for Arabic")
print("   - The notebook handles corruption gracefully")
print("   - Focus on PDFs that extract clean Arabic text")