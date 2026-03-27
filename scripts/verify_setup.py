#!/usr/bin/env python3
"""
Verify that your QIAS RAG setup is working correctly
"""

import sys

def check_dependencies():
    """Check if all required packages are installed"""
    print("Checking dependencies...")

    required_packages = [
        'torch', 'transformers', 'accelerate', 'bitsandbytes',
        'chromadb', 'sentence-transformers', 'PyMuPDF', 'pyyaml'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\nWarning: Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\nAll dependencies are installed!")
    return True

def check_cuda():
    """Check CUDA availability"""
    print("\nChecking CUDA support...")

    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print("CUDA is available")
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("CUDA is not available (CPU-only PyTorch)")
            print("   Standard attention will be used (works on CPU)")
            return False
    except Exception as e:
        print(f"CUDA check failed: {e}")
        return False

def test_model_import():
    """Test if model classes can be imported"""
    print("\nTesting model imports...")

    try:
        from qias_mawarith_rag.calculator import MiraathCase  # noqa: F401
        print("qias_mawarith_rag can be imported")
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False

def main():
    print("QIAS RAG Setup Verification")
    print("=" * 50)

    all_good = True

    # Check dependencies
    if not check_dependencies():
        all_good = False

    # Check CUDA
    cuda_available = check_cuda()

    # Test imports
    if not test_model_import():
        all_good = False

    print("\n" + "=" * 50)

    if all_good:
        print("Setup verification complete!")
        print("\nSummary:")
        print(f"   CUDA Available: {'Yes' if cuda_available else 'No (CPU-only)'}")
        print("   Attention: Will use standard attention (works on CPU)")
        print("\nYou can now run your RAG pipeline!")
        print("Try running your notebook: notebooks/QIAS_RAG_HF.ipynb")
    else:
        print("Setup verification failed!")
        print("Please fix the issues above before running the pipeline.")

if __name__ == "__main__":
    main()