from analytics import (
    pipeline_summary,
    billing_summary,
    customer_risk_analysis,
    data_quality_summary,
)
from query_parser import parse_query


def test_parser():
    assert parse_query("How is the business doing?")["intent"] == "executive_summary"
    assert parse_query("How much have we collected?")["intent"] == "collections"
    assert parse_query("Which customers are the biggest risk?")["intent"] == "customer_risk"
    q = parse_query("Mining pipeline this quarter")
    assert q["intent"] == "pipeline"
    assert q["sector"] == "Mining"


def test_analytics():
    deals = [
        {"deal_value": 2_000_000, "deal_status": "Open", "sector": "Mining"},
        {"deal_value": 1_000_000, "deal_status": "Won", "sector": "Powerline"},
        {"deal_value": 500_000, "deal_status": None, "sector": None},
    ]
    work_orders = [
        {
            "amount_excl_gst": 10_000_000,
            "billed_value_excl_gst": 5_000_000,
            "collected_amount": 4_000_000,
            "amount_receivable": 1_000_000,
            "customer_code": "C1",
            "execution_status": "Ongoing",
            "billing_status": "Pending",
            "invoice_status": "Pending",
        },
    ]

    p = pipeline_summary(deals)
    assert p["active_pipeline_value"] == 2_000_000
    assert p["won_value"] == 1_000_000

    b = billing_summary(work_orders)
    assert b["billed"] == 5_000_000
    assert b["receivable"] == 1_000_000

    risks = customer_risk_analysis(work_orders)
    assert risks[0][0] == "C1"

    q = data_quality_summary(deals, work_orders)
    assert q["missing_deal_status"] == 1
    assert q["missing_deal_sector"] == 1


if __name__ == "__main__":
    test_parser()
    test_analytics()
    print("Selection checks passed.")
