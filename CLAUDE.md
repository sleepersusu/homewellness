# HomeWellness Companion — CLAUDE.md

面試作業：Technical PM（AI & IoT）role。  
一個針對獨居長者的主動式 AI 健康伴侶——整合 IoT 感測器、Multi-Agent、Proactive Trigger。

---

## 快速理解這個專案

**一句話**：APScheduler 每 5 秒輪詢 IoT 數據，異常時自動觸發 CareAgent；長者也可以直接對話。

**資料流**：
```
IoT（mock_sensors.py）
  → APScheduler 每 5 秒輪詢
    → 偵測異常 → pending_proactive → st.rerun()
      → CareAgent（gpt-4o-mini）決策
        ├─ 普通問答 → 直接回應
        ├─ 趨勢分析 → call_analysis_agent → AnalysisAgent（claude-sonnet-4-6）
        └─ 生理異常 → call_alert_agent → AlertAgent（gpt-4o-mini）→ 通報家屬
```

---

## 目錄結構

```
app.py                    # Streamlit UI + APScheduler
agent/
  health_agent.py         # CareAgent（主控 orchestrator）
  analysis_agent.py       # AnalysisAgent（深度趨勢分析）
  alert_agent.py          # AlertAgent（緊急通報）
  tools.py                # 5 個 @tool 函式（所有 agent 共用）
  prompts.py              # 3 個 build_*_prompt() 函式
  memory.py               # _AgentWithMemory（session 記憶）
data/
  mock_sensors.py         # Mock IoT（get_mock_vitals 等）
  health_profile.json     # 病患靜態資料（陳阿嬤）
  health_history.json     # 近 30 天生理歷史
tests/                    # 31 個 pytest 測試
```

---

## 啟動與測試

```bash
# 環境
pip install -r requirements.txt
cp .env.example .env   # 填入 OPENAI_API_KEY, ANTHROPIC_API_KEY

# 啟動
streamlit run app.py

# 測試
pytest tests/ -v
pytest tests/ --cov=agent --cov=data --cov-report=term-missing
```

---

## 關鍵限制與陷阱

### LangChain 1.x API

```python
# 正確
from langchain.agents import create_agent
graph = create_agent(llm, tools=[...], system_prompt="...")
graph.invoke({"messages": [HumanMessage(content="...")]})

# 錯誤（已移除）
from langchain.agents import create_tool_calling_agent
```

### 循環 import 防護

`analysis_agent` 和 `alert_agent` 的 import 必須放在 `build_agent()` 函式**體內**（lazy import）。放在模組頂端會循環 import。

### Mock 異常模擬

```python
from data.mock_sensors import set_simulate_abnormal
set_simulate_abnormal(True)   # 讓 get_mock_vitals() 回傳心率 125、血氧 88
set_simulate_abnormal(False)  # 恢復正常
```

### Memory Wrapper

`RunnableWithMessageHistory` 已 deprecated，使用自建 `_AgentWithMemory`（`agent/memory.py`）。子代理（AnalysisAgent、AlertAgent）**不需要**記憶，只有 CareAgent 包 wrapper。

---

## 參考文件

| 主題 | 文件 |
|------|------|
| 專案結構 & 啟動 | `.claude/reference/project-overview.md` |
| 三代理架構設計 | `.claude/reference/multi-agent.md` |
| 5 個 LangChain 工具 | `.claude/reference/tools.md` |
| Session 記憶實作 | `.claude/reference/memory.md` |
| 三個 System Prompt | `.claude/reference/prompts.md` |
| IoT Mock 資料層 | `.claude/reference/iot-layer.md` |
| Streamlit UI + Scheduler | `.claude/reference/ui-scheduler.md` |

---

## Commit 規範

格式：`type(scope): 繁體中文描述`  
禁止：`Co-Authored-By: Claude` 或任何 AI 署名  
範例：`feat(agent): 新增多代理協調架構`
