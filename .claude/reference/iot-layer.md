# IoT 資料層（data/）

## 概覽

目前使用 Mock 模擬，正式架構對應 AWS IoT Core + MQTT。

```
data/
├── mock_sensors.py       # Mock IoT 感測器
├── health_profile.json   # 病患靜態檔案（不變）
└── health_history.json   # 近 30 天生理歷史
```

---

## mock_sensors.py

### 全域狀態與優先級

```python
_simulate_abnormal: bool = False   # 舊版相容，保留供測試
_vitals_override: dict | None = None   # 新：UI 場景模擬用

# get_mock_vitals() 優先級：
# _vitals_override（最高）> _simulate_abnormal > 隨機正常值
```

### `set_vitals_override(values: dict | None)`

UI 場景模擬的主要入口，傳 `None` 清除覆蓋值：

```python
# 場景預設
set_vitals_override({"heart_rate": 125, "spo2": 88})     # 心跳過快
set_vitals_override({"heart_rate": 42,  "spo2": 96})     # 心跳過慢
set_vitals_override({"heart_rate": 95,  "spo2": 85})     # 低血氧
set_vitals_override({"heart_rate": hr, "spo2": s, "temperature": t})  # 自訂
set_vitals_override(None)                                 # 清除，回到隨機
```

keys 為選填，未指定的項目回落到隨機正常值。

### `set_simulate_abnormal(value: bool)`

保留供測試使用。UI 已改用 `set_vitals_override()`。

### `get_mock_vitals() -> dict`

```python
# 正常模式（_vitals_override = None, _simulate_abnormal = False）
{"heart_rate": 72, "spo2": 98, "temperature": 26.0, "timestamp": "..."}

# 自訂覆蓋模式
{"heart_rate": 125, "spo2": 88, "temperature": 26.0, "timestamp": "..."}

# 舊版異常模式（_simulate_abnormal = True）
{"heart_rate": 125, "spo2": 88, "temperature": 26.5, "timestamp": "..."}
```

### `get_mock_sleep_report() -> dict`

```python
{"total_hours": 7.5, "deep_sleep_hours": 2.1, "wake_count": 1, "date": "..."}
```

### `get_mock_health_history(days: int) -> list[dict]`

回傳近 days 天的每日平均生理數據。若 `days < 1` 拋 `ValueError`。
```python
[
  {"date": "2026-05-18", "heart_rate_avg": 74, "spo2_avg": 97, "sleep_hours": 7.1},
  ...
]
```

---

## health_profile.json

靜態病患資料。`prompts.py`、`tools.py` 和 `app.py` 直接讀取。

```json
{
  "name": "陳阿嬤",
  "age": 72,
  "conditions": ["高血壓", "輕度糖尿病"],
  "medications": [
    {"name": "降血壓藥（Amlodipine 5mg）", "time": "08:00", "with_meal": true},
    {"name": "維生素D", "time": "13:00", "with_meal": true},
    {"name": "Metformin 500mg", "time": "19:00", "with_meal": true}
  ],
  "emergency_contacts": [
    {"name": "陳大文（兒子）", "phone": "0912-345-678"}
  ],
  "alert_thresholds": {
    "heart_rate_high": 120,
    "heart_rate_low": 50,
    "spo2_low": 90
  }
}
```

`alert_thresholds` 同時用於 APScheduler 偵測邏輯與 UI 頂部的閾值提示顯示。

`tools.py` 用絕對路徑載入：`Path(__file__).parent.parent / "data" / "health_profile.json"`

---

## health_history.json

近 30 天生理歷史，供 `get_health_trend` 使用。格式：
```json
[
  {"date": "2026-04-26", "heart_rate_avg": 73, "spo2_avg": 97, "sleep_hours": 7.2},
  ...
]
```

---

## 正式架構對應（AWS）

| Mock | 正式 |
|------|------|
| `mock_sensors.py` | IoT 手環 → MQTT → AWS IoT Core |
| `health_profile.json` | DynamoDB 病患資料表 |
| `health_history.json` | DynamoDB 時序數據表 |
| `set_vitals_override()` | 移除，由真實感測器數值觸發 |
| `set_simulate_abnormal()` | 移除，由真實感測器數值觸發 |
