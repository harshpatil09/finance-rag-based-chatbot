import json
import httpx
from groq import Groq
from sqlalchemy.orm import Session

from app.cores.config import settings
from app.models.chunk import DocumentChunk
from app.models.insight import ReportInsight

http_client = httpx.Client(verify=False)
groq_client = Groq(api_key=settings.GROQ_API_KEY, http_client=http_client)

EXTRACTION_PROMPT = """You are a financial data extraction specialist.
Extract key financial metrics from the provided text and return ONLY a valid JSON object.
No explanation, no markdown, no extra text — just the raw JSON.

Extract these fields (use null if not found, numbers only without $ or commas):
{
  "total_revenue": <number or null>,
  "net_income": <number or null>,
  "gross_profit": <number or null>,
  "operating_income": <number or null>,
  "eps_basic": <number or null>,
  "eps_diluted": <number or null>,
  "total_assets": <number or null>,
  "total_liabilities": <number or null>,
  "total_equity": <number or null>,
  "operating_cash_flow": <number or null>
}

All values should be in millions as reported. Return only the JSON, nothing else.
"""


def extract_insights(report_id: str, db: Session) -> ReportInsight:
    """
    Extract KPIs from a processed report using Groq LLM.
    Pulls the most relevant chunks (income statement, balance sheet, cash flow)
    and asks the LLM to extract structured numbers from them.
    """
    # Fetch the most relevant chunks — income statement and balance sheet
    # are where all the numbers live
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.report_id == report_id,
        DocumentChunk.section.in_([
            "income_statement", "balance_sheet",
            "cash_flow", "general"
        ])
    ).order_by(DocumentChunk.chunk_index).limit(10).all()

    if not chunks:
        raise ValueError(f"No chunks found for report {report_id}")

    # Combine chunk content into one context string
    context = "\n\n".join([c.content for c in chunks])

    # Ask Groq to extract structured KPIs as JSON
    response = groq_client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": f"Extract financial metrics from this report:\n\n{context}"}
        ],
        temperature=0.0,   # zero temperature = maximum determinism for data extraction
        max_tokens=500,
    )

    raw_text = response.choices[0].message.content.strip()

    # Parse JSON response — strip any accidental markdown fences
    clean = raw_text.replace("```json", "").replace("```", "").strip()
    data = json.loads(clean)

    # Calculate derived metrics if we have the base numbers
    gross_margin = None
    net_margin = None
    if data.get("total_revenue") and data.get("gross_profit"):
        gross_margin = round(data["gross_profit"] / data["total_revenue"] * 100, 2)
    if data.get("total_revenue") and data.get("net_income"):
        net_margin = round(data["net_income"] / data["total_revenue"] * 100, 2)

    # Delete existing insight for this report if re-processing
    db.query(ReportInsight).filter(ReportInsight.report_id == report_id).delete()

    insight = ReportInsight(
        report_id=report_id,
        total_revenue=data.get("total_revenue"),
        net_income=data.get("net_income"),
        gross_profit=data.get("gross_profit"),
        operating_income=data.get("operating_income"),
        eps_basic=data.get("eps_basic"),
        eps_diluted=data.get("eps_diluted"),
        total_assets=data.get("total_assets"),
        total_liabilities=data.get("total_liabilities"),
        total_equity=data.get("total_equity"),
        operating_cash_flow=data.get("operating_cash_flow"),
        gross_margin=gross_margin,
        net_margin=net_margin,
        raw_extraction=clean
    )

    db.add(insight)
    db.commit()
    db.refresh(insight)

    return insight