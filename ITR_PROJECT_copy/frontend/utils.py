"""
Shared helpers used across the Home page and the Live Scanner page.
Keeping these in one place means both pages always agree on how
risk scores are scaled, colored, and labeled.
"""

import plotly.graph_objects as go


def normalize_risk(score) -> float:
    """Coerce a raw model score into a 0.0–1.0 float, tolerant of 0–100 scales."""
    try:
        value = float(score)
    except (TypeError, ValueError):
        return 0.0
    if value > 1.0:
        value = value / 100.0
    return max(0.0, min(value, 1.0))


def distance_band(km: float) -> tuple[str, str]:
    """Return (label, css_class) for a distance-from-home value."""
    if km < 50:
        return "Nearby", "band-nearby"
    if km <= 300:
        return "Moderate", "band-moderate"
    return "Far", "band-far"


def risk_color(pct: float) -> str:
    if pct < 40:
        return "#22c55e"
    if pct < 70:
        return "#f59e0b"
    return "#ef4444"


def verdict_meta(decision: str) -> tuple[str, str]:
    """Return (css_class, human copy) for a final_decision label."""
    if decision == "FRAUD":
        return "verdict-fraud", "⚠️ High-risk pattern detected across the ensemble."
    if decision == "GENUINE":
        return "verdict-genuine", "✅ No strong fraud signal from the ensemble."
    return "verdict-unknown", "The backend returned an unrecognized decision label."


def risk_gauge(score) -> go.Figure:
    pct = normalize_risk(score) * 100.0
    
    # Use tokens: --success-green (#10B981), --warning-amber (#F59E0B), --danger-red (#EF4444)
    if pct < 40:
        bar_color = "#10B981"
    elif pct < 70:
        bar_color = "#F59E0B"
    else:
        bar_color = "#EF4444"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 36, "color": "#F9FAFB", "family": "Space Grotesk, sans-serif"}},
            title={"text": "Risk Score", "font": {"size": 14, "color": "#D1D5DB", "family": "Space Grotesk, sans-serif"}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "#475569",
                    "tickfont": {"color": "#94A3B8"},
                },
                "bar": {"color": bar_color, "thickness": 0.25},
                "bgcolor": "rgba(255,255,255,0.02)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "rgba(16, 185, 129, 0.15)"},
                    {"range": [40, 70], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [70, 100], "color": "rgba(239, 68, 68, 0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#FFFFFF", "width": 3},
                    "thickness": 0.8,
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
        font={"family": "Inter, sans-serif"},
    )
    return fig
