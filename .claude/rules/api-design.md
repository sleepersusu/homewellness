# Agent Tool Design — HomeWellness Companion

此專案沒有 REST API。對外介面是 **LangChain `@tool` 函式**，供 Agent 呼叫。

---

## Tool 設計規範

### 命名

- 函式名稱：`snake_case`，以動詞開頭（`get_`, `send_`, `call_`）
- 清楚表達「取得什麼」或「執行什麼動作」

```python
get_vitals()               # 正確：取得即時數值
get_sleep_report()         # 正確：取得睡眠報告
send_emergency_alert()     # 正確：執行通報動作

fetch_data()               # 避免：太模糊
data_tool()                # 避免：不清楚是什麼
```

### Docstring（必須）

LangChain 把 docstring 作為 tool description 傳給 LLM，LLM 靠它決定何時呼叫。必須說明：
1. 這個工具做什麼
2. 何時呼叫（觸發情境）
3. 參數說明（若有）

```python
@tool
def get_vitals() -> dict:
    """讀取即時生理數據：心率（heart_rate bpm）、血氧（spo2 %）、環境溫度（temperature °C）。
    當用戶提到頭暈、不舒服、胸悶、身體異常時使用此工具。"""
```

### 回傳型別

- 回傳 `dict`（結構化，LLM 容易解讀）或 `str`（確認訊息）
- 不拋例外——用 `{"error": "說明"}` 回傳錯誤，避免中斷 agent 流程

```python
@tool
def get_health_trend(days: int = 7) -> dict:
    if days < 1:
        return {"error": "days 必須 >= 1"}   # 回傳 error dict，不 raise
    ...
```

---

## Tool 分配原則

| 工具 | 給哪個 Agent |
|------|------------|
| `get_vitals` | CareAgent（即時問答）+ AlertAgent（異常評估） |
| `get_sleep_report` | CareAgent |
| `get_medication_schedule` | CareAgent |
| `get_health_trend` | AnalysisAgent（只給分析 agent，避免 CareAgent 直接深度分析） |
| `send_emergency_alert` | AlertAgent（只給緊急 agent，避免 CareAgent 誤觸） |

**原則**：最小權限原則。每個 Agent 只拿它需要的工具。

---

## Proactive 訊息格式（app.py → agent）

系統觸發的訊息前加 `（系統觸發）` 前綴，讓 Agent 知道這是背景觸發而非長者輸入：

```python
"（系統觸發）偵測到異常數值：心率 125 bpm，血氧 88%，請立即關心陳阿嬤。"
"（系統觸發）現在是早上8點，請主動問候陳阿嬤，分享昨晚睡眠報告。"
```
