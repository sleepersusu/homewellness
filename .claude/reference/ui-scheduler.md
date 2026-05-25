# Streamlit UI + APScheduler（app.py）

## 頁面佈局

```
st.columns([1, 2])
├── col_data（左 1/3）  — 即時數據面板 + Demo 控制台
└── col_chat（右 2/3）  — AI 健康對話視窗
```

---

## 左欄：即時數據面板（col_data）

每次 rerun 重新呼叫 `get_mock_vitals()` 和 `get_mock_sleep_report()`，顯示最新數值。

```
📊 即時生理數據
  [警報閾值提示]  心率：< 50 或 > 120 bpm ｜ 血氧：< 90%

  🎛️ 場景模擬（預設展開）
    ● 正常  ○ 心跳過快  ○ 心跳過慢  ○ 低血氧  ○ 自訂
    （自訂時顯示心率 / 血氧 / 溫度 slider）

  💓 心率：72 bpm（正常 / ⚠️ 異常）
  🩸 血氧：98%（正常 / ⚠️ 異常）
  😴 昨晚睡眠：7.5 hrs
  🌡️ 環境溫度：26.0°C

💊 今日用藥
  ⏰ 08:00 — 降血壓藥（Amlodipine 5mg）
  ⏰ 13:00 — 維生素D
  ⏰ 19:00 — Metformin 500mg

  ✏️ 調整用藥時間（可展開）
    time_input × 3，[重置為預設時間]

🎮 Demo 控制台
  [🌅 模擬早晨問候]
  [🚨 模擬心率異常（125 bpm）]
```

異常判定：`hr > 120 or hr < 50` / `spo2 < 90` → `st.metric` 顯示 `"⚠️ 異常"`。

---

## 場景模擬系統

場景 radio（`key="vitals_scenario"`）控制 `set_vitals_override()`，在 `get_mock_vitals()` 之前執行，確保 metric 顯示與 APScheduler 偵測都使用同一份數據。

```python
_SCENARIO_PRESETS = {
    "心跳過快": {"heart_rate": 125, "spo2": 88},
    "心跳過慢": {"heart_rate": 42,  "spo2": 96},
    "低血氧":   {"heart_rate": 95,  "spo2": 85},
}

# 場景應用（在 get_mock_vitals() 之前）
if scenario in _SCENARIO_PRESETS:
    set_vitals_override(_SCENARIO_PRESETS[scenario])
elif scenario == "自訂":
    set_vitals_override({"heart_rate": hr_val, "spo2": spo2_val, "temperature": temp_val})
else:  # 正常
    set_vitals_override(None)
```

Demo 按鈕「🚨 模擬心率異常」會將 `st.session_state.vitals_scenario = "心跳過快"`，讓 radio 在下次 rerun 自動顯示正確選項。

---

## 用藥時間編輯

```python
# med_overrides 存在 session_state，key 為藥名
if "med_overrides" not in st.session_state:
    st.session_state.med_overrides = {
        med["name"]: med["time"] for med in _PROFILE["medications"]
    }

# 顯示（讀 med_overrides）
for med in _PROFILE["medications"]:
    t = st.session_state.med_overrides.get(med["name"], med["time"])
    st.write(f"⏰ {t} — {med['name']}")

# 編輯（expander 內）
new_t = st.time_input(med["name"], value=dtime(h, m), key=f"med_time_{i}")
st.session_state.med_overrides[med["name"]] = new_t.strftime("%H:%M")
```

重置時刪除 `med_time_{i}` keys 讓 time_input 回到預設值。

---

## 右欄：對話視窗（col_chat）

```python
chat_container = st.container(height=520)   # 固定高度，可捲動
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_input := st.chat_input("和阿嬤的健康伴侶說話..."):
    response = invoke_agent(st.session_state.agent, user_input)
    st.rerun()
```

---

## APScheduler 主動監測

```python
from apscheduler.schedulers.background import BackgroundScheduler

if "scheduler_started" not in st.session_state:
    def _proactive_monitor():
        vitals = get_mock_vitals()   # 受 set_vitals_override 影響
        thresholds = ..._PROFILE["alert_thresholds"]
        if vitals["heart_rate"] > thresholds["heart_rate_high"] \
                or vitals["spo2"] < thresholds["spo2_low"]:
            st.session_state["pending_proactive"] = f"（系統觸發）..."

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(_proactive_monitor, "interval", seconds=5)
    _scheduler.start()
    st.session_state.scheduler_started = True
```

`scheduler_started` 防止 Streamlit rerun 重複建立 scheduler。

---

## Proactive Trigger 機制

```python
# app.py 頂部，每次 rerun 檢查
if st.session_state.pending_proactive:
    _msg = st.session_state.pending_proactive
    st.session_state.pending_proactive = None   # 清除，避免重複觸發
    response = invoke_agent(st.session_state.agent, _msg)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
```

**流程**：
1. `_proactive_monitor()` 每 5 秒由背景執行緒呼叫
2. 場景設為「心跳過快/心跳過慢/低血氧」或自訂異常值 → `get_mock_vitals()` 回傳異常數值
3. 偵測超閾值 → 寫入 `st.session_state.pending_proactive`
4. 下一次 rerun 時，頂部 proactive 檢查執行 → invoke_agent → st.rerun()
5. 對話視窗顯示 Agent 的主動回應

---

## Session State 一覽

| key | 型別 | 說明 |
|-----|------|------|
| `agent` | `_AgentWithMemory` | 已初始化的 CareAgent |
| `messages` | `list[dict]` | 對話歷史（role + content） |
| `model_key` | `str` | 當前模型組合，變更時重建 agent |
| `vitals_scenario` | `str` | 場景 radio 選項（正常/心跳過快/心跳過慢/低血氧/自訂） |
| `med_overrides` | `dict[str, str]` | 藥名 → 覆蓋時間（HH:MM） |
| `pending_proactive` | `str \| None` | 主動觸發訊息佇列 |
| `scheduler_started` | `bool` | 防止重複建立 scheduler |
