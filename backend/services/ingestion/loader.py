from pathlib import Path
from typing import List


class DocumentLoader:
    def __init__(self, source_dir: Path) -> None:
        self.source_dir = Path(source_dir)

    def load_documents(self) -> List[str]:
        raise NotImplementedError(
            "Implement document loading from files (PDF, Markdown, etc.)."
        ) 