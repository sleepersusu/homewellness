"""Mock IoT sensor data provider for testing and development."""

import random
from datetime import datetime, timedelta

_simulate_abnormal: bool = False


def set_simulate_abnormal(value: bool) -> None:
    """Set whether to simulate abnormal vital signs.

    Args:
        value: True to simulate abnormal readings, False for normal ranges.
    """
    global _simulate_abnormal
    _simulate_abnormal = value


def get_mock_vitals() -> dict[str, int | float | str]:
    """Get mock vital signs readings.

    Returns:
        Dictionary with heart_rate, spo2, temperature, and timestamp.
        If abnormal simulation is enabled, returns out-of-range values.
    """
    if _simulate_abnormal:
        return {
            "heart_rate": 125,
            "spo2": 88,
            "temperature": 26.5,
            "timestamp": datetime.now().isoformat(),
        }
    return {
        "heart_rate": random.randint(65, 85),
        "spo2": random.randint(95, 99),
        "temperature": round(random.uniform(25.0, 27.0), 1),
        "timestamp": datetime.now().isoformat(),
    }


def get_mock_sleep_report() -> dict[str, int | float | str]:
    """Get mock sleep data for the previous night.

    Returns:
        Dictionary with total_hours, deep_sleep_hours, wake_count, and date.
    """
    return {
        "total_hours": round(random.uniform(5.5, 8.0), 1),
        "deep_sleep_hours": round(random.uniform(1.5, 2.5), 1),
        "wake_count": random.randint(0, 3),
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
    }


def get_mock_health_history(days: int = 7) -> list[dict[str, int | float | str]]:
    """Get mock health history for the specified number of days.

    Args:
        days: Number of days of history to return (default: 7).

    Returns:
        List of daily health records with date, heart_rate_avg, spo2_avg, and sleep_hours.
    """
    if days < 1:
        raise ValueError(f"days must be >= 1, got {days}")
    return [
        {
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "heart_rate_avg": random.randint(68, 82),
            "spo2_avg": random.randint(95, 99),
            "sleep_hours": round(random.uniform(5.5, 8.0), 1),
        }
        for i in range(days)
    ]
