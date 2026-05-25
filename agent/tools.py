"""LangChain tools for the HomeWellness Companion health agent."""

import json
from pathlib import Path

from langchain_core.tools import tool

from data.mock_sensors import (
    get_mock_health_history,
    get_mock_sleep_report,
    get_mock_vitals,
)

_PROFILE_PATH = Path("data/health_profile.json")


def _load_profile() -> dict:
    """Load health profile from JSON file."""
    return json.loads(_PROFILE_PATH.read_text(encoding="utf-8"))


@tool
def get_vitals() -> dict:
    """讀取即時生理數據：心率（heart_rate bpm）、血氧（spo2 %）、環境溫度（temperature °C）。
    當用戶提到頭暈、不舒服、胸悶、身體異常時使用此工具。"""
    return get_mock_vitals()


@tool
def get_medication_schedule() -> dict:
    """查詢今日用藥計畫，回傳藥名、服用時間、是否隨餐。
    用於用藥提醒或用戶詢問今天該吃什麼藥時使用。"""
    profile = _load_profile()
    return {"name": profile["name"], "medications": profile["medications"]}


@tool
def get_sleep_report() -> dict:
    """取得昨晚睡眠報告：總時數（total_hours）、深眠時數（deep_sleep_hours）、起夜次數（wake_count）。
    用於早晨問候時主動分享，或用戶詢問睡眠狀況時。"""
    return get_mock_sleep_report()


@tool
def get_health_trend(days: int = 7) -> dict:
    """分析近 N 天生理數據趨勢（心率、血氧、睡眠平均值）。
    用於用戶詢問近期健康狀況，或提供週期性健康建議時。"""
    history = get_mock_health_history(days)
    return {
        "days": days,
        "avg_heart_rate": round(
            sum(r["heart_rate_avg"] for r in history) / len(history), 1
        ),
        "avg_spo2": round(sum(r["spo2_avg"] for r in history) / len(history), 1),
        "avg_sleep_hours": round(
            sum(r["sleep_hours"] for r in history) / len(history), 1
        ),
        "daily_records": history,
    }


@tool
def send_emergency_alert(reason: str) -> str:
    """當生理數據出現危險異常時，通報緊急聯絡人及診所。
    觸發條件：心率 < 50 或 > 120 bpm，或血氧 < 90%。"""
    profile = _load_profile()
    contact = profile["emergency_contacts"][0]
    confirmation = f"已通報 {contact['name']}（{contact['phone']}）：{reason}"
    print(f"[緊急通報] {confirmation}")
    return confirmation
