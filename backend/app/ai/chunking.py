from typing import List

def chunk_text(
        text: str,
        chunk_size: int = 40,
        overlap: int = 5
) -> List[str]:
    words = text.split()
    chunks = []

    start = 0
    text_length = len(words)

    while start < text_length:
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)

        start = end - overlap
        if start < 0:
            start = 0

        return chunks