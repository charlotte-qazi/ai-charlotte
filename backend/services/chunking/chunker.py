from typing import List


class TextChunker:
    def __init__(self, max_chars: int = 1200, overlap_chars: int = 200) -> None:
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars

    def chunk(self, text: str) -> List[str]:
        if not text:
            return []

        max_len = max(1, self.max_chars)
        overlap = max(0, min(self.overlap_chars, max_len - 1))

        chunks: List[str] = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + max_len, text_len)
            chunk_text = text[start:end]
            chunks.append(chunk_text)
            if end == text_len:
                break
            start = end - overlap

        return chunks 