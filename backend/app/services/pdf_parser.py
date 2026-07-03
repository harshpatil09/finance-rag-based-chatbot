import fitz           # PyMuPDF
import pdfplumber
import re
from dataclasses import dataclass
from typing import Literal


@dataclass
class ParsedChunk:
    """
    A single extracted piece of the document before it goes into the DB.
    Dataclass = lightweight container with typed fields, no ORM overhead.
    """
    content: str
    chunk_type: Literal["text", "table"]
    page_number: int
    section: str
    chunk_index: int


# Keywords that help us detect which section of the report we're in.
# Financial reports follow a fairly standard structure — we exploit that.
SECTION_KEYWORDS = {
    "income_statement": [
        "consolidated statements of operations",
        "consolidated statements of income",
        "net sales", "total net revenue", "gross margin"
    ],
    "balance_sheet": [
        "consolidated balance sheet",
        "total assets", "total liabilities",
        "stockholders equity", "shareholders equity"
    ],
    "cash_flow": [
        "consolidated statements of cash flows",
        "operating activities", "investing activities",
        "financing activities"
    ],
    "mda": [
        "management", "discussion", "analysis",
        "results of operations", "liquidity"
    ],
    "notes": [
        "notes to condensed", "notes to consolidated",
        "note 1", "note 2", "significant accounting"
    ],
}


def detect_section(text: str) -> str:
    """
    Guess which financial section this text belongs to by keyword matching.
    Returns a section label or 'general' if no match found.
    """
    text_lower = text.lower()
    for section, keywords in SECTION_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return section
    return "general"


def table_to_markdown(table: list[list]) -> str:
    """
    Convert a pdfplumber table (list of rows, each row is a list of cells)
    into a markdown table string.

    Why markdown? The LLM understands markdown tables well — it's been
    trained on vast amounts of markdown. Plain CSV would also work but
    markdown makes the header/data relationship more explicit.

    Example output:
    | Revenue | Q3 2024 | Q3 2023 |
    |---------|---------|---------|
    | iPhone  | 39,296  | 43,805  |
    """
    if not table or not table[0]:
        return ""

    # Replace None cells (empty cells in PDF) with empty string
    cleaned = [[cell or "" for cell in row] for row in table]

    # First row as header
    header = "| " + " | ".join(str(c).strip() for c in cleaned[0]) + " |"
    separator = "| " + " | ".join("---" for _ in cleaned[0]) + " |"
    rows = [
        "| " + " | ".join(str(c).strip() for c in row) + " |"
        for row in cleaned[1:]
        if any(c for c in row)  # skip entirely empty rows
    ]

    return "\n".join([header, separator] + rows)


def extract_text_chunks(pdf_path: str) -> list[ParsedChunk]:
    """
    Extract narrative text from the PDF using PyMuPDF.
    PyMuPDF is faster than pdfplumber for text and preserves reading order better.
    We skip pages that are mostly tables (pdfplumber handles those separately).
    """
    chunks = []
    chunk_index = 0
    current_section = "general"

    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc):
        text = page.get_text("text")  # "text" mode preserves reading order

        if not text.strip():
            continue  # skip empty pages (cover images, blank separators)

        # Update section detection as we move through the document
        detected = detect_section(text)
        if detected != "general":
            current_section = detected

        # Clean up excessive whitespace that PDF extraction often produces
        text = re.sub(r'\n{3,}', '\n\n', text)  # max 2 consecutive newlines
        text = re.sub(r'[ \t]+', ' ', text)       # collapse multiple spaces

        chunks.append(ParsedChunk(
            content=text.strip(),
            chunk_type="text",
            page_number=page_num + 1,
            section=current_section,
            chunk_index=chunk_index
        ))
        chunk_index += 1

    doc.close()
    return chunks


def extract_table_chunks(pdf_path: str) -> list[ParsedChunk]:
    """
    Extract tables using pdfplumber's spatial analysis.
    pdfplumber finds table boundaries by detecting lines and text alignment —
    it doesn't just grab all text, it reconstructs the grid structure.
    """
    chunks = []
    chunk_index = 10000  # offset so table chunk_index doesn't clash with text chunks

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()

            if not tables:
                continue

            # Get page text for section detection
            page_text = page.extract_text() or ""
            section = detect_section(page_text)

            for table in tables:
                markdown = table_to_markdown(table)

                if not markdown or len(markdown) < 20:
                    continue  # skip tiny/empty tables

                chunks.append(ParsedChunk(
                    content=markdown,
                    chunk_type="table",
                    page_number=page_num + 1,
                    section=section,
                    chunk_index=chunk_index
                ))
                chunk_index += 1

    return chunks


def parse_pdf(pdf_path: str) -> list[ParsedChunk]:
    """
    Main entry point. Combines text and table extraction.
    Tables override text for the same page region — pdfplumber is more
    accurate for structured data so we trust it over PyMuPDF for tables.
    """
    text_chunks = extract_text_chunks(pdf_path)
    table_chunks = extract_table_chunks(pdf_path)

    # Combine and sort by page number so chunks are in document order
    all_chunks = text_chunks + table_chunks
    all_chunks.sort(key=lambda c: (c.page_number, c.chunk_index))

    return all_chunks