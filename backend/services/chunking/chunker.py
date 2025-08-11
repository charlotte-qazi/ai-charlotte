from typing import List


class TextChunker:
    def __init__(self, max_tokens: int = 500, overlap: int = 50) -> None:
        self.max_tokens = max_tokens
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        raise NotImplementedError("Implement text chunking logic.") 