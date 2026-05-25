"""Tests for LangChain @tool functions."""

import pytest
from data.mock_sensors import set_simulate_abnormal


def test_get_vitals_schema():
    """Test get_vitals returns all required fields."""
    from agent.tools import get_vitals

    result = get_vitals.invoke({})
    assert "heart_rate" in result
    assert "spo2" in result
    assert "temperature" in result
    assert "timestamp" in result


def test_get_medication_schedule_schema():
    """Test get_medication_schedule returns profile and medications."""
    from agent.tools import get_medication_schedule

    result = get_medication_schedule.invoke({})
    assert "medications" in result
    assert "name" in result
    assert len(result["medications"]) > 0
    # Verify medication structure
    for med in result["medications"]:
        assert "name" in med
        assert "time" in med
        assert "with_meal" in med


def test_get_sleep_report_schema():
    """Test get_sleep_report returns all required fields."""
    from agent.tools import get_sleep_report

    result = get_sleep_report.invoke({})
    assert "total_hours" in result
    assert "deep_sleep_hours" in result
    assert "wake_count" in result
    assert "date" in result


def test_get_health_trend_schema():
    """Test get_health_trend returns trend data for specified days."""
    from agent.tools import get_health_trend

    result = get_health_trend.invoke({"days": 7})
    assert "avg_heart_rate" in result
    assert "avg_spo2" in result
    assert "avg_sleep_hours" in result
    assert "daily_records" in result
    assert len(result["daily_records"]) == 7


def test_get_health_trend_invalid_days():
    """Test get_health_trend returns error for invalid days."""
    from agent.tools import get_health_trend

    result = get_health_trend.invoke({"days": 0})
    assert "error" in result


def test_send_emergency_alert_returns_confirmation():
    """Test send_emergency_alert returns confirmation with contact info."""
    from agent.tools import send_emergency_alert

    result = send_emergency_alert.invoke({"reason": "心率 125 bpm"})
    assert "已通報" in result
    assert "陳大文" in result


def test_get_vitals_abnormal_mode():
    """Test get_vitals returns abnormal values when simulation is enabled."""
    set_simulate_abnormal(True)
    try:
        from agent.tools import get_vitals

        result = get_vitals.invoke({})
        # In abnormal mode: heart_rate=125, spo2=88
        assert result["heart_rate"] == 125 or result["spo2"] == 88
    finally:
        set_simulate_abnormal(False)
