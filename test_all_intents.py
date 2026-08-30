import unittest
from datetime import date

from analytics import (
    pipeline_summary,
    billing_summary,
    collections_summary,
    customer_risk_analysis,
    strongest_sector_analysis,
    data_quality_summary,
    format_data_quality_warning,
    ACTIVE_DEAL_STATUSES,
)
from query_parser import parse_query, get_quarter_date_range
from query_engine import filter_pipeline, pipeline_query
from bi_agent import (
    answer_question,
    format_currency,
    answer_pipeline,
    answer_strongest_sector,
    answer_executive_summary,
)


class TestSkylarkBIAgent(unittest.TestCase):

    def setUp(self):
        self.mock_deals = [
            {
                "deal_name": "Deal 1",
                "deal_status": "Open",
                "sector": "Powerline",
                "deal_value": 5_000_000.0,
                "tentative_close_date": "2026-08-15",
            },
            {
                "deal_name": "Deal 2",
                "deal_status": "On Hold",
                "sector": "Powerline",
                "deal_value": 3_000_000.0,
                "tentative_close_date": "2026-08-20",
            },
            {
                "deal_name": "Deal 3",
                "deal_status": "Open",
                "sector": "Mining",
                "deal_value": 2_000_000.0,
                "tentative_close_date": "2026-08-10",
            },
            {
                "deal_name": "Deal 4",
                "deal_status": "Won",
                "sector": "Mining",
                "deal_value": 10_000_000.0,
                "tentative_close_date": "2026-08-01",
            },
            {
                "deal_name": "Deal 5",
                "deal_status": "Open",
                "sector": None,  # Null sector
                "deal_value": 50_000_000.0,
                "tentative_close_date": "2026-08-01",
            },
            {
                "deal_name": "Deal 6",
                "deal_status": None,  # Missing status
                "sector": "Railways",
                "deal_value": 1_000_000.0,
                "tentative_close_date": "2026-08-01",
            },
        ]

        self.mock_work_orders = [
            {
                "work_order_name": "WO 1",
                "customer_code": "CUST_001",
                "amount_excl_gst": 10_000_000.0,
                "billed_value_excl_gst": 8_000_000.0,
                "collected_amount": 6_000_000.0,
                "amount_receivable": 2_000_000.0,
                "execution_status": "Completed",
                "billing_status": "Completed",
                "invoice_status": "Paid",
                "sector": "Powerline",
            },
            {
                "work_order_name": "WO 2",
                "customer_code": "CUST_002",
                "amount_excl_gst": 5_000_000.0,
                "billed_value_excl_gst": 2_000_000.0,
                "collected_amount": 1_000_000.0,
                "amount_receivable": 1_000_000.0,
                "execution_status": "Pause / Struck",  # Operational issue
                "billing_status": "Pending",  # Billing issue
                "invoice_status": "Overdue",
                "sector": "Mining",
            },
            {
                "work_order_name": "WO 3",
                "customer_code": None,  # Missing customer
                "amount_excl_gst": 1_000_000.0,
                "billed_value_excl_gst": None,
                "collected_amount": None,
                "amount_receivable": None,
                "execution_status": None,  # Missing status
                "sector": "Mining",
            },
        ]

    # 1. Executive Summary & Business Health
    def test_executive_summary_intent(self):
        q = parse_query("How is the business doing?")
        self.assertEqual(q["intent"], "executive_summary")
        ans = answer_executive_summary(self.mock_deals, self.mock_work_orders)
        self.assertIn("Business Health Snapshot", ans)
        self.assertIn("Sales pipeline", ans)

    # 2. Mining Pipeline This Quarter
    def test_mining_pipeline_quarter(self):
        parsed = parse_query("How's our Mining pipeline this quarter?")
        self.assertEqual(parsed["intent"], "pipeline")
        self.assertEqual(parsed["sector"], "Mining")
        ans = answer_pipeline(self.mock_deals, parsed)
        self.assertTrue("Pipeline for Mining" in ans or "No active Mining" in ans)

    # 3. Powerline Pipeline Query
    def test_powerline_pipeline(self):
        parsed = parse_query("What's the Powerline pipeline?")
        self.assertEqual(parsed["intent"], "pipeline")
        self.assertEqual(parsed["sector"], "Powerline")
        res = pipeline_query(self.mock_deals, sector="Powerline")
        self.assertEqual(res["number_of_deals"], 2)  # Open (5M) + On Hold (3M)
        self.assertEqual(res["pipeline_value"], 8_000_000.0)

    # 4. Canonical Active Deal Definition & Summary Consistency
    def test_active_deal_consistency(self):
        p_summary = pipeline_summary(self.mock_deals)
        self.assertEqual(p_summary["active_deals"], 4)
        self.assertEqual(p_summary["active_pipeline_value"], 60_000_000.0)

    # 5. Strongest Sector Analysis
    def test_strongest_sector_analysis(self):
        result = strongest_sector_analysis(self.mock_deals)
        self.assertEqual(result["strongest_sector"], "Powerline")
        self.assertEqual(result["strongest_pipeline_value"], 8_000_000.0)
        self.assertEqual(result["strongest_deal_count"], 2)
        self.assertEqual(result["missing_sector_deals"], 1)

    # 6. Strongest Sector Answer Formatting
    def test_strongest_sector_answer(self):
        ans = answer_strongest_sector(self.mock_deals)
        self.assertIn("Strongest Pipeline Sector: Powerline", ans)
        self.assertIn("₹8.00M across 2 active deals", ans)
        self.assertIn("1. Powerline — ₹8.00M", ans)

    # 7. No-Data Contract
    test_no_data_contract = None
    def test_no_data_contract_case(self):
        parsed = {
            "intent": "pipeline",
            "sector": "Mining",
            "quarter": "Q3",
            "year": 2030,
            "start_date": date(2030, 7, 1),
            "end_date": date(2030, 9, 30),
        }
        ans = answer_pipeline(self.mock_deals, parsed)
        self.assertIn("No active Mining opportunities were found for Q3 2030", ans)
        self.assertIn("so the pipeline is ₹0 across 0 active deals.", ans)

    # 8. Dynamic Date Range Parsing
    def test_date_range_parsing(self):
        start, end = get_quarter_date_range("Q3", 2026)
        self.assertEqual(start, date(2026, 7, 1))
        self.assertEqual(end, date(2026, 9, 30))

    # 9. Case & Punctuation Normalization
    def test_query_variations(self):
        q1 = parse_query("MINING pipeline q3 2026?")
        self.assertEqual(q1["intent"], "pipeline")
        self.assertEqual(q1["sector"], "Mining")

        q2 = parse_query("Which sector has the strongest pipeline?")
        self.assertEqual(q2["intent"], "strongest_sector")

    # 10. Unsupported Question Handling
    def test_unsupported_questions(self):
        q = parse_query("What is the weather?")
        self.assertEqual(q["intent"], "unsupported")

        ans = answer_question("What is the weather?")
        self.assertIn("I can answer questions about pipeline, billing, collections", ans)

    # 11. Collections Formula
    def test_collections_summary(self):
        b = collections_summary(self.mock_work_orders)
        self.assertEqual(b["collected"], 7_000_000.0)
        self.assertEqual(b["receivable"], 3_000_000.0)
        self.assertAlmostEqual(b["collection_rate"], 70.0)

    # 12. Customer Risk Ranking & Explanations
    def test_customer_risk(self):
        risks = customer_risk_analysis(self.mock_work_orders)
        top_cust, top_data = risks[0]
        self.assertEqual(top_cust, "CUST_002")
        self.assertEqual(top_data["billing_issues"], 2)
        self.assertEqual(top_data["operational_issues"], 1)

    # 13. Missing Data & Data Quality Warning Formatting
    def test_data_quality_formatting(self):
        quality = data_quality_summary(self.mock_deals, self.mock_work_orders)
        warning = format_data_quality_warning(quality)
        self.assertIn("1 deal has a missing status", warning)
        self.assertIn("1 deal has a missing sector values", warning)

    # 14. Dashboard ↔ Agent Consistency
    def test_dashboard_agent_consistency(self):
        p = pipeline_summary(self.mock_deals)
        formatted_val = format_currency(p["active_pipeline_value"])
        formatted_deals = str(p["active_deals"])

        ans = answer_executive_summary(self.mock_deals, self.mock_work_orders)
        self.assertIn(formatted_val, ans)
        self.assertIn(f"{formatted_deals} active deals", ans)

    # 15. Empty Dataset Resilience
    def test_empty_dataset(self):
        p = pipeline_summary([])
        self.assertEqual(p["active_pipeline_value"], 0.0)
        self.assertEqual(p["active_deals"], 0)


if __name__ == "__main__":
    unittest.main()
