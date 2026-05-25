# Architecture — HomeWellness Companion

## 系統架構概覽

```
IoT 資料層（data/mock_sensors.py）
    ↓ APScheduler 每 5 秒輪詢
觸發層（app.py — pending_proactive 機制）
    ↓
CareAgent — 首腦 Orchestrator（agent/health_agent.py · gpt-4o-mini）
    ├─ 直接工具：get_vitals / get_sleep_report / get_medication_schedule
    ├─ → call_analysis_agent → AnalysisAgent（analysis_agent.py · claude-sonnet-4-6）
    └─ → call_alert_agent   → AlertAgent（alert_agent.py · gpt-4o-mini）
    ↓ _AgentWithMemory session 記憶
UI 層（app.py — Streamlit）
```

---

## 檔案職責

| 檔案 | 職責 |
|------|------|
| `app.py` | Streamlit UI + APScheduler 心跳 + proactive trigger |
| `agent/health_agent.py` | CareAgent：主對話、工具決策、子代理協調 |
| `agent/analysis_agent.py` | AnalysisAgent：健康趨勢深度分析 |
| `agent/alert_agent.py` | AlertAgent：緊急數值評估與通報 |
| `agent/tools.py` | 所有 `@tool` 函式（5 個），所有 Agent 從此 import |
| `agent/prompts.py` | 三個 `build_*_prompt()`，從 `health_profile.json` 動態注入 |
| `agent/memory.py` | `_AgentWithMemory` + `InMemoryChatMessageHistory` session 記憶 |
| `data/mock_sensors.py` | Mock IoT 感測器，支援 `set_simulate_abnormal()` |
| `data/health_profile.json` | 病患靜態資料：姓名、用藥、聯絡人、警報閾值 |
| `data/health_history.json` | 近 30 天生理歷史，供 `get_health_trend` 使用 |

---

## LangChain 1.x 關鍵 API

```python
# 建立 agent（回傳 CompiledStateGraph）
from langchain.agents import create_agent
graph = create_agent(llm, tools=[...], system_prompt="...")

# 呼叫格式（langgraph 格式）
result = graph.invoke({"messages": [HumanMessage(content="...")]})
last = result["messages"][-1]
output = last.content
```

**禁止使用**（已在 LangChain 1.x 移除）：
- `create_tool_calling_agent`
- `RunnableWithMessageHistory`

---

## 循環 import 防護

`AnalysisAgent` 和 `AlertAgent` 的 import 必須放在 `build_agent()` **函式體內**（lazy import）。放在模組頂端會循環 import。

```python
def build_agent():
    from agent.analysis_agent import build_analysis_agent, invoke_analysis_agent  # lazy
    from agent.alert_agent import build_alert_agent, invoke_alert_agent            # lazy
    ...
```

---

## 子代理設計原則

- 子代理（AnalysisAgent、AlertAgent）**不包 memory wrapper**，每次 stateless 呼叫
- 只有 CareAgent 使用 `wrap_with_memory(graph)` 包裝
- 子代理被包成 `@tool` 函式，定義在 `build_agent()` 內部（閉包捕捉 graph）

---

## 參考

詳細說明見 `.claude/reference/multi-agent.md`
