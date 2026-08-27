import requests
import streamlit as st

from style import inject_css
from utils import verdict_meta, normalize_risk

st.set_page_config(
    page_title="Credit Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ---------------------------------------------------------------------
# Shared app state (also read/written by pages/1_Live_Scanner.py)
# ---------------------------------------------------------------------
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://127.0.0.1:8000"
if "last_result" not in st.session_state:
    st.session_state.last_result = None  # filled by the scanner page after a scan
if "scan_count" not in st.session_state:
    st.session_state.scan_count = 0


def check_backend(base_url: str) -> bool:
    try:
        r = requests.get(f"{base_url}/health", timeout=1.5)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        try:
            r = requests.get(base_url, timeout=1.5)
            return r.status_code < 500
        except requests.exceptions.RequestException:
            return False


# ---------------------------------------------------------------------
# Sidebar: connection settings, shared across pages via session_state
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Backend connection")
    st.session_state.api_url = st.text_input(
        "API base URL",
        value=st.session_state.api_url,
        help="Base URL of the FastAPI/Flask backend serving the ensemble model.",
    )
    online = check_backend(st.session_state.api_url)
    dot_class = "status-online" if online else "status-offline"
    status_text = "Backend online" if online else "Backend unreachable"
    st.markdown(
        f'<span class="status-dot {dot_class}"></span>{status_text}',
        unsafe_allow_html=True,
    )
    st.caption("Checked live on every page load.")
    st.divider()
    st.page_link("Home.py", label="Home", icon="🏠")
    st.page_link("pages/1_Live_Scanner.py", label="Live Scanner", icon="🔍")

# ---------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Hybrid ensemble · supervised + unsupervised</div>
        <h1>Credit Card Fraud Detection</h1>
        <p>
        A hybrid detection engine that combines a supervised gradient-boosted
        classifier with two unsupervised anomaly detectors. Score a transaction
        in real time and see exactly which model flagged it, and why.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

cta_col, stat_col = st.columns([1.4, 1])
with cta_col:
    st.page_link(
        "pages/1_Live_Scanner.py",
        label="🔍  Open the Live Scanner →",
        use_container_width=True,
    )
with stat_col:
    st.markdown(
        f"""
        <div class="panel" style="padding:0.85rem 1rem;">
            <div class="section-kicker">This session</div>
            <div style="color:#f4f7ff;font-size:1.4rem;font-weight:800;">
                {st.session_state.scan_count} scan(s) run
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Most recent scan (dynamic — populated once the user runs the scanner)
# ---------------------------------------------------------------------
if st.session_state.last_result:
    data = st.session_state.last_result
    decision = data.get("final_decision", "UNKNOWN")
    verdict_class, verdict_copy = verdict_meta(decision)
    risk_pct = normalize_risk(data.get("risk_score", 0.0)) * 100

    indicator_class = "indicator-fraud" if decision == "FRAUD" else "indicator-genuine"
    st.markdown(
        f"""
        <div class="result-panel">
            <div class="result-indicator {indicator_class}"></div>
            <div class="section-kicker">Most recent scan</div>
            <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap;margin:0.15rem 0 0.9rem 0;">
                <span class="verdict {verdict_class}">{decision}</span>
                <span style="color:var(--text-secondary);font-size:15px;">{verdict_copy}</span>
                <span style="color:var(--text-secondary);font-size:14px;margin-left:auto;">Risk: {risk_pct:.1f}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="hint-box">
        No transactions scanned yet this session. Head to the
        <b>Live Scanner</b> to score your first transaction.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ---------------------------------------------------------------------
# How it works
# ---------------------------------------------------------------------
st.markdown(
    '<div class="section-kicker">Process</div><div class="section-title">How a transaction gets scored</div>',
    unsafe_allow_html=True,
)

steps = [
    ("Submit transaction details", "Amount, distance from home, merchant category, transaction type, and card network are sent to the backend as a single JSON payload."),
    ("Three models score it independently", "XGBoost outputs a fraud probability, Isolation Forest flags statistical outliers, and an Autoencoder flags high reconstruction error."),
    ("Signals are combined into one verdict", "The backend merges the three signals into a single risk score and a final FRAUD / GENUINE decision, returned to the UI in real time."),
]
for i, (title, desc) in enumerate(steps, start=1):
    st.markdown(
        f"""
        <div style="display:flex;align-items:flex-start;margin-bottom:0.9rem;">
            <span class="step-num">{i}</span>
            <div>
                <div style="color:var(--text-primary);font-weight:600;font-size:16px;">{title}</div>
                <div style="color:var(--text-secondary);font-size:15px;line-height:1.6;">{desc}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ---------------------------------------------------------------------
# Model cards
# ---------------------------------------------------------------------
st.markdown(
    '<div class="section-kicker">Ensemble</div><div class="section-title">What each model contributes</div>',
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
cards = [
    ("🌲", "XGBoost classifier", "Supervised gradient-boosted trees trained on labeled fraud/genuine transactions. Outputs a fraud probability used as the primary risk driver."),
    ("🧭", "Isolation Forest", "Unsupervised outlier detector. Flags transactions that sit far outside normal spending patterns, useful for catching fraud types not seen in training data."),
    ("🧬", "Autoencoder", "Neural network trained to reconstruct genuine transactions. A high reconstruction error signals a transaction that doesn't look like normal cardholder behavior."),
]
for col, (icon, title, desc) in zip([m1, m2, m3], cards):
    with col:
        st.markdown(
            f"""
            <div class="feature-card">
                <div class="icon">{icon}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")
st.markdown(
    """
    <div class="hint-box">
    ⚠️ This UI only scores transactions in memory — nothing submitted here is stored or logged.
    </div>
    """,
    unsafe_allow_html=True,
)
