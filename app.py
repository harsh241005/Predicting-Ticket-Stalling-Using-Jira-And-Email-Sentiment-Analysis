"""
=============================================================================
SOCIO-TECHNICAL HEALTH MONITOR — Dashboard v3 (Dark Glass)
=============================================================================
Glassmorphism-meets-developer aesthetic for team managers.

Design direction: dark glass with cyan + amber accents
  - Deep navy base with ambient color glows
  - Semi-transparent cards with backdrop blur
  - Monospace for data/labels, Inter for body, Fraunces for display
  - Cyan as primary accent, amber for caution, red/green for risk states

USAGE:
    streamlit run dashboard.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import os
import re

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Ticket Health Monitor",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# DESIGN SYSTEM — CSS
# ============================================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
    :root {
        /* Base */
        --bg: #0a0e1a;
        --bg-deeper: #060912;
        --bg-soft: #0f1524;

        /* Glass */
        --glass-bg: rgba(255, 255, 255, 0.035);
        --glass-bg-hover: rgba(255, 255, 255, 0.055);
        --glass-border: rgba(255, 255, 255, 0.09);
        --glass-border-bright: rgba(255, 255, 255, 0.18);

        /* Text */
        --text: #f5f7fa;
        --text-soft: rgba(245, 247, 250, 0.7);
        --text-mute: rgba(245, 247, 250, 0.45);
        --text-dim: rgba(245, 247, 250, 0.25);

        /* Accents */
        --cyan: #22d3ee;
        --cyan-soft: rgba(34, 211, 238, 0.15);
        --cyan-glow: rgba(34, 211, 238, 0.35);
        --amber: #fbbf24;
        --amber-soft: rgba(251, 191, 36, 0.15);
        --amber-glow: rgba(251, 191, 36, 0.3);

        /* Risk signals */
        --risk-red: #ef4444;
        --risk-red-glow: rgba(239, 68, 68, 0.35);
        --risk-red-bg: rgba(239, 68, 68, 0.08);
        --risk-amber: #fbbf24;
        --risk-amber-glow: rgba(251, 191, 36, 0.3);
        --risk-amber-bg: rgba(251, 191, 36, 0.08);
        --risk-green: #10b981;
        --risk-green-glow: rgba(16, 185, 129, 0.3);
        --risk-green-bg: rgba(16, 185, 129, 0.08);

        /* Fonts */
        --font-display: 'JetBrains Mono', ui-monospace, monospace;
        --font-body: 'Inter', -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', ui-monospace, monospace;
    }

    /* ===== APP SHELL ===== */
    .stApp {
        background:
            radial-gradient(ellipse 900px 600px at 85% 0%, rgba(34, 211, 238, 0.12), transparent 60%),
            radial-gradient(ellipse 700px 500px at 10% 100%, rgba(251, 191, 36, 0.08), transparent 60%),
            radial-gradient(ellipse 1200px 800px at 50% 50%, rgba(99, 102, 241, 0.04), transparent 70%),
            var(--bg) !important;
        background-attachment: fixed !important;
    }

    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
        max-width: 1280px !important;
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { display: none; }
    #MainMenu, footer { visibility: hidden; }

    html, body, [class*="css"], .stMarkdown, p, span, div {
        font-family: var(--font-body);
        color: var(--text);
    }

    h1, h2, h3, h4, h5 {
        font-family: var(--font-display) !important;
        color: var(--text) !important;
    }

    /* ===== MASTHEAD ===== */
    .masthead {
        margin-bottom: 1.8rem;
        padding-bottom: 1.8rem;
        border-bottom: 0.5px solid var(--glass-border);
        position: relative;
    }
    .masthead::after {
        content: '';
        position: absolute;
        bottom: -0.5px; left: 0;
        width: 80px; height: 1px;
        background: var(--cyan);
        box-shadow: 0 0 12px var(--cyan-glow);
    }
    .masthead-kicker {
        font-family: var(--font-mono);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: var(--cyan);
        margin-bottom: 0.8rem;
        display: flex; align-items: center; gap: 0.6rem;
    }
    .masthead-kicker::before {
        content: '';
        display: inline-block;
        width: 6px; height: 6px;
        background: var(--cyan);
        border-radius: 50%;
        box-shadow: 0 0 8px var(--cyan);
    }
    .masthead-title {
        font-family: var(--font-display);
        font-size: 2.8rem;
        font-weight: 500 !important;
        line-height: 1;
        letter-spacing: -0.02em;
        color: var(--text);
        margin: 0;
    }
    .masthead-title em {
        font-style: normal;
        font-weight: 300;
        color: var(--cyan);
        text-shadow: 0 0 30px var(--cyan-glow);
    }
    .masthead-deck {
        font-family: var(--font-body);
        font-size: 1.02rem;
        font-weight: 300;
        color: var(--text-soft);
        margin-top: 1rem;
        max-width: 640px;
        line-height: 1.6;
    }
    .masthead-byline {
        display: flex;
        gap: 2rem;
        margin-top: 1.4rem;
        font-family: var(--font-mono);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        color: var(--text-mute);
        flex-wrap: wrap;
    }
    .byline-item strong {
        color: var(--text);
        font-weight: 600;
    }

    /* ===== SECTION HEADERS ===== */
    .section-number {
        font-family: var(--font-mono);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: var(--cyan);
        margin: 1.8rem 0 0.4rem 0;
        opacity: 0.75;
    }
    .section-title {
        font-family: var(--font-display);
        font-size: 1.4rem;
        font-weight: 500;
        line-height: 1.1;
        color: var(--text);
        margin: 0.6rem 0 0.6rem 0;
        letter-spacing: -0.01em;
        padding: 0.8rem 0 0.8rem 1rem;
        border-left: 2px solid var(--cyan);
        background: linear-gradient(to right, var(--cyan-soft), transparent 60%);
        border-radius: 0 8px 8px 0;
    }
    .section-title em {
        font-weight: 300;
        font-style: normal;
        color: var(--cyan);
    }

    /* ===== SELECTBOX ===== */
    div[data-baseweb="select"] > div {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 0.5px solid var(--glass-border) !important;
        border-radius: 10px !important;
        font-family: var(--font-mono) !important;
        font-size: 0.85rem !important;
        color: var(--text) !important;
        transition: all 0.25s ease;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: var(--cyan) !important;
        background: var(--glass-bg-hover) !important;
        box-shadow: 0 0 20px rgba(34, 211, 238, 0.15);
    }
    div[data-baseweb="select"] > div > div { color: var(--text) !important; }

    div[data-baseweb="popover"] {
        background: #0f1524 !important;
        border: 0.5px solid var(--glass-border-bright) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="popover"] li {
        background: transparent !important;
        color: var(--text-soft) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
    }
    div[data-baseweb="popover"] li:hover {
        background: var(--cyan-soft) !important;
        color: var(--cyan) !important;
    }

    .stSelectbox label {
        font-family: var(--font-mono) !important;
        font-size: 0.68rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2.5px !important;
        color: var(--text-mute) !important;
        font-weight: 500 !important;
    }

    /* ===== GLASS CARDS ===== */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 0.5px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.4rem 1.3rem;
        position: relative;
        overflow: hidden;
    }

    /* ===== VERDICT CARD ===== */
    .verdict-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 0.5px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem 1.4rem;
        position: relative;
        overflow: hidden;
    }
    .verdict-card.high {
        box-shadow: inset 0 0 80px var(--risk-red-bg), 0 0 30px rgba(239, 68, 68, 0.1);
        border-color: rgba(239, 68, 68, 0.25);
    }
    .verdict-card.medium {
        box-shadow: inset 0 0 80px var(--risk-amber-bg), 0 0 30px rgba(251, 191, 36, 0.1);
        border-color: rgba(251, 191, 36, 0.25);
    }
    .verdict-card.low {
        box-shadow: inset 0 0 80px var(--risk-green-bg), 0 0 30px rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.25);
    }
    .verdict-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
    }
    .verdict-card.high::before {
        background: linear-gradient(to right, transparent, var(--risk-red), transparent);
        box-shadow: 0 0 20px var(--risk-red-glow);
    }
    .verdict-card.medium::before {
        background: linear-gradient(to right, transparent, var(--risk-amber), transparent);
        box-shadow: 0 0 20px var(--risk-amber-glow);
    }
    .verdict-card.low::before {
        background: linear-gradient(to right, transparent, var(--risk-green), transparent);
        box-shadow: 0 0 20px var(--risk-green-glow);
    }

    .verdict-label {
        font-family: var(--font-mono);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: var(--text-mute);
        margin-bottom: 0.8rem;
    }
    .verdict-number {
        font-family: var(--font-display);
        font-size: 4.2rem;
        font-weight: 300;
        line-height: 0.95;
        letter-spacing: -0.03em;
        margin-bottom: 0.3rem;
    }
    .verdict-number.high {
        color: var(--risk-red);
        text-shadow: 0 0 40px var(--risk-red-glow);
    }
    .verdict-number.medium {
        color: var(--risk-amber);
        text-shadow: 0 0 40px var(--risk-amber-glow);
    }
    .verdict-number.low {
        color: var(--risk-green);
        text-shadow: 0 0 40px var(--risk-green-glow);
    }

    .verdict-tagline {
        font-family: var(--font-display);
        font-size: 0.8rem;
        font-weight: 500;
        font-style: normal;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 0.3rem;
    }
    .verdict-tagline.high { color: var(--risk-red); }
    .verdict-tagline.medium { color: var(--risk-amber); }
    .verdict-tagline.low { color: var(--risk-green); }

    .verdict-scale {
        display: flex;
        margin-top: 1.8rem;
        height: 6px;
        border-radius: 3px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.05);
    }
    .verdict-scale-segment { flex: 1; height: 100%; }
    .seg-low { background: linear-gradient(to right, transparent, rgba(16, 185, 129, 0.4)); }
    .seg-med { background: rgba(251, 191, 36, 0.4); }
    .seg-high { background: linear-gradient(to right, rgba(239, 68, 68, 0.4), rgba(239, 68, 68, 0.7)); }

    .verdict-scale-labels {
        display: flex;
        justify-content: space-between;
        margin-top: 0.5rem;
        font-family: var(--font-mono);
        font-size: 0.62rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--text-dim);
    }

    /* ===== TICKET META ===== */
    .meta-row {
        display: grid;
        grid-template-columns: 100px 1fr;
        gap: 1rem;
        padding: 0.6rem 0;
        border-bottom: 0.5px solid var(--glass-border);
    }
    .meta-row:last-child { border-bottom: none; }
    .meta-label {
        font-family: var(--font-mono);
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--text-mute);
        padding-top: 3px;
    }
    .meta-value {
        font-family: var(--font-body);
        font-size: 0.92rem;
        font-weight: 400;
        color: var(--text-soft);
    }
    .meta-value.bold { color: var(--text); font-weight: 500; }
    .meta-value .ticket-key {
        font-family: var(--font-mono);
        font-weight: 500;
        color: var(--cyan);
        text-shadow: 0 0 15px var(--cyan-glow);
    }

    /* ===== INSIGHT BLOCKS ===== */
    .insight-block {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 0.5px solid var(--glass-border);
        border-left-width: 2px;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.55rem;
        position: relative;
    }
    .insight-block.warning {
        border-left-color: var(--risk-red);
        background: linear-gradient(to right, var(--risk-red-bg), var(--glass-bg) 40%);
    }
    .insight-block.positive {
        border-left-color: var(--risk-green);
        background: linear-gradient(to right, var(--risk-green-bg), var(--glass-bg) 40%);
    }
    .insight-block.action {
        border-left-color: var(--cyan);
        background: linear-gradient(to right, var(--cyan-soft), var(--glass-bg) 40%);
    }

    .insight-kicker {
        font-family: var(--font-mono);
        font-size: 0.6rem;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        font-weight: 600;
        margin-bottom: 0.4rem;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }
    .insight-kicker::before {
        content: '';
        display: inline-block;
        width: 4px; height: 4px;
        border-radius: 50%;
    }
    .insight-kicker.warning {
        color: var(--risk-red);
    }
    .insight-kicker.warning::before { background: var(--risk-red); box-shadow: 0 0 6px var(--risk-red-glow); }
    .insight-kicker.positive {
        color: var(--risk-green);
    }
    .insight-kicker.positive::before { background: var(--risk-green); box-shadow: 0 0 6px var(--risk-green-glow); }
    .insight-kicker.action {
        color: var(--cyan);
    }
    .insight-kicker.action::before { background: var(--cyan); box-shadow: 0 0 6px var(--cyan-glow); }

    .insight-body {
        font-family: var(--font-body);
        font-size: 0.92rem;
        line-height: 1.55;
        color: var(--text-soft);
    }
    .insight-body strong {
        font-weight: 500;
        color: var(--text);
    }

    .insights-subhead {
        font-family: var(--font-display);
        font-size: 0.75rem;
        font-weight: 500;
        font-style: normal;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--text);
        margin: 1.2rem 0 0.6rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 0.5px solid var(--glass-border);
    }
    .insights-subhead:first-child { margin-top: 0; }

    /* ===== FEATURE ROWS ===== */
    .feature-name {
        font-family: var(--font-body);
        font-weight: 500;
        font-size: 0.92rem;
        color: var(--text);
    }
    .feature-name-sub {
        display: block;
        font-family: var(--font-body);
        font-size: 0.76rem;
        color: var(--text-mute);
        font-weight: 400;
        margin-top: 0.15rem;
    }
    .feature-value {
        font-family: var(--font-mono);
        font-size: 1.05rem;
        font-weight: 500;
        color: var(--text);
    }
    .feature-avg {
        font-family: var(--font-mono);
        font-size: 0.9rem;
        color: var(--text-mute);
    }
    .feature-status {
        font-family: var(--font-mono);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    .status-very_low { color: #dc2626; font-weight: 600; }
    .status-low { color: #f87171; }
    .status-normal { color: var(--text-mute); }
    .status-high { color: #34d399; }
    .status-very_high { color: #10b981; font-weight: 600; }

    /* ===== BUTTON ===== */
    .stButton > button {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        color: var(--cyan) !important;
        border: 0.5px solid var(--cyan) !important;
        border-radius: 10px !important;
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2.5px !important;
        font-weight: 500 !important;
        padding: 0.9rem 1.5rem !important;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 0 0 rgba(34, 211, 238, 0);
    }
    .stButton > button:hover {
        background: var(--cyan-soft) !important;
        color: var(--cyan) !important;
        border-color: var(--cyan) !important;
        box-shadow: 0 0 30px var(--cyan-glow);
        transform: translateY(-1px);
    }
    .stButton > button:active { transform: translateY(0); }

    /* ===== ALERT OVERRIDES ===== */
    .stAlert {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 0.5px solid var(--glass-border) !important;
        border-left-width: 2px !important;
        border-radius: 10px !important;
        font-family: var(--font-body) !important;
        color: var(--text) !important;
    }
    .stAlert[data-baseweb="notification"] { color: var(--text) !important; }
    .stAlert p, .stAlert div { color: var(--text) !important; }

    /* ===== FOOTER ===== */
    .footer-rule {
        border-top: 0.5px solid var(--glass-border);
        margin: 2rem 0 1rem 0;
    }
    .footer {
        font-family: var(--font-mono);
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        color: var(--text-dim);
        text-align: center;
        padding: 1rem 0;
    }
    .footer strong {
        color: var(--cyan);
        font-weight: 500;
    }

    /* ===== PARTICIPANTS ===== */
    .participants {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 0.5px solid var(--glass-border);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
    }
    .participants-label {
        font-family: var(--font-mono);
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        color: var(--text-mute);
        margin-bottom: 0.5rem;
    }
    .participants-list {
        font-family: var(--font-body);
        font-size: 0.88rem;
        color: var(--text-soft);
        line-height: 1.7;
    }
    .participants-count {
        font-family: var(--font-mono);
        font-size: 0.74rem;
        color: var(--cyan);
        margin-left: 0.4rem;
    }

    /* ===== DIVIDERS ===== */
    .rule {
        border: none;
        border-top: 0.5px solid var(--glass-border);
        margin: 2.5rem 0 1.5rem 0;
    }

    /* Plotly container transparency */
    .js-plotly-plot, .plotly { background: transparent !important; }

    /* Streamlit column padding fix */
    [data-testid="column"] { padding: 0 !important; }
    [data-testid="column"]:nth-child(odd) { padding-right: 0.5rem !important; }
    [data-testid="column"]:nth-child(even) { padding-left: 0.5rem !important; }

    /* Input autocomplete */
    input:-webkit-autofill { -webkit-text-fill-color: var(--text) !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# DATA LOADING
# ============================================================================
@st.cache_data
def load_data():
    ticket_path = "data/processed/isa3_ticket_level.csv"
    email_path = "data/processed/isa3_enriched_dataset.csv"
    model_path = "models/model_a_logistic.pkl"
    features_path = "models/model_a_features.pkl"

    for path in [ticket_path, email_path, model_path, features_path]:
        if not os.path.exists(path):
            st.error(f"File not found: {path}. Run scripts 01–05 first.")
            st.stop()

    ticket_df = pd.read_csv(ticket_path, low_memory=False)
    email_df = pd.read_csv(email_path, low_memory=False)
    model = joblib.load(model_path)
    features = joblib.load(features_path)
    return ticket_df, email_df, model, features


@st.cache_data
def get_dataset_stats(_ticket_df, features):
    stats = {}
    for f in features:
        if f in _ticket_df.columns:
            stats[f] = {
                'mean': _ticket_df[f].mean(),
                'std': _ticket_df[f].std(),
                'stalled_mean': _ticket_df[_ticket_df['is_stalled'] == 1][f].mean(),
                'active_mean': _ticket_df[_ticket_df['is_stalled'] == 0][f].mean(),
            }
    return stats


def extract_sender_name(sender_str):
    if pd.isna(sender_str):
        return "Unknown"
    match = re.match(r'^"?([^"<]+)"?\s*<', str(sender_str))
    if match:
        name = match.group(1).strip().strip('"')
        name = re.sub(r'\s*\(Jira\)\s*', '', name)
        return name
    return str(sender_str).split('@')[0]


FEATURE_LABELS = {
    'email_count_per_ticket': ('Email Volume', 'total emails on this ticket'),
    'subject_length': ('Subject Complexity', 'words per subject line'),
    'avg_sentiment': ('Discussion Tone', '-1 negative → +1 positive'),
    'sentiment_variance': ('Tone Variability', 'emotional range of discussion'),
    'sentiment_trend': ('Momentum', 'is mood improving or declining'),
    'priority_numeric': ('Priority Level', '1 trivial → 5 blocker'),
    'unique_senders': ('Team Engagement', 'distinct people in discussion'),
}

# Features where HIGH is BAD and LOW is GOOD (reverse color semantics)
REVERSE_SEMANTIC_FEATURES = {'sentiment_variance'}


def get_feature_status(feature, value, stats, ticket_df=None, features=None):
    if feature not in stats:
        return 'normal'
    mean = stats[feature]['mean']
    std = stats[feature]['std']
    if ticket_df is not None and feature in ticket_df.columns:
        values = ticket_df[feature].dropna()
        if len(values) > 0:
            percentile = (values < value).sum() / len(values) * 100
            if percentile < 15:
                return 'very_low'
            elif percentile < 35:
                return 'low'
            elif percentile > 85:
                return 'very_high'
            elif percentile > 65:
                return 'high'
            return 'normal'
    # Fallback: tighter z-score thresholds
    if std == 0:
        return 'normal'
    z = (value - mean) / std
    if z < -0.6:
        return 'very_low'
    elif z < -0.25:
        return 'low'
    elif z > 0.6:
        return 'very_high'
    elif z > 0.25:
        return 'high'
    return 'normal'


def generate_insights(ticket_data, features, stats, risk_prob, ticket_df=None):
    """Generate insights based on feature status (percentile-based, matches the table)."""
    warnings, positives, actions = [], [], []

    # --- Get email count for this ticket to validate sentiment features ---
    email_count = ticket_data.get('email_count_per_ticket', 0)
    has_sufficient_emails = email_count >= 3  # need 3+ emails for meaningful sentiment stats

    # Define which direction is GOOD vs BAD for each feature
    # good_when_high: more is better (likely to resolve)
    # good_when_low: less is better (likely to stall)
    FEATURE_DIRECTION = {
        'email_count_per_ticket': 'good_when_high',      # more emails = active discussion = healthier
        'unique_senders': 'good_when_high',              # more people = more engagement = healthier
        'avg_sentiment': 'good_when_high',               # positive tone = healthier
        'sentiment_trend': 'good_when_high',             # improving mood = healthier
        'priority_numeric': 'neutral',                   # high priority isn't good or bad by itself
        'subject_length': 'neutral',                     # subject length is neutral
        'sentiment_variance': 'good_when_low',           # high variance = disagreement = worse
    }

    for f in features:
        if f not in ticket_data or f not in stats:
            continue
        value = ticket_data[f]
        mean = stats[f]['mean']
        status = get_feature_status(f, value, stats, ticket_df, features)
        direction = FEATURE_DIRECTION.get(f, 'neutral')

        is_high_status = status in ('high', 'very_high')
        is_low_status = status in ('low', 'very_low')

        # Feature-specific insight generation
        if f == 'unique_senders':
            if is_low_status:
                warnings.append(
                    f"Only <strong>{int(value)} team member(s)</strong> engaged in this discussion — "
                    f"typical tickets have <strong>{mean:.0f} participants</strong>. "
                    "Low engagement is the strongest signal of stalling."
                )
                actions.append(
                    "Tag additional reviewers or surface this ticket in the next team standup. "
                    "Visibility drives momentum."
                )
            elif is_high_status:
                positives.append(
                    f"Strong team engagement with <strong>{int(value)} distinct participants</strong> "
                    f"(average: {mean:.0f}). Active collaboration moves tickets toward resolution."
                )

        elif f == 'email_count_per_ticket':
            if is_low_status:
                warnings.append(
                    f"Thin discussion trail — only <strong>{int(value)} emails</strong> exchanged, "
                    f"average is <strong>{mean:.0f}</strong>. "
                    "This ticket may be slipping through the cracks."
                )
                actions.append(
                    "A brief status check — even a quick 'any updates?' — can reignite dormant threads."
                )
            elif is_high_status:
                positives.append(
                    f"Active conversation with <strong>{int(value)} messages</strong> (average: {mean:.0f}). "
                    "The team is actively working this ticket."
                )

        elif f == 'sentiment_trend':
            if not has_sufficient_emails:
                continue  # skip — trend is meaningless with fewer than 3 emails
            if is_low_status or value < -0.15:
                warnings.append(
                    f"Conversation mood is declining (<strong>{value:+.2f}</strong>). "
                    "Sentiment trending negative often signals mounting frustration or unresolved blockers."
                )
                actions.append(
                    "Consider a synchronous conversation. Declining sentiment usually indicates "
                    "disagreement or ambiguity that email cannot resolve."
                )
            elif is_high_status or value > 0.15:
                positives.append(
                    f"Positive momentum — sentiment is improving (<strong>+{value:.2f}</strong>). "
                    "The discussion is moving toward resolution."
                )

        elif f == 'avg_sentiment':
            if email_count < 2:
                continue  # single-email sentiment is too noisy
            if is_low_status:
                warnings.append(
                    f"The overall tone of this discussion is negative "
                    f"(<strong>{value:.2f}</strong> on a -1 to +1 scale). "
                    "Team frustration may be accumulating."
                )
            elif is_high_status:
                positives.append(
                    f"Healthy discussion tone (<strong>{value:+.2f}</strong>) — "
                    "morale around this ticket is positive."
                )

        elif f == 'sentiment_variance':
            if not has_sufficient_emails:
                continue  # skip — variance is meaningless with fewer than 3 emails
            # For variance: HIGH is bad (disagreement), LOW is good (consistency)
            if is_high_status:
                warnings.append(
                    f"High emotional variance (<strong>{value:.2f}</strong>) — "
                    "the discussion swings between positive and negative. "
                    "This often indicates contested approaches or design disagreement."
                )
                actions.append(
                    "Review the email thread for conflicting viewpoints. "
                    "An alignment meeting may resolve the impasse faster than further email."
                )
            elif is_low_status:
                positives.append(
                    f"Consistent emotional tone (variance: <strong>{value:.2f}</strong>) — "
                    "the team is aligned in their communication about this ticket."
                )

        elif f == 'priority_numeric':
            if value >= 4 and risk_prob > 0.5:
                priority_name = 'Blocker' if value == 5 else 'Critical'
                warnings.append(
                    f"<strong>{priority_name} priority</strong> ticket flagged high-risk for stalling — "
                    "these tickets block downstream work."
                )
                actions.append(
                    "Escalate to the project lead. High-priority stalled tickets compound organisational debt."
                )

        elif f == 'subject_length':
            # Subject length doesn't have strong positive/negative meaning, skip
            pass

    # Fallback insights if nothing triggered
    if not actions and risk_prob > 0.5:
        actions.append(
            "Monitor this ticket closely. If no clear owner exists, assigning one is the single most "
            "effective intervention."
        )

    if not positives and risk_prob <= 0.3:
        positives.append(
            "This ticket exhibits healthy communication signals across all measured dimensions. "
            "No immediate intervention required."
        )

    return warnings, positives, actions


# ============================================================================
# MAIN
# ============================================================================
def main():
    ticket_df, email_df, model, features = load_data()
    stats = get_dataset_stats(ticket_df, features)

    # ===== MASTHEAD =====
    st.markdown("""
    <div class="masthead">
        <div class="masthead-kicker">Socio-Technical Health Monitor · Dissertation Project</div>
        <div class="masthead-title">Ticket Health <em>Monitor</em></div>
        <div class="masthead-deck">
            Predicting stalled software tickets through the language of team communication.
            A tool for managers who'd rather intervene early than investigate late.
        </div>
        <div class="masthead-byline">
            <div class="byline-item"><strong>Dataset</strong> · 916 Hadoop tickets · 46,486 emails</div>
            <div class="byline-item"><strong>Model</strong> · Logistic Regression · 7 features</div>
            <div class="byline-item"><strong>Coverage</strong> · 2018–2024</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ===== SELECTOR =====
    st.markdown('<div class="section-title">Choose a ticket <em>for analysis</em></div>', unsafe_allow_html=True)

    ticket_options = {}
    for _, row in ticket_df.iterrows():
        key = row['ticket_key']
        summary = str(row.get('summary', ''))[:70] if 'summary' in row.index else ''
        label = f"{key} — {summary}"
        ticket_options[label] = key

    selected_label = st.selectbox(
        "TICKET",
        options=list(ticket_options.keys()),
        label_visibility="collapsed",
        index=0,
    )
    selected_ticket = ticket_options[selected_label]
    ticket_row = ticket_df[ticket_df['ticket_key'] == selected_ticket].iloc[0]

    # ===== PREDICTION =====
    # Use DataFrame with feature names to avoid sklearn warnings
    ticket_features = pd.DataFrame([ticket_row[features].values], columns=features)
    risk_prob = model.predict_proba(ticket_features)[0][1]

    if risk_prob >= 0.6:
        risk_class, risk_tagline = "high", "Intervention Warranted"
    elif risk_prob >= 0.35:
        risk_class, risk_tagline = "medium", "Warrants Observation"
    else:
        risk_class, risk_tagline = "low", "Communication Healthy"

    # ===== VERDICT & META =====
    col_verdict, col_meta = st.columns([1, 1])

    with col_verdict:
        st.markdown(f"""
        <div class="verdict-card {risk_class}">
            <div class="verdict-label">Stall Probability</div>
            <div class="verdict-number {risk_class}">{risk_prob:.0%}</div>
            <div class="verdict-tagline {risk_class}">{risk_tagline}</div>
            <div class="verdict-scale">
                <div class="verdict-scale-segment seg-low"></div>
                <div class="verdict-scale-segment seg-med"></div>
                <div class="verdict-scale-segment seg-high"></div>
            </div>
            <div class="verdict-scale-labels">
                <span>Low</span><span>Elevated</span><span>High</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="height: 0.8rem;"></div>', unsafe_allow_html=True)

        if st.button("REVEAL ACTUAL OUTCOME"):
            actual = int(ticket_row['is_stalled'])
            # Determine which zone the prediction fell into
            if risk_prob >= 0.6:
                zone = "high"
            elif risk_prob >= 0.35:
                zone = "elevated"
            else:
                zone = "low"

            if actual == 1:  # Ticket actually stalled
                if zone == "high":
                    st.success(f"✓ Correctly flagged as HIGH RISK. This ticket did stall. Model predicted {risk_prob:.0%}.")
                elif zone == "elevated":
                    st.info(f"◐ Partially correct. Model flagged this ticket for observation ({risk_prob:.0%} risk) and it did stall.")
                else:
                    st.error(f"✗ Missed. This ticket stalled but model predicted only {risk_prob:.0%} — low risk zone.")
            else:  # Ticket actually resolved
                if zone == "low":
                    st.success(f"✓ Correctly identified as LOW RISK. This ticket was resolved. Model predicted {risk_prob:.0%}.")
                elif zone == "elevated":
                    st.info(f"◐ Reasonable caution. Model flagged this ticket for observation ({risk_prob:.0%} risk) but it resolved fine.")
                else:
                    st.warning(f"⚠ False alarm. This ticket resolved but model predicted {risk_prob:.0%} — high risk zone.")

    with col_meta:
        st.markdown(f"""
        <div class="glass-card">
            <div class="meta-row">
                <div class="meta-label">Ticket</div>
                <div class="meta-value"><span class="ticket-key">{selected_ticket}</span></div>
            </div>
            <div class="meta-row">
                <div class="meta-label">Project</div>
                <div class="meta-value bold">{ticket_row.get('project.key', 'N/A')}</div>
            </div>
            <div class="meta-row">
                <div class="meta-label">Type</div>
                <div class="meta-value">{ticket_row.get('issuetype.name', 'N/A')}</div>
            </div>
            <div class="meta-row">
                <div class="meta-label">Priority</div>
                <div class="meta-value">{ticket_row.get('priority', 'N/A')}</div>
            </div>
            <div class="meta-row">
                <div class="meta-label">Summary</div>
                <div class="meta-value" style="font-size: 0.85rem;">{str(ticket_row.get('summary', 'No summary'))[:200]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ===== INSIGHTS =====
    st.markdown('<div style="margin-top: -1rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">What this ticket <em>is telling us</em></div>', unsafe_allow_html=True)

    ticket_data = {f: ticket_row[f] for f in features if f in ticket_row.index}
    warnings, positives, actions = generate_insights(ticket_data, features, stats, risk_prob, ticket_df)

    if warnings:
        st.markdown('<div class="insights-subhead">Risk factors</div>', unsafe_allow_html=True)
        for w in warnings:
            st.markdown(f"""
            <div class="insight-block warning">
                <div class="insight-kicker warning">Concern</div>
                <div class="insight-body">{w}</div>
            </div>
            """, unsafe_allow_html=True)

    if positives:
        st.markdown('<div class="insights-subhead">Positive signals</div>', unsafe_allow_html=True)
        for p in positives:
            st.markdown(f"""
            <div class="insight-block positive">
                <div class="insight-kicker positive">Healthy</div>
                <div class="insight-body">{p}</div>
            </div>
            """, unsafe_allow_html=True)

    if actions:
        st.markdown('<div class="insights-subhead">Recommended interventions</div>', unsafe_allow_html=True)
        for a in actions:
            st.markdown(f"""
            <div class="insight-block action">
                <div class="insight-kicker action">Action</div>
                <div class="insight-body">{a}</div>
            </div>
            """, unsafe_allow_html=True)

    # ===== FEATURE BREAKDOWN =====
    st.markdown('<div class="section-title">Communication signals, <em>measured</em></div>', unsafe_allow_html=True)
    st.markdown('<div style="background: rgba(255,255,255,0.025); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 0.5px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 1.5rem 1.5rem 0.5rem 1.5rem; margin-bottom: 1rem;">', unsafe_allow_html=True)

    # Header row
    col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([2.5, 1, 1, 1, 2.5])
    header_style = 'font-family:var(--font-mono); font-size:0.62rem; text-transform:uppercase; letter-spacing:2.5px; color:var(--text-mute); padding-bottom:0.7rem; border-bottom:0.5px solid var(--glass-border-bright);'
    with col_h1: st.markdown(f'<div style="{header_style}">Feature</div>', unsafe_allow_html=True)
    with col_h2: st.markdown(f'<div style="{header_style} text-align:right;">This Ticket</div>', unsafe_allow_html=True)
    with col_h3: st.markdown(f'<div style="{header_style} text-align:right;">Avg</div>', unsafe_allow_html=True)
    with col_h4: st.markdown(f'<div style="{header_style}">Status</div>', unsafe_allow_html=True)
    with col_h5: st.markdown(f'<div style="{header_style}">Distribution</div>', unsafe_allow_html=True)

    for f in features:
        if f not in ticket_row.index or f not in stats:
            continue
        # Hide features with low actionability for managers
        if f in ('priority_numeric', 'subject_length'):
            continue
        value = ticket_row[f]
        mean = stats[f]['mean']
        status = get_feature_status(f, value, stats, ticket_df, features)
        label, sublabel = FEATURE_LABELS.get(f, (f, ''))
        status_text_map = {
            'very_low': 'LOW',
            'low': 'BELOW AVG',
            'normal': 'TYPICAL',
            'high': 'ABOVE AVG',
            'very_high': 'HIGH',
        }
        status_text = status_text_map[status]
        # For reverse-semantic features, swap the CSS color class so high status shows red
        if f in REVERSE_SEMANTIC_FEATURES:
            css_status_map = {
                'very_low': 'very_high',   # low variance = good = green
                'low': 'high',
                'normal': 'normal',
                'high': 'low',             # high variance = bad = red
                'very_high': 'very_low',
            }
            status_class = f"status-{css_status_map[status]}"
        else:
            status_class = f"status-{status}"

        max_val = max(abs(value), abs(mean)) * 1.6 if max(abs(value), abs(mean)) > 0 else 1

        # Color map — for most features, high is good (green), low is bad (red)
        color_map_normal = {
            'very_low': '#dc2626',
            'low': '#f87171',
            'normal': 'rgba(245,247,250,0.4)',
            'high': '#34d399',
            'very_high': '#10b981',
        }
        # Reverse for features where HIGH is bad
        color_map_reverse = {
            'very_low': '#10b981',
            'low': '#34d399',
            'normal': 'rgba(245,247,250,0.4)',
            'high': '#f87171',
            'very_high': '#dc2626',
        }
        color_map = color_map_reverse if f in REVERSE_SEMANTIC_FEATURES else color_map_normal
        bar_color = color_map[status]
        avg_color = 'rgba(255, 255, 255, 0.12)'

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[mean], y=['avg'], orientation='h',
            marker=dict(color=avg_color, line=dict(width=0)),
            width=0.55, showlegend=False,
            hovertemplate=f'Avg: {mean:.2f}<extra></extra>',
        ))
        # Ensure minimum visible bar width — zero values still need a colored marker
        min_visible_width = max_val * 0.035
        display_value = value if abs(value) > min_visible_width else min_visible_width
        fig.add_trace(go.Bar(
            x=[display_value], y=['this'], orientation='h',
            marker=dict(color=bar_color, line=dict(width=0)),
            width=0.55, showlegend=False,
            hovertemplate=f'This ticket: {value:.2f}<extra></extra>',
        ))
        fig.update_layout(
            height=48,
            margin=dict(t=4, b=4, l=0, r=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False,
                       range=[min(0, value * 1.2), max_val]),
            yaxis=dict(showticklabels=False, showgrid=False,
                       categoryorder='array', categoryarray=['this', 'avg']),
            barmode='group', bargap=0.15,
        )

        c1, c2, c3, c4, c5 = st.columns([2.5, 1, 1, 1, 2.5])
        row_border = 'border-bottom:0.5px solid var(--glass-border);'
        with c1:
            st.markdown(f"""
            <div style="padding:0.8rem 0; {row_border}">
                <div class="feature-name">{label}</div>
                <span class="feature-name-sub">{sublabel}</span>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="padding:1rem 0; text-align:right; {row_border}" class="feature-value">{value:.2f}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div style="padding:1.05rem 0; text-align:right; {row_border}" class="feature-avg">{mean:.2f}</div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div style="padding:1.05rem 0; {row_border}" class="feature-status {status_class}">{status_text}</div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div style="padding:0.25rem 0; {row_border}">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ===== TIMELINE =====
    st.markdown('<div class="section-title">How the discussion <em>unfolded</em></div>', unsafe_allow_html=True)

    ticket_emails = email_df[email_df['ticket_key'] == selected_ticket].copy()

    if len(ticket_emails) > 0:
        ticket_emails['email_dt'] = pd.to_datetime(ticket_emails['email_dt'], errors='coerce', utc=True)
        ticket_emails = ticket_emails.dropna(subset=['email_dt']).sort_values('email_dt')
        ticket_emails['sender_name'] = ticket_emails['sender'].apply(extract_sender_name)

        if len(ticket_emails) >= 2:
            fig_tl = go.Figure()

            # Positive/negative background zones
            fig_tl.add_hrect(y0=0.3, y1=1.0, fillcolor="#10b981", opacity=0.05, line_width=0)
            fig_tl.add_hrect(y0=-1.0, y1=-0.3, fillcolor="#ef4444", opacity=0.05, line_width=0)

            # Connecting line
            fig_tl.add_trace(go.Scatter(
                x=ticket_emails['email_dt'],
                y=ticket_emails['behavior_score'],
                mode='lines',
                line=dict(color='rgba(34, 211, 238, 0.4)', width=1.5),
                showlegend=False,
                hoverinfo='skip',
            ))

            # Points with glow
            colors = ticket_emails['behavior_score'].apply(
                lambda x: '#ef4444' if x < -0.15 else ('#fbbf24' if abs(x) <= 0.15 else '#10b981')
            )
            subj_col = 'email_subject_clean' if 'email_subject_clean' in ticket_emails.columns else 'email_subject'
            fig_tl.add_trace(go.Scatter(
                x=ticket_emails['email_dt'],
                y=ticket_emails['behavior_score'],
                mode='markers',
                marker=dict(
                    size=12, color=colors,
                    line=dict(width=1.5, color='rgba(10, 14, 26, 0.9)'),
                ),
                customdata=list(zip(
                    ticket_emails['sender_name'],
                    ticket_emails[subj_col].astype(str).str[:55]
                )),
                hovertemplate=(
                    '<b>%{customdata[0]}</b><br>'
                    '%{x|%d %b %Y}<br>'
                    'Sentiment: <b>%{y:.2f}</b><br>'
                    '<i>%{customdata[1]}</i>'
                    '<extra></extra>'
                ),
                showlegend=False,
            ))

            fig_tl.add_hline(
                y=0, line_dash="dot", line_color="rgba(245, 247, 250, 0.25)", line_width=1,
                annotation_text="neutral", annotation_position="right",
                annotation_font=dict(family='JetBrains Mono', size=10, color='rgba(245, 247, 250, 0.45)'),
            )

            fig_tl.update_layout(
                height=340,
                margin=dict(t=20, b=50, l=60, r=30),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=True, gridcolor='rgba(255,255,255,0.04)', gridwidth=1,
                    linecolor='rgba(255,255,255,0.15)', showline=True, linewidth=0.5,
                    tickfont=dict(family='JetBrains Mono', size=10, color='rgba(245,247,250,0.6)'),
                ),
                yaxis=dict(
                    title=dict(text='SENTIMENT SCORE', font=dict(family='JetBrains Mono', size=10, color='rgba(245,247,250,0.45)')),
                    range=[-1.1, 1.1],
                    showgrid=True, gridcolor='rgba(255,255,255,0.04)', gridwidth=1,
                    zeroline=False,
                    linecolor='rgba(255,255,255,0.15)', showline=True, linewidth=0.5,
                    tickfont=dict(family='JetBrains Mono', size=10, color='rgba(245,247,250,0.6)'),
                ),
                hoverlabel=dict(
                    bgcolor='#0f1524', bordercolor='#22d3ee',
                    font=dict(family='Inter', size=12, color='#f5f7fa'),
                ),
                showlegend=False,
            )
            st.plotly_chart(fig_tl, use_container_width=True, config={'displayModeBar': False})

            participants = ticket_emails['sender_name'].unique()
            display_list = ", ".join(participants[:12])
            overflow = f" <span class='participants-count'>+ {len(participants) - 12} others</span>" if len(participants) > 12 else ""

            st.markdown(f"""
            <div class="participants">
                <div class="participants-label">Discussion participants <span class="participants-count">({len(participants)} total)</span></div>
                <div class="participants-list">{display_list}{overflow}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(f"Only {len(ticket_emails)} email available — minimum 2 required for timeline.")
    else:
        st.warning("No email data for this ticket.")

    # ===== FOOTER =====
    st.markdown('<div class="footer-rule"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        Socio-Technical Health Monitor &nbsp;·&nbsp;
        <strong>ISA III Dissertation</strong> &nbsp;·&nbsp;
        Apache Hadoop 2018–2024 &nbsp;·&nbsp;
        Logistic Regression · 7 features
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()