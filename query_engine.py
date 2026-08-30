from datetime import datetime, date
from analytics import ACTIVE_DEAL_STATUSES


def parse_date(date_string):
    """Convert YYYY-MM-DD string to a date object safely."""
    if not date_string:
        return None

    try:
        return datetime.strptime(str(date_string).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def filter_pipeline(
    deals,
    sector=None,
    start_date=None,
    end_date=None
):
    """
    Filter deals for Active Pipeline.
    Canonical Active Statuses: Open + On Hold.
    Pipeline Date Field: tentative_close_date (used for pipeline timing).
    """
    results = []

    for deal in deals:
        status = (deal.get("deal_status") or "").strip().lower()

        # Active pipeline filter
        if status not in ACTIVE_DEAL_STATUSES:
            continue

        # Sector filter
        if sector:
            deal_sector = (deal.get("sector") or "").strip().lower()
            if deal_sector != sector.strip().lower():
                continue

        # Date range filter against tentative_close_date
        if start_date or end_date:
            close_date = parse_date(deal.get("tentative_close_date"))

            # Fall back to created_date if tentative_close_date is unassigned
            if close_date is None:
                close_date = parse_date(deal.get("created_date"))

            if close_date is None:
                continue

            if start_date and close_date < start_date:
                continue

            if end_date and close_date > end_date:
                continue

        results.append(deal)

    return results


def pipeline_query(
    deals,
    sector=None,
    quarter=None,
    year=None,
    start_date=None,
    end_date=None
):
    """Return structured pipeline calculations."""
    results = filter_pipeline(
        deals,
        sector=sector,
        start_date=start_date,
        end_date=end_date
    )

    total_value = sum(
        deal.get("deal_value") or 0.0
        for deal in results
    )

    return {
        "number_of_deals": len(results),
        "pipeline_value": total_value,
        "deals": results,
        "sector": sector,
        "quarter": quarter,
        "year": year,
    }