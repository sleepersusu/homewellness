# Streamlit UI + APScheduler（app.py）

## 頁面佈局

```
Sidebar
├── ⚙️ 模型設定（CareAgent / AnalysisAgent / AlertAgent selectbox）
└── 📊 效能監控（最近一次延遲 / Token / 費用 + 累計統計）

st.columns([1, 2])
├── col_data（左 1/3）  — 即時數據面板 + Demo 控制台
└── col_chat（右 2/3）  — AI 健康對話視窗
```

---

## Sidebar：模型設定 + 效能監控

```python
with st.sidebar:
    # 模型選擇（三個 selectbox）
    care_model     = st.selectbox("🤖 CareAgent", AVAILABLE_MODELS, ...)
    analysis_model = st.selectbox("🧪 AnalysisAgent", AVAILABLE_MODELS, ...)
    alert_model    = st.selectbox("🚨 AlertAgent", AVAILABLE_MODELS, ...)

    # 模型組合變更時自動重建 agent 並清空對話
    model_key = f"{care_model}|{analysis_model}|{alert_model}"
    if st.session_state.get("model_key") != model_key:
        st.session_state.model_key = model_key
        st.session_state.pop("agent", None)
        st.session_state.messages = []

    st.divider()
    st.header("📊 效能監控")

    # 最近一次
    last = st.session_state.get("last_stats")
    if last:
        m1, m2 = st.columns(2)
        m1.metric("⏱️ 延遲", f"{last['latency']} s")
        m2.metric("💰 費用", f"${last['cost_usd']:.5f}")
        m3, m4 = st.columns(2)
        m3.metric("📥 輸入 Token", f"{last['input_tokens']:,}")
        m4.metric("📤 輸出 Token", f"{last['output_tokens']:,}")
        st.caption(f"模型：{last['model']}")

    # 累計統計
    cum = st.session_state.get("cumulative_stats", {})
    if cum.get("calls", 0) > 0:
        st.metric("🔢 對話次數", cum["calls"])
        st.metric("🪙 總 Token", f"{cum['total_tokens']:,}")
        st.metric("💵 總費用", f"${cum['total_cost']:.4f}")
```

---

## 左欄：即時數據面板（col_data）

每次 rerun 重新呼叫 `get_mock_vitals()` 和 `get_mock_sleep_report()`，顯示最新數值。

```
📊 即時生理數據
  [警報閾值提示 3 列]
    💓 心率：< 50 或 > 120 bpm  ｜  🩸 血氧：< 90%  ｜  🩺 收縮壓：> 140 mmHg

  🎛️ 場景模擬（預設展開）
    ● 正常  ○ 心跳過快  ○ 心跳過慢  ○ 低血氧  ○ 高血壓  ○ 自訂
    （自訂時第一列：心率 / 血氧 / 溫度 slider）
    （自訂時第二列：收縮壓 / 舒張壓 slider）

  💓 心率：72 bpm（正常 / ⚠️ 異常）
  🩸 血氧：98%（正常 / ⚠️ 異常）
  🩺 血壓：120/80 mmHg（正常 / ⚠️ 異常）
  🚶 今日步數：4,321 步
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

異常判定：`hr > 120 or hr < 50` / `spo2 < 90` / `bp["systolic"] > 140` → `st.metric` 顯示 `"⚠️ 異常"`。

---

## 場景模擬系統

場景 radio（`key="vitals_scenario"`）控制 `set_vitals_override()`，在 `get_mock_vitals()` 之前執行。

```python
_SCENARIO_OPTIONS = ["正常", "心跳過快", "心跳過慢", "低血氧", "高血壓", "自訂"]

_SCENARIO_PRESETS = {
    "心跳過快": {"heart_rate": 125, "spo2": 88},
    "心跳過慢": {"heart_rate": 42,  "spo2": 96},
    "低血氧":   {"heart_rate": 95,  "spo2": 85},
    "高血壓":   {"blood_pressure": {"systolic": 168, "diastolic": 108}},
}

# 場景應用（在 get_mock_vitals() 之前）
if scenario in _SCENARIO_PRESETS:
    set_vitals_override(_SCENARIO_PRESETS[scenario])
elif scenario == "自訂":
    # 第一列
    hr_val, spo2_val, temp_val = c1.slider(...), c2.slider(...), c3.slider(...)
    # 第二列
    systolic_val, diastolic_val = c4.slider(...), c5.slider(...)
    set_vitals_override({
        "heart_rate": hr_val, "spo2": spo2_val, "temperature": temp_val,
        "blood_pressure": {"systolic": systolic_val, "diastolic": diastolic_val},
    })
else:  # 正常
    set_vitals_override(None)
    set_simulate_abnormal(False)
```

---

## 用藥時間編輯

```python
if "med_overrides" not in st.session_state:
    st.session_state.med_overrides = {
        med["name"]: med["time"] for med in _PROFILE["medications"]
    }

for med in _PROFILE["medications"]:
    t = st.session_state.med_overrides.get(med["name"], med["time"])
    st.write(f"⏰ {t} — {med['name']}")

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
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("思考中..."):
        response, stats = invoke_agent(
            st.session_state.agent, user_input,
            model=st.session_state.get("care_model", "gpt-4o-mini"),
        )
    _record_stats(stats)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
```

---

## Stats 記錄輔助函式

```python
def _record_stats(stats: dict) -> None:
    st.session_state.last_stats = stats
    c = st.session_state.cumulative_stats
    c["calls"] += 1
    c["total_tokens"] += stats["total_tokens"]
    c["total_cost"] += stats["cost_usd"]
```

所有 `invoke_agent()` 呼叫（Demo 按鈕 × 2、chat input、proactive trigger）都在取得回傳值後立即呼叫 `_record_stats(stats)`。

---

## APScheduler 主動監測

```python
from apscheduler.schedulers.background import BackgroundScheduler

if "scheduler_started" not in st.session_state:
    def _proactive_monitor():
        vitals = get_mock_vitals()
        thresholds = ..._PROFILE["alert_thresholds"]
        bp = vitals["blood_pressure"]
        if (
            vitals["heart_rate"] > thresholds["heart_rate_high"]
            or vitals["spo2"] < thresholds["spo2_low"]
            or bp["systolic"] > thresholds["systolic_high"]   # 血壓異常
        ):
            st.session_state["pending_proactive"] = (
                f"（系統觸發）偵測到異常：心率 {vitals['heart_rate']} bpm，"
                f"血氧 {vitals['spo2']}%，"
                f"血壓 {bp['systolic']}/{bp['diastolic']} mmHg，請立即關心陳阿嬤。"
            )

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
    with st.spinner("Agent 偵測到異常..."):
        _resp, _stats = invoke_agent(
            st.session_state.agent, _msg,
            model=st.session_state.get("care_model", "gpt-4o-mini"),
        )
    _record_stats(_stats)
    st.session_state.messages.append({"role": "assistant", "content": _resp})
    st.rerun()
```

**流程**：
1. `_proactive_monitor()` 每 5 秒由背景執行緒呼叫
2. 場景設為異常值（心跳過快/心跳過慢/低血氧/高血壓）或自訂異常值 → `get_mock_vitals()` 回傳異常數值
3. 偵測超閾值 → 寫入 `st.session_state.pending_proactive`
4. 下一次 rerun 時，頂部 proactive 檢查執行 → invoke_agent → _record_stats → st.rerun()
5. 對話視窗顯示 Agent 的主動回應；sidebar 效能監控即時更新

---

## Session State 一覽

| key | 型別 | 說明 |
|-----|------|------|
| `agent` | `_AgentWithMemory` | 已初始化的 CareAgent |
| `messages` | `list[dict]` | 對話歷史（role + content） |
| `model_key` | `str` | 當前模型組合，變更時重建 agent |
| `vitals_scenario` | `str` | 場景 radio（正常/心跳過快/心跳過慢/低血氧/高血壓/自訂） |
| `med_overrides` | `dict[str, str]` | 藥名 → 覆蓋時間（HH:MM） |
| `pending_proactive` | `str \| None` | 主動觸發訊息佇列 |
| `scheduler_started` | `bool` | 防止重複建立 scheduler |
| `last_stats` | `dict \| None` | 最近一次 invoke_agent 的效能數據 |
| `cumulative_stats` | `dict` | 累計統計：`calls`, `total_tokens`, `total_cost` |
