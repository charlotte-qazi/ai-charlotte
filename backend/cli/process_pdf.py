import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from backend.services.ingestion.loader import PDFLoader
from backend.services.chunking.chunker import TextChunker


def write_jsonl(output_path: Path, records: List[Dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def process_pdf(
    input_pdf: Path,
    output_jsonl: Path,
    max_chars: int,
    overlap_chars: int,
    source_label: str,
) -> None:
    loader = PDFLoader(input_pdf)
    full_text = loader.load_text()

    chunker = TextChunker(max_chars=max_chars, overlap_chars=overlap_chars)
    chunks = chunker.chunk(full_text)

    records: List[Dict[str, Any]] = []
    for index, chunk_text in enumerate(chunks):
        records.append(
            {
                "id": f"{input_pdf.stem}-{index}",
                "chunk_index": index,
                "text": chunk_text,
                "source": source_label or str(input_pdf),
                "metadata": {
                    "filename": input_pdf.name,
                    "path": str(input_pdf),
                },
            }
        )

    write_jsonl(output_jsonl, records)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest a PDF, chunk it, and write JSONL chunks to output"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to input PDF (e.g., data/raw/cv.pdf)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/cv_chunks.jsonl"),
        help="Path to output JSONL (default: data/processed/cv_chunks.jsonl)",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=1200,
        help="Maximum characters per chunk",
    )
    parser.add_argument(
        "--overlap-chars",
        type=int,
        default=200,
        help="Overlap characters between chunks",
    )
    parser.add_argument(
        "--source-label",
        type=str,
        default="cv",
        help="Source label to attach to chunks",
    )

    args = parser.parse_args()
    process_pdf(
        input_pdf=args.input,
        output_jsonl=args.output,
        max_chars=args.max_chars,
        overlap_chars=args.overlap_chars,
        source_label=args.source_label,
    )


if __name__ == "__main__":
    main() 