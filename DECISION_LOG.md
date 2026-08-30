Decision Log: Skylark Monday.com BI Intelligence Agent
Executive Overview

The Skylark Business Intelligence Agent is a deterministic intelligence layer built over live Monday.com data (Deals and Work Orders boards). This document outlines key architecture decisions, data modeling assumptions, financial trade offs, handling of real world messy data, and our interpretation of leadership updates.

1. Key Assumptions & Canonical Data Modeling
1.1 Canonical Active Deal Definition

Problem: In raw business data, deal statuses include Open, On Hold, Won, Dead, and missing values. Discrepancies often arise when active pipeline metrics use different status filters across dashboards and reports.

Decision: We established ONE canonical definition:

Active Deal Statuses = Open, On Hold

Impact:

active_pipeline_value and active_deals count use this exact definition universally across the Streamlit dashboard, executive summaries, sector rankings, and dynamic query responses.
Guarantees 100% metric consistency across all UI components (for example, ₹688.15M active pipeline across 51 active deals).
1.2 Date Interpretation & Dynamic Period Filtering

Problem: Deals contain multiple date fields (tentative_close_date, actual_close_date, created_date). Hardcoding date strings like Q3 2026 reduces flexibility and risks false query matches.

Decision:

Pipeline timing relies primarily on tentative_close_date (with fallback to created_date if unassigned).
All period queries (Q1 to Q4, this quarter, this month, this year) are dynamically converted into concrete date bounds (start date, end date).
Date filtering evaluates start_date <= tentative_close_date <= end_date.
1.3 Collections & Financial Formulas

Formula: Collection Rate is explicitly defined as:

Collection Rate = Collected Amount / (Collected Amount + Receivable Amount) × 100

Impact: Provides clear visibility into cash realization vs. outstanding exposure.

2. Technical Architecture & Trade Offs
2.1 Deterministic Python Analytics vs. LLM Calculations

Trade Off:

LLM Calculations: Using Large Language Models to calculate financial figures or run SQL queries directly on raw text introduces risks of hallucinations, math errors, and non reproducible answers.
Chosen Architecture (Deterministic Layer): We separate Intent Understanding from Business Calculations. The query parser extracts structured intents and parameters; pure Python functions in analytics.py perform all computations.

Justification: For executive leadership, financial calculations must be 100% accurate, predictable, and explainable.

2.2 Explicit Data Loading Pipeline

Single Path: monday_client.py → data_normalizer.py → analytics.py (load_data()) → query_engine.py → bi_agent.py → app.py.

Justification: Eliminates fragile dynamic import guessing and ensures all components use the identical data normalization pipeline.

3. Data Resilience & Messy Data Treatment
3.1 Data Normalization Strategy
Dates: Standardized using multi format parsing
Text & Numbers: Stripped of whitespace, case normalized, and safely cast to floats/nulls.
Null / Missing Sectors: Missing sectors are excluded from winning Strongest Sector calculations to prevent Unknown records from winning rankings.
3.2 Dynamic Data Quality Warnings

Rather than silently filling or hiding incomplete data, the agent dynamically appends grammatically correct warning banners to query responses:

Data quality: 1 deal has a missing status; 8 deals have missing sector values; 4 Work Orders have missing execution status.

3.3 No Data Contract

When zero records match a filtered query, the system explicitly returns:

No active Mining opportunities were found for Q3 2026, so the pipeline is ₹0 across 0 active deals.

Never treats zero as a system failure or invents dummy figures.
4. Interpretation of Leadership Updates
4.1 Founder Level Executive Summaries

We interpreted "preparing data for leadership updates" as providing an immediate, high density Business Health Snapshot that synthesizes performance across all operational silos:

Sales Pipeline: Total active value and deal count.
Revenue & Billing Realization: Billed amount vs. total work order value.
Collections & Cash Realization: Collected cash vs. receivables and collection rate.
Operations Breakdown: Completed vs. ongoing work orders.
Customer Risk Exposure: Top high risk client accounts flagged with reasons.