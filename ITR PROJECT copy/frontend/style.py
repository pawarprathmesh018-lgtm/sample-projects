"""
Central design system for the app. Both Home.py and pages/*.py call
inject_css() once at the top so every page looks like one product
instead of a form bolted onto a landing page.
"""

import streamlit as st

BASE_CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700;800&display=swap");

:root {
    --bg-base: #0F172A;
    --bg-surface: #1E293B;
    --bg-surface-hover: #334155;
    --border-color: rgba(255, 255, 255, 0.12);
    --text-primary: #F9FAFB;
    --text-secondary: #D1D5DB;
    --accent-blue: #3B82F6;
    --success-green: #10B981;
    --warning-amber: #F59E0B;
    --danger-red: #EF4444;
}

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
    color: var(--text-primary);
}

h1, h2, h3, h4, h5, h6 {
    font-family: "Space Grotesk", sans-serif !important;
    color: #FFFFFF !important;
}

.stApp {
    background-color: var(--bg-base);
    background-image: radial-gradient(1000px 500px at 10% 0%, rgba(59, 130, 246, 0.08) 0%, transparent 60%),
                      radial-gradient(1000px 500px at 90% 100%, rgba(139, 92, 246, 0.08) 0%, transparent 60%);
    color: var(--text-primary);
}

header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    max-width: 1080px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* ---------- Typography Overrides ---------- */
p, li {
    font-size: 15px !important;
    line-height: 1.6 !important;
    color: var(--text-primary) !important;
}
.stMarkdown p { color: var(--text-primary) !important; }
[data-testid="stCaption"] { color: var(--text-secondary) !important; font-size: 13px !important; }

/* ---------- Sidebar / nav ---------- */
section[data-testid="stSidebar"] {
    background: #0B101E;
    border-right: 1px solid var(--border-color);
}
section[data-testid="stSidebar"] * { color: var(--text-secondary) !important; }

/* ---------- Input Fields ---------- */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div {
    background-color: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.75rem !important;
    font-size: 15px !important;
}
.stTextInput > div > div:focus-within,
.stNumberInput > div > div:focus-within,
.stSelectbox > div > div:focus-within {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 1px var(--accent-blue) !important;
}
label { color: var(--text-primary) !important; font-weight: 500 !important; font-size: 14px !important; }

/* ---------- Shared surface cards ---------- */
.hero {
    background: linear-gradient(180deg, var(--bg-surface), rgba(30, 41, 59, 0.6));
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 2.2rem 2.4rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.25);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.hero:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.3);
}
.hero h1 {
    margin: 0 0 0.5rem 0;
    font-size: 34px;
    letter-spacing: -0.03em;
}
.hero p {
    margin: 0;
    color: var(--text-secondary) !important;
    font-size: 16px !important;
    max-width: 800px;
}
.eyebrow {
    display: inline-block;
    font-family: "Space Grotesk", sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-blue);
    margin-bottom: 0.5rem;
}

.panel {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}

div[data-testid="stForm"] {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.8rem;
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    margin-bottom: 2rem;
}

.section-kicker {
    font-family: "Space Grotesk", sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
}
.section-title {
    font-family: "Space Grotesk", sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 1rem;
}

.hint-box {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    color: var(--text-secondary);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    font-size: 14px;
    margin: 0.5rem 0 1rem 0;
}

/* ---------- Badges / bands / status pills ---------- */
.band {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    border-radius: 999px;
    padding: 0.25rem 0.75rem;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.band-nearby { background: rgba(16, 185, 129, 0.15); color: var(--success-green); border: 1px solid rgba(16, 185, 129, 0.3); }
.band-moderate { background: rgba(245, 158, 11, 0.15); color: var(--warning-amber); border: 1px solid rgba(245, 158, 11, 0.3); }
.band-far { background: rgba(239, 68, 68, 0.15); color: var(--danger-red); border: 1px solid rgba(239, 68, 68, 0.3); }

.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 8px;
}
.status-online { background: var(--success-green); box-shadow: 0 0 8px var(--success-green); }
.status-offline { background: var(--danger-red); box-shadow: 0 0 8px var(--danger-red); }

.result-panel {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem 1.75rem;
    margin-top: 1.5rem;
    box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    position: relative;
    overflow: hidden;
}

.verdict {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 999px;
    padding: 0.4rem 1rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    font-size: 13px;
    font-family: "Space Grotesk", sans-serif;
}
.verdict-fraud { background: rgba(239, 68, 68, 0.15); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.4); }
.verdict-genuine { background: rgba(16, 185, 129, 0.15); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.4); }
.verdict-unknown { background: rgba(255, 255, 255, 0.1); color: var(--text-secondary); border: 1px solid var(--border-color); }

/* Glowing left border indicator for verdict */
.result-indicator {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 6px;
}
.indicator-fraud { background: var(--danger-red); box-shadow: 2px 0 10px rgba(239, 68, 68, 0.5); }
.indicator-genuine { background: var(--success-green); box-shadow: 2px 0 10px rgba(16, 185, 129, 0.5); }

/* ---------- Metrics ---------- */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.25);
}
div[data-testid="stMetric"] label { color: var(--text-secondary) !important; font-size: 13px !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 24px;
    font-family: "Space Grotesk", sans-serif;
    color: #FFFFFF !important;
}

/* ---------- Buttons ---------- */
.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    width: 100%;
    background: linear-gradient(135deg, #3B82F6, #2563EB) !important;
    color: white !important;
    border: 0 !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.25rem !important;
    font-family: "Space Grotesk", sans-serif;
    font-weight: 600 !important;
    font-size: 16px !important;
    letter-spacing: 0.02em;
    transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4) !important;
}
.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(135deg, #4F8EF7, #3B82F6) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6) !important;
    transform: translateY(-1px);
}
.stButton > button:active,
div[data-testid="stFormSubmitButton"] > button:active {
    transform: scale(0.98);
}

a[data-testid="stPageLink"] {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.2s ease;
}
a[data-testid="stPageLink"]:hover {
    background: var(--bg-surface-hover);
    border-color: var(--accent-blue);
    transform: translateX(4px);
}

/* ---------- Feature / model cards on Home ---------- */
.feature-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    height: 100%;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.25);
    border-color: rgba(255,255,255,0.2);
}
.feature-card .icon { font-size: 24px; margin-bottom: 0.75rem; }
.feature-card h4 { margin: 0 0 0.5rem 0; color: #FFFFFF; font-size: 18px; }
.feature-card p { margin: 0; color: var(--text-secondary) !important; font-size: 14px !important; line-height: 1.6; }

.step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px; height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3B82F6, #2563EB);
    color: white;
    font-weight: 700;
    font-family: "Space Grotesk", sans-serif;
    font-size: 16px;
    margin-right: 1rem;
    flex-shrink: 0;
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4);
}

/* Custom Model Breakdown Cards (used in scanner) */
.model-breakdown-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-top: 3px solid var(--border-color);
    transition: transform 0.2s ease;
}
.model-breakdown-card:hover {
    transform: translateY(-2px);
    background: var(--bg-surface-hover);
}
.model-xgb { border-top-color: #3B82F6; }
.model-iso { border-top-color: #8B5CF6; }
.model-ae { border-top-color: #F59E0B; }

.model-title {
    font-family: "Space Grotesk", sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}
.model-value {
    font-family: "Space Grotesk", sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #FFFFFF;
}
</style>
"""

def inject_css() -> None:
    st.markdown(BASE_CSS, unsafe_allow_html=True)
