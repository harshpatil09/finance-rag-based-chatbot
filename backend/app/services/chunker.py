from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.pdf_parser import ParsedChunk


# These settings are tuned for financial documents:
# - 500 tokens ~ 375 words — enough context for a financial statement paragraph
# - 50 token overlap — ensures no sentence is cut off at a boundary
# - The splitter tries to break on: paragraph → newline → sentence → word
#   It never splits mid-word.
CHUNK_SIZE = 500      # characters (approx 375 tokens for English text)
CHUNK_OVERLAP = 50

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],  # priority order of split points
    length_function=len,
)


def split_chunks(raw_chunks: list[ParsedChunk]) -> list[ParsedChunk]:
    """
    Takes page-level chunks from the parser and splits long text chunks
    into smaller pieces. Tables are NEVER split — a table must stay whole
    or the row/column relationships break entirely.
    """
    final_chunks = []
    new_index = 0

    for chunk in raw_chunks:
        if chunk.chunk_type == "table":
            # Tables stay as-is — splitting a table destroys its structure
            chunk.chunk_index = new_index
            final_chunks.append(chunk)
            new_index += 1
            continue

        # For text chunks, split if they're longer than CHUNK_SIZE
        if len(chunk.content) <= CHUNK_SIZE:
            chunk.chunk_index = new_index
            final_chunks.append(chunk)
            new_index += 1
        else:
            sub_texts = text_splitter.split_text(chunk.content)
            for sub_text in sub_texts:
                final_chunks.append(ParsedChunk(
                    content=sub_text,
                    chunk_type="text",
                    page_number=chunk.page_number,
                    section=chunk.section,
                    chunk_index=new_index
                ))
                new_index += 1

    return final_chunks