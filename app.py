import streamlit as st
from datetime import datetime

from bi_agent import (
    answer_question,
    format_currency,
)
from analytics import (
    load_data,
    pipeline_summary,
    billing_summary,
    work_order_summary,
)

# Page setup with wide layout
st.set_page_config(
    page_title="Skylark BI Intelligence Agent",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject Skylark Drones Aerospace Theme CSS (Sky Cyan, Midnight Navy, Telemetry Blue)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        max-width: 1200px;
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
    }

    /* Skylark Aerospace Hero Container */
    .hero-banner {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(15, 23, 42, 0.9) 60%, rgba(9, 13, 22, 0.95) 100%);
        border: 1px solid rgba(14, 165, 233, 0.3);
        border-radius: 16px;
        padding: 1.75rem 2rem;
        margin-top: 0 !important;
        margin-bottom: 1.75rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px -10px rgba(14, 165, 233, 0.25);
    }
    .hero-title {
        font-size: 2.35rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #38bdf8 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.4rem 0;
        line-height: 1.2;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0;
    }

    /* Custom KPI Cards - Skylark Color Palette */
    .kpi-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px -5px rgba(14, 165, 233, 0.2);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
    }
    .kpi-sky::before { background: linear-gradient(90deg, #0284c7, #38bdf8); }
    .kpi-emerald::before { background: linear-gradient(90deg, #059669, #34d399); }
    .kpi-amber::before { background: linear-gradient(90deg, #d97706, #fbbf24); }
    .kpi-cyan::before { background: linear-gradient(90deg, #0891b2, #22d3ee); }

    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #f8fafc;
    }

    /* Query Section Styling */
    .section-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-top: 1.75rem;
        margin-bottom: 0.75rem;
    }

    /* Answer Container Styling */
    .answer-card {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.12) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        margin-top: 1.25rem;
        box-shadow: 0 10px 30px -10px rgba(14, 165, 233, 0.2);
    }
    .answer-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .answer-body {
        font-size: 1.05rem;
        line-height: 1.7;
        color: #f1f5f9;
        white-space: pre-line;
    }

    /* Streamlit Input Custom Overrides */
    .stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #0284c7 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.25) !important;
    }
    
    /* Primary Action Button */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
        border: none !important;
        color: #ffffff !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Banner
st.markdown(
    """
    <div class="hero-banner">
      <h1 class="hero-title">Skylark Executive BI Agent</h1>
      <p class="hero-subtitle">Aerial Intelligence & Spatial Analytics • Founder-level queries across deals, work orders, revenue, and customer risks.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Fetch Centralized Metrics
try:
    deals, work_orders = load_data()
    p = pipeline_summary(deals)
    b = billing_summary(work_orders)
    w = work_order_summary(work_orders)

    # Render Custom Glassmorphic KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-sky">
              <div class="kpi-label">Active Sales Pipeline</div>
              <div class="kpi-value">{format_currency(p["active_pipeline_value"])}</div>
              <div style="font-size: 0.78rem; color: #38bdf8; margin-top: 0.3rem;">{p['active_deals']} Active Deals</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card kpi-emerald">
              <div class="kpi-label">Billed Revenue</div>
              <div class="kpi-value">{format_currency(b["billed"])}</div>
              <div style="font-size: 0.78rem; color: #34d399; margin-top: 0.3rem;">{b['billing_rate']:.1f}% Billed Realization</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card kpi-amber">
              <div class="kpi-label">Outstanding Receivable</div>
              <div class="kpi-value">{format_currency(b["receivable"])}</div>
              <div style="font-size: 0.78rem; color: #fbbf24; margin-top: 0.3rem;">{b['collection_rate']:.1f}% Collection Rate</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-cyan">
              <div class="kpi-label">Work Orders Executed</div>
              <div class="kpi-value">{w['number_of_work_orders']:,}</div>
              <div style="font-size: 0.78rem; color: #22d3ee; margin-top: 0.3rem;">{format_currency(w['completed_value'])} Completed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

except Exception as exc:
    st.error("Could not fetch live Monday.com metrics. Please check `.env` API credentials.")

# Suggested Questions Section
st.markdown('<div class="section-header">💡 Try Asking a Founder Question</div>', unsafe_allow_html=True)

examples = [
    "How is the business doing?",
    "Which sector has the strongest pipeline?",
    "How's our Mining pipeline this quarter?",
    "How much have we collected?",
    "Which customers are the biggest risk?",
    "What's our billing situation?",
]

cols = st.columns(2)
for i, example in enumerate(examples):
    if cols[i % 2].button(example, use_container_width=True, key=f"example_{i}"):
        st.session_state["question"] = example.strip().strip('"').strip("'")

st.markdown('<div class="section-header">💬 Ask the Intelligence Agent</div>', unsafe_allow_html=True)

question = st.text_input(
    "Enter your business question:",
    value=st.session_state.get("question", "").strip().strip('"').strip("'"),
    placeholder="e.g. Which sector has the strongest pipeline?",
    label_visibility="collapsed",
)

if st.button("🛸 Run BI Query", type="primary", use_container_width=False):
    clean_q = question.strip().strip('"').strip("'")
    if not clean_q:
        st.warning("Please enter a business question.")
    else:
        with st.spinner("Analyzing business records..."):
            try:
                result = answer_question(clean_q)
                answer, _, warning = result.partition("\n\n⚠️ Data quality:")

                # Render Translucent Glass Answer Card
                st.markdown(
                    f"""
                    <div class="answer-card">
                      <div class="answer-header">
                        <span>🛰️ Skylark Intelligence Answer</span>
                      </div>
                      <div class="answer-body">{answer}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if warning:
                    st.warning("Data quality: " + warning)

                st.caption(
                    f"Answer computed from data • "
                    f"{datetime.now().strftime('%d %b %Y, %H:%M')}"
                )

            except Exception as exc:
                st.error(
                    "The agent could not complete the request. "
                    "Check the configuration."
                )
                st.exception(exc)

# Minimal Aerospace Footer
st.markdown(
    """
    <hr style="border: 0; border-top: 1px solid rgba(56, 189, 248, 0.15); margin: 3.5rem 0 1rem 0;">
    <div style="font-size: 0.82rem; color: #64748b; text-align: center;">
      Skylark Drones Technical Assignment • Aerial Intelligence Layer
    </div>
    """,
    unsafe_allow_html=True,
)
