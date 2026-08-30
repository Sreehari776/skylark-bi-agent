from monday_client import get_deals, get_work_orders
from data_normalizer import normalize_deal, normalize_work_order

# ============================================================
# CANONICAL DEFINITIONS
# ============================================================

ACTIVE_DEAL_STATUSES = {"open", "on hold"}


def _text(value):
    """Clean text helper for case-insensitive matching."""
    return (value or "").strip().lower()


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """
    Centralized data-loading function.
    Loads live Monday.com data and normalizes into canonical dict structures.

    Returns:
        deals (list of dict), work_orders (list of dict)
    """
    _, raw_deals = get_deals()
    _, raw_work_orders = get_work_orders()

    deals = [normalize_deal(item) for item in raw_deals]
    work_orders = [normalize_work_order(item) for item in raw_work_orders]

    return deals, work_orders


# ============================================================
# PIPELINE ANALYTICS
# ============================================================

def pipeline_summary(deals):
    """
    Summarize sales pipeline using the canonical ACTIVE_DEAL_STATUSES definition.
    Active Deals = status in {"open", "on hold"}.
    """
    totals = {
        "total_deal_value": 0.0,
        "active_pipeline_value": 0.0,
        "on_hold_value": 0.0,
        "won_value": 0.0,
        "dead_value": 0.0,
        "missing_status_value": 0.0,
        "total_deals": len(deals),
        "active_deals": 0,
        "open_deals": 0,
        "on_hold_deals": 0,
        "won_deals": 0,
        "dead_deals": 0,
        "missing_status_deals": 0,
    }

    for deal in deals:
        value = deal.get("deal_value") or 0.0
        status = _text(deal.get("deal_status"))
        totals["total_deal_value"] += value

        if status in ACTIVE_DEAL_STATUSES:
            totals["active_pipeline_value"] += value
            totals["active_deals"] += 1
            if status == "open":
                totals["open_deals"] += 1
            elif status == "on hold":
                totals["on_hold_value"] += value
                totals["on_hold_deals"] += 1
        elif status == "won":
            totals["won_value"] += value
            totals["won_deals"] += 1
        elif status == "dead":
            totals["dead_value"] += value
            totals["dead_deals"] += 1
        else:
            totals["missing_status_value"] += value
            totals["missing_status_deals"] += 1

    return totals


def pipeline_by_sector(deals):
    """Group total deal value by sector."""
    result = {}
    for deal in deals:
        sector = deal.get("sector") or "Unknown"
        result[sector] = result.get(sector, 0.0) + (deal.get("deal_value") or 0.0)
    return result


def active_pipeline_by_sector(deals):
    """Group active pipeline value by sector."""
    result = {}
    for deal in deals:
        if _text(deal.get("deal_status")) not in ACTIVE_DEAL_STATUSES:
            continue
        sector = deal.get("sector") or "Unknown"
        result[sector] = result.get(sector, 0.0) + (deal.get("deal_value") or 0.0)
    return result


def strongest_sector_analysis(deals):
    """
    Identify the sector with the strongest active pipeline.
    Ignores missing/null/Unknown sector values from winning calculation,
    reporting missing-sector data separately.
    """
    sector_data = {}
    missing_sector_deals = 0
    missing_sector_value = 0.0

    for deal in deals:
        status = _text(deal.get("deal_status"))
        if status not in ACTIVE_DEAL_STATUSES:
            continue

        sector = deal.get("sector")
        val = deal.get("deal_value") or 0.0

        if not sector or _text(sector) in {"unknown", "none", ""}:
            missing_sector_deals += 1
            missing_sector_value += val
            continue

        if sector not in sector_data:
            sector_data[sector] = {"pipeline_value": 0.0, "active_deals": 0}

        sector_data[sector]["pipeline_value"] += val
        sector_data[sector]["active_deals"] += 1

    if not sector_data:
        return {
            "strongest_sector": None,
            "strongest_pipeline_value": 0.0,
            "strongest_deal_count": 0,
            "sector_rankings": [],
            "missing_sector_deals": missing_sector_deals,
            "missing_sector_value": missing_sector_value,
        }

    sorted_sectors = sorted(
        [
            {
                "sector": sec,
                "pipeline_value": info["pipeline_value"],
                "active_deals": info["active_deals"],
            }
            for sec, info in sector_data.items()
        ],
        key=lambda x: (x["pipeline_value"], x["active_deals"]),
        reverse=True,
    )

    top = sorted_sectors[0]

    return {
        "strongest_sector": top["sector"],
        "strongest_pipeline_value": top["pipeline_value"],
        "strongest_deal_count": top["active_deals"],
        "sector_rankings": sorted_sectors,
        "missing_sector_deals": missing_sector_deals,
        "missing_sector_value": missing_sector_value,
    }


# ============================================================
# WORK ORDERS & BILLING ANALYTICS
# ============================================================

def work_order_summary(work_orders):
    """Summarize Work Order execution statuses and amounts."""
    result = {
        "total_work_order_value": 0.0,
        "completed_value": 0.0,
        "ongoing_value": 0.0,
        "not_started_value": 0.0,
        "partial_completed_value": 0.0,
        "paused_value": 0.0,
        "pending_client_value": 0.0,
        "missing_status_value": 0.0,
        "number_of_work_orders": len(work_orders),
    }

    for wo in work_orders:
        value = wo.get("amount_excl_gst") or 0.0
        status = _text(wo.get("execution_status"))
        result["total_work_order_value"] += value

        if status == "completed":
            result["completed_value"] += value
        elif status in {"ongoing", "executed until current month"}:
            result["ongoing_value"] += value
        elif status == "not started":
            result["not_started_value"] += value
        elif status == "partial completed":
            result["partial_completed_value"] += value
        elif status == "pause / struck":
            result["paused_value"] += value
        elif status == "details pending from client":
            result["pending_client_value"] += value
        else:
            result["missing_status_value"] += value

    return result


def billing_summary(work_orders):
    """
    Summarize financial billing and collections.
    Formula: collection_rate = collected / (collected + receivable) if (collected + receivable) > 0 else 0
    """
    total = sum(w.get("amount_excl_gst") or 0.0 for w in work_orders)
    billed = sum(w.get("billed_value_excl_gst") or 0.0 for w in work_orders)
    receivable = sum(w.get("amount_receivable") or 0.0 for w in work_orders)
    collected = sum(w.get("collected_amount") or 0.0 for w in work_orders)

    denom = collected + receivable

    return {
        "total_value": total,
        "billed": billed,
        "receivable": receivable,
        "collected": collected,
        "billing_rate": (billed / total * 100.0) if total else 0.0,
        "collection_rate": (collected / denom * 100.0) if denom > 0 else 0.0,
    }


def collections_summary(work_orders):
    """Explicit helper for collections query intent."""
    return billing_summary(work_orders)


def customer_risk_analysis(work_orders):
    """
    Rank customers using deterministic risk scoring:
    - Unpaid receivable exposure
    - Billing issues (billing_status or invoice_status pending / update required)
    - Operational issues (execution_status paused / details pending)
    """
    customers = {}

    for wo in work_orders:
        customer = wo.get("customer_code") or "Unknown"
        data = customers.setdefault(customer, {
            "receivable": 0.0,
            "billing_issues": 0,
            "operational_issues": 0,
            "work_orders": 0,
        })

        data["work_orders"] += 1
        data["receivable"] += wo.get("amount_receivable") or 0.0

        billing_status = _text(wo.get("billing_status"))
        invoice_status = _text(wo.get("invoice_status"))

        if billing_status in {"update required", "pending"}:
            data["billing_issues"] += 1
        if invoice_status in {"pending", "overdue"}:
            data["billing_issues"] += 1

        execution_status = _text(wo.get("execution_status"))
        if execution_status in {"pause / struck", "details pending from client"}:
            data["operational_issues"] += 1

    for customer, data in customers.items():
        score = 0
        if data["receivable"] > 0:
            score += 2
        if data["receivable"] >= 5_000_000:
            score += 3
        elif data["receivable"] >= 1_000_000:
            score += 2
        score += data["billing_issues"] + data["operational_issues"]
        data["risk_score"] = score

    return sorted(
        customers.items(),
        key=lambda item: (item[1]["risk_score"], item[1]["receivable"]),
        reverse=True,
    )


def sector_performance(deals, work_orders):
    """Return comparable sector-level pipeline and Work Order metrics."""
    sectors = set()
    sectors.update(d.get("sector") for d in deals if d.get("sector"))
    sectors.update(w.get("sector") for w in work_orders if w.get("sector"))
    sectors.discard("Unknown")
    sectors.discard(None)

    rows = []
    for sector in sorted(sectors):
        active_pipeline = sum(
            d.get("deal_value") or 0.0
            for d in deals
            if d.get("sector") == sector
            and _text(d.get("deal_status")) in ACTIVE_DEAL_STATUSES
        )
        active_deals = sum(
            1
            for d in deals
            if d.get("sector") == sector
            and _text(d.get("deal_status")) in ACTIVE_DEAL_STATUSES
        )
        won = sum(
            d.get("deal_value") or 0.0
            for d in deals
            if d.get("sector") == sector and _text(d.get("deal_status")) == "won"
        )
        wo_value = sum(
            w.get("amount_excl_gst") or 0.0
            for w in work_orders
            if w.get("sector") == sector
        )
        billed = sum(
            w.get("billed_value_excl_gst") or 0.0
            for w in work_orders
            if w.get("sector") == sector
        )
        rows.append({
            "sector": sector,
            "active_pipeline": active_pipeline,
            "active_deals": active_deals,
            "won_value": won,
            "work_order_value": wo_value,
            "billed_value": billed,
            "billing_rate": (billed / wo_value * 100.0) if wo_value else 0.0,
        })

    return sorted(rows, key=lambda r: r["active_pipeline"], reverse=True)


# ============================================================
# DATA QUALITY
# ============================================================

def data_quality_summary(deals, work_orders):
    """Count missing fields that can distort BI results."""
    return {
        "missing_deal_status": sum(1 for d in deals if not d.get("deal_status")),
        "missing_deal_sector": sum(1 for d in deals if not d.get("sector")),
        "missing_wo_status": sum(1 for w in work_orders if not w.get("execution_status")),
        "missing_customer": sum(1 for w in work_orders if not w.get("customer_code")),
        "missing_receivable": sum(
            1 for w in work_orders if w.get("amount_receivable") is None
        ),
    }


def format_data_quality_warning(quality):
    """Format data quality dictionary into professional, grammatically correct English string."""
    warnings = []

    if quality.get("missing_deal_status"):
        count = quality["missing_deal_status"]
        noun = "deal" if count == 1 else "deals"
        verb = "has a" if count == 1 else "have"
        warnings.append(f"{count} {noun} {verb} missing status")

    if quality.get("missing_deal_sector"):
        count = quality["missing_deal_sector"]
        noun = "deal" if count == 1 else "deals"
        verb = "has a" if count == 1 else "have"
        warnings.append(f"{count} {noun} {verb} missing sector values")

    if quality.get("missing_wo_status"):
        count = quality["missing_wo_status"]
        noun = "Work Order" if count == 1 else "Work Orders"
        verb = "has a" if count == 1 else "have"
        warnings.append(f"{count} {noun} {verb} missing execution status")

    if quality.get("missing_customer"):
        count = quality["missing_customer"]
        noun = "Work Order" if count == 1 else "Work Orders"
        verb = "has a" if count == 1 else "have"
        warnings.append(f"{count} {noun} {verb} missing customer values")

    if quality.get("missing_receivable"):
        count = quality["missing_receivable"]
        noun = "Work Order" if count == 1 else "Work Orders"
        verb = "has" if count == 1 else "have"
        warnings.append(f"{count} {noun} {verb} missing receivable data")

    if not warnings:
        return ""

    return "⚠️ Data quality: " + "; ".join(warnings) + "."
