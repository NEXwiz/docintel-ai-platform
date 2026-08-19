"""
Format-specific text chunkers for PDF, HTML, and Markdown.

Each chunker understands the structural semantics of its format and
produces chunks that respect document boundaries (headings, tables,
code blocks, list groups, etc.).
"""

import re
from typing import List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class FormatChunk:
    """A chunk produced by a format-aware chunker."""
    text: str
    section: Optional[str] = None
    chunk_type: str = "text"  # text, table, code, list, heading
    page: Optional[int] = None
    metadata: dict = field(default_factory=dict)


def _count_tokens(text: str) -> int:
    """Approximate token count by whitespace splitting."""
    return len(text.split())


# ---------------------------------------------------------------------------
# PDF Chunker
# ---------------------------------------------------------------------------

def chunk_pdf(text: str, chunk_size: int = 200) -> List[FormatChunk]:
    """
    Chunk PDF-extracted text with awareness of:
    - Page boundaries (double newlines from extraction)
    - Headings (ALL-CAPS lines, numbered sections)
    - Tables (pipe-delimited blocks)
    - Paragraphs
    """
    chunks: List[FormatChunk] = []
    current_section = None

    # Split into page-like blocks (PDF extraction uses double-newline between pages)
    pages = re.split(r'\n{3,}', text)

    for page_idx, page_text in enumerate(pages, start=1):
        page_text = page_text.strip()
        if not page_text:
            continue

        # Split page into structural elements
        elements = _split_pdf_elements(page_text)

        for elem_type, elem_text in elements:
            if not elem_text.strip():
                continue

            if elem_type == "heading":
                current_section = elem_text.strip()
                # Small headings go inline with the next chunk
                if _count_tokens(elem_text) <= 10:
                    continue
                # Long headings become their own chunk
                chunks.append(FormatChunk(
                    text=elem_text,
                    section=current_section,
                    chunk_type="heading",
                    page=page_idx
                ))
                continue

            if elem_type == "table":
                # Tables are atomic — never split a table
                if _count_tokens(elem_text) <= chunk_size * 1.5:
                    chunks.append(FormatChunk(
                        text=elem_text,
                        section=current_section,
                        chunk_type="table",
                        page=page_idx
                    ))
                else:
                    # Very large table: split by rows
                    rows = elem_text.split('\n')
                    header = rows[0] if rows else ""
                    current_rows = [header]
                    current_tokens = _count_tokens(header)

                    for row in rows[1:]:
                        row_tokens = _count_tokens(row)
                        if current_tokens + row_tokens > chunk_size and len(current_rows) > 1:
                            chunks.append(FormatChunk(
                                text='\n'.join(current_rows),
                                section=current_section,
                                chunk_type="table",
                                page=page_idx
                            ))
                            current_rows = [header]  # repeat header
                            current_tokens = _count_tokens(header)

                        current_rows.append(row)
                        current_tokens += row_tokens

                    if len(current_rows) > 1:
                        chunks.append(FormatChunk(
                            text='\n'.join(current_rows),
                            section=current_section,
                            chunk_type="table",
                            page=page_idx
                        ))
                continue

            # Regular text — split into sentence-based chunks
            text_chunks = _chunk_text_block(elem_text, chunk_size)
            for tc in text_chunks:
                chunks.append(FormatChunk(
                    text=tc,
                    section=current_section,
                    chunk_type="text",
                    page=page_idx
                ))

    return chunks


def _split_pdf_elements(text: str) -> List[Tuple[str, str]]:
    """Split a PDF page into typed elements (heading, table, text)."""
    elements = []
    lines = text.split('\n')
    current_type = "text"
    current_lines = []

    for line in lines:
        stripped = line.strip()

        # Detect headings: ALL-CAPS, numbered sections, short bold-like lines
        if (_is_heading_line(stripped) and _count_tokens(stripped) <= 15):
            if current_lines:
                elements.append((current_type, '\n'.join(current_lines)))
                current_lines = []
            elements.append(("heading", stripped))
            current_type = "text"
            continue

        # Detect table rows (pipe-delimited)
        if '|' in stripped and stripped.count('|') >= 2:
            if current_type != "table" and current_lines:
                elements.append((current_type, '\n'.join(current_lines)))
                current_lines = []
            current_type = "table"
            current_lines.append(line)
            continue

        # If we were in a table and hit a non-table line, flush
        if current_type == "table":
            elements.append(("table", '\n'.join(current_lines)))
            current_lines = []
            current_type = "text"

        current_lines.append(line)

    if current_lines:
        elements.append((current_type, '\n'.join(current_lines)))

    return elements


def _is_heading_line(line: str) -> bool:
    """Check if a line looks like a heading."""
    if not line or len(line) < 2:
        return False
    # ALL-CAPS lines (3+ chars, not just numbers/symbols)
    if re.match(r'^[A-Z][A-Z0-9\s\-:]{2,80}$', line):
        return True
    # Numbered headings: "1.2 Introduction", "3. Methods"
    if re.match(r'^\d+(?:\.\d+)*\.?\s+[A-Z]', line):
        return True
    # Markdown-style (from DOCX conversion)
    if re.match(r'^#{1,6}\s+', line):
        return True
    return False


# ---------------------------------------------------------------------------
# HTML Chunker
# ---------------------------------------------------------------------------

def chunk_html(text: str, chunk_size: int = 200) -> List[FormatChunk]:
    """
    Chunk HTML content by semantic elements.
    Requires text to be raw HTML (not pre-extracted text).
    Uses BeautifulSoup for parsing.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        # Fallback: treat as plain text
        return [FormatChunk(text=t, chunk_type="text")
                for t in _chunk_text_block(text, chunk_size)]

    soup = BeautifulSoup(text, 'html.parser')

    # Remove noise elements
    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
        tag.decompose()

    chunks: List[FormatChunk] = []
    current_section = None

    # Process elements in document order
    for element in soup.find_all([
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'div', 'section', 'article',
        'table', 'ul', 'ol', 'pre', 'blockquote'
    ]):
        tag_name = element.name
        elem_text = element.get_text(separator=' ', strip=True)

        if not elem_text:
            continue

        # Headings
        if tag_name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(tag_name[1])
            current_section = elem_text
            prefix = "#" * level
            chunks.append(FormatChunk(
                text=f"{prefix} {elem_text}",
                section=current_section,
                chunk_type="heading"
            ))
            continue

        # Tables — extract as pipe-delimited
        if tag_name == 'table':
            table_text = _html_table_to_text(element)
            if table_text:
                chunks.append(FormatChunk(
                    text=table_text,
                    section=current_section,
                    chunk_type="table"
                ))
            continue

        # Code blocks
        if tag_name == 'pre':
            code_text = element.get_text(strip=True)
            if code_text:
                chunks.append(FormatChunk(
                    text=f"```\n{code_text}\n```",
                    section=current_section,
                    chunk_type="code"
                ))
            continue

        # Lists — group items together
        if tag_name in ('ul', 'ol'):
            items = element.find_all('li')
            list_text = '\n'.join(
                f"{'•' if tag_name == 'ul' else f'{i+1}.'} {li.get_text(strip=True)}"
                for i, li in enumerate(items)
                if li.get_text(strip=True)
            )
            if list_text:
                if _count_tokens(list_text) <= chunk_size:
                    chunks.append(FormatChunk(
                        text=list_text,
                        section=current_section,
                        chunk_type="list"
                    ))
                else:
                    for tc in _chunk_text_block(list_text, chunk_size):
                        chunks.append(FormatChunk(
                            text=tc,
                            section=current_section,
                            chunk_type="list"
                        ))
            continue

        # Regular paragraphs and divs
        if _count_tokens(elem_text) > 5:  # Skip tiny fragments
            for tc in _chunk_text_block(elem_text, chunk_size):
                chunks.append(FormatChunk(
                    text=tc,
                    section=current_section,
                    chunk_type="text"
                ))

    # Deduplicate (nested elements can cause repeats)
    seen = set()
    deduped = []
    for c in chunks:
        key = c.text[:100]
        if key not in seen:
            seen.add(key)
            deduped.append(c)

    return deduped


def _html_table_to_text(table_element) -> str:
    """Convert an HTML table to pipe-delimited text."""
    rows = []
    for tr in table_element.find_all('tr'):
        cells = [td.get_text(strip=True).replace('\n', ' ')
                 for td in tr.find_all(['td', 'th'])]
        if any(cells):
            rows.append(' | '.join(cells))

    if not rows:
        return ""

    # Add markdown-style separator after header row
    if len(rows) > 1:
        col_count = rows[0].count('|') + 1
        separator = ' | '.join(['---'] * col_count)
        rows.insert(1, separator)

    return '\n'.join(rows)


# ---------------------------------------------------------------------------
# Markdown Chunker
# ---------------------------------------------------------------------------

def chunk_markdown(text: str, chunk_size: int = 200) -> List[FormatChunk]:
    """
    Chunk Markdown with awareness of:
    - Heading hierarchy (#, ##, ###)
    - Code blocks (``` ... ```)
    - Tables (pipe-delimited)
    - Lists (bullet/numbered)
    - Frontmatter (YAML --- blocks)
    """
    chunks: List[FormatChunk] = []

    # Strip frontmatter
    text = _strip_frontmatter(text)

    # Split into structural blocks
    blocks = _split_markdown_blocks(text)

    current_section = None

    for block_type, block_text in blocks:
        block_text = block_text.strip()
        if not block_text:
            continue

        if block_type == "heading":
            current_section = block_text.lstrip('#').strip()
            chunks.append(FormatChunk(
                text=block_text,
                section=current_section,
                chunk_type="heading"
            ))
            continue

        if block_type == "code":
            # Code blocks are atomic
            if _count_tokens(block_text) <= chunk_size * 2:
                chunks.append(FormatChunk(
                    text=block_text,
                    section=current_section,
                    chunk_type="code"
                ))
            else:
                # Very long code: split by lines
                lines = block_text.split('\n')
                lang_line = lines[0] if lines else "```"
                current_block = [lang_line]
                current_tokens = 1

                for line in lines[1:]:
                    if line.strip() == '```':
                        current_block.append('```')
                        chunks.append(FormatChunk(
                            text='\n'.join(current_block),
                            section=current_section,
                            chunk_type="code"
                        ))
                        break

                    line_tokens = _count_tokens(line)
                    if current_tokens + line_tokens > chunk_size and len(current_block) > 1:
                        current_block.append('```')
                        chunks.append(FormatChunk(
                            text='\n'.join(current_block),
                            section=current_section,
                            chunk_type="code"
                        ))
                        current_block = [lang_line]
                        current_tokens = 1

                    current_block.append(line)
                    current_tokens += line_tokens
            continue

        if block_type == "table":
            chunks.append(FormatChunk(
                text=block_text,
                section=current_section,
                chunk_type="table"
            ))
            continue

        if block_type == "list":
            if _count_tokens(block_text) <= chunk_size:
                chunks.append(FormatChunk(
                    text=block_text,
                    section=current_section,
                    chunk_type="list"
                ))
            else:
                for tc in _chunk_text_block(block_text, chunk_size):
                    chunks.append(FormatChunk(
                        text=tc,
                        section=current_section,
                        chunk_type="list"
                    ))
            continue

        # Regular text paragraphs
        for tc in _chunk_text_block(block_text, chunk_size):
            chunks.append(FormatChunk(
                text=tc,
                section=current_section,
                chunk_type="text"
            ))

    return chunks


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter from markdown."""
    if text.startswith('---'):
        end = text.find('---', 3)
        if end != -1:
            return text[end + 3:].strip()
    return text


def _split_markdown_blocks(text: str) -> List[Tuple[str, str]]:
    """Split markdown into typed blocks."""
    blocks = []
    lines = text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Heading
        if re.match(r'^#{1,6}\s+', stripped):
            blocks.append(("heading", stripped))
            i += 1
            continue

        # Code block
        if stripped.startswith('```'):
            code_lines = [line]
            i += 1
            while i < len(lines):
                code_lines.append(lines[i])
                if lines[i].strip() == '```' and len(code_lines) > 1:
                    i += 1
                    break
                i += 1
            blocks.append(("code", '\n'.join(code_lines)))
            continue

        # Table (pipe-delimited lines)
        if '|' in stripped and stripped.count('|') >= 2:
            table_lines = [line]
            i += 1
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            blocks.append(("table", '\n'.join(table_lines)))
            continue

        # List items
        if re.match(r'^[\s]*[-*+]\s|^\s*\d+\.\s', stripped):
            list_lines = [line]
            i += 1
            while i < len(lines):
                ls = lines[i].strip()
                if re.match(r'^[-*+]\s|^\d+\.\s', ls) or (ls and lines[i][0] == ' '):
                    list_lines.append(lines[i])
                    i += 1
                elif not ls:
                    # Empty line might be between list items
                    if i + 1 < len(lines) and re.match(r'^[\s]*[-*+]\s|^\s*\d+\.\s', lines[i + 1].strip()):
                        list_lines.append(lines[i])
                        i += 1
                    else:
                        break
                else:
                    break
            blocks.append(("list", '\n'.join(list_lines)))
            continue

        # Regular text paragraph
        if stripped:
            para_lines = [line]
            i += 1
            while i < len(lines):
                ls = lines[i].strip()
                if not ls:
                    i += 1
                    break
                if re.match(r'^#{1,6}\s+', ls) or ls.startswith('```') or re.match(r'^[-*+]\s|^\d+\.\s', ls):
                    break
                para_lines.append(lines[i])
                i += 1
            blocks.append(("text", '\n'.join(para_lines)))
            continue

        i += 1

    return blocks


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def _chunk_text_block(text: str, chunk_size: int) -> List[str]:
    """Split a text block into chunks of approximately chunk_size tokens.
    Uses sentence-aware splitting."""
    if _count_tokens(text) <= chunk_size:
        return [text]

    sentences = _split_into_sentences(text)
    chunks = []
    current = []
    current_tokens = 0

    for sentence in sentences:
        s_tokens = _count_tokens(sentence)

        if s_tokens > chunk_size:
            # Flush current
            if current:
                chunks.append(' '.join(current))
                current = []
                current_tokens = 0
            # Hard split oversized sentence
            words = sentence.split()
            for j in range(0, len(words), chunk_size):
                chunks.append(' '.join(words[j:j + chunk_size]))
            continue

        if current_tokens + s_tokens > chunk_size and current:
            chunks.append(' '.join(current))
            current = []
            current_tokens = 0

        current.append(sentence)
        current_tokens += s_tokens

    if current:
        chunks.append(' '.join(current))

    return chunks


def _split_into_sentences(text: str) -> List[str]:
    """Simple sentence splitter for use within format chunkers."""
    # Split on sentence-ending punctuation followed by space + capital
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"])', text)
    result = []
    for p in parts:
        p = p.strip()
        if p:
            result.append(p)
    if not result:
        # Fallback: split on newlines
        result = [l.strip() for l in text.split('\n') if l.strip()]
    return result if result else [text]
