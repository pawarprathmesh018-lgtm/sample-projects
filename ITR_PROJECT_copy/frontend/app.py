import streamlit as st
import requests
import plotly.graph_objects as go

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(
    page_title="Credit Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap");

    html, body, [class*="css"] {
        font-family: "DM Sans", sans-serif;
    }

    .stApp {
        background: radial-gradient(1200px 600px at 12% -10%, #1b2a4a 0%, transparent 55%),
                    radial-gradient(900px 500px at 100% 0%, #2a1528 0%, transparent 50%),
                    #0b1020;
        color: #e8eef8;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    #MainMenu, footer { visibility: hidden; }

    .block-container {
        max-width: 1080px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 1.6rem 1.8rem 1.35rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 18px 50px rgba(0,0,0,0.28);
    }
    .hero h1 {
        margin: 0 0 0.35rem 0;
        font-size: 1.85rem;
        letter-spacing: -0.02em;
        color: #f4f7ff;
    }
    .hero p {
        margin: 0;
        color: #b7c3d9;
        font-size: 0.98rem;
        line-height: 1.5;
    }
    .eyebrow {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #8eb4ff;
        margin-bottom: 0.45rem;
    }

    div[data-testid="stForm"] {
        background: rgba(17, 24, 43, 0.88);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 1.35rem 1.4rem 1.1rem;
        box-shadow: 0 16px 40px rgba(0,0,0,0.25);
    }

    .section-kicker {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #93a4c7;
        margin-bottom: 0.2rem;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f3f6ff;
        margin-bottom: 0.85rem;
    }

    .hint-box {
        background: rgba(91, 140, 255, 0.10);
        border: 1px solid rgba(91, 140, 255, 0.22);
        color: #c9d7f2;
        border-radius: 12px;
        padding: 0.7rem 0.85rem;
        font-size: 0.86rem;
        line-height: 1.45;
        margin: 0.15rem 0 0.85rem 0;
    }

    .band {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border-radius: 999px;
        padding: 0.22rem 0.7rem;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .band-nearby { background: rgba(46, 204, 113, 0.16); color: #7dffb6; border: 1px solid rgba(46, 204, 113, 0.28); }
    .band-moderate { background: rgba(241, 196, 15, 0.16); color: #ffe38a; border: 1px solid rgba(241, 196, 15, 0.28); }
    .band-far { background: rgba(231, 76, 60, 0.16); color: #ffb0a8; border: 1px solid rgba(231, 76, 60, 0.28); }

    .result-panel {
        background: rgba(17, 24, 43, 0.92);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 1.2rem 1.3rem 0.4rem;
        margin-top: 1.1rem;
        box-shadow: 0 16px 40px rgba(0,0,0,0.25);
    }
    .verdict {
        display: inline-block;
        border-radius: 999px;
        padding: 0.38rem 0.9rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        font-size: 0.82rem;
    }
    .verdict-fraud { background: rgba(231, 76, 60, 0.18); color: #ff9d96; border: 1px solid rgba(231, 76, 60, 0.4); }
    .verdict-genuine { background: rgba(46, 204, 113, 0.16); color: #7dffb6; border: 1px solid rgba(46, 204, 113, 0.38); }
    .verdict-unknown { background: rgba(255,255,255,0.08); color: #d5def0; border: 1px solid rgba(255,255,255,0.16); }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 0.7rem 0.8rem 0.55rem;
    }
    div[data-testid="stMetric"] label { color: #9aabc8 !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.15rem;
        color: #f4f7ff !important;
    }

    .stButton > button,
    div[data-testid="stFormSubmitButton"] button {
        width: 100%;
        background: linear-gradient(90deg, #3b82f6, #6366f1) !important;
        color: white !important;
        border: 0 !important;
        border-radius: 12px !important;
        padding: 0.65rem 1rem;
        font-weight: 700;
        letter-spacing: 0.01em;
    }
    .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(90deg, #4f8ef7, #7577f3) !important;
        color: white !important;
        border: 0 !important;
    }

    [data-testid="stCaption"] { color: #93a4c7 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def distance_band(km: float) -> tuple[str, str]:
    if km < 50:
        return "Nearby", "band-nearby"
    if km <= 300:
        return "Moderate", "band-moderate"
    return "Far", "band-far"


def normalize_risk(score) -> float:
    try:
        value = float(score)
    except (TypeError, ValueError):
        return 0.0
    if value > 1.0:
        value = value / 100.0
    return max(0.0, min(value, 1.0))


def risk_gauge(score: float) -> go.Figure:
    pct = normalize_risk(score) * 100.0
    if pct < 40:
        bar_color = "#22c55e"
    elif pct < 70:
        bar_color = "#f59e0b"
    else:
        bar_color = "#ef4444"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 32, "color": "#f4f7ff"}},
            title={"text": "Risk score", "font": {"size": 14, "color": "#9aabc8"}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "#93a4c7",
                    "tickfont": {"color": "#93a4c7"},
                },
                "bar": {"color": bar_color, "thickness": 0.28},
                "bgcolor": "rgba(255,255,255,0.04)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "rgba(34, 197, 94, 0.18)"},
                    {"range": [40, 70], "color": "rgba(245, 158, 11, 0.18)"},
                    {"range": [70, 100], "color": "rgba(239, 68, 68, 0.18)"},
                ],
                "threshold": {
                    "line": {"color": "#f4f7ff", "width": 2},
                    "thickness": 0.75,
                    "value": pct,
                },
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=260,
        margin=dict(t=50, b=10, l=30, r=30),
        font={"family": "DM Sans, sans-serif"},
    )
    return fig


st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Realtime scoring</div>
        <h1>Credit Fraud Detection Engine</h1>
        <p>Enter a transaction and the ensemble model will return a fraud / genuine decision,
        an overall risk score, and a per-model breakdown. Nothing is stored — this is a scoring UI only.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

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
        st.caption(
            "Billed amount in USD. Larger amounts raise risk when they look unusual for the cardholder."
        )

    with distance_col:
        distance = st.number_input(
            "Distance from home (km)",
            min_value=0.0,
            value=5.2,
            help="How far the transaction occurred from the cardholder's registered home address (km). Larger distances, especially combined with high amounts, are a common fraud signal.",
        )
        band_label, band_class = distance_band(distance)
        st.markdown(
            f'<span class="band {band_class}">{band_label}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="hint-box">
                How far the transaction occurred from the cardholder's registered home address (km).
                Larger distances, especially combined with high amounts, are a common fraud signal.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        merchant_category = st.selectbox(
            "Merchant category",
            ["grocery", "electronics", "travel", "entertainment", "online_services"],
            help="Where the card was used. Grocery is typically lower risk; electronics, travel, and online services are more often associated with fraud.",
        )
        st.caption("Type of merchant. Electronics, travel, and online services tend to be higher risk than grocery.")
    with col2:
        transaction_type = st.selectbox(
            "Transaction type",
            ["in_store_chip", "online_checkout", "international_online"],
            help="How the payment was made. In-store chip is usually safer; online and especially international online checkouts carry more fraud risk.",
        )
        st.caption("How the payment was made. Online and international checkouts are generally riskier than in-store chip.")
    with col3:
        card_type = st.selectbox(
            "Card type",
            ["visa", "mastercard", "amex"],
            help="Card network used for this payment. This is contextual input for the model, not a verdict on the cardholder.",
        )
        st.caption("Card network (Visa, Mastercard, or Amex). Used as context by the model, not as a decision by itself.")

    submit = st.form_submit_button("Analyze risk")

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
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()

                decision = data.get("final_decision", "UNKNOWN")
                risk_score = data.get("risk_score", 0.0)
                risk_pct = normalize_risk(risk_score)

                if decision == "FRAUD":
                    verdict_class = "verdict-fraud"
                    verdict_copy = "High-risk pattern detected across the ensemble."
                elif decision == "GENUINE":
                    verdict_class = "verdict-genuine"
                    verdict_copy = "No strong fraud signal from the ensemble."
                else:
                    verdict_class = "verdict-unknown"
                    verdict_copy = "The backend returned an unrecognized decision label."

                st.markdown(
                    f"""
                    <div class="result-panel">
                    <div class="section-kicker">Result</div>
                    <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap;margin:0.15rem 0 0.35rem 0;">
                        <span class="verdict {verdict_class}">{decision}</span>
                        <span style="color:#b7c3d9;font-size:0.95rem;">{verdict_copy}</span>
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
                    st.caption(
                        "Green < 40% · Amber 40–70% · Red > 70%. Score is scaled to 0–100% for display only."
                    )

                st.markdown(
                    '<div class="section-kicker" style="margin-top:0.4rem;">Model breakdown</div>',
                    unsafe_allow_html=True,
                )
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric(
                        "XGBoost fraud prob",
                        f"{float(data.get('xgb_fraud_prob', 0.0)):.4f}",
                    )
                with m2:
                    iso_flag = data.get("iso_forest_anomaly")
                    st.metric(
                        "Isolation Forest",
                        "Anomaly" if iso_flag else "Normal",
                    )
                with m3:
                    if "autoencoder_anomaly" in data:
                        ae_flag = data.get("autoencoder_anomaly")
                        st.metric(
                            "Autoencoder",
                            "Anomaly" if ae_flag else "Normal",
                        )
                    else:
                        st.metric("Autoencoder", "—")
                with m4:
                    if "autoencoder_mse" in data:
                        st.metric(
                            "Autoencoder MSE",
                            f"{float(data.get('autoencoder_mse', 0.0)):.4f}",
                        )
                    else:
                        st.metric("Autoencoder MSE", "—")

            else:
                st.error(f"Error connecting to backend: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error(
                "Failed to connect to the backend API. Please ensure the backend server is running on http://localhost:8000"
            )
