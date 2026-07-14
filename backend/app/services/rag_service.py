import httpx
from groq import Groq
from app.cores.config import settings
from app.services.embedding_service import embed_text
from app.services.vector_service import search_similar

# Bypass corporate SSL certificate verification for Groq API calls
# This is safe for internal dev — in production the cert issue won't exist
http_client = httpx.Client(verify=False)

groq_client = Groq(
    api_key=settings.GROQ_API_KEY,
    http_client=http_client
)

SYSTEM_PROMPT = """You are a highly skilled financial analyst assistant.
You answer questions about company quarterly financial reports accurately and concisely.

Rules you must follow:
- Only use information from the provided context chunks
- Always cite specific numbers and figures when available
- If the answer is not in the context, say "I cannot find this information in the provided report"
- Format numbers clearly (e.g. $94.9 billion, not 94930)
- Keep answers focused and professional
- When referencing data, mention which section it came from (e.g. "According to the income statement...")
"""


def build_context(chunks: list[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks):
        payload = chunk["payload"]
        section = payload.get("section", "general").replace("_", " ").title()
        page = payload.get("page_number", "?")
        chunk_type = payload.get("chunk_type", "text")
        content = payload.get("content", "")
        context_parts.append(
            f"[Source {i+1} | {section} | Page {page} | {chunk_type}]\n{content}"
        )
    return "\n\n---\n\n".join(context_parts)


def query_report(question: str, report_id: str, top_k: int = 5) -> dict:
    query_vector = embed_text(question)
    chunks = search_similar(query_vector=query_vector, report_id=report_id, top_k=top_k)

    if not chunks:
        return {"answer": "No relevant information found in this report.", "sources": [], "question": question}

    context = build_context(chunks)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""Here are the relevant sections from the financial report:

{context}

---

Question: {question}

Please answer based only on the information provided above."""
        }
    ]

    response = groq_client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0.1,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content

    sources = [
        {
            "rank": i + 1,
            "score": round(chunk["score"], 4),
            "section": chunk["payload"].get("section", "").replace("_", " ").title(),
            "page": chunk["payload"].get("page_number"),
            "chunk_type": chunk["payload"].get("chunk_type"),
            "preview": chunk["payload"].get("content", "")[:150]
        }
        for i, chunk in enumerate(chunks)
    ]

    return {"answer": answer, "sources": sources, "question": question}


def query_report_stream(question: str, report_id: str, top_k: int = 5):
    query_vector = embed_text(question)
    chunks = search_similar(query_vector=query_vector, report_id=report_id, top_k=top_k)

    if not chunks:
        yield "data: No relevant information found in this report.\n\n"
        yield "data: [DONE]\n\n"
        return

    context = build_context(chunks)