from pathlib import Path
from typing import List


class DocumentLoader:
    def __init__(self, source_dir: Path) -> None:
        self.source_dir = Path(source_dir)

    def load_documents(self) -> List[str]:
        raise NotImplementedError(
            "Implement document loading from files (PDF, Markdown, etc.)."
        )


class PDFLoader:
    def __init__(self, pdf_path: Path) -> None:
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")

    def load_text_by_page(self) -> List[str]:
        from pypdf import PdfReader

        reader = PdfReader(str(self.pdf_path))
        page_texts: List[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            page_texts.append(text)
        return page_texts

    def load_text(self) -> str:
        pages = self.load_text_by_page()
        return "\n\n".join(pages) 