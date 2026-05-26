# tests/test_charts.py
import plotly.graph_objects as go
from data.mock_sensors import get_mock_health_history

_TH = {
    "heart_rate_high": 120,
    "heart_rate_low": 50,
    "spo2_low": 90,
    "systolic_high": 140,
    "diastolic_high": 90,
}


def test_build_trend_chart_returns_figure():
    from charts import build_trend_chart
    history = get_mock_health_history(30)
    fig = build_trend_chart(history, _TH)
    assert isinstance(fig, go.Figure)


def test_build_trend_chart_has_three_traces():
    from charts import build_trend_chart
    history = get_mock_health_history(30)
    fig = build_trend_chart(history, _TH)
    assert len(fig.data) == 3


def test_build_trend_chart_has_four_threshold_shapes():
    from charts import build_trend_chart
    history = get_mock_health_history(30)
    fig = build_trend_chart(history, _TH)
    # HR high, HR low, SpO2 low, systolic high
    assert len(fig.layout.shapes) == 4


def test_build_trend_chart_data_length_matches_history():
    from charts import build_trend_chart
    history = get_mock_health_history(7)
    fig = build_trend_chart(history, _TH)
    assert len(fig.data[0].x) == 7
    assert len(fig.data[1].x) == 7
    assert len(fig.data[2].x) == 7


def test_build_trend_chart_height_is_set():
    from charts import build_trend_chart
    history = get_mock_health_history(30)
    fig = build_trend_chart(history, _TH)
    assert fig.layout.height is not None
    assert fig.layout.height >= 400
