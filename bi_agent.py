from datetime import datetime

from analytics import (
    load_data,
    pipeline_summary,
    billing_summary,
    work_order_summary,
    customer_risk_analysis,
    strongest_sector_analysis,
    sector_performance,
    data_quality_summary,
    format_data_quality_warning,
)
from query_parser import parse_query
from query_engine import pipeline_query


# ============================================================
# FORMATTING HELPERS
# ============================================================

def format_currency(value):
    """Format INR values consistently."""
    try:
        value = float(value or 0)
    except (TypeError, ValueError):
        value = 0.0

    if abs(value) >= 1_000_000_000:
        return f"₹{value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"₹{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"₹{value / 1_000:.2f}K"

    return f"₹{value:,.0f}"


# ============================================================
# INTENT FORMATTERS
# ============================================================

def answer_pipeline(deals, parsed):
    """Format sales pipeline query answer, enforcing the No-Data contract."""
    result = pipeline_query(
        deals,
        sector=parsed.get("sector"),
        quarter=parsed.get("quarter"),
        year=parsed.get("year"),
        start_date=parsed.get("start_date"),
        end_date=parsed.get("end_date"),
    )

    sector = parsed.get("sector") or "all sectors"

    quarter = parsed.get("quarter")
    year = parsed.get("year")

    if quarter and year:
        period = f"{quarter} {year}"
    elif quarter:
        period = quarter
    elif year:
        period = str(year)
    else:
        period = "all periods"

    count = result["number_of_deals"]
    val = result["pipeline_value"]

    # NO-DATA CONTRACT
    if count == 0:
        return (
            f"No active {sector} opportunities were found for {period}, "
            f"so the pipeline is ₹0 across 0 active deals."
        )

    deal_str = "1 active deal" if count == 1 else f"{count} active deals"

    return (
        f"Pipeline for {sector} in {period}: "
        f"{format_currency(val)} across {deal_str}."
    )


def answer_strongest_sector(deals):
    """Format strongest sector analysis with winner details, ranked list, and uniform Million formatting."""
    analysis = strongest_sector_analysis(deals)

    winning_sector = analysis.get("strongest_sector")
    if not winning_sector:
        return "No active pipeline data is available to determine the strongest sector."

    val = analysis["strongest_pipeline_value"]
    count = analysis["strongest_deal_count"]
    rankings = analysis["sector_rankings"]
    missing_deals = analysis.get("missing_sector_deals", 0)
    missing_val = analysis.get("missing_sector_value", 0.0)

    deal_str = "1 active deal" if count == 1 else f"{count} active deals"
    lines = [
        f"Strongest Pipeline Sector: {winning_sector} — {format_currency(val)} across {deal_str}.",
        "",
        "Sector ranking:"
    ]

    for i, row in enumerate(rankings, 1):
        d_count = row["active_deals"]
        d_text = "1 active deal" if d_count == 1 else f"{d_count} active deals"
        p_val = row["pipeline_value"]
        formatted_p_val = f"₹{p_val / 1_000_000:.2f}M" if p_val >= 100_000 else format_currency(p_val)
        lines.append(
            f"{i}. {row['sector']} — {formatted_p_val} ({d_text})"
        )

    if missing_deals > 0:
        m_deal_text = "1 deal has" if missing_deals == 1 else f"{missing_deals} deals have"
        lines.extend([
            "",
            f"Note: {m_deal_text} a missing sector value ({format_currency(missing_val)})."
        ])

    return "\n".join(lines)


def answer_work_orders(work_orders):
    """Format work order operational summary."""
    summary = work_order_summary(work_orders)

    return (
        f"Work Orders: {summary['number_of_work_orders']} total.\n"
        f"• Completed value: {format_currency(summary['completed_value'])}\n"
        f"• Ongoing value: {format_currency(summary['ongoing_value'])}\n"
        f"• Not started: {format_currency(summary['not_started_value'])}\n"
        f"• Partially completed: {format_currency(summary['partial_completed_value'])}"
    )


def answer_billing(work_orders):
    """Format billing summary."""
    b = billing_summary(work_orders)

    return (
        f"Billing overview:\n"
        f"• Total Work Order value: {format_currency(b['total_value'])}\n"
        f"• Billed: {format_currency(b['billed'])} ({b['billing_rate']:.1f}%)\n"
        f"• Receivable: {format_currency(b['receivable'])}"
    )


def answer_collections(work_orders):
    """Format collections summary using explicit formula."""
    b = billing_summary(work_orders)

    return (
        f"Collections overview:\n"
        f"• Collected so far: {format_currency(b['collected'])}\n"
        f"• Still receivable: {format_currency(b['receivable'])}\n"
        f"• Collection rate: {b['collection_rate']:.1f}%"
    )


def answer_revenue(work_orders):
    """Format revenue summary."""
    b = billing_summary(work_orders)

    return (
        f"Revenue overview:\n"
        f"• Billed: {format_currency(b['billed'])}\n"
        f"• Total Work Order value: {format_currency(b['total_value'])}\n"
        f"• Billing completion: {b['billing_rate']:.1f}%"
    )


def answer_customer_risk(work_orders):
    """Format customer risk analysis with explicit risk reasons."""
    risks = customer_risk_analysis(work_orders)

    if not risks:
        return "I couldn't find enough Work Order data to assess customer risk."

    lines = ["Top Customer Risks:", ""]

    for i, (customer, data) in enumerate(risks[:5], 1):
        issues = []
        if data.get("billing_issues"):
            issues.append(f"{data['billing_issues']} billing issue(s)")
        if data.get("operational_issues"):
            issues.append(f"{data['operational_issues']} operational issue(s)")

        issue_text = ""
        if issues:
            issue_text = " — " + ", ".join(issues)

        lines.append(
            f"{i}. {customer} — {format_currency(data['receivable'])} receivable — "
            f"risk score {data['risk_score']}{issue_text}."
        )

    return "\n".join(lines)


def answer_sector_performance(deals, work_orders):
    """Format overall sector performance table."""
    rows = sector_performance(deals, work_orders)

    if not rows:
        return "No sector-level data is available."

    lines = ["Sector Performance Summary:", ""]

    for i, row in enumerate(rows[:7], 1):
        d_count = row["active_deals"]
        d_text = "1 deal" if d_count == 1 else f"{d_count} deals"
        lines.append(
            f"{i}. {row['sector']} — "
            f"{format_currency(row['active_pipeline'])} active pipeline ({d_text}), "
            f"{format_currency(row['work_order_value'])} Work Orders, "
            f"{row['billing_rate']:.1f}% billed."
        )

    return "\n".join(lines)


def answer_executive_summary(deals, work_orders):
    """Format Business Health Snapshot ensuring 100% metric consistency."""
    p = pipeline_summary(deals)
    b = billing_summary(work_orders)
    w = work_order_summary(work_orders)
    risks = customer_risk_analysis(work_orders)

    deal_str = "1 active deal" if p['active_deals'] == 1 else f"{p['active_deals']} active deals"

    lines = [
        "Business Health Snapshot",
        "",
        f"• Sales pipeline: {format_currency(p['active_pipeline_value'])} across {deal_str}.",
        f"• Revenue billed: {format_currency(b['billed'])} of {format_currency(b['total_value'])} ({b['billing_rate']:.1f}% billed).",
        f"• Collections: {format_currency(b['collected'])} collected; {format_currency(b['receivable'])} receivable ({b['collection_rate']:.1f}% collection rate).",
        f"• Operations: {w['number_of_work_orders']} Work Orders ({format_currency(w['completed_value'])} completed, {format_currency(w['ongoing_value'])} ongoing).",
    ]

    if risks:
        customer, risk = risks[0]
        lines.append(
            f"• Highest customer risk: {customer} (risk score {risk['risk_score']}, {format_currency(risk['receivable'])} receivable)."
        )

    return "\n".join(lines)


# ============================================================
# MAIN AGENT ORCHESTRATOR
# ============================================================

def answer_question(question):
    """
    Main entry point for natural language questions.
    Loads data, parses query, computes metrics, formats answer and appends data quality warning.
    """
    if not question:
        return "Please enter a business question."

    # Clean text of quotes
    question = str(question).strip().strip('"').strip("'")
    if not question:
        return "Please enter a business question."

    # Single explicit data loading path
    deals, work_orders = load_data()

    parsed = parse_query(question)
    intent = parsed.get("intent")

    if intent == "executive_summary":
        answer = answer_executive_summary(deals, work_orders)
    elif intent == "strongest_sector":
        answer = answer_strongest_sector(deals)
    elif intent == "pipeline":
        answer = answer_pipeline(deals, parsed)
    elif intent == "work_orders":
        answer = answer_work_orders(work_orders)
    elif intent == "revenue":
        answer = answer_revenue(work_orders)
    elif intent == "billing":
        answer = answer_billing(work_orders)
    elif intent == "collections":
        answer = answer_collections(work_orders)
    elif intent == "customer_risk":
        answer = answer_customer_risk(work_orders)
    elif intent == "sector_performance":
        answer = answer_sector_performance(deals, work_orders)
    else:
        answer = (
            "I can answer questions about pipeline, billing, collections, "
            "work orders, sectors, and customer risk. "
            "Please ask a business intelligence question on these topics."
        )

    quality = data_quality_summary(deals, work_orders)
    warning = format_data_quality_warning(quality)

    if warning:
        return f"{answer}\n\n{warning}"

    return answer