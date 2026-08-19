"""
Advanced text chunking with sentence-aware splitting, structural preservation,
and recursive fallback for oversized segments.

Strategy:
  1. Split text into structural sections (headings, paragraphs, list items)
  2. Within each section, split into sentences using regex
  3. Group sentences into chunks of ~CHUNK_SIZE tokens with OVERLAP_SENTENCES overlap
  4. If a single sentence exceeds CHUNK_SIZE, recursively split on sub-sentence boundaries
  5. Every chunk carries metadata: section heading (if any) and chunk index
"""

import re
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """A text chunk with optional metadata for retrieval context."""
    text: str
    index: int = 0
    section: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_text(self) -> str:
        """Return enriched text with section context prepended."""
        if self.section:
            return f"[{self.section}]\n{self.text}"
        return self.text


# ---------------------------------------------------------------------------
# Sentence tokenizer (regex-based, no NLTK dependency)
# ---------------------------------------------------------------------------

# Matches sentence-ending punctuation followed by whitespace + capital letter or end-of-string.
# We avoid using variable-length lookbehinds (unsupported in Python <3.11).
# Instead, we handle abbreviations in the _split_sentences function.
_SENTENCE_BOUNDARY = re.compile(
    r'[.!?]'
    r'(?=\s+[A-Z"]|\s*$)',
    re.MULTILINE
)

# Common abbreviations that should NOT be treated as sentence boundaries
_ABBREVIATIONS = frozenset({
    'mr', 'mrs', 'ms', 'dr', 'prof', 'jr', 'sr', 'st', 'vs',
    'etc', 'approx', 'dept', 'govt', 'inc', 'corp', 'ltd', 'co',
    'fig', 'vol', 'no', 'ed', 'rev', 'gen', 'sgt', 'col',
})

# Heading patterns common in extracted document text
_HEADING_PATTERN = re.compile(
    r'^(?:'
    r'(?:#{1,6}\s+.+)'           # Markdown headings
    r'|(?:[A-Z][A-Z0-9\s]{2,80}$)'  # ALL-CAPS lines (common in PDFs)
    r'|(?:\d+(?:\.\d+)*\s+[A-Z].+$)'  # Numbered headings: "1.2 Introduction"
    r')',
    re.MULTILINE
)


def _count_tokens(text: str) -> int:
    """Approximate token count by whitespace splitting. Fast and good enough
    for chunking decisions (avoids tiktoken dependency)."""
    return len(text.split())


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences using regex boundaries.
    Filters out false boundaries from abbreviations (Mr., Dr., etc.).
    Falls back to splitting on newlines if no sentence boundaries are found."""
    if not text.strip():
        return []

    # Find candidate split points, then filter out abbreviation matches
    split_points = []
    for match in _SENTENCE_BOUNDARY.finditer(text):
        pos = match.start()  # Position of the punctuation mark

        # Check if the word before the punctuation is an abbreviation
        preceding = text[:pos].rstrip()
        if preceding:
            last_word = preceding.split()[-1].lower().rstrip('.')
            if last_word in _ABBREVIATIONS:
                continue  # Skip — this is an abbreviation, not a sentence end

            # Skip decimal numbers (e.g., "3.14")
            if preceding[-1].isdigit() and text[pos] == '.':
                continue

        split_points.append(match.end())

    # Build sentences from split points
    parts = []
    last_end = 0
    for end in split_points:
        sentence = text[last_end:end].strip()
        if sentence:
            parts.append(sentence)
        last_end = end

    # Remainder after last match
    remainder = text[last_end:].strip()
    if remainder:
        parts.append(remainder)

    # If regex found nothing useful, split on double newlines then single newlines
    if len(parts) <= 1 and len(text.split()) > 60:
        paragraphs = re.split(r'\n\s*\n', text)
        if len(paragraphs) > 1:
            parts = [p.strip() for p in paragraphs if p.strip()]
        else:
            lines = text.split('\n')
            parts = [l.strip() for l in lines if l.strip()]

    return parts if parts else [text.strip()]


def _extract_sections(text: str) -> List[dict]:
    """Split text into structural sections based on heading patterns.
    Returns a list of dicts: {"heading": str|None, "body": str}."""
    lines = text.split('\n')
    sections = []
    current_heading = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_lines.append('')
            continue

        # Check if this line looks like a heading
        if (_HEADING_PATTERN.match(stripped)
                and _count_tokens(stripped) <= 15
                and len(stripped) < 120):
            # Save previous section
            if current_lines:
                body = '\n'.join(current_lines).strip()
                if body:
                    sections.append({
                        "heading": current_heading,
                        "body": body
                    })
            current_heading = stripped.lstrip('#').strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Final section
    if current_lines:
        body = '\n'.join(current_lines).strip()
        if body:
            sections.append({
                "heading": current_heading,
                "body": body
            })

    # If no sections were found (no headings detected), treat entire text as one section
    if not sections:
        sections.append({"heading": None, "body": text.strip()})

    return sections


def _recursive_split(text: str, max_tokens: int) -> List[str]:
    """Recursively split text that's too long for a single chunk.
    Tries sentence boundaries first, then clauses, then hard word splits."""
    if _count_tokens(text) <= max_tokens:
        return [text]

    # Try sentence split
    sentences = _split_sentences(text)
    if len(sentences) > 1:
        result = []
        for s in sentences:
            result.extend(_recursive_split(s, max_tokens))
        return result

    # Try clause-level split (semicolons, commas before conjunctions)
    clauses = re.split(r'(?<=[;,])\s+(?=(?:and|or|but|which|that|however)\b)', text)
    if len(clauses) > 1:
        result = []
        for c in clauses:
            result.extend(_recursive_split(c, max_tokens))
        return result

    # Hard split by words as last resort
    words = text.split()
    result = []
    for i in range(0, len(words), max_tokens):
        chunk_words = words[i:i + max_tokens]
        result.append(' '.join(chunk_words))
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chunk_text(
        text: str,
        chunk_size: int = 200,
        overlap_sentences: int = 2,
        respect_sections: bool = True
) -> List[str]:
    """
    Chunk text into semantically coherent pieces for embedding.

    Args:
        text: The full document text to chunk.
        chunk_size: Target chunk size in tokens (words). Default 200.
        overlap_sentences: Number of sentences to overlap between chunks. Default 2.
        respect_sections: If True, never merge chunks across section boundaries.

    Returns:
        List of chunk strings, each enriched with section context if available.
    """
    if not text or not text.strip():
        return []

    # Clean up common extraction artifacts
    text = _clean_text(text)

    # Extract document structure
    if respect_sections:
        sections = _extract_sections(text)
    else:
        sections = [{"heading": None, "body": text}]

    all_chunks: List[Chunk] = []
    chunk_index = 0

    for section in sections:
        heading = section["heading"]
        body = section["body"]

        if not body.strip():
            continue

        # Split section body into sentences
        sentences = _split_sentences(body)

        # Handle sentences that are individually too long
        expanded_sentences = []
        for s in sentences:
            if _count_tokens(s) > chunk_size:
                expanded_sentences.extend(_recursive_split(s, chunk_size))
            else:
                expanded_sentences.append(s)
        sentences = expanded_sentences

        # Group sentences into chunks with overlap
        i = 0
        while i < len(sentences):
            current_chunk_sentences = []
            current_tokens = 0

            # Fill chunk up to chunk_size
            while i < len(sentences):
                sentence_tokens = _count_tokens(sentences[i])
                if current_tokens + sentence_tokens > chunk_size and current_chunk_sentences:
                    break
                current_chunk_sentences.append(sentences[i])
                current_tokens += sentence_tokens
                i += 1

            chunk_text_str = ' '.join(current_chunk_sentences)
            chunk = Chunk(
                text=chunk_text_str,
                index=chunk_index,
                section=heading
            )
            all_chunks.append(chunk)
            chunk_index += 1

            # Step back by overlap_sentences for context continuity
            if overlap_sentences > 0 and i < len(sentences):
                i = max(i - overlap_sentences, i - len(current_chunk_sentences) + 1)

    # Return enriched text strings
    return [c.to_text() for c in all_chunks]


def chunk_text_with_metadata(
        text: str,
        chunk_size: int = 200,
        overlap_sentences: int = 2,
        respect_sections: bool = True
) -> List[dict]:
    """
    Same as chunk_text but returns dicts with text and metadata.
    Useful for storing richer payload in the vector DB.

    Returns:
        List of {"text": str, "index": int, "section": str|None}
    """
    if not text or not text.strip():
        return []

    text = _clean_text(text)

    if respect_sections:
        sections = _extract_sections(text)
    else:
        sections = [{"heading": None, "body": text}]

    results = []
    chunk_index = 0

    for section in sections:
        heading = section["heading"]
        body = section["body"]

        if not body.strip():
            continue

        sentences = _split_sentences(body)
        expanded = []
        for s in sentences:
            if _count_tokens(s) > chunk_size:
                expanded.extend(_recursive_split(s, chunk_size))
            else:
                expanded.append(s)
        sentences = expanded

        i = 0
        while i < len(sentences):
            current = []
            tokens = 0
            while i < len(sentences):
                st = _count_tokens(sentences[i])
                if tokens + st > chunk_size and current:
                    break
                current.append(sentences[i])
                tokens += st
                i += 1

            results.append({
                "text": ' '.join(current),
                "index": chunk_index,
                "section": heading
            })
            chunk_index += 1

            if overlap_sentences > 0 and i < len(sentences):
                i = max(i - overlap_sentences, i - len(current) + 1)

    return results


def _clean_text(text: str) -> str:
    """Clean common extraction artifacts from PDF/DOCX text."""
    # Collapse excessive whitespace (common in PDF extraction)
    text = re.sub(r'[ \t]{3,}', '  ', text)
    # Remove page number artifacts (e.g., "- 12 -", "Page 12 of 50")
    text = re.sub(r'\n\s*-?\s*\d+\s*-?\s*\n', '\n', text)
    text = re.sub(r'\n\s*Page\s+\d+\s+of\s+\d+\s*\n', '\n', text, flags=re.IGNORECASE)
    # Collapse more than 2 consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Fix broken hyphenation from PDF line breaks (e.g., "docu-\nment" -> "document")
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    # Remove null bytes and control characters (except newline/tab)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return text.strip()


# ---------------------------------------------------------------------------
# Smart routing: dispatch to format-specific chunker
# ---------------------------------------------------------------------------

def smart_chunk(
        text: str,
        format_tag: str = "plain",
        chunk_size: int = 200,
        method: str = "auto"
) -> List[str]:
    """
    Route text to the appropriate chunker based on format and method.

    Args:
        text: The extracted document text.
        format_tag: One of "pdf", "html", "markdown", "docx", "plain".
        chunk_size: Target chunk size in tokens.
        method: "auto" (format-aware), "semantic", or "structural" (existing).

    Returns:
        List of chunk strings.
    """
    if not text or not text.strip():
        return []

    text = _clean_text(text)

    # Semantic chunking — uses embedding similarity
    if method == "semantic":
        return semantic_chunk_text(text, chunk_size=chunk_size)

    # Structural chunking — the existing sentence-aware method
    if method == "structural":
        return chunk_text(text, chunk_size=chunk_size)

    # Auto mode — use format-specific chunkers
    from app.ai.format_chunkers import chunk_pdf, chunk_html, chunk_markdown, FormatChunk

    format_chunkers = {
        "pdf": chunk_pdf,
        "html": chunk_html,
        "markdown": chunk_markdown,
    }

    chunker = format_chunkers.get(format_tag)
    if chunker:
        format_chunks: List[FormatChunk] = chunker(text, chunk_size=chunk_size)
        # Convert FormatChunks to enriched strings
        result = []
        for fc in format_chunks:
            if fc.section:
                result.append(f"[{fc.section}]\n{fc.text}")
            else:
                result.append(fc.text)
        return result

    # Fallback: existing structural chunking for plain text / docx
    return chunk_text(text, chunk_size=chunk_size)


# ---------------------------------------------------------------------------
# Semantic chunking (uses local sentence-transformers)
# ---------------------------------------------------------------------------

def semantic_chunk_text(
        text: str,
        chunk_size: int = 200,
        similarity_threshold: float = 0.3,
) -> List[str]:
    """
    Chunk text by embedding similarity between consecutive sentences.
    Uses local sentence-transformers model (no API cost).

    Strategy:
      1. Split into sentences
      2. Embed each sentence locally
      3. Compute cosine similarity between consecutive pairs
      4. Split where similarity drops below threshold
      5. Group resulting segments up to chunk_size

    Falls back to structural chunking if sentence-transformers unavailable.
    """
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        # Fallback if sentence-transformers not installed
        return chunk_text(text, chunk_size=chunk_size)

    sentences = _split_sentences(text)
    if len(sentences) <= 1:
        return [text.strip()] if text.strip() else []

    # Expand oversized sentences
    expanded = []
    for s in sentences:
        if _count_tokens(s) > chunk_size:
            expanded.extend(_recursive_split(s, chunk_size))
        else:
            expanded.append(s)
    sentences = expanded

    if len(sentences) <= 1:
        return sentences

    # Embed all sentences locally
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(sentences, show_progress_bar=False)

    # Compute cosine similarity between consecutive sentence pairs
    similarities = []
    for i in range(len(embeddings) - 1):
        a = embeddings[i]
        b = embeddings[i + 1]
        cos_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)
        similarities.append(float(cos_sim))

    # Find split points where similarity drops
    # Use dynamic threshold: mean - 1 std, but no lower than similarity_threshold
    if similarities:
        mean_sim = np.mean(similarities)
        std_sim = np.std(similarities)
        dynamic_threshold = max(mean_sim - std_sim, similarity_threshold)
    else:
        dynamic_threshold = similarity_threshold

    # Build semantic segments
    segments = []
    current_segment = [sentences[0]]

    for i, sim in enumerate(similarities):
        if sim < dynamic_threshold:
            # Boundary found — save current segment
            segments.append(current_segment)
            current_segment = [sentences[i + 1]]
        else:
            current_segment.append(sentences[i + 1])

    if current_segment:
        segments.append(current_segment)

    # Group segments into chunks respecting chunk_size
    chunks = []
    for segment in segments:
        segment_text = ' '.join(segment)
        if _count_tokens(segment_text) <= chunk_size:
            chunks.append(segment_text)
        else:
            # Sub-chunk oversized segments
            current = []
            current_tokens = 0
            for sent in segment:
                st = _count_tokens(sent)
                if current_tokens + st > chunk_size and current:
                    chunks.append(' '.join(current))
                    current = []
                    current_tokens = 0
                current.append(sent)
                current_tokens += st
            if current:
                chunks.append(' '.join(current))

    return chunks


# ---------------------------------------------------------------------------
# Parent-child chunking (for parent-child retrieval)
# ---------------------------------------------------------------------------

def create_parent_child_chunks(
        text: str,
        parent_size: int = 400,
        child_size: int = 100,
        format_tag: str = "plain",
) -> List[dict]:
    """
    Create parent and child chunks for parent-child retrieval.

    Small child chunks are used for search precision.
    Parent chunks provide broader context for LLM generation.

    Returns:
        List of dicts:
        {
            "child_text": str,       # small chunk for embedding
            "parent_text": str,      # broader context for LLM
            "parent_id": int,        # parent chunk index
            "child_id": int,         # child chunk index
        }
    """
    if not text or not text.strip():
        return []

    text = _clean_text(text)

    # Create parent chunks using format-aware or structural chunking
    parent_chunks = smart_chunk(text, format_tag=format_tag, chunk_size=parent_size)

    results = []
    child_id = 0

    for parent_id, parent_text in enumerate(parent_chunks):
        # Create child chunks within each parent
        child_chunks = chunk_text(parent_text, chunk_size=child_size, overlap_sentences=0)

        for child_text in child_chunks:
            results.append({
                "child_text": child_text,
                "parent_text": parent_text,
                "parent_id": parent_id,
                "child_id": child_id,
            })
            child_id += 1

    return results