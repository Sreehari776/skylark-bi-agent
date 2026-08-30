import re
from datetime import date, datetime

SECTORS = [
    "Aviation",
    "Construction",
    "DSP",
    "Manufacturing",
    "Mining",
    "Others",
    "Powerline",
    "Railways",
    "Renewables",
    "Security and Surveillance",
    "Tender",
]


def current_quarter_info(today=None):
    """Return (quarter_str, year_int, start_date, end_date) for current date."""
    if today is None:
        today = date.today()

    year = today.year
    month = today.month

    if month <= 3:
        q_name = "Q1"
        s_date = date(year, 1, 1)
        e_date = date(year, 3, 31)
    elif month <= 6:
        q_name = "Q2"
        s_date = date(year, 4, 1)
        e_date = date(year, 6, 30)
    elif month <= 9:
        q_name = "Q3"
        s_date = date(year, 7, 1)
        e_date = date(year, 9, 30)
    else:
        q_name = "Q4"
        s_date = date(year, 10, 1)
        e_date = date(year, 12, 31)

    return q_name, year, s_date, e_date


def get_quarter_date_range(quarter_str, year_int=None):
    """Convert Q1-Q4 and year into start_date and end_date objects."""
    if year_int is None:
        year_int = date.today().year

    q = quarter_str.upper()

    if q == "Q1":
        return date(year_int, 1, 1), date(year_int, 3, 31)
    elif q == "Q2":
        return date(year_int, 4, 1), date(year_int, 6, 30)
    elif q == "Q3":
        return date(year_int, 7, 1), date(year_int, 9, 30)
    elif q == "Q4":
        return date(year_int, 10, 1), date(year_int, 12, 31)

    return None, None


def parse_query(question):
    """
    Map natural-language business questions to structured intents and date range bounds.
    """
    raw_text = question or ""
    text = raw_text.lower().strip()
    text_clean = re.sub(r"[^\w\s]", " ", text)
    words = set(text_clean.split())

    intent = "unsupported"

    # Executive Summary / Business Health
    if any(p in text for p in [
        "how is the business", "how's the business", "how is business", "business doing",
        "overall performance", "how are we doing", "company doing",
        "overall picture", "executive summary", "business health",
        "business performance", "give me a summary", "management attention",
    ]):
        intent = "executive_summary"

    # Strongest Sector
    elif any(p in text for p in [
        "strongest sector", "strongest pipeline", "highest pipeline",
        "best sector", "best performing sector", "top sector",
        "performing best",
    ]) and ("sector" in text or "pipeline" in text or "performing" in text):
        intent = "strongest_sector"

    # Sector Performance (general)
    elif any(p in text for p in [
        "sector performance", "sector summary", "sector breakdown", "compare sectors",
    ]):
        intent = "sector_performance"

    # Customer Risk
    elif any(p in text for p in [
        "risk", "risky", "biggest risk", "customer risk", "collection risk",
    ]):
        intent = "customer_risk"

    # Collections
    elif any(p in text for p in [
        "collection", "collected", "cash received", "money collected",
        "who owes", "receivable", "outstanding payment", "money pending",
    ]):
        intent = "collections"

    # Revenue
    elif "revenue" in text:
        intent = "revenue"

    # Billing
    elif any(p in text for p in ["billing", "billed", "invoice"]):
        intent = "billing"

    # Work Orders
    elif any(p in text for p in ["work order", "work orders", "execution status"]):
        intent = "work_orders"

    # General Pipeline
    elif any(p in text for p in [
        "pipeline", "sales outlook", "sales funnel", "how much is in",
    ]):
        intent = "pipeline"

    # Sector keyword without explicit intent -> intent is pipeline
    elif any(s.lower() in text for s in SECTORS):
        intent = "pipeline"

    # Unsupported / Off-topic domain check
    elif any(unsupported_kw in text for unsupported_kw in [
        "weather", "ceo", "joke", "president", "sports", "recipe", "who is", "what is the weather",
    ]):
        intent = "unsupported"

    # Extract Sector
    sector = next(
        (s for s in SECTORS if s.lower() in words or s.lower() in text),
        None,
    )

    # Date and Quarter parsing
    quarter_name = None
    year_num = None
    start_date = None
    end_date = None

    if "this quarter" in text or "current quarter" in text:
        quarter_name, year_num, start_date, end_date = current_quarter_info()
    else:
        # Match Q1-Q4 and optional year
        match = re.search(r"\b(q[1-4])\s*(20\d{2})?\b", text)
        if match:
            quarter_name = match.group(1).upper()
            year_num = int(match.group(2)) if match.group(2) else date.today().year
            start_date, end_date = get_quarter_date_range(quarter_name, year_num)
        else:
            # Match explicit year alone e.g. "2026"
            year_match = re.search(r"\b(20\d{2})\b", text)
            if year_match:
                year_num = int(year_match.group(1))
                start_date = date(year_num, 1, 1)
                end_date = date(year_num, 12, 31)

    return {
        "intent": intent,
        "sector": sector,
        "quarter": quarter_name,
        "year": year_num,
        "start_date": start_date,
        "end_date": end_date,
        "raw_question": question,
    }
