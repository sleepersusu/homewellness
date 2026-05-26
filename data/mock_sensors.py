"""Mock IoT sensor data provider for testing and development."""

import random
from datetime import datetime, timedelta

_simulate_abnormal: bool = False
_vitals_override: dict | None = None


def set_simulate_abnormal(value: bool) -> None:
    """Set whether to simulate abnormal vital signs."""
    global _simulate_abnormal
    _simulate_abnormal = value


def set_vitals_override(values: dict | None) -> None:
    """Override specific vitals values. Pass None to clear.

    Args:
        values: dict with optional keys heart_rate, spo2, temperature,
                blood_pressure ({"systolic": int, "diastolic": int}), steps.
    """
    global _vitals_override
    _vitals_override = values


def get_mock_vitals() -> dict[str, int | float | str | dict]:
    """Get mock vital signs readings.

    Priority: custom override > abnormal simulation > random normal.
    """
    if _vitals_override is not None:
        default_bp = {"systolic": random.randint(110, 135), "diastolic": random.randint(70, 85)}
        return {
            "heart_rate": _vitals_override.get("heart_rate", random.randint(65, 85)),
            "spo2": _vitals_override.get("spo2", random.randint(95, 99)),
            "temperature": _vitals_override.get("temperature", round(random.uniform(25.0, 27.0), 1)),
            "blood_pressure": _vitals_override.get("blood_pressure", default_bp),
            "steps": _vitals_override.get("steps", random.randint(500, 8000)),
            "timestamp": datetime.now().isoformat(),
        }
    if _simulate_abnormal:
        return {
            "heart_rate": 125,
            "spo2": 88,
            "temperature": 26.5,
            "blood_pressure": {"systolic": 165, "diastolic": 105},
            "steps": random.randint(500, 8000),
            "timestamp": datetime.now().isoformat(),
        }
    return {
        "heart_rate": random.randint(65, 85),
        "spo2": random.randint(95, 99),
        "temperature": round(random.uniform(25.0, 27.0), 1),
        "blood_pressure": {"systolic": random.randint(110, 135), "diastolic": random.randint(70, 85)},
        "steps": random.randint(500, 8000),
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
            "blood_pressure_systolic_avg": random.randint(112, 138),
            "blood_pressure_diastolic_avg": random.randint(72, 88),
            "steps": random.randint(2000, 8000),
        }
        for i in range(days)
    ]
