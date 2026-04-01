import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

from models import (
    calculate_rfm, segment_customers, calculate_clv,
    perform_abc_analysis, forecast_revenue, cohort_retention
)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FinAnaly – E-Commerce Financial Intelligence",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS  (dark glassmorphism theme)
# ═════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Dark canvas ─────────────────────────────────────────────────────── */
    .stApp {
        background: linear-gradient(135deg, #0d0f1e 0%, #111827 50%, #0a0c18 100%);
        color: #e8eaf6;
    }

    /* ── Sidebar ─────────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #13103a 0%, #0e0b2e 60%, #0a0820 100%) !important;
        border-right: 2px solid #7c3aed !important;
        box-shadow: 4px 0 30px rgba(124, 58, 237, 0.25) !important;
        min-width: 260px !important;
    }
    [data-testid="stSidebarContent"] {
        padding: 0 !important;
    }

    /* ── Sidebar logo banner ─────────────────────────────────────────────── */
    .sidebar-logo {
        padding: 28px 20px 16px 20px;
        border-bottom: 1px solid rgba(124,58,237,0.3);
        margin-bottom: 8px;
    }
    .sidebar-logo .brand {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        display: block;
        margin-bottom: 2px;
    }
    .sidebar-logo .tagline {
        font-size: 0.72rem;
        color: #6366f1;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* ── Nav section label ───────────────────────────────────────────────── */
    .nav-label {
        padding: 10px 20px 4px 20px;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #4c4f7a;
    }

    /* ── Nav buttons ─────────────────────────────────────────────────────── */
    .nav-btn {
        display: flex;
        align-items: center;
        gap: 12px;
        width: 100%;
        margin: 2px 0;
        padding: 11px 20px;
        border-radius: 0;
        border: none;
        border-left: 3px solid transparent;
        background: transparent;
        color: #8b8fc9;
        font-size: 0.88rem;
        font-weight: 500;
        cursor: pointer;
        text-align: left;
        transition: all 0.18s ease;
        font-family: 'Inter', sans-serif;
    }
    .nav-btn:hover {
        background: rgba(124,58,237,0.15) !important;
        color: #c4b5fd !important;
        border-left-color: #7c3aed !important;
    }
    .nav-btn.active {
        background: linear-gradient(90deg, rgba(124,58,237,0.25), rgba(37,99,235,0.12)) !important;
        color: #ffffff !important;
        border-left-color: #a78bfa !important;
        font-weight: 600 !important;
        box-shadow: inset 0 0 20px rgba(124,58,237,0.1);
    }
    .nav-btn .nav-icon {
        font-size: 1.1rem;
        min-width: 24px;
        text-align: center;
    }
    .nav-btn .nav-text { flex: 1; }
    .nav-btn.active .nav-arrow { color: #a78bfa; }
    .nav-btn .nav-arrow { color: transparent; font-size: 0.75rem; }

    /* ── Date filter inside sidebar ──────────────────────────────────────── */
    .sidebar-section {
        padding: 14px 20px;
        border-top: 1px solid rgba(124,58,237,0.2);
        margin-top: 8px;
    }
    .sidebar-section-title {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #4c4f7a;
        margin-bottom: 10px;
    }

    /* ── Style streamlit date input in sidebar ───────────────────────────── */
    [data-testid="stSidebar"] [data-testid="stDateInput"] input {
        background: rgba(124,58,237,0.12) !important;
        border: 1px solid rgba(124,58,237,0.4) !important;
        color: #c4b5fd !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
    }
    [data-testid="stSidebar"] label {
        color: #6366f1 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }

    /* ── Sidebar footer / stats strip ────────────────────────────────────── */
    .sidebar-footer {
        padding: 16px 20px 24px;
        border-top: 1px solid rgba(124,58,237,0.2);
        margin-top: 8px;
    }
    .sidebar-stat {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 4px 0;
        font-size: 0.75rem;
        color: #5b5f8a;
    }
    .sidebar-stat .dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: #7c3aed;
        animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.75); }
    }

    /* ── Hide default Streamlit radio (we use custom buttons) ────────────── */
    [data-testid="stSidebar"] [data-testid="stRadio"] { display: none !important; }

    /* ── Hero header ─────────────────────────────────────────────────────── */
    .hero-header {
        background: linear-gradient(90deg, #7c3aed, #2563eb, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 24px;
    }

    /* ── KPI cards ───────────────────────────────────────────────────────── */
    .kpi-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 16px;
        padding: 22px 26px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s, border-color 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: #7c3aed;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: #64748b;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 2.0rem;
        font-weight: 700;
        color: #e8eaf6;
    }
    .kpi-delta {
        font-size: 0.82rem;
        color: #34d399;
        margin-top: 4px;
    }

    /* ── Section divider / badge ─────────────────────────────────────────── */
    .section-badge {
        display: inline-block;
        padding: 3px 14px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        background: linear-gradient(90deg, #7c3aed33, #2563eb33);
        border: 1px solid #7c3aed66;
        color: #a78bfa;
        margin-bottom: 8px;
    }
    .section-title {
        font-size: 1.55rem;
        font-weight: 700;
        color: #e8eaf6;
        margin-bottom: 4px;
    }
    .section-desc {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 24px;
    }

    /* ── Insight box ─────────────────────────────────────────────────────── */
    .insight-box {
        background: rgba(124, 58, 237, 0.12);
        border-left: 3px solid #7c3aed;
        border-radius: 0 12px 12px 0;
        padding: 14px 18px;
        color: #c4b5fd;
        font-size: 0.9rem;
        margin-top: 12px;
    }

    /* ── Plotly chart containers ─────────────────────────────────────────── */
    .stPlotlyChart {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        padding: 8px !important;
    }

    /* ── Streamlit metric tweaks ─────────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 16px !important;
    }

    /* ── Tabs ────────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab"] {
        color: #64748b;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #a78bfa !important;
        border-bottom-color: #7c3aed !important;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }

    /* ── Style actual Streamlit buttons in sidebar as nav items ───────────── */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 12px 20px !important;
        border-radius: 0 !important;
        border: none !important;
        border-left: 3px solid transparent !important;
        background: transparent !important;
        color: #8b8fc9 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.18s ease !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: none !important;
        letter-spacing: 0.01em;
        margin: 1px 0 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(124,58,237,0.18) !important;
        color: #c4b5fd !important;
        border-left-color: #7c3aed !important;
        transform: none !important;
    }
    /* Active nav button (uses a special class set via JS or data-active) */
    [data-testid="stSidebar"] .stButton > button[data-active="true"],
    [data-testid="stSidebar"] .nav-active-btn .stButton > button {
        background: linear-gradient(90deg, rgba(124,58,237,0.28), rgba(37,99,235,0.14)) !important;
        color: #ffffff !important;
        border-left-color: #a78bfa !important;
        font-weight: 700 !important;
    }

    /* ── Active page indicator (rendered above the button) ───────────────── */
    .nav-active-indicator {
        display: none; /* hidden, used only as a CSS signal */
    }
    /* When there's a nav-active-btn sibling, the NEXT st.button gets active style */
    .nav-active-btn + div .stButton > button {
        background: linear-gradient(90deg, rgba(124,58,237,0.30), rgba(37,99,235,0.15)) !important;
        color: #ffffff !important;
        border-left: 3px solid #a78bfa !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ═════════════════════════════════════════════════════════════════════════════
# PLOTLY THEME
# ═════════════════════════════════════════════════════════════════════════════
CHART_BG    = "rgba(0,0,0,0)"
PAPER_BG    = "rgba(0,0,0,0)"
GRID_COLOR  = "rgba(255,255,255,0.06)"
FONT_COLOR  = "#94a3b8"
PALETTE     = ["#7c3aed","#2563eb","#06b6d4","#10b981","#f59e0b","#ef4444","#ec4899","#8b5cf6"]

def base_layout(**kwargs):
    return dict(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="Inter", color=FONT_COLOR),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        margin=dict(l=20, r=20, t=40, b=20),
        **kwargs,
    )

# ═════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Loading retail dataset…")
def load_data():
    path = "data/online_retail_cleaned.parquet"
    if os.path.exists(path):
        return pd.read_parquet(path)
    st.error("⚠️  Data not found. Run `fast_data_loader.py` first.")
    return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# Pre-compute heavy aggregations (accepts df so cache invalidates on date filter change)
@st.cache_data(show_spinner="Crunching RFM…")
def get_rfm(_df):
    rfm  = calculate_rfm(_df)
    segs = segment_customers(rfm)
    with_clv = calculate_clv(segs)
    return with_clv

@st.cache_data(show_spinner="Running ABC classification…")
def get_abc(_df):
    return perform_abc_analysis(_df)

@st.cache_data(show_spinner="Fitting forecast model…")
def get_forecast(_df, periods=16):
    return forecast_revenue(_df, periods=periods)

@st.cache_data(show_spinner="Building cohort table…")
def get_cohort(_df):
    return cohort_retention(_df)

# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR  (custom HTML nav buttons)
# ═════════════════════════════════════════════════════════════════════════════

# ── Page definitions ──────────────────────────────────────────────────────────
NAV_PAGES = [
    {"key": "overview",     "icon": "🏠", "label": "Overview & KPIs",       "tag": "🏠 Overview & KPIs"},
    {"key": "churn",        "icon": "📉", "label": "Churn & RFM",           "tag": "📉 Churn & RFM"},
    {"key": "profitability","icon": "💰", "label": "Profitability (ABC)",   "tag": "💰 Profitability (ABC)"},
    {"key": "forecast",     "icon": "📈", "label": "Revenue Forecast",      "tag": "📈 Revenue Forecast"},
    {"key": "cohort",       "icon": "🔬", "label": "Cohort Retention",      "tag": "🔬 Cohort Retention"},
]

# ── Store selected page in session state ──────────────────────────────────────
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "overview"

# ── Sidebar layout ────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand logo
    st.markdown(
        '<div class="sidebar-logo">'
        '  <span class="brand">💹 FinAnaly</span>'
        '  <span class="tagline">E-Commerce Intelligence</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Navigation label
    st.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)

    # Custom nav buttons via st.button (one per page)
    for nav in NAV_PAGES:
        is_active = (st.session_state.nav_page == nav["key"])
        # Inject active styling via a wrapping container CSS class
        if is_active:
            st.markdown(
                f'<div class="nav-active-btn">'
                f'  <div class="nav-active-indicator">{nav["icon"]}  {nav["label"]}  ›</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        # Always render the real clickable button (styled by CSS above)
        if st.button(f"{nav['icon']}  {nav['label']}", key=f"btn_{nav['key']}",
                     use_container_width=True):
            st.session_state.nav_page = nav["key"]
            st.rerun()

    # Date filter
    st.markdown('<div class="sidebar-section"><div class="sidebar-section-title">Date Filter</div>', unsafe_allow_html=True)
    min_d = df["InvoiceDate"].min().date()
    max_d = df["InvoiceDate"].max().date()
    date_range = st.date_input("", value=(min_d, max_d), min_value=min_d, max_value=max_d, key="date_filter")
    if len(date_range) == 2:
        df = df[(df["InvoiceDate"].dt.date >= date_range[0]) & (df["InvoiceDate"].dt.date <= date_range[1])]
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer stats
    total_rev_sidebar = df["Revenue"].sum()
    total_cust_sidebar = df["Customer ID"].nunique()
    st.markdown(
        f'<div class="sidebar-footer">'
        f'  <div class="sidebar-stat"><span class="dot"></span>Portfolio Project · Data Science</div>'
        f'  <div class="sidebar-stat"><span class="dot"></span>Dataset: UCI Online Retail II</div>'
        f'  <div class="sidebar-stat"><span class="dot"></span>'
        f'  {total_cust_sidebar:,} customers · £{total_rev_sidebar/1e6:.1f}M revenue</div>'
        f'  <div class="sidebar-stat"><span class="dot"></span>Stack: Python · Pandas · Plotly</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ─── Map session state key → page string used in if/elif blocks ───────────────
page = next(n["tag"] for n in NAV_PAGES if n["key"] == st.session_state.nav_page)

# ═════════════════════════════════════════════════════════════════════════════
# HELPER
# ═════════════════════════════════════════════════════════════════════════════
def kpi(label, value, delta=""):
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    st.markdown(
        f'<div class="kpi-card">'
        f'  <div class="kpi-label">{label}</div>'
        f'  <div class="kpi-value">{value}</div>'
        f'  {delta_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

def section(badge, title, desc=""):
    st.markdown(f'<div class="section-badge">{badge}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if desc:
        st.markdown(f'<div class="section-desc">{desc}</div>', unsafe_allow_html=True)

def insight(text):
    st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 – OVERVIEW & KPIs
# ═════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview & KPIs":
    st.markdown('<div class="hero-header">E-Commerce Financial Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">End-to-End Analytics · Revenue · Churn · Profitability · Forecasting</div>', unsafe_allow_html=True)

    # KPI row
    total_rev  = df["Revenue"].sum()
    total_cust = df["Customer ID"].nunique()
    total_ord  = df["Invoice"].nunique()
    aov        = total_rev / max(total_ord, 1)
    total_qty  = df["Quantity"].sum()
    avg_items  = total_qty / max(total_ord, 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Gross Revenue",    f"£{total_rev:,.0f}",  "All transactions")
    with c2: kpi("Unique Customers", f"{total_cust:,}",     "Customer base")
    with c3: kpi("Total Orders",     f"{total_ord:,}",      "Invoice count")
    with c4: kpi("Avg Order Value",  f"£{aov:,.2f}",        "Revenue / order")
    with c5: kpi("Avg Items / Order",f"{avg_items:,.1f}",   "Qty / invoice")

    st.markdown("<br>", unsafe_allow_html=True)

    # Tab layout for charts
    t1, t2, t3 = st.tabs(["📅 Monthly Revenue", "📦 Revenue by Country", "📊 Revenue Distribution"])

    with t1:
        monthly = df.set_index("InvoiceDate").resample("M")["Revenue"].sum().reset_index()
        monthly.columns = ["Month", "Revenue"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Revenue"],
            fill="tozeroy", mode="lines+markers",
            line=dict(color="#7c3aed", width=2.5),
            marker=dict(size=6, color="#a78bfa"),
            fillcolor="rgba(124,58,237,0.15)",
            name="Monthly Revenue",
        ))
        fig.update_layout(**base_layout(title="Monthly Gross Revenue (£)"))
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        country_rev = df.groupby("Country")["Revenue"].sum().nlargest(10).reset_index()
        fig2 = px.bar(
            country_rev, x="Revenue", y="Country", orientation="h",
            color="Revenue", color_continuous_scale=["#2563eb","#7c3aed","#ec4899"],
            text_auto="£,.0f",
        )
        fig2.update_layout(**base_layout(title="Top 10 Countries by Revenue"))
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    with t3:
        fig3 = px.histogram(
            df[df["Revenue"] < df["Revenue"].quantile(0.99)],
            x="Revenue", nbins=80,
            color_discrete_sequence=["#06b6d4"],
        )
        fig3.update_layout(**base_layout(title="Revenue Per Transaction Distribution"))
        st.plotly_chart(fig3, use_container_width=True)

    # Day-of-week heatmap
    st.divider()
    section("HEATMAP", "Revenue by Day & Hour", "Identify peak trading windows across the week.")
    df_tmp = df.copy()
    df_tmp["Hour"]    = df_tmp["InvoiceDate"].dt.hour
    df_tmp["DayName"] = df_tmp["InvoiceDate"].dt.day_name()
    heat = df_tmp.groupby(["DayName", "Hour"])["Revenue"].sum().unstack(fill_value=0)
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heat = heat.reindex([d for d in day_order if d in heat.index])
    fig4 = px.imshow(
        heat, color_continuous_scale="Viridis",
        labels=dict(x="Hour of Day", y="Day", color="Revenue £"),
        aspect="auto",
    )
    fig4.update_layout(**base_layout(title="Revenue Heatmap – Day × Hour"))
    st.plotly_chart(fig4, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 – CHURN & RFM
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📉 Churn & RFM":
    section("CHURN ANALYTICS", "Customer Segmentation & Churn Risk",
            "RFM scoring to detect silent churn in non-contractual e-commerce.")

    rfm_df = get_rfm(df)

    # Summary KPIs
    churning = rfm_df[rfm_df["Segment"].str.contains("At Risk|Sleepers|Lost", case=False)]
    champions = rfm_df[rfm_df["Segment"].str.contains("Champion", case=False)]
    at_risk_rev = churning["MonetaryValue"].sum()
    champ_rev   = champions["MonetaryValue"].sum()

    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi("Total Customers",    f"{len(rfm_df):,}",           "In analysis window")
    with k2: kpi("At-Risk / Churning", f"{len(churning):,}",         f"£{at_risk_rev:,.0f} revenue at stake")
    with k3: kpi("Champions",          f"{len(champions):,}",        f"£{champ_rev:,.0f} revenue")
    with k4: kpi("Avg CLV (3yr)",      f"£{rfm_df['CLV'].mean():,.0f}", "Est. lifetime value")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Customer Distribution by Segment**")
        seg_counts = rfm_df["Segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Count"]
        fig = px.pie(
            seg_counts, names="Segment", values="Count", hole=0.55,
            color_discrete_sequence=PALETTE,
        )
        fig.update_layout(**base_layout(), showlegend=True, legend=dict(font=dict(size=11)))
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Revenue Share by Segment**")
        seg_rev = rfm_df.groupby("Segment")["MonetaryValue"].sum().reset_index()
        fig2 = px.bar(
            seg_rev.sort_values("MonetaryValue", ascending=True),
            x="MonetaryValue", y="Segment", orientation="h",
            color="Segment", text_auto="£,.0f",
            color_discrete_sequence=PALETTE,
        )
        fig2.update_layout(**base_layout(), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Churn Risk Matrix
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Churn Risk Matrix — Recency vs Frequency**")
    fig3 = px.scatter(
        rfm_df,
        x="Recency", y="Frequency",
        color="Segment", size="MonetaryValue",
        size_max=35, opacity=0.75,
        hover_data={"Customer ID": True, "MonetaryValue": True, "Churn_Risk_Score": True, "CLV": True},
        color_discrete_sequence=PALETTE,
        labels={"Recency": "Days Since Last Purchase (↑ = Churning)", "Frequency": "Number of Orders"},
    )
    fig3.update_layout(**base_layout(title="Bubble Size = Monetary Value | Right-Side Customers = Churn Risk"))
    st.plotly_chart(fig3, use_container_width=True)
    insight("Customers in the top-left (High Frequency, Low Recency) are your most loyal. "
            "Customers drifting to the right with falling frequency are silently churning.")

    # CLV Distribution
    st.divider()
    st.markdown("**Customer Lifetime Value Distribution (3-Year Projection)**")
    clv_cap = rfm_df["CLV"].quantile(0.97)
    fig4 = px.histogram(
        rfm_df[rfm_df["CLV"] <= clv_cap], x="CLV", color="Segment",
        nbins=60, barmode="overlay",
        color_discrete_sequence=PALETTE, opacity=0.75,
    )
    fig4.update_layout(**base_layout(title="CLV Distribution by Segment"))
    st.plotly_chart(fig4, use_container_width=True)

    # Table – top at-risk high-value customers
    st.divider()
    section("ACTION TABLE", "High-Value Customers at Churn Risk", "Prioritize these for win-back campaigns.")
    winback = (
        rfm_df[rfm_df["Segment"].str.contains("At Risk|Sleepers", case=False)]
        .nlargest(20, "MonetaryValue")[["Customer ID","Recency","Frequency","MonetaryValue","Churn_Risk_Score","CLV"]]
        .rename(columns={"MonetaryValue": "Revenue (£)", "CLV": "Est. 3yr CLV (£)"})
    )
    st.dataframe(winback.reset_index(drop=True), use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 – PROFITABILITY (ABC)
# ═════════════════════════════════════════════════════════════════════════════
elif page == "💰 Profitability (ABC)":
    section("PARETO ANALYSIS", "Product Profitability – ABC Classification",
            "Identifying the 20% of SKUs that generate 80% of revenue.")

    abc_df = get_abc(df)

    a = abc_df[abc_df["ABC_Class"] == "A – High Value"]
    b = abc_df[abc_df["ABC_Class"] == "B – Medium Value"]
    c = abc_df[abc_df["ABC_Class"] == "C – Low Value"]

    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi("Class A SKUs",   f"{len(a):,}",   "≤70% of cumulative revenue")
    with k2: kpi("Class B SKUs",   f"{len(b):,}",   "70–90% band")
    with k3: kpi("Class C SKUs",   f"{len(c):,}",   "Long-tail, bottom 10%")
    with k4: kpi("Total Products", f"{len(abc_df):,}", "Unique SKUs")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("**Top 25 Products by Revenue**")
        fig = px.bar(
            abc_df.head(25), x="Description", y="Revenue", color="ABC_Class",
            color_discrete_map={
                "A – High Value": "#7c3aed",
                "B – Medium Value": "#2563eb",
                "C – Low Value": "#64748b",
            },
            text_auto="£,.0f",
        )
        fig.update_layout(**base_layout(), xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Revenue Share by ABC Class**")
        class_rev = abc_df.groupby("ABC_Class")["Revenue"].sum().reset_index()
        fig2 = px.pie(
            class_rev, names="ABC_Class", values="Revenue", hole=0.55,
            color_discrete_map={
                "A – High Value": "#7c3aed",
                "B – Medium Value": "#2563eb",
                "C – Low Value": "#64748b",
            },
        )
        fig2.update_layout(**base_layout())
        st.plotly_chart(fig2, use_container_width=True)

    # Pareto curve
    st.markdown("**Pareto Curve – Cumulative Revenue Distribution**")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=list(range(1, len(abc_df)+1)), y=abc_df["Cumulative_Pct"] * 100,
        mode="lines", fill="tozeroy",
        line=dict(color="#7c3aed", width=2.5),
        fillcolor="rgba(124,58,237,0.12)",
        name="Cumulative Revenue %",
    ))
    fig3.add_hline(y=70, line_dash="dash", line_color="#34d399", annotation_text="70% Revenue Threshold (Class A cutoff)")
    fig3.add_hline(y=90, line_dash="dash", line_color="#f59e0b", annotation_text="90% Revenue Threshold (Class B cutoff)")
    fig3.update_layout(**base_layout(
        title="Pareto Curve – Product Revenue Concentration",
        xaxis_title="Number of Products",
        yaxis_title="Cumulative Revenue (%)",
    ))
    st.plotly_chart(fig3, use_container_width=True)
    insight(f"Just {len(a)} SKUs ({len(a)/len(abc_df)*100:.1f}% of catalogue) drive 70% of total revenue. "
            "Focus procurement and marketing budgets on Class A products.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 – REVENUE FORECAST
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📈 Revenue Forecast":
    section("TIME-SERIES", "Revenue Forecasting – Next 16 Weeks",
            "Holt-Winters Exponential Smoothing with trend & seasonal decomposition.")

    hist, fc = get_forecast(df, periods=16)

    has_fc = not fc.empty

    if has_fc:
        predicted_total = fc["Forecasted_Revenue"].sum()
        recent_8 = hist["Revenue"].tail(8).sum()
        growth = ((predicted_total - recent_8) / max(recent_8, 1)) * 100
        peak_wk = fc.loc[fc["Forecasted_Revenue"].idxmax(), "InvoiceDate"]
    else:
        predicted_total = growth = 0
        peak_wk = "N/A"

    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi("Forecast Period",     "16 Weeks",              "Next quarter +")
    with k2: kpi("Projected Revenue",   f"£{predicted_total:,.0f}", "Cumulative forecast")
    with k3: kpi("vs Prior 8w",         f"{growth:+.1f}%",       "Revenue momentum")
    with k4: kpi("Peak Forecast Week",  str(peak_wk)[:10] if has_fc else "—", "Highest projected week")

    st.markdown("<br>", unsafe_allow_html=True)

    # Main forecast chart
    fig = go.Figure()

    # Confidence band (simple ±10%)
    if has_fc:
        fc_band_upper = fc["Forecasted_Revenue"] * 1.10
        fc_band_lower = fc["Forecasted_Revenue"] * 0.90
        fig.add_trace(go.Scatter(
            x=pd.concat([fc["InvoiceDate"], fc["InvoiceDate"][::-1]]),
            y=pd.concat([fc_band_upper, fc_band_lower[::-1]]),
            fill="toself", fillcolor="rgba(239,68,68,0.10)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, name="±10% Confidence Band",
        ))

    fig.add_trace(go.Scatter(
        x=hist["InvoiceDate"], y=hist["Revenue"],
        mode="lines", name="Historical Revenue",
        line=dict(color="#7c3aed", width=2.5),
    ))

    if has_fc:
        fig.add_trace(go.Scatter(
            x=fc["InvoiceDate"], y=fc["Forecasted_Revenue"],
            mode="lines+markers", name="Forecast",
            line=dict(color="#ef4444", width=2.5, dash="dash"),
            marker=dict(size=7, color="#ef4444"),
        ))

    # Add vertical separator — Plotly date axes need ms-epoch or ISO string in this format
    cutoff_ms = int(hist["InvoiceDate"].max().timestamp() * 1000)
    fig.add_vline(x=cutoff_ms, line_dash="dot", line_color="#94a3b8",
                  annotation_text="Forecast Start", annotation_position="top right")

    fig.update_layout(**base_layout(
        title="Weekly Revenue – Historical & 16-Week Forecast",
        xaxis_title="Date", yaxis_title="Revenue (£)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    ))
    st.plotly_chart(fig, use_container_width=True)

    if has_fc:
        insight("The shaded band represents ±10% uncertainty. At seasonal peaks (e.g., Q4), "
                "expect upper-bound scenarios to dominate due to holiday demand.")

    # Weekly trend table
    if has_fc:
        st.divider()
        st.markdown("**Forecast Detail – Week by Week**")
        fc_table = fc.copy()
        fc_table["InvoiceDate"] = fc_table["InvoiceDate"].dt.strftime("%Y-%m-%d")
        fc_table["Forecasted_Revenue"] = fc_table["Forecasted_Revenue"].apply(lambda x: f"£{x:,.0f}")
        fc_table.columns = ["Week Starting", "Forecasted Revenue"]
        st.dataframe(fc_table, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5 – COHORT RETENTION
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🔬 Cohort Retention":
    section("COHORT ANALYSIS", "Monthly Customer Retention Heatmap",
            "Track what percentage of customers from each acquisition cohort return over subsequent months.")

    retention = get_cohort(df)


    fig = px.imshow(
        retention,
        color_continuous_scale=["#0d0f1e","#1e1b4b","#4c1d95","#7c3aed","#a78bfa"],
        labels=dict(x="Months After First Purchase", y="Acquisition Cohort", color="Retention %"),
        text_auto=".0f",
        aspect="auto",
    )
    fig.update_layout(
        **base_layout(title="Cohort Retention (%) – Monthly"),
        coloraxis_colorbar=dict(title="Retention %"),
    )
    st.plotly_chart(fig, use_container_width=True)

    insight("Month 0 is always 100% (first purchase). Darker purple cells in later months indicate "
            "strong repeat-purchase behaviour — a positive signal for long-term revenue health.")

    # Summary stats
    st.divider()
    st.markdown("**Average Retention by Period**")
    avg_ret = retention.mean().reset_index()
    avg_ret.columns = ["Period (Months)", "Avg Retention (%)"]
    fig2 = px.bar(
        avg_ret, x="Period (Months)", y="Avg Retention (%)",
        color="Avg Retention (%)",
        color_continuous_scale=["#1e1b4b","#7c3aed","#a78bfa"],
        text_auto=".1f",
    )
    fig2.update_layout(**base_layout(title="Average Retention Rate Across all Cohorts"))
    fig2.update_coloraxes(showscale=False)
    st.plotly_chart(fig2, use_container_width=True)
