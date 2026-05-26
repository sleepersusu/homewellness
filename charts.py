# charts.py — Plotly chart builders（純函式，不依賴 Streamlit）
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def build_trend_chart(history: list[dict], thresholds: dict) -> go.Figure:
    """Build a 3-row Plotly subplot showing 30-day health trends with threshold lines.

    Args:
        history: list of daily records from get_mock_health_history(), sorted by date.
        thresholds: alert_thresholds dict from health_profile.json.

    Returns:
        go.Figure with heart rate, SpO2, and systolic BP subplots.
    """
    dates = [r["date"] for r in history]

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("💓 心率 (bpm)", "🩸 血氧 SpO2 (%)", "🩺 收縮壓 (mmHg)"),
        vertical_spacing=0.08,
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[r["heart_rate_avg"] for r in history],
            name="心率",
            mode="lines+markers",
            line=dict(color="#4C9BE8", width=2),
            marker=dict(size=4),
        ),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[r["spo2_avg"] for r in history],
            name="血氧",
            mode="lines+markers",
            line=dict(color="#6CBF84", width=2),
            marker=dict(size=4),
        ),
        row=2, col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[r["blood_pressure_systolic_avg"] for r in history],
            name="收縮壓",
            mode="lines+markers",
            line=dict(color="#E86B4C", width=2),
            marker=dict(size=4),
        ),
        row=3, col=1,
    )

    _red = dict(color="rgba(220,50,50,0.7)", dash="dash", width=1.5)
    _orange = dict(color="rgba(255,165,0,0.7)", dash="dash", width=1.5)

    # Heart rate thresholds
    fig.add_shape(type="line", xref="paper", x0=0, x1=1,
                  yref="y",  y0=thresholds["heart_rate_high"], y1=thresholds["heart_rate_high"],
                  line=_red)
    fig.add_shape(type="line", xref="paper", x0=0, x1=1,
                  yref="y",  y0=thresholds["heart_rate_low"],  y1=thresholds["heart_rate_low"],
                  line=_orange)
    # SpO2 lower threshold
    fig.add_shape(type="line", xref="paper", x0=0, x1=1,
                  yref="y2", y0=thresholds["spo2_low"], y1=thresholds["spo2_low"],
                  line=_red)
    # Systolic upper threshold
    fig.add_shape(type="line", xref="paper", x0=0, x1=1,
                  yref="y3", y0=thresholds["systolic_high"], y1=thresholds["systolic_high"],
                  line=_red)

    fig.update_layout(
        height=520,
        showlegend=False,
        margin=dict(t=40, b=20, l=60, r=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")

    return fig
