# Multi-Agent 架構

## 三個 Agent 的分工

```
CareAgent（首腦）
├── 直接工具：get_vitals / get_sleep_report / get_medication_schedule
├── → call_analysis_agent(query)  →  AnalysisAgent（深度分析）
└── → call_alert_agent(situation) →  AlertAgent（緊急通報）
```

**CareAgent** (`health_agent.py`)
- 模型：`gpt-4o-mini`
- 職責：主對話、工具決策、子代理協調
- 有 session 記憶（`_AgentWithMemory` wrapper）

**AnalysisAgent** (`analysis_agent.py`)
- 模型：預設 `gemini-2.5-flash`（可在 Streamlit sidebar 切換，支援 OpenAI / Gemini）
- 職責：近 N 天趨勢分析、異常模式識別
- 工具：`get_health_trend(days)`
- 無記憶（stateless，每次獨立呼叫）

**AlertAgent** (`alert_agent.py`)
- 模型：`gpt-4o-mini`（快速低延遲，緊急不能等）
- 職責：評估異常數值、決定是否通報、執行通報
- 工具：`get_vitals()` + `send_emergency_alert(reason)`
- 無記憶（stateless）

---

## 關鍵實作細節

### create_agent API（LangChain 1.x）

```python
from langchain.agents import create_agent  # 正確
# 注意：create_tool_calling_agent 在 LangChain 1.x 已移除

graph = create_agent(llm, tools=tool_list, system_prompt="...")
# 回傳 CompiledStateGraph（langgraph）
# 呼叫格式：graph.invoke({"messages": [HumanMessage(content=...)]})
```

### 子代理包裝成工具（避免循環 import）

```python
def build_agent():
    # 必須放在函式體內 lazy import，否則循環 import
    from agent.analysis_agent import build_analysis_agent, invoke_analysis_agent
    from agent.alert_agent import build_alert_agent, invoke_alert_agent

    analysis_graph = build_analysis_agent()
    alert_graph = build_alert_agent()

    @tool
    def call_analysis_agent(query: str) -> str:
        """..."""
        return invoke_analysis_agent(analysis_graph, query)

    @tool
    def call_alert_agent(situation: str) -> str:
        """..."""
        return invoke_alert_agent(alert_graph, situation)
```

### 子代理呼叫格式

```python
def invoke_analysis_agent(graph, query: str) -> str:
    result = graph.invoke({"messages": [HumanMessage(content=query)]})
    last = result["messages"][-1]
    return last.content if hasattr(last, "content") else str(last)
```

### CareAgent（invoke_agent）回傳格式

```python
# invoke_agent 回傳 tuple[str, dict]，stats 含效能數據
text, stats = invoke_agent(agent, user_input, model="gpt-4o-mini")
# stats = {
#   "latency": 1.23,        # 秒
#   "input_tokens": 420,
#   "output_tokens": 85,
#   "total_tokens": 505,
#   "cost_usd": 0.0000863,  # 依 _MODEL_PRICES 計算
#   "model": "gpt-4o-mini",
# }
```

---

## 為什麼這樣設計

| 問題 | 解法 |
|------|------|
| 單一 Agent 上下文過大（5+ 工具同時在 context） | 主代理只掌 3 直接工具，深度任務委派 |
| 健康趨勢分析需要更強的推理 | AnalysisAgent 預設用 gemini-2.5-flash，可切換 |
| 緊急通報要低延遲 | AlertAgent 用 gpt-4o-mini，不走複雜推理 |
| 子代理循環 import | lazy import 放進 build_agent() 函式體 |
| RunnableWithMessageHistory deprecated | 自建 _AgentWithMemory wrapper |
