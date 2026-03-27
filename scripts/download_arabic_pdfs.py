"""
Script to download ARABIC ONLY Islamic inheritance (Al-Mawarith) PDF resources
for enhancing the QIAS train set distribution weaknesses in:
- Awl (العول) cases - only 3.20% in train set
- Radd (الرد) cases - only 0.90% in train set
- Complex inheritance scenarios
"""

import requests
from pathlib import Path
import time

# ARABIC PDF URLs to download - focused on Awl/Radd and complex cases
ARABIC_PDF_RESOURCES = [
    {
        "url": "https://archive.org/download/ sharh_al_sirajiyyah/sharh_al_sirajiyyah.pdf",
        "filename": "01_sharh_al_sirajiyyah_hanafi.pdf",
        "description": "شرح السراجية - Hanafi Inheritance Law (Arabic)"
    },
    {
        "url": "https://archive.org/download/matn_ar_rahabiyyah/matn_ar_rahabiyyah.pdf",
        "filename": "02_matn_ar_rahabiyyah_shafii.pdf",
        "description": "متن الرحبية - Shafi'i Inheritance Law (Arabic)"
    },
    {
        "url": "https://archive.org/download/al_faraed_fil_mirath/al_faraed_fil_mirath.pdf",
        "filename": "03_al_faraed_fil_mirath_classic.pdf",
        "description": "الفرائض في الميراث - Classical Arabic Text"
    },
    {
        "url": "https://archive.org/download/mukhtasar_al_wasit_faraed/mukhtasar_al_wasit.pdf",
        "filename": "04_mukhtasar_al_wasit_maliki.pdf",
        "description": "مختصر الوسيط في الفرائض - Maliki Inheritance (Arabic)"
    },
    {
        "url": "https://archive.org/download/talkhis_fiqh_faraed/talkhis_fiqh_faraed.pdf",
        "filename": "05_talkhis_fiqh_faraed_uthaymeen.pdf",
        "description": "تلخيص فقه الفرائض - Ibn Uthaymeen (Arabic)"
    },
    {
        "url": "https://archive.org/download/awl_radd_mirath/awl_radd_mirath.pdf",
        "filename": "06_awl_radd_cases_specialized.pdf",
        "description": "العول والرد في المواريث - Specialized Awl/Radd (Arabic)"
    }
]

# Alternative sources for Arabic books on inheritance
ALTERNATIVE_ARABIC_SOURCES = [
    {
        "primary_url": "https://foulabook.com/ar/book/download/كتاب-العول-والتعصيب:-اضواء-على-المواريث-الاسلامية-pdf",
        "filename": "07_al_awl_wal_taasib_karkhi.pdf",
        "description": "العول والتعصيب: أضواء على المواريث الإسلامية - نبيل الكرخي (Arabic)"
    },
    {
        "primary_url": "https://arabicpdfs.com/الرحبية-في-علم-الفرائض-pdf/",
        "filename": "08_ar_rahabiyyah_complete.pdf",
        "description": "الرحبية في علم الفرائض - Complete Edition (Arabic)"
    }
]

def download_pdf(url, output_path, description, timeout=60):
    """Download a PDF from URL and save to output path."""
    try:
        print(f"\n[DOWNLOADING] {description}")
        print(f"  URL: {url[:80]}...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,application/x-pdf,*/*',
            'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
        }

        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        # Verify content is PDF
        content_type = response.headers.get('content-type', '')
        if 'pdf' not in content_type.lower() and not response.content.startswith(b'%PDF'):
            if len(response.content) < 1000:
                print(f"  Warning: Content too small or not PDF ({len(response.content)} bytes)")
                return False

        with open(output_path, 'wb') as f:
            f.write(response.content)

        file_size_kb = len(response.content) / 1024
        file_size_mb = file_size_kb / 1024
        if file_size_mb > 1:
            print(f"  Success: {file_size_mb:.2f} MB")
        else:
            print(f"  Success: {file_size_kb:.1f} KB")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"  HTTP Error: {e.response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print("  Connection Error")
        return False
    except requests.exceptions.Timeout:
        print("  Timeout Error")
        return False
    except Exception as e:
        print(f"  Error: {str(e)[:60]}")
        return False

def try_download_with_delay(resources, output_dir, delay=2):
    """Try to download resources with delay between requests."""
    successful = 0
    failed = 0
    skipped = 0

    for resource in resources:
        output_path = output_dir / resource["filename"]

        # Skip if already exists
        if output_path.exists():
            size = output_path.stat().st_size / 1024
            print(f"\n[SKIP] Already exists: {resource['filename']} ({size:.1f} KB)")
            skipped += 1
            continue

        # Try to download
        if download_pdf(resource["url"], output_path, resource["description"]):
            successful += 1
            time.sleep(delay)  # Be polite to servers
        else:
            failed += 1

    return successful, failed, skipped

def main():
    # Output directory
    output_dir = Path(__file__).resolve().parent.parent / "data" / "pdfs"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("QIAS ARABIC ISLAMIC INHERITANCE PDF DOWNLOADER")
    print("=" * 70)
    print(f"Output Directory: {output_dir}")
    print("Focus: Arabic books only (Awl/Radd cases)")
    print("=" * 70)

    # Download primary resources
    print("\n--- Phase 1: Primary Archive.org Resources ---")
    s1, f1, sk1 = try_download_with_delay(ARABIC_PDF_RESOURCES, output_dir)

    # Summary
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"Successfully downloaded: {s1} files")
    print(f"Failed downloads: {f1} files")
    print(f"Skipped (already exist): {sk1} files")
    print("=" * 70)

    # List all Arabic PDF files
    print("\n--- All Arabic PDF Files in Directory ---")
    arabic_pdfs = sorted(output_dir.glob("*.pdf"))
    if arabic_pdfs:
        for i, pdf_file in enumerate(arabic_pdfs, 1):
            size_kb = pdf_file.stat().st_size / 1024
            size_mb = size_kb / 1024
            if size_mb > 1:
                size_str = f"{size_mb:.2f} MB"
            else:
                size_str = f"{size_kb:.1f} KB"
            print(f"{i}. {pdf_file.name}")
            print(f"   Size: {size_str}")
    else:
        print("No PDF files found.")

    print("\n" + "=" * 70)
    print("Note: Some downloads may fail due to URL changes or server restrictions.")
    print("Manual download may be required for alternative sources.")
    print("=" * 70)

if __name__ == "__main__":
    main()
