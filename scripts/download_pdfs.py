"""
Script to download Islamic inheritance (Al-Mawarith) PDF resources
for enhancing the QIAS train set distribution.
"""

import requests
from pathlib import Path

# PDF URLs to download - focused on covering Awl/Radd cases and complex inheritance scenarios
PDF_RESOURCES = [
    {
        "url": "https://archive.org/download/AsSirajiyyahAsSirajiFilMirathEnglishTranslation/As-Sirajiyyah%20(As%20Siraji%20fil%20Mirath)%20-%20English%20Translation.pdf",
        "filename": "01_as_sirajiyyah_fil_mirath_english.pdf",
        "description": "As-Sirajiyyah Fil Mirath - Hanafi Inheritance Law (Covers Awl/Radd)"
    },
    {
        "url": "https://archive.org/download/IslamicLawOfInheritanceByShaykhDrMuhammadAbdulHaiArifir.a/IslamicLawOfInheritanceByShaykhDrMuhammadAbdulHaiArifir.a.pdf",
        "filename": "02_islamic_law_of_inheritance_arifi.pdf",
        "description": "Islamic Law of Inheritance by Dr. Abdul Hai Arifi"
    },
    {
        "url": "https://archive.org/download/etaoin/Fiqih%20Islam%20Wa%20Adillatuhu%2010.pdf",
        "filename": "03_fiqih_islam_wa_adillatuhu_vol10.pdf",
        "description": "Fiqih Islam Wa Adillatuhu Vol 10 - Inheritance (Warisan) - 4 Madhabs"
    },
    {
        "url": "https://archive.org/download/studiesinquranad0000powe/studiesinquranad0000powe.pdf",
        "filename": "04_studies_quran_hadith_inheritance_powers.pdf",
        "description": "Studies in Qur'an and Hadith - Formation of Islamic Inheritance Law"
    },
    {
        "url": "https://archive.org/download/mirathalanbiyain0000unse/mirathalanbiyain0000unse.pdf",
        "filename": "05_mirath_al_anbiya_inheritance.pdf",
        "description": "Mirath al-Anbiya - Inheritance of the Prophets"
    }
]

def download_pdf(url, output_path, description):
    """Download a PDF from URL and save to output path."""
    try:
        print(f"Downloading: {description}")
        print(f"URL: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=60, allow_redirects=True)
        response.raise_for_status()

        # Check if content is PDF
        content_type = response.headers.get('content-type', '')
        if 'pdf' not in content_type.lower() and not response.content.startswith(b'%PDF'):
            print(f"  Warning: Content may not be PDF (type: {content_type})")

        with open(output_path, 'wb') as f:
            f.write(response.content)

        file_size = len(response.content) / 1024  # KB
        print(f"  Success: Saved to {output_path} ({file_size:.1f} KB)\n")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"  Error: HTTP {e.response.status_code} - {e}\n")
        return False
    except Exception as e:
        print(f"  Error: {e}\n")
        return False

def main():
    # Output directory
    output_dir = Path(__file__).resolve().parent.parent / "data" / "pdfs"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("QIAS Islamic Inheritance PDF Downloader")
    print("=" * 70)
    print(f"Output directory: {output_dir}")
    print()

    successful = 0
    failed = 0

    for resource in PDF_RESOURCES:
        output_path = output_dir / resource["filename"]

        if output_path.exists():
            print(f"Skipping (already exists): {resource['filename']}")
            successful += 1
            continue

        if download_pdf(resource["url"], output_path, resource["description"]):
            successful += 1
        else:
            failed += 1

    print("=" * 70)
    print(f"Download complete: {successful} successful, {failed} failed")
    print("=" * 70)

    # List downloaded files
    print("\nDownloaded files:")
    for pdf_file in sorted(output_dir.glob("*.pdf")):
        size = pdf_file.stat().st_size / 1024
        print(f"  - {pdf_file.name} ({size:.1f} KB)")

if __name__ == "__main__":
    main()
