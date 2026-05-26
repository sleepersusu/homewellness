# LangChain Tools（agent/tools.py）

所有 `@tool` 函式都定義在這個檔案，由各 Agent 按需取用。

---

## 6 個工具一覽

| 工具 | 使用方的 Agent | 資料來源 |
|------|--------------|---------|
| `get_vitals()` | CareAgent, AlertAgent | `mock_sensors.get_mock_vitals()` |
| `get_sleep_report()` | CareAgent | `mock_sensors.get_mock_sleep_report()` |
| `get_medication_schedule()` | CareAgent | `health_profile.json` |
| `get_health_trend(days)` | AnalysisAgent | `mock_sensors.get_mock_health_history(days)` |
| `send_emergency_alert(reason)` | AlertAgent | `health_profile.json`（讀緊急聯絡人） |
| `schedule_followup(reason, delay_minutes)` | AlertAgent | `scheduler_tools`（threading.Timer） |

---

## 各工具詳細說明

### `get_vitals() -> dict`

回傳即時生理數據。
```python
{
  "heart_rate": 72,
  "spo2": 98,
  "temperature": 26.0,
  "steps": 4321,
  "blood_pressure": {"systolic": 120, "diastolic": 80}
}
# 異常模式（set_simulate_abnormal(True)）：{"heart_rate": 125, "spo2": 88, ...}
```
觸發情境：長者說「頭暈」「不舒服」「胸悶」，或 APScheduler 偵測到異常。

### `get_sleep_report() -> dict`

昨晚睡眠報告。
```python
{"total_hours": 7.5, "deep_sleep_hours": 2.1, "wake_count": 1}
```
觸發情境：早晨問候時主動分享，或長者問昨晚睡得好不好。

### `get_medication_schedule() -> dict`

今日用藥計畫（讀 health_profile.json）。
```python
{"name": "陳阿嬤", "medications": [
    {"name": "降血壓藥（Amlodipine 5mg）", "time": "08:00", "with_meal": true},
    ...
]}
```

### `get_health_trend(days: int = 7) -> dict`

分析近 N 天平均心率、血氧、睡眠時數（`days >= 1`，否則回傳 error dict）。
```python
{
  "days": 7,
  "avg_heart_rate": 74.2,
  "avg_spo2": 97.1,
  "avg_sleep_hours": 7.0,
  "daily_records": [...]
}
```

### `send_emergency_alert(reason: str) -> str`

通報緊急聯絡人（目前為 console print + 回傳確認字串）。
```python
"已通報 陳大文（兒子）（0912-345-678）：心率 125 bpm，超過閾值"
```
觸發條件：心率 > 120 或 < 50 bpm，或血氧 < 90%。

### `schedule_followup(reason: str, delay_minutes: int = 0) -> str`

緊急通報後排程追蹤關懷（cron-as-tool）。AlertAgent 通報後必須呼叫此工具。
- `delay_minutes=0` → 使用 Streamlit sidebar 的全域設定（預設 30 分鐘）
- `delay_minutes>0` → 使用指定分鐘數
```python
# 回傳確認字串
"✅ 已排程 30 分鐘後追蹤確認「心率異常後追蹤」"
```
實作：`threading.Timer(delay_seconds, _enqueue, args=[msg])` → `_followup_queue` → APScheduler `pop_followup()` → `pending_proactive`。

---

## 注意事項

- 所有工具透過 `from agent.tools import ...` 引入各 Agent
- `get_health_trend` 的 `days < 1` 會回傳 `{"error": "days 必須 >= 1"}`，不拋例外
- `_PROFILE_PATH` 使用 `Path(__file__).parent.parent / "data" / "health_profile.json"` 絕對路徑，避免 cwd 問題
- `schedule_followup` 在函式體內 lazy import `scheduler_tools`，與 APScheduler 的 `pop_followup()` 解耦
