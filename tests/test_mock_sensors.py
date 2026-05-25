import pytest
from data.mock_sensors import (
    get_mock_vitals,
    get_mock_sleep_report,
    get_mock_health_history,
    set_simulate_abnormal,
    set_vitals_override,
)


def test_get_mock_vitals_schema():
    """Test that mock vitals have all required keys."""
    set_simulate_abnormal(False)
    vitals = get_mock_vitals()
    assert "heart_rate" in vitals
    assert "spo2" in vitals
    assert "temperature" in vitals
    assert "timestamp" in vitals


def test_get_mock_vitals_normal_ranges():
    """Test that normal mode vitals fall within expected ranges."""
    set_simulate_abnormal(False)
    for _ in range(20):
        v = get_mock_vitals()
        assert 65 <= v["heart_rate"] <= 85
        assert 95 <= v["spo2"] <= 99


def test_get_mock_vitals_abnormal_mode():
    """Test that abnormal mode produces out-of-range vitals."""
    set_simulate_abnormal(True)
    try:
        v = get_mock_vitals()
        assert v["heart_rate"] > 120 or v["spo2"] < 90
    finally:
        set_simulate_abnormal(False)


def test_get_mock_sleep_report_schema():
    """Test that mock sleep report has all required keys."""
    report = get_mock_sleep_report()
    assert "total_hours" in report
    assert "deep_sleep_hours" in report
    assert "wake_count" in report
    assert "date" in report


def test_get_mock_health_history_length():
    """Test that health history returns correct number of days."""
    assert len(get_mock_health_history(7)) == 7
    assert len(get_mock_health_history(30)) == 30


def test_get_mock_health_history_schema():
    """Test that health history records have all required keys."""
    for record in get_mock_health_history(3):
        assert "date" in record
        assert "heart_rate_avg" in record
        assert "spo2_avg" in record
        assert "sleep_hours" in record


def test_get_mock_health_history_invalid_days():
    """Test that invalid days argument raises ValueError."""
    with pytest.raises(ValueError):
        get_mock_health_history(0)


def test_set_vitals_override_returns_exact_values():
    """Test that overridden vitals are returned exactly as set."""
    set_vitals_override({"heart_rate": 130, "spo2": 85, "temperature": 28.5})
    try:
        v = get_mock_vitals()
        assert v["heart_rate"] == 130
        assert v["spo2"] == 85
        assert v["temperature"] == 28.5
    finally:
        set_vitals_override(None)


def test_set_vitals_override_partial_keys_fallback_to_random():
    """Test that unspecified keys in override fall back to random normal values."""
    set_vitals_override({"heart_rate": 42})
    try:
        for _ in range(10):
            v = get_mock_vitals()
            assert v["heart_rate"] == 42
            assert 95 <= v["spo2"] <= 99
    finally:
        set_vitals_override(None)


def test_set_vitals_override_none_restores_normal_range():
    """Test that clearing override returns vitals to random normal range."""
    set_vitals_override({"heart_rate": 150, "spo2": 80})
    set_vitals_override(None)
    set_simulate_abnormal(False)
    for _ in range(20):
        v = get_mock_vitals()
        assert 65 <= v["heart_rate"] <= 85
        assert 95 <= v["spo2"] <= 99


def test_set_vitals_override_takes_priority_over_simulate_abnormal():
    """Test that vitals override has higher priority than simulate_abnormal flag."""
    set_simulate_abnormal(True)
    set_vitals_override({"heart_rate": 60, "spo2": 97})
    try:
        v = get_mock_vitals()
        assert v["heart_rate"] == 60
        assert v["spo2"] == 97
    finally:
        set_vitals_override(None)
        set_simulate_abnormal(False)
