import requests
import streamlit as st

from style import inject_css
from utils import normalize_risk, distance_band, risk_gauge, verdict_meta

st.set_page_config(
    page_title="Live Scanner · Credit Fraud Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ---------------------------------------------------------------------
# Shared state (set on Home.py; default here too so this page also
# works if someone lands on it directly)
# ---------------------------------------------------------------------
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://127.0.0.1:8000"
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "scan_count" not in st.session_state:
    st.session_state.scan_count = 0

API_URL = f"{st.session_state.api_url.rstrip('/')}/predict"


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


with st.sidebar:
    st.markdown("### ⚙️ Backend connection")
    st.session_state.api_url = st.text_input(
        "API base URL", value=st.session_state.api_url
    )
    online = check_backend(st.session_state.api_url)
    dot_class = "status-online" if online else "status-offline"
    st.markdown(
        f'<span class="status-dot {dot_class}"></span>'
        f'{"Backend online" if online else "Backend unreachable"}',
        unsafe_allow_html=True,
    )
    st.divider()
    st.page_link("Home.py", label="Home", icon="🏠")
    st.page_link("pages/1_Live_Scanner.py", label="Live Scanner", icon="🔍")

# ---------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Realtime scoring</div>
        <h1>Live Transaction Scanner</h1>
        <p>Enter a transaction and the ensemble model returns a fraud / genuine
        decision, an overall risk score, and a per-model breakdown. Nothing is stored.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not online:
    st.markdown(
        f"""
        <div class="hint-box" style="border-color: rgba(231,76,60,0.35); background: rgba(231,76,60,0.08); color:#ffb0a8;">
        Backend at <b>{st.session_state.api_url}</b> is not responding. Start the API server,
        or update the URL in the sidebar, before submitting a scan.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------
# Form
# ---------------------------------------------------------------------
with st.form("transaction_form"):
    st.markdown(
        '<div class="section-kicker">Input</div><div class="section-title">Transaction details</div>',
        unsafe_allow_html=True,
    )

    amount_col, distance_col = st.columns(2)
    with amount_col:
        amount = st.number_input(
            "Transaction amount ($)",
            min_value=0.0,
            value=120.50,
            help="The billed amount in USD. Unusually large charges, especially with a far-from-home location or online checkout, are a common fraud signal.",
        )
        st.caption("Larger amounts raise risk when they look unusual for the cardholder.")

    with distance_col:
        distance = st.number_input(
            "Distance from home (km)",
            min_value=0.0,
            value=5.2,
            help="How far the transaction occurred from the cardholder's registered home address (km).",
        )
        band_label, band_class = distance_band(distance)
        st.markdown(f'<span class="band {band_class}">{band_label}</span>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="hint-box">
                Larger distances, especially combined with high amounts,
                are a common fraud signal.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        merchant_category = st.selectbox(
            "Merchant category",
            ["grocery", "electronics", "travel", "entertainment", "online_services"],
            help="Grocery is typically lower risk; electronics, travel, and online services are more often associated with fraud.",
        )
        st.caption("Electronics, travel, and online services tend to be higher risk than grocery.")
    with col2:
        transaction_type = st.selectbox(
            "Transaction type",
            ["in_store_chip", "online_checkout", "international_online"],
            help="In-store chip is usually safer; online and international checkouts carry more fraud risk.",
        )
        st.caption("Online and international checkouts are generally riskier than in-store chip.")
    with col3:
        card_type = st.selectbox(
            "Card type",
            ["visa", "mastercard", "amex"],
            help="Contextual input for the model, not a verdict on the cardholder.",
        )
        st.caption("Card network. Used as context by the model, not as a decision by itself.")

    submit = st.form_submit_button("Analyze risk", disabled=not online)

# ---------------------------------------------------------------------
# Submit → call backend → render results
# ---------------------------------------------------------------------
if submit:
    payload = {
        "amount": amount,
        "distance_from_home": distance,
        "merchant_category": merchant_category,
        "transaction_type": transaction_type,
        "card_type": card_type,
    }

    with st.spinner("Analyzing transaction..."):
        try:
            response = requests.post(API_URL, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                st.session_state.last_result = data
                st.session_state.scan_count += 1

                decision = data.get("final_decision", "UNKNOWN")
                risk_score = data.get("risk_score", 0.0)
                risk_pct = normalize_risk(risk_score)
                verdict_class, verdict_copy = verdict_meta(decision)

                indicator_class = "indicator-fraud" if decision == "FRAUD" else "indicator-genuine"
                st.markdown(
                    f"""
                    <div class="result-panel">
                        <div class="result-indicator {indicator_class}"></div>
                        <div class="section-kicker">Result</div>
                        <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap;margin:0.15rem 0 0.35rem 0;">
                            <span class="verdict {verdict_class}">{decision}</span>
                            <span style="color:var(--text-secondary);font-size:15px;">{verdict_copy}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                gauge_col, bar_col = st.columns([1.15, 1])
                with gauge_col:
                    st.plotly_chart(
                        risk_gauge(risk_score),
                        use_container_width=True,
                        config={"displayModeBar": False},
                    )
                with bar_col:
                    st.markdown(
                        f"<p style='color:#9aabc8;margin:0.4rem 0 0.35rem 0;'>Normalized risk ({risk_pct*100:.1f}%)</p>",
                        unsafe_allow_html=True,
                    )
                    st.progress(risk_pct)
                    st.caption(f"Raw risk_score from API: {float(risk_score):.4f}")
                    st.caption("Green < 40% · Amber 40–70% · Red > 70%. Score is scaled to 0–100% for display only.")

                st.markdown(
                    '<div class="section-kicker" style="margin-top:0.4rem;">Model breakdown</div>',
                    unsafe_allow_html=True,
                )
                m1, m2, m3, m4 = st.columns(4)
                
                xgb_val = f"{float(data.get('xgb_fraud_prob', 0.0)):.4f}"
                with m1:
                    st.markdown(f'<div class="model-breakdown-card model-xgb"><div class="model-title">XGBoost Prob</div><div class="model-value">{xgb_val}</div></div>', unsafe_allow_html=True)
                
                iso_val = "Anomaly" if data.get("iso_forest_anomaly") else "Normal"
                with m2:
                    st.markdown(f'<div class="model-breakdown-card model-iso"><div class="model-title">Isolation Forest</div><div class="model-value">{iso_val}</div></div>', unsafe_allow_html=True)
                
                ae_val = "Anomaly" if data.get("autoencoder_anomaly", False) else "Normal" if "autoencoder_anomaly" in data else "—"
                with m3:
                    st.markdown(f'<div class="model-breakdown-card model-ae"><div class="model-title">Autoencoder</div><div class="model-value">{ae_val}</div></div>', unsafe_allow_html=True)
                
                ae_mse = f"{float(data.get('autoencoder_mse', 0.0)):.4f}" if "autoencoder_mse" in data else "—"
                with m4:
                    st.markdown(f'<div class="model-breakdown-card model-ae"><div class="model-title">Autoencoder MSE</div><div class="model-value">{ae_mse}</div></div>', unsafe_allow_html=True)

                with st.expander("Raw API response"):
                    st.json(data)

            else:
                st.error(f"Error connecting to backend: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error(
                f"Failed to connect to the backend API at {st.session_state.api_url}. "
                "Please ensure the backend server is running."
            )
        except requests.exceptions.Timeout:
            st.error("The backend took too long to respond. Please try again.")
