# Skylark BI Intelligence Agent

A deterministic Business Intelligence agent over live Monday.com data (Deals and Work Orders boards) with a Streamlit interface.

---

## 🏗️ Architecture Overview

```text
User Question
    ↓
Query Parser (Intent & Dynamic Date Bounds)
    ↓
Normalized Monday.com Data (Deals + Work Orders)
    ↓
Deterministic Python Analytics (analytics.py)
    ↓
BI Agent Formatter (bi_agent.py)
    ↓
Streamlit UI (app.py)
```

The agent separates natural-language intent recognition from business logic calculations. Numerical figures are computed directly from live normalized source data.

---

## ⚡ Supported Intent Categories

- **Executive Summary / Business Health**: `"How is the business doing?"`
- **Strongest Sector Ranking**: `"Which sector has the strongest pipeline?"`
- **Pipeline Analysis**: `"How's our Mining pipeline this quarter?"` / `"What's the Powerline pipeline?"`
- **Collections & Receivables**: `"How much have we collected?"`
- **Customer Risk Exposure**: `"Which customers are the biggest risk?"`
- **Billing Realization**: `"What's our billing situation?"`
- **Work Orders Operations**: `"How are our work orders doing?"`

---

## 🛠️ Setup Instructions

### 1. Environment Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configuration (`.env`)

Create a `.env` file in the root directory:

```env
MONDAY_API_TOKEN=your_monday_api_v2_token
DEALS_BOARD_ID=your_deals_board_id
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
```

---

## 🚀 Running the Application

Start the Streamlit dashboard:

```bash
streamlit run app.py
```

---

## 🧪 Running Automated Tests

Run the comprehensive unit test suite covering all 12+ intent scenarios, data quality formatting, and dashboard consistency:

```bash
python -m unittest test_all_intents.py
python test_quality.py
```

---

## 📄 Key Deliverables & Documentation

- [DECISION_LOG.md](DECISION_LOG.md): Detailed 2-page decision log covering assumptions, active deal definitions, date range calculations, messy data strategy, and leadership update interpretation.
