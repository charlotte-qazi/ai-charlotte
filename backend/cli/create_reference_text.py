#!/usr/bin/env python3
"""
Helper script to create a reference text file from PDF extraction.
This creates a baseline for quality testing.

Usage:
python -m backend.cli.create_reference_text --input data/raw/cv.pdf --output data/raw/cv_reference.txt
"""

import argparse
from pathlib import Path

from backend.services.ingestion.loader import PDFLoader


def clean_extracted_text(text: str) -> str:
    """Clean up extracted text for use as reference."""
    # You can add manual corrections here if needed
    # For example, fix known extraction issues:
    
    # Fix common PDF extraction issues
    text = text.replace('\n \n', '\n')  # Remove isolated spaces
    text = text.replace('  ', ' ')      # Reduce double spaces
    
    # You might want to manually review and edit the output file
    # to create the "gold standard" reference text
    
    return text


def create_reference_text(pdf_path: Path, output_path: Path, manual_review: bool = True):
    """Extract text from PDF and save as reference file."""
    
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print(f"📄 Extracting text from: {pdf_path}")
    
    # Extract text
    loader = PDFLoader(pdf_path)
    extracted_text = loader.load_text()
    
    # Clean text
    cleaned_text = clean_extracted_text(extracted_text)
    
    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(cleaned_text)
    
    print(f"✅ Reference text created: {output_path}")
    print(f"   📝 {len(cleaned_text):,} characters")
    print(f"   📏 {len(cleaned_text.split()):,} words")
    
    if manual_review:
        print(f"\n📋 Next steps:")
        print(f"   1. Review and edit {output_path} to fix any extraction errors")
        print(f"   2. This will become your 'gold standard' for quality testing")
        print(f"   3. Run: pytest tests/integration/test_pdf_quality.py -v -s")
        
        print(f"\n📖 Preview (first 300 chars):")
        print("-" * 60)
        print(repr(cleaned_text[:300]) + "...")
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="Create reference text from PDF")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to input PDF"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output reference text file"
    )
    parser.add_argument(
        "--no-manual-review",
        action="store_true",
        help="Skip manual review instructions"
    )
    
    args = parser.parse_args()
    create_reference_text(
        args.input, 
        args.output, 
        manual_review=not args.no_manual_review
    )


if __name__ == "__main__":
    main() 