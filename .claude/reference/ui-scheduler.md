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
  💓 心率：72 bpm（正常 / ⚠️ 異常）
  🩸 血氧：98%（正常 / ⚠️ 異常）
  😴 昨晚睡眠：7.5 hrs
  🌡️ 環境溫度：26.0°C

💊 今日用藥
  ⏰ 08:00 — 降血壓藥（Amlodipine 5mg）
  ⏰ 13:00 — 維生素D
  ⏰ 19:00 — Metformin 500mg

🎮 Demo 控制台
  [🌅 模擬早晨問候]
  [🚨 模擬心率異常（125 bpm）]
  [🔄 恢復正常數值]   ← 只在 simulate_abnormal=True 時顯示
```

異常判定：`hr > 120 or hr < 50` / `spo2 < 90` → `st.metric` 顯示 `"⚠️ 異常"`。

---

## 右欄：對話視窗（col_chat）

```python
chat_container = st.container(height=520)   # 固定高度，可捲動
# 顯示歷史訊息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 輸入欄
if user_input := st.chat_input("和阿嬤的健康伴侶說話..."):
    ...
    response = invoke_agent(st.session_state.agent, user_input)
    st.rerun()
```

---

## APScheduler 主動監測

```python
from apscheduler.schedulers.background import BackgroundScheduler

if "scheduler_started" not in st.session_state:
    def _proactive_monitor():
        vitals = get_mock_vitals()
        if vitals["heart_rate"] > 120 or vitals["spo2"] < 90:
            st.session_state["pending_proactive"] = f"（系統觸發）..."

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(_proactive_monitor, "interval", seconds=5)
    _scheduler.start()
    st.session_state.scheduler_started = True
```

`scheduler_started` 用 `st.session_state` 防止 Streamlit rerun 重複建立 scheduler。

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
2. 偵測異常 → 寫入 `st.session_state.pending_proactive`
3. 下一次 rerun 時，頂部 proactive 檢查執行 → invoke_agent → st.rerun()
4. 對話視窗顯示 Agent 的主動回應

---

## Session State 一覽

| key | 型別 | 說明 |
|-----|------|------|
| `agent` | `_AgentWithMemory` | 已初始化的 CareAgent |
| `messages` | `list[dict]` | 對話歷史（role + content） |
| `simulate_abnormal` | `bool` | 是否啟用異常模擬 |
| `pending_proactive` | `str \| None` | 主動觸發訊息佇列 |
| `scheduler_started` | `bool` | 防止重複建立 scheduler |
